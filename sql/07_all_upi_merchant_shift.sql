-- Is the PhonePe Retail shift part of a wider all-UPI merchant-payment shift?
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/07_all_upi_merchant_shift.sql

-- 1. Source coverage and quality. The one warning is a September 2023 source
-- total that differs from P2P + P2M by 1 million transactions; fields remain
-- unchanged and the report documents it.
SELECT COUNT(*) AS monthly_rows,
       MIN(month_start_date) AS first_month,
       MAX(month_start_date) AS last_month
FROM national_upi_p2p_p2m_monthly;

-- 2. Compare like-for-like full quarters. P2M and PhonePe Retail are related
-- merchant-payment concepts but not guaranteed to be identical classifications.
WITH national_quarterly AS (
  SELECT printf('%04d-Q%d', year, ((month - 1) / 3) + 1) AS period,
         100.0 * SUM(p2m_volume_mn) / SUM(total_volume_mn) AS p2m_share_pct
  FROM national_upi_p2p_p2m_monthly
  WHERE month_start_date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY year, ((month - 1) / 3)
), phonepe_quarterly AS (
  SELECT printf('%04d-Q%d', year, CAST(SUBSTR(quarter, 2) AS INTEGER)) AS period,
         100.0 * SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS retail_share_pct
  FROM phonepe_state_transactions
  WHERE quarter_start_date BETWEEN '2022-01-01' AND '2026-01-01'
  GROUP BY year, quarter
)
SELECT n.period,
       ROUND(n.p2m_share_pct, 1) AS all_upi_p2m_share_pct,
       ROUND(p.retail_share_pct, 1) AS phonepe_retail_share_pct
FROM national_quarterly AS n
JOIN phonepe_quarterly AS p USING (period)
ORDER BY n.period;

-- 3. Endpoint summary for that common period.
WITH national_quarterly AS (
  SELECT printf('%04d-Q%d', year, ((month - 1) / 3) + 1) AS period,
         100.0 * SUM(p2m_volume_mn) / SUM(total_volume_mn) AS p2m_share_pct
  FROM national_upi_p2p_p2m_monthly
  WHERE month_start_date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY year, ((month - 1) / 3)
), phonepe_quarterly AS (
  SELECT printf('%04d-Q%d', year, CAST(SUBSTR(quarter, 2) AS INTEGER)) AS period,
         100.0 * SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS retail_share_pct
  FROM phonepe_state_transactions
  WHERE quarter_start_date BETWEEN '2022-01-01' AND '2026-01-01'
  GROUP BY year, quarter
)
SELECT 'All UPI P2M share' AS measure,
       ROUND(MAX(CASE WHEN period = '2022-Q1' THEN p2m_share_pct END), 1) AS share_2022_q1_pct,
       ROUND(MAX(CASE WHEN period = '2026-Q1' THEN p2m_share_pct END), 1) AS share_2026_q1_pct,
       ROUND(MAX(CASE WHEN period = '2026-Q1' THEN p2m_share_pct END) - MAX(CASE WHEN period = '2022-Q1' THEN p2m_share_pct END), 1) AS change_percentage_points
FROM national_quarterly
UNION ALL
SELECT 'PhonePe Retail share',
       ROUND(MAX(CASE WHEN period = '2022-Q1' THEN retail_share_pct END), 1),
       ROUND(MAX(CASE WHEN period = '2026-Q1' THEN retail_share_pct END), 1),
       ROUND(MAX(CASE WHEN period = '2026-Q1' THEN retail_share_pct END) - MAX(CASE WHEN period = '2022-Q1' THEN retail_share_pct END), 1)
FROM phonepe_quarterly;
