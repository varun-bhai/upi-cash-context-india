-- Exploratory SQL: use these results to decide what to investigate next.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/03_exploratory_patterns.sql

-- Question 1: In the common 2020 Q3–2025 Q1 window, how did national UPI and
-- NFS-at-ATM activity change? NFS is a cash-access proxy, not all cash use.
WITH bounds AS (
  SELECT MIN(quarter_start_date) AS first_q, MAX(quarter_start_date) AS last_q
  FROM v_national_payment_quarterly_pivot
)
SELECT
  b.first_q,
  b.last_q,
  ROUND(first.upi_volume_lakh, 2) AS first_upi_lakh,
  ROUND(last.upi_volume_lakh, 2) AS last_upi_lakh,
  ROUND(100.0 * (last.upi_volume_lakh / first.upi_volume_lakh - 1), 1) AS upi_volume_change_pct,
  ROUND(first.nfs_atm_volume_lakh, 2) AS first_nfs_lakh,
  ROUND(last.nfs_atm_volume_lakh, 2) AS last_nfs_lakh,
  ROUND(100.0 * (last.nfs_atm_volume_lakh / first.nfs_atm_volume_lakh - 1), 1) AS nfs_volume_change_pct
FROM bounds AS b
JOIN v_national_payment_quarterly_pivot AS first ON first.quarter_start_date = b.first_q
JOIN v_national_payment_quarterly_pivot AS last ON last.quarter_start_date = b.last_q;

-- Question 2: Did the mix of PhonePe transaction categories change?
WITH totals AS (
  SELECT quarter_start_date, SUM(transaction_count) AS total_count
  FROM phonepe_state_transactions
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY quarter_start_date
)
SELECT t.quarter_start_date,
       t.source_category,
       ROUND(SUM(t.transaction_count) / 1000000.0, 1) AS transactions_million,
       ROUND(100.0 * SUM(t.transaction_count) / totals.total_count, 1) AS transaction_share_pct
FROM phonepe_state_transactions AS t
JOIN totals ON totals.quarter_start_date = t.quarter_start_date
WHERE t.quarter_start_date IN ('2020-07-01', '2025-01-01')
GROUP BY t.quarter_start_date, t.source_category
ORDER BY t.quarter_start_date, transaction_share_pct DESC;

-- Question 3: Which states are largest on PhonePe at the last common quarter?
SELECT state_name,
       ROUND(transaction_count / 1000000.0, 2) AS transactions_million,
       ROUND(transaction_value_inr / 10000000000.0, 2) AS value_ten_billion_inr,
       ROUND(registered_users / 1000000.0, 2) AS registered_users_million
FROM v_phonepe_state_quarterly
WHERE quarter_start_date = '2025-01-01'
ORDER BY transaction_count DESC
LIMIT 10;

-- Question 4: Which sizeable states had the fastest PhonePe transaction growth?
-- We require at least 100,000 starting transactions to avoid tiny bases
-- dominating the ranking.
WITH endpoints AS (
  SELECT state_slug, state_name, quarter_start_date, transaction_count,
         ROW_NUMBER() OVER (PARTITION BY state_slug ORDER BY quarter_start_date) AS first_rank,
         ROW_NUMBER() OVER (PARTITION BY state_slug ORDER BY quarter_start_date DESC) AS last_rank
  FROM v_phonepe_state_quarterly
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
), paired AS (
  SELECT state_slug, MAX(state_name) AS state_name,
         MAX(CASE WHEN first_rank = 1 THEN transaction_count END) AS first_count,
         MAX(CASE WHEN last_rank = 1 THEN transaction_count END) AS last_count
  FROM endpoints
  GROUP BY state_slug
)
SELECT state_name,
       ROUND(first_count / 1000000.0, 3) AS first_transactions_million,
       ROUND(last_count / 1000000.0, 3) AS last_transactions_million,
       ROUND(100.0 * (last_count * 1.0 / first_count - 1), 1) AS growth_pct
FROM paired
WHERE first_count >= 100000
ORDER BY growth_pct DESC
LIMIT 10;

-- Question 5: Where are there most PhonePe transactions relative to registered
-- PhonePe users? This is a platform activity ratio, not a population measure.
SELECT state_name,
       ROUND(1.0 * transaction_count / registered_users, 1) AS transactions_per_registered_user,
       ROUND(transaction_count / 1000000.0, 1) AS total_transactions_million,
       ROUND(registered_users / 1000000.0, 1) AS registered_users_million
FROM v_phonepe_state_quarterly
WHERE quarter_start_date = '2025-01-01'
  AND registered_users >= 1000000
ORDER BY transactions_per_registered_user DESC
LIMIT 12;

-- Question 6: Was the Retail-share increase broad across states/UTs, or only
-- caused by a few large states? A change in percentage points is more useful
-- here than a percentage growth rate for a share.
WITH state_shares AS (
  SELECT state_slug, state_name, quarter_start_date,
         SUM(transaction_count) AS total_count,
         SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) AS retail_count
  FROM phonepe_state_transactions
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY state_slug, state_name, quarter_start_date
), paired AS (
  SELECT state_slug, MAX(state_name) AS state_name,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN 100.0 * retail_count / total_count END) AS early_retail_share,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN 100.0 * retail_count / total_count END) AS later_retail_share
  FROM state_shares
  GROUP BY state_slug
)
SELECT COUNT(*) AS states_uts,
       SUM(later_retail_share > early_retail_share) AS share_increased,
       SUM(later_retail_share <= early_retail_share) AS share_not_increased,
       ROUND(AVG(later_retail_share - early_retail_share), 1) AS average_change_percentage_points
FROM paired;

WITH state_shares AS (
  SELECT state_slug, state_name, quarter_start_date,
         SUM(transaction_count) AS total_count,
         SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) AS retail_count
  FROM phonepe_state_transactions
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY state_slug, state_name, quarter_start_date
), paired AS (
  SELECT state_slug, MAX(state_name) AS state_name,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN 100.0 * retail_count / total_count END) AS early_retail_share,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN 100.0 * retail_count / total_count END) AS later_retail_share
  FROM state_shares
  GROUP BY state_slug
)
SELECT state_name,
       ROUND(early_retail_share, 1) AS retail_share_2020_q3_pct,
       ROUND(later_retail_share, 1) AS retail_share_2025_q1_pct,
       ROUND(later_retail_share - early_retail_share, 1) AS change_percentage_points
FROM paired
ORDER BY change_percentage_points DESC
LIMIT 10;
