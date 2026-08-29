-- Remaining core portfolio questions from the original project brief.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/14_core_portfolio_questions.sql

-- 1. Which states/UTs led by PhonePe transaction value in the latest quarter?
WITH latest AS (
  SELECT MAX(quarter_start_date) AS quarter_start_date
  FROM v_phonepe_state_quarterly
)
SELECT
  q.quarter_start_date,
  q.state_name,
  ROUND(q.transaction_value_inr / 1000000000000.0, 2) AS transaction_value_inr_trillion,
  ROUND(q.transaction_count / 1000000.0, 1) AS transaction_count_mn
FROM v_phonepe_state_quarterly AS q
JOIN latest AS l ON l.quarter_start_date = q.quarter_start_date
ORDER BY q.transaction_value_inr DESC
LIMIT 10;

-- 2. Latest same-quarter year-on-year state growth in both transaction count
-- and value. This compares 2026 Q2 to 2025 Q2, so the seasonal quarter is the
-- same. It is PhonePe activity, not all-UPI activity in a state.
WITH current AS (
  SELECT * FROM v_phonepe_state_quarterly
  WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly)
), previous AS (
  SELECT * FROM v_phonepe_state_quarterly
  WHERE quarter_start_date = date((SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly), '-1 year')
)
SELECT
  c.state_name,
  ROUND(c.transaction_count / 1000000.0, 1) AS latest_transactions_mn,
  ROUND(100.0 * (1.0 * c.transaction_count / p.transaction_count - 1), 1) AS transaction_count_yoy_pct,
  ROUND(100.0 * (1.0 * c.transaction_value_inr / p.transaction_value_inr - 1), 1) AS transaction_value_yoy_pct
FROM current AS c
JOIN previous AS p ON p.state_slug = c.state_slug
ORDER BY transaction_count_yoy_pct DESC;

-- 3. Rolling four-quarter state growth. This smooths a single quarter's noise:
-- for each state we compare the total from 2025 Q3--2026 Q2 with the total
-- from 2024 Q3--2025 Q2.
WITH rolling AS (
  SELECT
    state_slug,
    state_name,
    quarter_start_date,
    SUM(transaction_count) OVER (
      PARTITION BY state_slug ORDER BY quarter_start_date
      ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS transactions_rolling_4q,
    SUM(transaction_value_inr) OVER (
      PARTITION BY state_slug ORDER BY quarter_start_date
      ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS value_rolling_4q
  FROM v_phonepe_state_quarterly
), comparison AS (
  SELECT
    *,
    LAG(transactions_rolling_4q, 4) OVER (PARTITION BY state_slug ORDER BY quarter_start_date) AS transactions_rolling_4q_year_ago,
    LAG(value_rolling_4q, 4) OVER (PARTITION BY state_slug ORDER BY quarter_start_date) AS value_rolling_4q_year_ago
  FROM rolling
)
SELECT
  state_name,
  ROUND(transactions_rolling_4q / 1000000.0, 1) AS latest_4q_transactions_mn,
  ROUND(100.0 * (1.0 * transactions_rolling_4q / transactions_rolling_4q_year_ago - 1), 1) AS rolling_4q_transaction_growth_pct,
  ROUND(100.0 * (1.0 * value_rolling_4q / value_rolling_4q_year_ago - 1), 1) AS rolling_4q_value_growth_pct
FROM comparison
WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly)
ORDER BY rolling_4q_transaction_growth_pct DESC;

-- 4. Adoption tiers. We rank the same rolling four-quarter growth rate into
-- three relative groups: the top nine state/UTs are High, the bottom nine are
-- Low, and the middle 18 are Medium. This is a portfolio segmentation rule,
-- not a statement about an objectively good or bad growth rate.
WITH rolling AS (
  SELECT
    state_slug,
    state_name,
    quarter_start_date,
    SUM(transaction_count) OVER (
      PARTITION BY state_slug ORDER BY quarter_start_date
      ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS transactions_rolling_4q
  FROM v_phonepe_state_quarterly
), comparison AS (
  SELECT
    *,
    LAG(transactions_rolling_4q, 4) OVER (PARTITION BY state_slug ORDER BY quarter_start_date) AS transactions_rolling_4q_year_ago
  FROM rolling
), latest AS (
  SELECT
    state_name,
    transactions_rolling_4q,
    100.0 * (1.0 * transactions_rolling_4q / transactions_rolling_4q_year_ago - 1) AS rolling_4q_transaction_growth_pct,
    NTILE(4) OVER (ORDER BY 1.0 * transactions_rolling_4q / transactions_rolling_4q_year_ago) AS growth_quartile
  FROM comparison
  WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly)
)
SELECT
  state_name,
  ROUND(transactions_rolling_4q / 1000000.0, 1) AS latest_4q_transactions_mn,
  ROUND(rolling_4q_transaction_growth_pct, 1) AS rolling_4q_transaction_growth_pct,
  CASE
    WHEN growth_quartile = 4 THEN 'High growth'
    WHEN growth_quartile = 1 THEN 'Low growth'
    ELSE 'Medium growth'
  END AS adoption_growth_tier
FROM latest
ORDER BY growth_quartile DESC, rolling_4q_transaction_growth_pct DESC;

-- 5. Did the per-resident transaction ranking change? A per-resident ranking
-- compares different-sized states fairly. Positive rank change means a state
-- moved nearer to rank 1 between 2025 Q2 and 2026 Q2.
WITH selected AS (
  SELECT
    state_name,
    quarter_start_date,
    transactions_per_resident,
    DENSE_RANK() OVER (PARTITION BY quarter_start_date ORDER BY transactions_per_resident DESC) AS intensity_rank
  FROM v_phonepe_state_quarterly_per_capita
  WHERE quarter_start_date IN ('2025-04-01', '2026-04-01')
), ranks AS (
  SELECT
    state_name,
    MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN intensity_rank END) AS rank_2025_q2,
    MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN intensity_rank END) AS rank_2026_q2,
    MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN transactions_per_resident END) AS transactions_per_resident_2025_q2,
    MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN transactions_per_resident END) AS transactions_per_resident_2026_q2
  FROM selected
  GROUP BY state_name
)
SELECT
  state_name,
  rank_2025_q2,
  rank_2026_q2,
  rank_2025_q2 - rank_2026_q2 AS rank_change_up_is_positive,
  ROUND(transactions_per_resident_2026_q2, 1) AS transactions_per_resident_2026_q2
FROM ranks
ORDER BY rank_change_up_is_positive DESC, rank_2026_q2;

-- 6. National rolling trend: how did all-UPI and NFS ATM cash-access volume
-- change over the last available four-quarter period in the RBI-derived data?
WITH quarterly AS (
  SELECT
    quarter_start_date,
    upi_volume_lakh,
    nfs_atm_volume_lakh,
    SUM(upi_volume_lakh) OVER (ORDER BY quarter_start_date ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS upi_rolling_4q_lakh,
    SUM(nfs_atm_volume_lakh) OVER (ORDER BY quarter_start_date ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS nfs_atm_rolling_4q_lakh
  FROM v_national_payment_quarterly_pivot
), comparison AS (
  SELECT
    *,
    LAG(upi_rolling_4q_lakh, 4) OVER (ORDER BY quarter_start_date) AS upi_rolling_4q_lakh_year_ago,
    LAG(nfs_atm_rolling_4q_lakh, 4) OVER (ORDER BY quarter_start_date) AS nfs_atm_rolling_4q_lakh_year_ago
  FROM quarterly
)
SELECT
  quarter_start_date AS latest_quarter_available,
  ROUND(upi_rolling_4q_lakh / 100.0, 1) AS latest_4q_upi_transactions_bn,
  ROUND(100.0 * (1.0 * upi_rolling_4q_lakh / upi_rolling_4q_lakh_year_ago - 1), 1) AS upi_rolling_4q_growth_pct,
  ROUND(nfs_atm_rolling_4q_lakh / 100.0, 1) AS latest_4q_nfs_atm_withdrawals_bn,
  ROUND(100.0 * (1.0 * nfs_atm_rolling_4q_lakh / nfs_atm_rolling_4q_lakh_year_ago - 1), 1) AS nfs_atm_rolling_4q_growth_pct
FROM comparison
WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_national_payment_quarterly_pivot);
