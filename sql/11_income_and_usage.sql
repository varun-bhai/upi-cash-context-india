-- One-snapshot check: do higher-income states tend to have more PhonePe use?
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/11_income_and_usage.sql

-- 1. Coverage. Two PhonePe geographies are absent because the Economic Survey
-- table does not publish State Domestic Product estimates for them.
SELECT
  (SELECT COUNT(*) FROM state_per_capita_nsdp_snapshot) AS income_snapshot_states_uts,
  (SELECT COUNT(*) FROM v_phonepe_state_q1_2024_with_nsdp) AS matched_phonepe_q1_2024_states_uts,
  (SELECT GROUP_CONCAT(state_name, '; ')
   FROM v_phonepe_state_quarterly_per_capita
   WHERE quarter_start_date = '2024-01-01'
     AND state_slug NOT IN (SELECT state_slug FROM state_per_capita_nsdp_snapshot WHERE financial_year = '2023-24')
  ) AS unmatched_phonepe_states_uts;

-- 2. Cross-state associations. We use the natural log of income because raw
-- rupee values range widely and a few small, high-income UTs would otherwise
-- dominate the comparison. Correlation describes co-movement, not causation.
WITH state_metrics AS (
  SELECT
    p.state_name,
    p.per_capita_nsdp_current_inr,
    LN(p.per_capita_nsdp_current_inr) AS log_per_capita_nsdp,
    p.transactions_per_resident,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_q1_2024_with_nsdp AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  GROUP BY p.state_slug, p.state_name
), averages AS (
  SELECT
    AVG(log_per_capita_nsdp) AS mean_log_income,
    AVG(transactions_per_resident) AS mean_transactions,
    AVG(registered_users_per_resident) AS mean_users,
    AVG(registered_merchants_per_resident) AS mean_merchants,
    AVG(retail_share_pct) AS mean_retail_share
  FROM state_metrics
)
SELECT
  COUNT(*) AS states_uts,
  ROUND(SUM((log_per_capita_nsdp - mean_log_income) * (transactions_per_resident - mean_transactions)) /
    SQRT(SUM((log_per_capita_nsdp - mean_log_income) * (log_per_capita_nsdp - mean_log_income)) *
         SUM((transactions_per_resident - mean_transactions) * (transactions_per_resident - mean_transactions))), 3)
    AS income_vs_transaction_intensity_correlation,
  ROUND(SUM((log_per_capita_nsdp - mean_log_income) * (registered_users_per_resident - mean_users)) /
    SQRT(SUM((log_per_capita_nsdp - mean_log_income) * (log_per_capita_nsdp - mean_log_income)) *
         SUM((registered_users_per_resident - mean_users) * (registered_users_per_resident - mean_users))), 3)
    AS income_vs_user_density_correlation,
  ROUND(SUM((log_per_capita_nsdp - mean_log_income) * (registered_merchants_per_resident - mean_merchants)) /
    SQRT(SUM((log_per_capita_nsdp - mean_log_income) * (log_per_capita_nsdp - mean_log_income)) *
         SUM((registered_merchants_per_resident - mean_merchants) * (registered_merchants_per_resident - mean_merchants))), 3)
    AS income_vs_merchant_density_correlation,
  ROUND(SUM((log_per_capita_nsdp - mean_log_income) * (retail_share_pct - mean_retail_share)) /
    SQRT(SUM((log_per_capita_nsdp - mean_log_income) * (log_per_capita_nsdp - mean_log_income)) *
         SUM((retail_share_pct - mean_retail_share) * (retail_share_pct - mean_retail_share))), 3)
    AS income_vs_retail_share_correlation
FROM state_metrics CROSS JOIN averages;

-- 3. Concrete state profiles. This shows why income is an incomplete story.
WITH state_metrics AS (
  SELECT
    p.state_name,
    p.per_capita_nsdp_current_inr,
    p.transactions_per_resident,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_q1_2024_with_nsdp AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  GROUP BY p.state_slug, p.state_name
)
SELECT
  state_name,
  per_capita_nsdp_current_inr AS income_per_person_inr,
  ROUND(transactions_per_resident, 1) AS transactions_per_resident,
  ROUND(100.0 * registered_users_per_resident, 1) AS registered_users_per_100_residents,
  ROUND(100.0 * registered_merchants_per_resident, 1) AS registered_merchants_per_100_residents,
  ROUND(retail_share_pct, 1) AS retail_share_pct
FROM state_metrics
ORDER BY per_capita_nsdp_current_inr DESC;
