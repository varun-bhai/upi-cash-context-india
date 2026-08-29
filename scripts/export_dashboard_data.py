#!/usr/bin/env python3
"""Export small, chart-ready CSV tables from the project's SQLite database.

These files are presentation inputs only. Their calculations remain in the
database/schema and this script so a Power BI, Tableau, or spreadsheet
dashboard does not need hand-edited totals.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data/upi_cash_displacement.sqlite"
OUTPUT_DIR = PROJECT_ROOT / "data/dashboard"

QUERIES = {
    "national_quarterly_payments_context.csv": """
        WITH base AS (
            SELECT
                quarter_start_date,
                year,
                quarter,
                upi_volume_lakh,
                upi_value_crore,
                nfs_atm_volume_lakh,
                nfs_atm_value_crore
            FROM v_national_payment_quarterly_pivot
        ), baseline AS (
            SELECT upi_volume_lakh AS upi_baseline, nfs_atm_volume_lakh AS nfs_baseline
            FROM base
            ORDER BY quarter_start_date
            LIMIT 1
        )
        SELECT
            b.quarter_start_date,
            b.year,
            b.quarter,
            b.upi_volume_lakh / 100.0 AS all_upi_transactions_bn,
            b.upi_value_crore AS all_upi_value_crore,
            100.0 * b.upi_value_crore / b.upi_volume_lakh AS all_upi_average_ticket_inr,
            b.nfs_atm_volume_lakh / 100.0 AS nfs_atm_withdrawals_bn,
            b.nfs_atm_value_crore AS nfs_atm_withdrawal_value_crore,
            100.0 * b.nfs_atm_value_crore / b.nfs_atm_volume_lakh AS nfs_atm_average_withdrawal_inr,
            100.0 * b.upi_volume_lakh / baseline.upi_baseline AS all_upi_volume_index_first_quarter_100,
            100.0 * b.nfs_atm_volume_lakh / baseline.nfs_baseline AS nfs_atm_volume_index_first_quarter_100
        FROM base AS b
        CROSS JOIN baseline
        ORDER BY b.quarter_start_date;
    """,
    "national_annual_cash_reliance.csv": """
        SELECT
            financial_year,
            currency_with_public_crore,
            demand_deposits_crore,
            currency_to_demand_deposits_ratio,
            100.0 * currency_with_public_crore / demand_deposits_crore AS currency_per_100_demand_deposit_rupees,
            time_basis
        FROM national_cash_reliance_annual
        ORDER BY financial_year;
    """,
    "national_payment_mix_quarterly.csv": """
        WITH phonepe AS (
            SELECT
                quarter_start_date,
                year,
                quarter,
                100.0 * SUM(CASE WHEN source_category = 'P2P' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS phonepe_p2p_share_pct,
                100.0 * SUM(CASE WHEN source_category = 'Retail' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS phonepe_retail_share_pct,
                100.0 * SUM(CASE WHEN source_category = 'Utility' THEN transaction_count ELSE 0 END) / SUM(transaction_count) AS phonepe_utility_share_pct
            FROM phonepe_state_transactions
            GROUP BY quarter_start_date, year, quarter
        ), all_upi AS (
            SELECT
                printf('%04d-Q%d', year, ((month - 1) / 3) + 1) AS period,
                100.0 * SUM(p2m_volume_mn) / SUM(total_volume_mn) AS all_upi_p2m_share_pct
            FROM national_upi_p2p_p2m_monthly
            GROUP BY year, ((month - 1) / 3)
        )
        SELECT
            p.quarter_start_date,
            p.year,
            p.quarter,
            p.phonepe_p2p_share_pct,
            p.phonepe_retail_share_pct,
            p.phonepe_utility_share_pct,
            a.all_upi_p2m_share_pct
        FROM phonepe AS p
        LEFT JOIN all_upi AS a
            ON a.period = printf('%04d-Q%d', p.year, CAST(SUBSTR(p.quarter, 2) AS INTEGER))
        ORDER BY p.quarter_start_date;
    """,
    "state_scale_growth_business_signals.csv": """
        WITH state_metrics AS (
            SELECT
                p.state_slug,
                p.state_name,
                p.quarter_start_date,
                p.transaction_count,
                p.transaction_value_inr,
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
            GROUP BY p.state_slug, p.state_name, p.quarter_start_date
        ), rolling_base AS (
            SELECT
                state_slug,
                quarter_start_date,
                SUM(transaction_count) OVER (
                    PARTITION BY state_slug ORDER BY quarter_start_date
                    ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
                ) AS transactions_rolling_4q
            FROM v_phonepe_state_quarterly
        ), rolling AS (
            SELECT
                *,
                LAG(transactions_rolling_4q, 4) OVER (
                    PARTITION BY state_slug ORDER BY quarter_start_date
                ) AS transactions_rolling_4q_year_ago
            FROM rolling_base
        ), latest_ranked AS (
            SELECT
                m.*,
                NTILE(4) OVER (ORDER BY registered_users_per_resident) AS user_density_quartile,
                NTILE(4) OVER (ORDER BY transactions_per_registered_user) AS transactions_per_user_quartile,
                NTILE(4) OVER (ORDER BY registered_merchants_per_resident) AS merchant_density_quartile,
                NTILE(4) OVER (ORDER BY retail_share_pct) AS retail_share_quartile,
                NTILE(4) OVER (ORDER BY transaction_count) AS transaction_scale_quartile
            FROM state_metrics AS m
            WHERE quarter_start_date = (SELECT MAX(quarter_start_date) FROM state_metrics)
        ), prior AS (
            SELECT state_slug, transaction_count
            FROM state_metrics
            WHERE quarter_start_date = date((SELECT MAX(quarter_start_date) FROM state_metrics), '-1 year')
        )
        SELECT
            l.state_slug,
            l.state_name,
            l.quarter_start_date AS latest_quarter_start_date,
            l.transaction_count / 1000000.0 AS latest_quarter_transactions_mn,
            l.transaction_value_inr / 1000000000000.0 AS latest_quarter_transaction_value_inr_trillion,
            100.0 * (1.0 * l.transaction_count / prior.transaction_count - 1) AS transaction_count_yoy_pct,
            r.transactions_rolling_4q / 1000000.0 AS latest_rolling_4q_transactions_mn,
            100.0 * (1.0 * r.transactions_rolling_4q / r.transactions_rolling_4q_year_ago - 1) AS rolling_4q_transaction_growth_pct,
            l.transactions_per_resident,
            100.0 * l.registered_users_per_resident AS registered_users_per_100_residents,
            l.transactions_per_registered_user,
            100.0 * l.registered_merchants_per_resident AS merchants_per_100_residents,
            l.retail_share_pct,
            CASE
                WHEN l.user_density_quartile >= 3 AND l.transactions_per_user_quartile <= 2
                  AND l.merchant_density_quartile <= 2 AND l.retail_share_quartile <= 2
                  THEN 'Investigate both activation and merchant acceptance'
                WHEN l.user_density_quartile >= 3 AND l.transactions_per_user_quartile <= 2
                  THEN 'Investigate activation of existing registered users'
                WHEN l.user_density_quartile >= 3 AND l.merchant_density_quartile <= 2 AND l.retail_share_quartile <= 2
                  THEN 'Investigate merchant acceptance/onboarding'
                WHEN l.transaction_scale_quartile >= 3 AND l.transactions_per_user_quartile >= 3
                  THEN 'Protect high-use core market experience'
                ELSE 'Monitor; validate with local and product data'
            END AS business_question_to_investigate
        FROM latest_ranked AS l
        JOIN prior ON prior.state_slug = l.state_slug
        JOIN rolling AS r
            ON r.state_slug = l.state_slug
           AND r.quarter_start_date = l.quarter_start_date
        ORDER BY l.transaction_count DESC;
    """,
}

EXPECTED_ROWS = {
    "national_quarterly_payments_context.csv": 19,
    "national_annual_cash_reliance.csv": 7,
    "national_payment_mix_quarterly.csv": 34,
    "state_scale_growth_business_signals.csv": 36,
}


def export_table(connection: sqlite3.Connection, filename: str, query: str) -> int:
    cursor = connection.execute(query)
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"Dashboard query returned no rows: {filename}")
    if len(rows) != EXPECTED_ROWS[filename]:
        raise ValueError(f"Dashboard query returned {len(rows)} rows for {filename}; expected {EXPECTED_ROWS[filename]}")
    fields = [column[0] for column in cursor.description]
    with (OUTPUT_DIR / filename).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Missing project database: {DATABASE_PATH}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        counts = {filename: export_table(connection, filename, query) for filename, query in QUERIES.items()}
    finally:
        connection.close()
    manifest = {
        "purpose": "Dashboard-ready, presentation-layer CSVs exported from the reproducible SQLite database.",
        "database": str(DATABASE_PATH.relative_to(PROJECT_ROOT)),
        "tables": counts,
        "warnings": [
            "NFS ATM withdrawals are a national cash-access proxy, not total cash use.",
            "Currency-to-demand-deposits is an annual national monetary-context ratio, not cash spending or causal evidence.",
            "PhonePe state measures are not all-UPI state totals.",
            "Business signals are prompts for investigation, not investment recommendations.",
        ],
    }
    with (OUTPUT_DIR / "dashboard_data_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    print("Created dashboard data exports:")
    for filename, count in counts.items():
        print(f"  {filename}: {count} rows")


if __name__ == "__main__":
    main()
