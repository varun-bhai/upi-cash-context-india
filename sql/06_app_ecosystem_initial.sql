-- First look at the official NPCI national UPI-app data.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/06_app_ecosystem_initial.sql

-- 1. Coverage and missing month check.
SELECT COUNT(*) AS app_month_rows,
       COUNT(DISTINCT app_name) AS distinct_app_names,
       MIN(month_start_date) AS first_month,
       MAX(month_start_date) AS last_month
FROM national_upi_app_monthly;

-- 2. A like-for-like January comparison: PhonePe, Google Pay, and Paytm.
WITH selected AS (
  SELECT month_start_date, app_name, total_volume_mn, volume_market_share_pct
  FROM v_national_upi_app_monthly
  WHERE month_start_date IN ('2022-01-01', '2026-01-01')
    AND app_name IN ('PhonePe', 'Google Pay', 'Paytm')
)
SELECT month_start_date,
       app_name,
       ROUND(total_volume_mn, 2) AS volume_million,
       ROUND(volume_market_share_pct, 2) AS volume_share_pct
FROM selected
ORDER BY month_start_date, volume_million DESC;

-- 3. Change in market share. Percentage points are used for shares: a move
-- from 15% to 8% is a -7 point change, not a confusing -47% share change.
WITH selected AS (
  SELECT month_start_date, app_name, volume_market_share_pct
  FROM v_national_upi_app_monthly
  WHERE month_start_date IN ('2022-01-01', '2026-01-01')
    AND app_name IN ('PhonePe', 'Google Pay', 'Paytm')
), paired AS (
  SELECT app_name,
         MAX(CASE WHEN month_start_date = '2022-01-01' THEN volume_market_share_pct END) AS share_2022,
         MAX(CASE WHEN month_start_date = '2026-01-01' THEN volume_market_share_pct END) AS share_2026
  FROM selected
  GROUP BY app_name
)
SELECT app_name,
       ROUND(share_2022, 2) AS share_jan_2022_pct,
       ROUND(share_2026, 2) AS share_jan_2026_pct,
       ROUND(share_2026 - share_2022, 2) AS change_percentage_points
FROM paired
ORDER BY change_percentage_points DESC;

-- 4. Latest available month: the leading apps by volume.
SELECT month_start_date,
       app_name,
       ROUND(total_volume_mn, 2) AS volume_million,
       ROUND(volume_market_share_pct, 2) AS volume_share_pct
FROM v_national_upi_app_monthly
WHERE month_start_date = (SELECT MAX(month_start_date) FROM v_national_upi_app_monthly)
ORDER BY total_volume_mn DESC
LIMIT 10;
