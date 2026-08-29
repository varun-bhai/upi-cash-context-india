-- Per-resident inspection and convergence check.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/08_per_capita_adoption.sql

-- 1. Coverage: every PhonePe state-quarter must have an official population
-- denominator before we compare states per resident.
SELECT
  (SELECT COUNT(*) FROM v_phonepe_state_quarterly) AS phonepe_state_quarters,
  (SELECT COUNT(*) FROM v_phonepe_state_quarterly_per_capita) AS matched_state_quarters,
  (SELECT COUNT(*) FROM population_state_annual) AS annual_population_rows;

-- 2. Which larger states and smaller states had the highest transaction
-- intensity at the beginning and later in the series? This is a rate, not a
-- statement that each resident is a unique PhonePe user.
SELECT
  quarter_start_date,
  state_name,
  ROUND(transactions_per_resident, 1) AS transactions_per_resident,
  ROUND(100.0 * registered_users_per_resident, 1) AS registered_users_per_100_residents,
  ROUND(100.0 * registered_merchants_per_resident, 1) AS registered_merchants_per_100_residents
FROM v_phonepe_state_quarterly_per_capita
WHERE quarter_start_date IN ('2018-01-01', '2025-01-01')
ORDER BY quarter_start_date, transactions_per_resident DESC;

-- 3. Sigma convergence: the standard deviation of log intensity across states.
-- A lower number means a measure is becoming less unequal. This describes a
-- pattern; it does not explain why it happened.
WITH intensities AS (
  SELECT quarter_start_date,
         'transactions_per_resident' AS measure,
         LN(transactions_per_resident) AS log_intensity
  FROM v_phonepe_state_quarterly_per_capita
  WHERE transactions_per_resident > 0
  UNION ALL
  SELECT quarter_start_date,
         'registered_users_per_resident' AS measure,
         LN(registered_users_per_resident) AS log_intensity
  FROM v_phonepe_state_quarterly_per_capita
  WHERE registered_users_per_resident > 0
), moments AS (
  SELECT quarter_start_date, measure,
         AVG(log_intensity) AS mean_log_intensity,
         AVG(log_intensity * log_intensity) AS mean_square_log_intensity,
         COUNT(*) AS states_uts
  FROM intensities
  GROUP BY quarter_start_date, measure
)
SELECT
  quarter_start_date,
  measure,
  states_uts,
  ROUND(SQRT(mean_square_log_intensity - mean_log_intensity * mean_log_intensity), 3) AS sigma_log_intensity
FROM moments
ORDER BY measure, quarter_start_date;
