-- Practical business questions for a UPI app, using the latest complete
-- PhonePe state/UT quarter in this project (currently 2026 Q2).
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/12_business_opportunity_signals.sql

-- 1. Check the latest period and whether the operational measures are complete.
SELECT
  quarter_start_date AS latest_quarter_start,
  COUNT(*) AS states_uts,
  SUM(registered_users IS NOT NULL) AS states_uts_with_users,
  SUM(registered_merchants IS NOT NULL) AS states_uts_with_merchants
FROM v_phonepe_state_quarterly_per_capita
WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly_per_capita);

-- 2. Turn three practical questions into transparent state-level signals:
--    a) Existing users but relatively few transactions per registered user?
--       -> investigate user activation, repeat use, or local use cases.
--    b) Many registered users but relatively few merchants and Retail payments?
--       -> investigate merchant acceptance/onboarding.
--    c) Large, high-use markets?
--       -> protect reliability and customer/merchant experience.
-- Quartiles are comparison groups, not proof of an opportunity or a directive.
WITH latest AS (
  SELECT
    p.state_name,
    p.population_persons,
    p.transaction_count,
    p.registered_users,
    p.registered_merchants,
    p.transactions_per_resident,
    p.registered_users_per_resident,
    p.registered_merchants_per_resident,
    1.0 * p.transaction_count / NULLIF(p.registered_users, 0) AS transactions_per_registered_user,
    100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END)
      / SUM(t.transaction_count) AS retail_share_pct
  FROM v_phonepe_state_quarterly_per_capita AS p
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = p.state_slug
   AND t.quarter_start_date = p.quarter_start_date
  WHERE p.quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly_per_capita)
  GROUP BY p.state_slug, p.state_name
), ranked AS (
  SELECT
    *,
    NTILE(4) OVER (ORDER BY registered_users_per_resident) AS user_density_quartile,
    NTILE(4) OVER (ORDER BY transactions_per_registered_user) AS transactions_per_user_quartile,
    NTILE(4) OVER (ORDER BY registered_merchants_per_resident) AS merchant_density_quartile,
    NTILE(4) OVER (ORDER BY retail_share_pct) AS retail_share_quartile,
    NTILE(4) OVER (ORDER BY transaction_count) AS transaction_scale_quartile
  FROM latest
)
SELECT
  state_name,
  ROUND(100.0 * registered_users_per_resident, 1) AS registered_users_per_100_residents,
  ROUND(transactions_per_registered_user, 1) AS transactions_per_registered_user,
  ROUND(100.0 * registered_merchants_per_resident, 1) AS merchants_per_100_residents,
  ROUND(retail_share_pct, 1) AS retail_share_pct,
  ROUND(transaction_count / 1000000.0, 1) AS quarterly_transactions_mn,
  CASE
    WHEN user_density_quartile >= 3 AND transactions_per_user_quartile <= 2
      AND merchant_density_quartile <= 2 AND retail_share_quartile <= 2
      THEN 'Investigate both activation and merchant acceptance'
    WHEN user_density_quartile >= 3 AND transactions_per_user_quartile <= 2
      THEN 'Investigate activation of existing registered users'
    WHEN user_density_quartile >= 3 AND merchant_density_quartile <= 2 AND retail_share_quartile <= 2
      THEN 'Investigate merchant acceptance/onboarding'
    WHEN transaction_scale_quartile >= 3 AND transactions_per_user_quartile >= 3
      THEN 'Protect high-use core market experience'
    ELSE 'Monitor; validate with local and product data'
  END AS business_question_to_investigate
FROM ranked
ORDER BY
  CASE business_question_to_investigate
    WHEN 'Investigate both activation and merchant acceptance' THEN 1
    WHEN 'Investigate activation of existing registered users' THEN 2
    WHEN 'Investigate merchant acceptance/onboarding' THEN 3
    WHEN 'Protect high-use core market experience' THEN 4
    ELSE 5
  END,
  quarterly_transactions_mn DESC;

-- 3. A business-facing summary: count states/UTs in each signal group.
WITH latest AS (
  SELECT
    p.state_slug,
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
  WHERE p.quarter_start_date = (SELECT MAX(quarter_start_date) FROM v_phonepe_state_quarterly_per_capita)
  GROUP BY p.state_slug
), ranked AS (
  SELECT
    *,
    NTILE(4) OVER (ORDER BY registered_users_per_resident) AS user_density_quartile,
    NTILE(4) OVER (ORDER BY transactions_per_registered_user) AS transactions_per_user_quartile,
    NTILE(4) OVER (ORDER BY registered_merchants_per_resident) AS merchant_density_quartile,
    NTILE(4) OVER (ORDER BY retail_share_pct) AS retail_share_quartile,
    NTILE(4) OVER (ORDER BY transaction_count) AS transaction_scale_quartile
  FROM latest
), labelled AS (
  SELECT CASE
    WHEN user_density_quartile >= 3 AND transactions_per_user_quartile <= 2
      AND merchant_density_quartile <= 2 AND retail_share_quartile <= 2
      THEN 'Activation + merchant acceptance'
    WHEN user_density_quartile >= 3 AND transactions_per_user_quartile <= 2
      THEN 'Activation of existing users'
    WHEN user_density_quartile >= 3 AND merchant_density_quartile <= 2 AND retail_share_quartile <= 2
      THEN 'Merchant acceptance/onboarding'
    WHEN transaction_scale_quartile >= 3 AND transactions_per_user_quartile >= 3
      THEN 'Protect high-use core experience'
    ELSE 'Monitor and validate locally'
  END AS business_signal
  FROM ranked
)
SELECT business_signal, COUNT(*) AS states_uts
FROM labelled
GROUP BY business_signal
ORDER BY states_uts DESC, business_signal;
