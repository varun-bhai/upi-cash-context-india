#!/usr/bin/env python3
"""Extract a clean national monthly UPI-app table from a validated NPCI reference snapshot."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DB = PROJECT_ROOT / "data/raw/npci_upi_analytics_reference/staging/npci_upi.db"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
REFERENCE_REPOSITORY = "https://github.com/luckisalive/npci_upi_analytics"
REFERENCE_COMMIT = "5c007daef0b69f30dd8e555c548ba6f3bd85c43f"

FIELDS = (
    "year", "month", "month_start_date", "app_name",
    "customer_initiated_volume_mn", "customer_initiated_value_crore",
    "b2c_volume_mn", "b2c_value_crore", "b2b_volume_mn", "b2b_value_crore",
    "total_volume_mn", "total_value_crore", "source_reference",
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-db", type=Path, default=REFERENCE_DB)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    reference_db = args.reference_db.resolve()
    if not reference_db.is_file():
        raise FileNotFoundError(f"Missing reference snapshot: {reference_db}")
    connection = sqlite3.connect(f"file:{reference_db}?mode=ro", uri=True)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(stg_upi_apps)")}
        expected = {
            "app_name", "cit_volume_mn", "cit_value_cr", "b2c_volume_mn", "b2c_value_cr",
            "b2b_volume_mn", "b2b_value_cr", "total_volume_mn", "total_value_cr", "year", "month",
        }
        if not expected.issubset(columns):
            raise ValueError(f"Reference schema changed. Missing: {sorted(expected - columns)}")
        source_rows = connection.execute(
            """
            SELECT year, month, app_name, cit_volume_mn, cit_value_cr,
                   b2c_volume_mn, b2c_value_cr, b2b_volume_mn, b2b_value_cr,
                   total_volume_mn, total_value_cr
            FROM stg_upi_apps
            ORDER BY year, month, app_name
            """
        ).fetchall()
    finally:
        connection.close()

    duplicate_keys = [key for key, count in Counter((row[0], row[1], row[2]) for row in source_rows).items() if count > 1]
    if duplicate_keys:
        raise ValueError(f"Reference snapshot has duplicate app-month rows: {duplicate_keys[:5]}")

    rows: list[dict[str, str]] = []
    for source in source_rows:
        year, month, app_name, *measures = source
        if not isinstance(year, int) or not isinstance(month, int) or not 1 <= month <= 12:
            raise ValueError(f"Invalid year/month: {year!r}, {month!r}")
        if not app_name or measures[6] is None or any(value is not None and value < 0 for value in measures):
            raise ValueError(f"Invalid app or negative measure for {year}-{month:02d}: {app_name!r}")
        def text(value: float | None) -> str:
            return "" if value is None else str(value)
        rows.append({
            "year": str(year),
            "month": str(month),
            "month_start_date": f"{year:04d}-{month:02d}-01",
            "app_name": str(app_name),
            "customer_initiated_volume_mn": text(measures[0]),
            "customer_initiated_value_crore": text(measures[1]),
            "b2c_volume_mn": text(measures[2]),
            "b2c_value_crore": text(measures[3]),
            "b2b_volume_mn": text(measures[4]),
            "b2b_value_crore": text(measures[5]),
            "total_volume_mn": text(measures[6]),
            "total_value_crore": text(measures[7]),
            "source_reference": f"NPCI UPI Ecosystem Statistics via {REFERENCE_REPOSITORY}@{REFERENCE_COMMIT}",
        })

    # We checked these three July 2025 values against the official NPCI browser
    # table before accepting the reference snapshot.
    expected_july_2025 = {
        "PhonePe": (8931.24, 1220140.68),
        "Google Pay": (6922.92, 891297.38),
        "Paytm": (1366.05, 143650.62),
    }
    found = {(row["app_name"]): (float(row["total_volume_mn"]), float(row["total_value_crore"])) for row in rows if row["month_start_date"] == "2025-07-01"}
    for app, expected_values in expected_july_2025.items():
        actual = found.get(app)
        if actual is None or any(abs(a - b) > 0.001 for a, b in zip(actual, expected_values)):
            raise ValueError(f"Official NPCI validation failed for {app} in 2025-07: {actual!r}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "npci_upi_app_monthly.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    months = sorted({row["month_start_date"] for row in rows})
    report = {
        "source": "Official NPCI UPI Ecosystem Statistics; locally accessed through a public reference snapshot after validation.",
        "official_source_url": "https://www.npci.org.in/product/ecosystem-statistics/upi",
        "reference_repository": REFERENCE_REPOSITORY,
        "reference_commit": REFERENCE_COMMIT,
        "rows_written": len(rows),
        "months": len(months),
        "coverage": {"first_month": months[0], "last_month": months[-1]},
        "missing_calendar_months_within_range": ["2026-03-01"],
        "distinct_app_names": len({row["app_name"] for row in rows}),
        "missing_measure_cells_preserved_as_blank": {
            field: sum(row[field] == "" for row in rows)
            for field in FIELDS
            if field.endswith("_mn") or field.endswith("_crore")
        },
        "official_browser_validation": {
            "month": "2025-07-01",
            "apps": expected_july_2025,
            "result": "matched official NPCI app table",
        },
        "interpretation_note": "App rows are national monthly totals. App volume follows NPCI payer-app attribution and is not state-level app usage.",
    }
    with (output_dir / "npci_upi_app_data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(rows):,} app-month rows across {len(months)} months")


if __name__ == "__main__":
    main()
