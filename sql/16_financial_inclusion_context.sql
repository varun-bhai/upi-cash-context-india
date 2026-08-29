-- State financial-inclusion context using PMJDY's 19 August 2026 snapshot.
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/16_financial_inclusion_context.sql
--
-- PMJDY beneficiaries are not verified unique people, active bank-account
-- holders, or active UPI users. These are descriptive cross-state checks only.

-- 1. State coverage and the components of the PMJDY snapshot, aligned near
-- PhonePe's 2026 Q2 state quarter.
SELECT
  state_name,
  ROUND(100.0 * pmjdy_beneficiaries_per_resident, 1) AS pmjdy_beneficiaries_per_100_residents,
  ROUND(100.0 * registered_users_per_resident, 1) AS phonepe_registered_users_per_100_residents,
  ROUND(transactions_per_resident, 1) AS phonepe_transactions_per_resident,
  ROUND(100.0 * pmjdy_rupay_cards_per_beneficiary, 1) AS rupay_cards_per_100_pmjdy_beneficiaries,
  ROUND(pmjdy_balance_inr_per_beneficiary, 0) AS pmjdy_balance_inr_per_beneficiary
FROM v_phonepe_state_q2_2026_with_pmjdy
ORDER BY pmjdy_beneficiaries_per_resident DESC;

-- 2. Pearson correlations across the 36 states/UTs. A correlation describes
-- whether two measures move together in this single cross-section; it does
-- not show that one causes the other.
WITH cohort AS (
  SELECT
    pmjdy_beneficiaries_per_resident AS x,
    registered_users_per_resident AS phonepe_user_density,
    transactions_per_resident AS phonepe_transaction_intensity
  FROM v_phonepe_state_q2_2026_with_pmjdy
), moments AS (
  SELECT
    AVG(x) AS mean_x,
    AVG(phonepe_user_density) AS mean_user_density,
    AVG(phonepe_transaction_intensity) AS mean_transaction_intensity,
    AVG(x * phonepe_user_density) AS mean_xy_users,
    AVG(x * phonepe_transaction_intensity) AS mean_xy_transactions,
    AVG(x * x) AS mean_x_squared,
    AVG(phonepe_user_density * phonepe_user_density) AS mean_user_density_squared,
    AVG(phonepe_transaction_intensity * phonepe_transaction_intensity) AS mean_transaction_intensity_squared
  FROM cohort
)
SELECT
  ROUND(
    (mean_xy_users - mean_x * mean_user_density) /
    SQRT((mean_x_squared - mean_x * mean_x) *
         (mean_user_density_squared - mean_user_density * mean_user_density)),
    3
  ) AS correlation_pmjdy_beneficiary_density_vs_phonepe_user_density,
  ROUND(
    (mean_xy_transactions - mean_x * mean_transaction_intensity) /
    SQRT((mean_x_squared - mean_x * mean_x) *
         (mean_transaction_intensity_squared - mean_transaction_intensity * mean_transaction_intensity)),
    3
  ) AS correlation_pmjdy_beneficiary_density_vs_phonepe_transaction_intensity
FROM moments;

-- 3. A deliberately cautious follow-up list: state/UTs in the top half of
-- PMJDY beneficiary density but bottom half of PhonePe registered-user
-- density. This is a prompt to understand conditions locally, not a ranked
-- marketing-spend recommendation.
WITH ranked AS (
  SELECT
    state_name,
    pmjdy_beneficiaries_per_resident,
    registered_users_per_resident,
    transactions_per_resident,
    NTILE(2) OVER (ORDER BY pmjdy_beneficiaries_per_resident DESC) AS pmjdy_density_half,
    NTILE(2) OVER (ORDER BY registered_users_per_resident ASC) AS phonepe_user_density_half
  FROM v_phonepe_state_q2_2026_with_pmjdy
)
SELECT
  state_name,
  ROUND(100.0 * pmjdy_beneficiaries_per_resident, 1) AS pmjdy_beneficiaries_per_100_residents,
  ROUND(100.0 * registered_users_per_resident, 1) AS phonepe_registered_users_per_100_residents,
  ROUND(transactions_per_resident, 1) AS phonepe_transactions_per_resident,
  'Investigate local onboarding, device access, and merchant acceptance; do not infer cause from this table.' AS next_question
FROM ranked
WHERE pmjdy_density_half = 1
  AND phonepe_user_density_half = 1
ORDER BY pmjdy_beneficiaries_per_resident DESC;
