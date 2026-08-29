#!/usr/bin/env python3
"""Load the project's cleaned CSVs into a reproducible SQLite database."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data/processed"
SCHEMA_PATH = PROJECT_ROOT / "sql/01_schema.sql"
DEFAULT_DATABASE = PROJECT_ROOT / "data/upi_cash_displacement.sqlite"

TABLES = (
    (
        "phonepe_state_transactions",
        "phonepe_state_transaction_quarterly.csv",
        ("state_slug", "state_name", "year", "quarter", "quarter_start_date", "source_category", "transaction_count", "transaction_value_inr", "source_file"),
        "INSERT INTO phonepe_state_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "phonepe_state_users",
        "phonepe_state_user_quarterly.csv",
        ("state_slug", "state_name", "year", "quarter", "quarter_start_date", "registered_count", "source_file"),
        "INSERT INTO phonepe_state_users VALUES (?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "phonepe_state_merchants",
        "phonepe_state_merchant_quarterly.csv",
        ("state_slug", "state_name", "year", "quarter", "quarter_start_date", "registered_count", "source_file"),
        "INSERT INTO phonepe_state_merchants VALUES (?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "population_state_annual",
        "population_state_annual.csv",
        (
            "state_slug", "state_name", "year", "population_persons",
            "source_state_or_aggregation", "source_table", "source_date_basis",
            "source_url", "method_note",
        ),
        "INSERT INTO population_state_annual VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "state_internet_subscribers_snapshot",
        "trai_state_internet_subscribers_june_2024.csv",
        (
            "as_of_date", "state_slug", "state_name", "rural_subscribers_mn",
            "urban_subscribers_mn", "total_subscribers_mn",
            "rural_subscribers_per_100_population", "urban_subscribers_per_100_population",
            "total_subscribers_per_100_population", "source_table", "source_url",
            "interpretation_note",
        ),
        "INSERT INTO state_internet_subscribers_snapshot VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "state_per_capita_nsdp_snapshot",
        "economic_survey_state_per_capita_nsdp_fy2023_24.csv",
        (
            "financial_year", "state_slug", "state_name", "per_capita_nsdp_current_inr",
            "price_basis", "series_base_year", "source_table", "source_url", "availability_note",
        ),
        "INSERT INTO state_per_capita_nsdp_snapshot VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "state_pmjdy_financial_inclusion_snapshot",
        "pmjdy_state_financial_inclusion_2026_08_19.csv",
        (
            "as_of_date", "state_slug", "state_name",
            "beneficiaries_rural_semiurban_count", "beneficiaries_urban_metro_count",
            "total_beneficiaries_count", "balance_in_beneficiary_accounts_crore",
            "rupay_debit_cards_issued_count", "source_table", "source_url",
            "interpretation_note",
        ),
        "INSERT INTO state_pmjdy_financial_inclusion_snapshot VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "national_payment_quarterly",
        "idp_rbi_national_payment_indicators_quarterly.csv",
        ("year", "quarter", "quarter_start_date", "payment_mode", "months_included", "days_observed", "volume_lakh", "value_crore"),
        "INSERT INTO national_payment_quarterly VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "national_cash_reliance_annual",
        "rbi_annual_cash_reliance.csv",
        (
            "financial_year", "currency_with_public_crore", "demand_deposits_crore",
            "currency_to_demand_deposits_ratio", "source_table", "source_url",
            "time_basis", "interpretation_note",
        ),
        "INSERT INTO national_cash_reliance_annual VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "national_upi_app_monthly",
        "npci_upi_app_monthly.csv",
        (
            "year", "month", "month_start_date", "app_name",
            "customer_initiated_volume_mn", "customer_initiated_value_crore",
            "b2c_volume_mn", "b2c_value_crore", "b2b_volume_mn", "b2b_value_crore",
            "total_volume_mn", "total_value_crore", "source_reference",
        ),
        "INSERT INTO national_upi_app_monthly VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
    (
        "national_upi_p2p_p2m_monthly",
        "npci_upi_p2p_p2m_monthly.csv",
        (
            "year", "month", "month_start_date", "total_volume_mn", "total_value_crore",
            "p2p_volume_mn", "p2p_value_crore", "p2m_volume_mn", "p2m_value_crore",
            "source_p2p_share_pct", "source_p2m_share_pct", "source_reference",
        ),
        "INSERT INTO national_upi_p2p_p2m_monthly VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ),
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    return parser.parse_args()


def convert(column: str, value: str) -> object:
    if column == "quarter" and value in {"1", "2", "3", "4"}:
        # PhonePe's CSV retains the numeric source label; the database uses the
        # same Q1–Q4 convention as the national RBI-derived table.
        return f"Q{value}"
    if column in {
        "year", "transaction_count", "registered_count", "population_persons",
        "per_capita_nsdp_current_inr", "months_included", "days_observed",
        "beneficiaries_rural_semiurban_count", "beneficiaries_urban_metro_count",
        "total_beneficiaries_count", "rupay_debit_cards_issued_count",
    }:
        return int(value)
    if column in {
        "transaction_value_inr", "volume_lakh", "value_crore",
        "rural_subscribers_mn", "urban_subscribers_mn", "total_subscribers_mn",
        "rural_subscribers_per_100_population", "urban_subscribers_per_100_population",
        "total_subscribers_per_100_population",
        "customer_initiated_volume_mn", "customer_initiated_value_crore",
        "b2c_volume_mn", "b2c_value_crore", "b2b_volume_mn", "b2b_value_crore",
        "total_volume_mn", "total_value_crore",
        "p2p_volume_mn", "p2p_value_crore", "p2m_volume_mn", "p2m_value_crore",
        "source_p2p_share_pct", "source_p2m_share_pct",
        "currency_with_public_crore", "demand_deposits_crore", "currency_to_demand_deposits_ratio",
        "balance_in_beneficiary_accounts_crore",
    }:
        if value == "":
            return None
        return float(value)
    return value


def rows_from_csv(path: Path, columns: tuple[str, ...]) -> list[tuple[object, ...]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(columns).issubset(reader.fieldnames):
            raise ValueError(f"{path.name} does not have the expected columns: {columns}")
        return [tuple(convert(column, row[column]) for column in columns) for row in reader]


def main() -> None:
    args = arguments()
    database = args.database.resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        counts: list[tuple[str, int]] = []
        for table, filename, columns, insert_sql in TABLES:
            rows = rows_from_csv(PROCESSED_DIR / filename, columns)
            connection.executemany(insert_sql, rows)
            counts.append((table, len(rows)))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    print(f"Created {database}")
    for table, count in counts:
        print(f"  {table}: {count:,} rows")


if __name__ == "__main__":
    main()
