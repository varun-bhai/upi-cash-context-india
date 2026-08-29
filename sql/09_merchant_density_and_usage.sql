-- Does higher PhonePe merchant density line up with higher usage intensity?
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/09_merchant_density_and_usage.sql

-- 1. Data availability. Missing merchant records are retained as missing; the
-- later 2019+ period has every state/UT available for fair comparisons.
SELECT
  quarter_start_date,
  COUNT(*) AS state_quarters,
  SUM(CASE WHEN registered_merchants IS NOT NULL THEN 1 ELSE 0 END) AS merchant_records_present
FROM v_phonepe_state_quarterly_per_capita
GROUP BY quarter_start_date
ORDER BY quarter_start_date;

-- 2. Same-quarter association across states in 2025 Q1. Pearson correlation
-- is descriptive: it cannot tell us whether merchants caused usage or whether
-- high-usage places attracted more merchants.
WITH state_metrics AS (
  SELECT
    p.state_name,
    p.transactions_per_resident,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_quarterly_per_capita AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  WHERE p.quarter_start_date = '2025-01-01'
    AND p.registered_merchants_per_resident IS NOT NULL
  GROUP BY p.state_slug, p.state_name
), averages AS (
  SELECT
    AVG(transactions_per_resident) AS mean_transactions,
    AVG(registered_users_per_resident) AS mean_users,
    AVG(registered_merchants_per_resident) AS mean_merchants,
    AVG(retail_share_pct) AS mean_retail_share
  FROM state_metrics
)
SELECT
  COUNT(*) AS states_uts,
  ROUND(
    SUM((registered_merchants_per_resident - mean_merchants) * (transactions_per_resident - mean_transactions)) /
    SQRT(SUM((registered_merchants_per_resident - mean_merchants) * (registered_merchants_per_resident - mean_merchants)) *
         SUM((transactions_per_resident - mean_transactions) * (transactions_per_resident - mean_transactions))), 3
  ) AS merchant_density_vs_transaction_intensity_correlation,
  ROUND(
    SUM((registered_users_per_resident - mean_users) * (transactions_per_resident - mean_transactions)) /
    SQRT(SUM((registered_users_per_resident - mean_users) * (registered_users_per_resident - mean_users)) *
         SUM((transactions_per_resident - mean_transactions) * (transactions_per_resident - mean_transactions))), 3
  ) AS user_density_vs_transaction_intensity_correlation,
  ROUND(
    SUM((registered_merchants_per_resident - mean_merchants) * (retail_share_pct - mean_retail_share)) /
    SQRT(SUM((registered_merchants_per_resident - mean_merchants) * (registered_merchants_per_resident - mean_merchants)) *
         SUM((retail_share_pct - mean_retail_share) * (retail_share_pct - mean_retail_share))), 3
  ) AS merchant_density_vs_retail_share_correlation
FROM state_metrics CROSS JOIN averages;

-- 3. Do states that added more merchant density also tend to increase usage
-- intensity more? This compares log changes from 2020 Q1 to 2025 Q1. It is
-- still an association and has no controls for income, internet, or other
-- factors that could move both measures.
WITH observations AS (
  SELECT
    state_slug,
    MAX(CASE WHEN quarter_start_date = '2020-01-01' THEN transactions_per_resident END) AS transactions_2020,
    MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN transactions_per_resident END) AS transactions_2025,
    MAX(CASE WHEN quarter_start_date = '2020-01-01' THEN registered_users_per_resident END) AS users_2020,
    MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN registered_users_per_resident END) AS users_2025,
    MAX(CASE WHEN quarter_start_date = '2020-01-01' THEN registered_merchants_per_resident END) AS merchants_2020,
    MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN registered_merchants_per_resident END) AS merchants_2025
  FROM v_phonepe_state_quarterly_per_capita
  WHERE quarter_start_date IN ('2020-01-01', '2025-01-01')
  GROUP BY state_slug
), changes AS (
  SELECT
    LN(transactions_2025 / transactions_2020) AS log_change_transactions,
    LN(users_2025 / users_2020) AS log_change_users,
    LN(merchants_2025 / merchants_2020) AS log_change_merchants
  FROM observations
  WHERE transactions_2020 > 0 AND users_2020 > 0 AND merchants_2020 > 0
), averages AS (
  SELECT AVG(log_change_transactions) AS mean_transactions,
         AVG(log_change_users) AS mean_users,
         AVG(log_change_merchants) AS mean_merchants
  FROM changes
)
SELECT
  COUNT(*) AS states_uts,
  ROUND(
    SUM((log_change_merchants - mean_merchants) * (log_change_transactions - mean_transactions)) /
    SQRT(SUM((log_change_merchants - mean_merchants) * (log_change_merchants - mean_merchants)) *
         SUM((log_change_transactions - mean_transactions) * (log_change_transactions - mean_transactions))), 3
  ) AS merchant_density_growth_vs_transaction_growth_correlation,
  ROUND(
    SUM((log_change_users - mean_users) * (log_change_transactions - mean_transactions)) /
    SQRT(SUM((log_change_users - mean_users) * (log_change_users - mean_users)) *
         SUM((log_change_transactions - mean_transactions) * (log_change_transactions - mean_transactions))), 3
  ) AS user_density_growth_vs_transaction_growth_correlation
FROM changes CROSS JOIN averages;

-- 4. Concrete examples: states with the most registered PhonePe merchants per
-- 100 residents in 2025 Q1, alongside their usage intensity and Retail share.
WITH state_metrics AS (
  SELECT
    p.state_name,
    p.transactions_per_resident,
    p.registered_merchants_per_resident,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_quarterly_per_capita AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  WHERE p.quarter_start_date = '2025-01-01'
  GROUP BY p.state_slug, p.state_name
)
SELECT
  state_name,
  ROUND(100.0 * registered_merchants_per_resident, 2) AS registered_merchants_per_100_residents,
  ROUND(transactions_per_resident, 1) AS transactions_per_resident,
  ROUND(retail_share_pct, 1) AS retail_share_pct
FROM state_metrics
ORDER BY registered_merchants_per_resident DESC
LIMIT 10;
