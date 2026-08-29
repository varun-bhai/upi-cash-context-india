-- Follow-up investigation: PhonePe Retail-share shift and merchant context.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/04_retail_shift_deep_dive.sql

-- 1. The raw dataset uses the same three category labels throughout the series.
-- This verifies label continuity, not necessarily that the provider's internal
-- definitions never changed.
SELECT source_category,
       COUNT(*) AS state_quarter_category_rows,
       COUNT(DISTINCT quarter_start_date) AS quarters_present,
       MIN(quarter_start_date) AS first_quarter,
       MAX(quarter_start_date) AS last_quarter
FROM phonepe_state_transactions
GROUP BY source_category
ORDER BY source_category;

-- 2. Is the Retail-share shift broad?
WITH state_shares AS (
  SELECT state_slug, state_name, quarter_start_date,
         SUM(transaction_count) AS total_count,
         SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) AS retail_count
  FROM phonepe_state_transactions
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY state_slug, state_name, quarter_start_date
), paired AS (
  SELECT state_slug,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN 100.0 * retail_count / total_count END) AS early_retail_share,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN 100.0 * retail_count / total_count END) AS later_retail_share
  FROM state_shares
  GROUP BY state_slug
)
SELECT COUNT(*) AS states_uts,
       SUM(later_retail_share > early_retail_share) AS share_increased,
       ROUND(AVG(later_retail_share - early_retail_share), 1) AS average_change_percentage_points
FROM paired;

-- 3. Merchant records are complete in this comparison window if this returns
-- zero rows. A missing merchant record must never be interpreted as zero.
SELECT quarter_start_date,
       COUNT(*) AS states_with_transactions,
       SUM(registered_merchants IS NOT NULL) AS states_with_merchant_data
FROM v_phonepe_state_quarterly
WHERE quarter_start_date BETWEEN '2020-07-01' AND '2025-01-01'
GROUP BY quarter_start_date
HAVING states_with_transactions <> states_with_merchant_data;

-- 4. Is a larger *absolute* rise in registered PhonePe merchants associated
-- with a larger Retail-share change? Pearson correlation here is descriptive
-- only; it does not identify a causal relationship.
WITH state_period AS (
  SELECT q.state_slug, q.state_name, q.quarter_start_date,
         100.0 * SUM(CASE WHEN t.source_category = 'Retail' THEN t.transaction_count ELSE 0 END) / SUM(t.transaction_count) AS retail_share,
         q.registered_merchants
  FROM v_phonepe_state_quarterly AS q
  JOIN phonepe_state_transactions AS t
    ON t.state_slug = q.state_slug AND t.quarter_start_date = q.quarter_start_date
  WHERE q.quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY q.state_slug, q.state_name, q.quarter_start_date, q.registered_merchants
), paired AS (
  SELECT state_slug,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN retail_share END) AS early_retail_share,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN retail_share END) AS later_retail_share,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN registered_merchants END) AS early_merchants,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN registered_merchants END) AS later_merchants
  FROM state_period
  GROUP BY state_slug
), changes AS (
  SELECT later_retail_share - early_retail_share AS retail_share_change_points,
         later_merchants - early_merchants AS additional_merchants
  FROM paired
), moments AS (
  SELECT AVG(retail_share_change_points) AS avg_retail_change,
         AVG(additional_merchants) AS avg_merchant_additions
  FROM changes
)
SELECT COUNT(*) AS states_uts,
       ROUND(
         SUM((retail_share_change_points - avg_retail_change) * (additional_merchants - avg_merchant_additions)) /
         SQRT(
           SUM((retail_share_change_points - avg_retail_change) * (retail_share_change_points - avg_retail_change)) *
           SUM((additional_merchants - avg_merchant_additions) * (additional_merchants - avg_merchant_additions))
         ),
         3
       ) AS pearson_correlation
FROM changes CROSS JOIN moments;
