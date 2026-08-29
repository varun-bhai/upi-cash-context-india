-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/02_initial_inspection.sql

-- 1. Does each table have the expected number of rows and time coverage?
SELECT 'phonepe_state_transactions' AS table_name,
       COUNT(*) AS rows,
       MIN(quarter_start_date) AS first_quarter,
       MAX(quarter_start_date) AS last_quarter
FROM phonepe_state_transactions
UNION ALL
SELECT 'phonepe_state_users', COUNT(*), MIN(quarter_start_date), MAX(quarter_start_date)
FROM phonepe_state_users
UNION ALL
SELECT 'phonepe_state_merchants', COUNT(*), MIN(quarter_start_date), MAX(quarter_start_date)
FROM phonepe_state_merchants
UNION ALL
SELECT 'national_payment_quarterly', COUNT(*), MIN(quarter_start_date), MAX(quarter_start_date)
FROM national_payment_quarterly;

-- 2. PhonePe transaction categories: exact labels and row counts.
SELECT source_category,
       COUNT(*) AS state_quarter_rows,
       MIN(quarter_start_date) AS first_quarter,
       MAX(quarter_start_date) AS last_quarter
FROM phonepe_state_transactions
GROUP BY source_category
ORDER BY source_category;

-- 3. State/UT coverage. All should have 34 transaction quarters.
SELECT state_name,
       COUNT(DISTINCT quarter_start_date) AS transaction_quarters,
       MIN(quarter_start_date) AS first_quarter,
       MAX(quarter_start_date) AS last_quarter
FROM phonepe_state_transactions
GROUP BY state_slug, state_name
ORDER BY transaction_quarters, state_name;

-- 4. The first five complete national quarters. NFS-at-ATM is a cash-access
-- proxy only; do not describe it as all cash use.
SELECT quarter_start_date,
       ROUND(upi_volume_lakh, 2) AS upi_volume_lakh,
       ROUND(imps_volume_lakh, 2) AS imps_volume_lakh,
       ROUND(nfs_atm_volume_lakh, 2) AS nfs_atm_volume_lakh
FROM v_national_payment_quarterly_pivot
ORDER BY quarter_start_date
LIMIT 5;

-- 5. A completeness check: merchant data has known early gaps. NULL means
-- missing source data, not zero merchants.
SELECT COUNT(*) AS state_quarter_rows,
       SUM(registered_merchants IS NULL) AS rows_without_merchant_data,
       SUM(registered_users IS NULL) AS rows_without_user_data
FROM v_phonepe_state_quarterly;
