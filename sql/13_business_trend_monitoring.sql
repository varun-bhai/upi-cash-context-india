-- Business monitoring question: from 2025 Q2 to 2026 Q2, did state-level
-- usage, user reach, merchant reach, and Retail mix improve or weaken?
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/13_business_trend_monitoring.sql

WITH state_quarter_metrics AS (
  SELECT
    p.state_slug,
    p.state_name,
    p.quarter_start_date,
    p.transaction_count,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    1.0 * p.transaction_count / NULLIF(p.registered_users, 0) AS transactions_per_registered_user,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_quarterly_per_capita AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  WHERE p.quarter_start_date IN ('2025-04-01', '2026-04-01')
  GROUP BY p.state_slug, p.state_name, p.quarter_start_date
), comparison AS (
  SELECT
    current.state_name,
    current.transaction_count AS transactions_2026_q2,
    previous.transaction_count AS transactions_2025_q2,
    current.registered_users_per_resident AS user_density_2026_q2,
    previous.registered_users_per_resident AS user_density_2025_q2,
    current.registered_merchants_per_resident AS merchant_density_2026_q2,
    previous.registered_merchants_per_resident AS merchant_density_2025_q2,
    current.transactions_per_registered_user AS transactions_per_user_2026_q2,
    previous.transactions_per_registered_user AS transactions_per_user_2025_q2,
    current.retail_share_pct AS retail_share_2026_q2,
    previous.retail_share_pct AS retail_share_2025_q2
  FROM state_quarter_metrics AS current
  JOIN state_quarter_metrics AS previous
    ON previous.state_slug = current.state_slug
   AND previous.quarter_start_date = '2025-04-01'
  WHERE current.quarter_start_date = '2026-04-01'
)
SELECT
  state_name,
  ROUND(transactions_2026_q2 / 1000000.0, 1) AS transactions_2026_q2_mn,
  ROUND(100.0 * (1.0 * transactions_2026_q2 / NULLIF(transactions_2025_q2, 0) - 1), 1) AS transactions_yoy_pct,
  ROUND(100.0 * user_density_2026_q2, 1) AS users_per_100_2026_q2,
  ROUND(100.0 * (user_density_2026_q2 / NULLIF(user_density_2025_q2, 0) - 1), 1) AS user_density_yoy_pct,
  ROUND(transactions_per_user_2026_q2, 1) AS transactions_per_user_2026_q2,
  ROUND(100.0 * (transactions_per_user_2026_q2 / NULLIF(transactions_per_user_2025_q2, 0) - 1), 1) AS transactions_per_user_yoy_pct,
  ROUND(100.0 * merchant_density_2026_q2, 1) AS merchants_per_100_2026_q2,
  ROUND(100.0 * (merchant_density_2026_q2 / NULLIF(merchant_density_2025_q2, 0) - 1), 1) AS merchant_density_yoy_pct,
  ROUND(retail_share_2026_q2 - retail_share_2025_q2, 1) AS retail_share_yoy_change_pp
FROM comparison
ORDER BY transactions_2026_q2 DESC;

-- Summarise the national pattern represented by the 36 state/UT rows. This is
-- a PhonePe total, not all-UPI India. Values are weighted by transactions.
WITH state_quarter_metrics AS (
  SELECT
    p.quarter_start_date,
    p.transaction_count,
    p.registered_users,
    p.registered_merchants,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_quarterly_per_capita AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  WHERE p.quarter_start_date IN ('2025-04-01', '2026-04-01')
  GROUP BY p.state_slug, p.quarter_start_date
), aggregate AS (
  SELECT
    quarter_start_date,
    SUM(transaction_count) AS transactions,
    SUM(registered_users) AS registered_users,
    SUM(registered_merchants) AS registered_merchants,
    SUM(transaction_count * retail_share_pct) / SUM(transaction_count) AS weighted_retail_share_pct
  FROM state_quarter_metrics
  GROUP BY quarter_start_date
)
SELECT
  ROUND(100.0 * (1.0 * MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN transactions END) /
                 MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN transactions END) - 1), 1)
    AS phonepe_transactions_yoy_pct,
  ROUND(100.0 * (1.0 * MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN registered_users END) /
                 MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN registered_users END) - 1), 1)
    AS registered_users_yoy_pct,
  ROUND(100.0 * (1.0 * MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN registered_merchants END) /
                 MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN registered_merchants END) - 1), 1)
    AS registered_merchants_yoy_pct,
  ROUND(MAX(CASE WHEN quarter_start_date = '2026-04-01' THEN weighted_retail_share_pct END) -
        MAX(CASE WHEN quarter_start_date = '2025-04-01' THEN weighted_retail_share_pct END), 1)
    AS retail_share_yoy_change_pp
FROM aggregate;
