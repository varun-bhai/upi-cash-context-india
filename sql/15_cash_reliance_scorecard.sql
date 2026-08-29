-- National Cash Reliance Scorecard
-- Run with:
-- sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/15_cash_reliance_scorecard.sql
--
-- RBI Table 41 contains annual-average monetary aggregates.  The payment
-- figures are annual totals made from four complete calendar quarters.  They
-- are put side by side as national context, never as evidence that UPI caused
-- a change in cash use.

-- 1. The complete matched financial years and their component measures.
SELECT
  financial_year,
  ROUND(currency_with_public_crore / 100000.0, 2) AS currency_with_public_lakh_crore,
  ROUND(demand_deposits_crore / 100000.0, 2) AS demand_deposits_lakh_crore,
  ROUND(currency_to_demand_deposits_ratio, 3) AS cash_to_demand_deposits_ratio,
  complete_quarters,
  ROUND(upi_volume_lakh / 10000.0, 2) AS all_upi_transactions_bn,
  ROUND(upi_average_ticket_inr, 0) AS all_upi_average_ticket_inr,
  ROUND(nfs_atm_volume_lakh / 10000.0, 2) AS nfs_atm_withdrawals_bn,
  ROUND(nfs_atm_average_withdrawal_inr, 0) AS nfs_atm_average_withdrawal_inr
FROM v_national_cash_reliance_with_upi
ORDER BY financial_year;

-- 2. How did the two endpoints change? This uses FY 2021-22 and FY 2023-24,
-- the first and last financial years with all four payment quarters present.
WITH paired AS (
  SELECT *
  FROM v_national_cash_reliance_with_upi
  WHERE financial_year IN ('2021-22', '2023-24')
), endpoints AS (
  SELECT
    MAX(CASE WHEN financial_year = '2021-22' THEN currency_with_public_crore END) AS currency_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN currency_with_public_crore END) AS currency_end,
    MAX(CASE WHEN financial_year = '2021-22' THEN demand_deposits_crore END) AS deposits_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN demand_deposits_crore END) AS deposits_end,
    MAX(CASE WHEN financial_year = '2021-22' THEN currency_to_demand_deposits_ratio END) AS ratio_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN currency_to_demand_deposits_ratio END) AS ratio_end,
    MAX(CASE WHEN financial_year = '2021-22' THEN upi_volume_lakh END) AS upi_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN upi_volume_lakh END) AS upi_end,
    MAX(CASE WHEN financial_year = '2021-22' THEN upi_average_ticket_inr END) AS ticket_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN upi_average_ticket_inr END) AS ticket_end,
    MAX(CASE WHEN financial_year = '2021-22' THEN nfs_atm_volume_lakh END) AS nfs_start,
    MAX(CASE WHEN financial_year = '2023-24' THEN nfs_atm_volume_lakh END) AS nfs_end
  FROM paired
)
SELECT
  'FY 2021-22 to FY 2023-24' AS comparison_window,
  ROUND(100.0 * (currency_end / currency_start - 1), 1) AS currency_with_public_change_pct,
  ROUND(100.0 * (deposits_end / deposits_start - 1), 1) AS demand_deposits_change_pct,
  ROUND(100.0 * (ratio_end / ratio_start - 1), 1) AS cash_to_demand_deposits_ratio_change_pct,
  ROUND(100.0 * (upi_end / upi_start - 1), 1) AS all_upi_transaction_volume_change_pct,
  ROUND(100.0 * (ticket_end / ticket_start - 1), 1) AS all_upi_average_ticket_change_pct,
  ROUND(100.0 * (nfs_end / nfs_start - 1), 1) AS nfs_atm_withdrawal_volume_change_pct
FROM endpoints;

-- 3. Longer monetary context. This has seven years, rather than the three
-- matched years above, because it comes entirely from RBI Table 41.
SELECT
  financial_year,
  ROUND(currency_to_demand_deposits_ratio, 3) AS cash_to_demand_deposits_ratio,
  ROUND(100.0 * currency_with_public_crore / demand_deposits_crore, 1) AS cash_per_100_demand_deposit_rupees
FROM national_cash_reliance_annual
ORDER BY financial_year;
