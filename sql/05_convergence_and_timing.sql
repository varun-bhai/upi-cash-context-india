-- Follow-up investigation: convergence and timing of PhonePe Retail-share change.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/05_convergence_and_timing.sql

-- 1. Convergence test: did a lower starting Retail share predict a bigger later
-- increase? A strongly negative correlation would support the catch-up idea.
WITH state_shares AS (
  SELECT state_slug, state_name, quarter_start_date,
         100.0 * SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS retail_share
  FROM phonepe_state_transactions
  WHERE quarter_start_date IN ('2020-07-01', '2025-01-01')
  GROUP BY state_slug, state_name, quarter_start_date
), paired AS (
  SELECT state_slug,
         MAX(CASE WHEN quarter_start_date = '2020-07-01' THEN retail_share END) AS starting_retail_share,
         MAX(CASE WHEN quarter_start_date = '2025-01-01' THEN retail_share END) AS ending_retail_share
  FROM state_shares
  GROUP BY state_slug
), changes AS (
  SELECT starting_retail_share,
         ending_retail_share - starting_retail_share AS retail_share_change_points
  FROM paired
), moments AS (
  SELECT AVG(starting_retail_share) AS avg_start,
         AVG(retail_share_change_points) AS avg_change
  FROM changes
)
SELECT COUNT(*) AS states_uts,
       ROUND(
         SUM((starting_retail_share - avg_start) * (retail_share_change_points - avg_change)) /
         SQRT(
           SUM((starting_retail_share - avg_start) * (starting_retail_share - avg_start)) *
           SUM((retail_share_change_points - avg_change) * (retail_share_change_points - avg_change))
         ),
         3
       ) AS correlation_starting_share_vs_change_points
FROM changes CROSS JOIN moments;

-- 2. When did the national PhonePe Retail share change most from one quarter
-- to the next? This identifies periods for later contextual research.
WITH national_mix AS (
  SELECT quarter_start_date,
         100.0 * SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS retail_share_pct
  FROM phonepe_state_transactions
  WHERE quarter_start_date BETWEEN '2020-07-01' AND '2025-01-01'
  GROUP BY quarter_start_date
), changes AS (
  SELECT quarter_start_date,
         retail_share_pct,
         retail_share_pct - LAG(retail_share_pct) OVER (ORDER BY quarter_start_date) AS change_points_from_previous_quarter
  FROM national_mix
)
SELECT quarter_start_date,
       ROUND(retail_share_pct, 1) AS retail_share_pct,
       ROUND(change_points_from_previous_quarter, 1) AS change_points_from_previous_quarter
FROM changes
WHERE change_points_from_previous_quarter IS NOT NULL
ORDER BY ABS(change_points_from_previous_quarter) DESC
LIMIT 8;
