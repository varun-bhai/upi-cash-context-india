-- One-snapshot check: does state internet-subscription density line up with
-- PhonePe usage in the same April-June 2024 quarter?
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/10_internet_access_and_usage.sql

-- 1. Verify that the one June-2024 TRAI snapshot matches every state/UT in the
-- relevant PhonePe quarter.
SELECT
  (SELECT COUNT(*) FROM state_internet_subscribers_snapshot) AS internet_snapshot_states_uts,
  (SELECT COUNT(*) FROM v_phonepe_state_q2_2024_with_internet) AS matched_phonepe_q2_2024_states_uts;

-- 2. Same-quarter cross-state associations. Internet subscriptions can exceed
-- population because subscriptions are not unique people. The result is a
-- descriptive correlation, not an estimate of causal internet impact.
WITH state_metrics AS (
  SELECT
    p.state_name,
    p.internet_subscribers_per_100_population,
    p.transactions_per_resident,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_q2_2024_with_internet AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  GROUP BY p.state_slug, p.state_name
), averages AS (
  SELECT
    AVG(internet_subscribers_per_100_population) AS mean_internet,
    AVG(transactions_per_resident) AS mean_transactions,
    AVG(registered_users_per_resident) AS mean_users,
    AVG(registered_merchants_per_resident) AS mean_merchants,
    AVG(retail_share_pct) AS mean_retail_share
  FROM state_metrics
)
SELECT
  COUNT(*) AS states_uts,
  ROUND(
    SUM((internet_subscribers_per_100_population - mean_internet) * (transactions_per_resident - mean_transactions)) /
    SQRT(SUM((internet_subscribers_per_100_population - mean_internet) * (internet_subscribers_per_100_population - mean_internet)) *
         SUM((transactions_per_resident - mean_transactions) * (transactions_per_resident - mean_transactions))), 3
  ) AS internet_vs_transaction_intensity_correlation,
  ROUND(
    SUM((internet_subscribers_per_100_population - mean_internet) * (registered_users_per_resident - mean_users)) /
    SQRT(SUM((internet_subscribers_per_100_population - mean_internet) * (internet_subscribers_per_100_population - mean_internet)) *
         SUM((registered_users_per_resident - mean_users) * (registered_users_per_resident - mean_users))), 3
  ) AS internet_vs_user_density_correlation,
  ROUND(
    SUM((internet_subscribers_per_100_population - mean_internet) * (registered_merchants_per_resident - mean_merchants)) /
    SQRT(SUM((internet_subscribers_per_100_population - mean_internet) * (internet_subscribers_per_100_population - mean_internet)) *
         SUM((registered_merchants_per_resident - mean_merchants) * (registered_merchants_per_resident - mean_merchants))), 3
  ) AS internet_vs_merchant_density_correlation,
  ROUND(
    SUM((internet_subscribers_per_100_population - mean_internet) * (retail_share_pct - mean_retail_share)) /
    SQRT(SUM((internet_subscribers_per_100_population - mean_internet) * (internet_subscribers_per_100_population - mean_internet)) *
         SUM((retail_share_pct - mean_retail_share) * (retail_share_pct - mean_retail_share))), 3
  ) AS internet_vs_retail_share_correlation
FROM state_metrics CROSS JOIN averages;

-- 3. Concrete examples. A high subscription density is not guaranteed to mean
-- high PhonePe intensity, which helps prevent an over-simple interpretation.
SELECT
  state_name,
  ROUND(internet_subscribers_per_100_population, 1) AS internet_subscribers_per_100_population,
  ROUND(transactions_per_resident, 1) AS transactions_per_resident,
  ROUND(100.0 * registered_users_per_resident, 1) AS registered_users_per_100_residents,
  ROUND(100.0 * registered_merchants_per_resident, 1) AS registered_merchants_per_100_residents
FROM v_phonepe_state_q2_2024_with_internet
ORDER BY internet_subscribers_per_100_population DESC
LIMIT 12;
