#!/usr/bin/env python3
"""Extract clean monthly national UPI P2P/P2M statistics from the NPCI reference snapshot."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DB = PROJECT_ROOT / "data/raw/npci_upi_analytics_reference/staging/npci_upi.db"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
REFERENCE_REPOSITORY = "https://github.com/luckisalive/npci_upi_analytics"
REFERENCE_COMMIT = "5c007daef0b69f30dd8e555c548ba6f3bd85c43f"
FIELDS = (
    "year", "month", "month_start_date", "total_volume_mn", "total_value_crore",
    "p2p_volume_mn", "p2p_value_crore", "p2m_volume_mn", "p2m_value_crore",
    "source_p2p_share_pct", "source_p2m_share_pct", "source_reference",
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-db", type=Path, default=REFERENCE_DB)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    source_path = args.reference_db.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Missing reference snapshot: {source_path}")
    connection = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
    try:
        rows = connection.execute(
            """
            SELECT year, month, total_volume_mn, total_value_cr,
                   p2p_volume_mn, p2p_value_cr, p2m_volume_mn, p2m_value_cr,
                   p2p_share_pct, p2m_share_pct
            FROM stg_p2p_p2m
            ORDER BY year, month
            """
        ).fetchall()
    finally:
        connection.close()

    months = {(year, month) for year, month, *_ in rows}
    if len(months) != len(rows):
        raise ValueError("Reference snapshot has duplicate P2P/P2M month rows")
    clean_rows: list[dict[str, str]] = []
    reconciliation_warnings: list[dict[str, object]] = []
    for row in rows:
        year, month, total_volume, total_value, p2p_volume, p2p_value, p2m_volume, p2m_value, p2p_share, p2m_share = row
        if not isinstance(year, int) or not isinstance(month, int) or not 1 <= month <= 12:
            raise ValueError(f"Invalid year/month: {year!r}, {month!r}")
        measures = (total_volume, total_value, p2p_volume, p2p_value, p2m_volume, p2m_value, p2p_share, p2m_share)
        if any(value is None or value < 0 for value in measures):
            raise ValueError(f"Missing or negative required value in {year}-{month:02d}")
        volume_difference = total_volume - p2p_volume - p2m_volume
        value_difference = total_value - p2p_value - p2m_value
        # Ignore small published rounding differences; flag material gaps.
        if abs(volume_difference) > 0.1 or abs(value_difference) > 0.1:
            reconciliation_warnings.append({
                "month": f"{year:04d}-{month:02d}-01",
                "volume_difference_mn": volume_difference,
                "value_difference_crore": value_difference,
                "decision": "Preserved all published fields unchanged; warn rather than overwrite a source total.",
            })
        clean_rows.append({
            "year": str(year), "month": str(month), "month_start_date": f"{year:04d}-{month:02d}-01",
            "total_volume_mn": str(total_volume), "total_value_crore": str(total_value),
            "p2p_volume_mn": str(p2p_volume), "p2p_value_crore": str(p2p_value),
            "p2m_volume_mn": str(p2m_volume), "p2m_value_crore": str(p2m_value),
            "source_p2p_share_pct": str(p2p_share), "source_p2m_share_pct": str(p2m_share),
            "source_reference": f"NPCI UPI Ecosystem Statistics via {REFERENCE_REPOSITORY}@{REFERENCE_COMMIT}",
        })

    expected_aug_2025 = (20008.31, 2485472.91, 7303.15, 1761675.49, 12705.16, 723797.42)
    august = next(row for row in clean_rows if row["month_start_date"] == "2025-08-01")
    actual_august = tuple(float(august[field]) for field in (
        "total_volume_mn", "total_value_crore", "p2p_volume_mn", "p2p_value_crore", "p2m_volume_mn", "p2m_value_crore",
    ))
    if any(abs(actual - expected) > 0.001 for actual, expected in zip(actual_august, expected_aug_2025)):
        raise ValueError(f"Official NPCI validation failed for 2025-08: {actual_august!r}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "npci_upi_p2p_p2m_monthly.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(clean_rows)
    report = {
        "source": "Official NPCI UPI Ecosystem Statistics; locally accessed through a public reference snapshot after validation.",
        "official_source_url": "https://www.npci.org.in/product/ecosystem-statistics/upi",
        "reference_repository": REFERENCE_REPOSITORY,
        "reference_commit": REFERENCE_COMMIT,
        "rows_written": len(clean_rows),
        "coverage": {"first_month": clean_rows[0]["month_start_date"], "last_month": clean_rows[-1]["month_start_date"]},
        "official_browser_validation": {"month": "2025-08-01", "published_values": expected_aug_2025, "result": "matched official NPCI P2P/P2M table"},
        "source_reconciliation_warnings": reconciliation_warnings,
        "interpretation_note": "P2P is person-to-person and P2M is person-to-merchant. These are national monthly totals across UPI, not PhonePe-only data.",
    }
    with (output_dir / "npci_upi_p2p_p2m_data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(clean_rows):,} P2P/P2M monthly rows with {len(reconciliation_warnings)} source warning(s)")


if __name__ == "__main__":
    main()
