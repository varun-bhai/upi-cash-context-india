#!/usr/bin/env python3
"""Compare two independently sourced national UPI monthly series.

The NPCI app-level table should add up closely to the RBI-derived national UPI
series.  This script makes that check visible and preserves exceptions rather
than silently treating unlike figures as interchangeable.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
APP_PATH = PROCESSED / "npci_upi_app_monthly.csv"
RBI_PATH = PROCESSED / "idp_rbi_national_payment_indicators_monthly.csv"
OUTPUT_PATH = PROCESSED / "national_upi_source_comparison_monthly.csv"
REPORT_PATH = PROCESSED / "national_upi_source_comparison_report.json"

FIELDS = (
    "month_start_date", "npci_app_rows", "npci_apps_total_volume_mn",
    "idp_rbi_upi_volume_mn", "volume_difference_mn", "volume_ratio",
    "npci_apps_total_value_crore", "idp_rbi_upi_value_crore",
    "value_difference_crore", "value_ratio", "idp_days_observed",
    "idp_calendar_days", "comparison_status",
)


def decimal_text(value: Decimal | None) -> str:
    """Render a decimal without scientific notation or false precision."""
    if value is None:
        return ""
    return format(value.quantize(Decimal("0.000001")), "f").rstrip("0").rstrip(".")


def main() -> None:
    app_totals: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"rows": 0, "volume": Decimal("0"), "value": Decimal("0")}
    )
    with APP_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            month = row["month_start_date"]
            app_totals[month]["rows"] += 1  # type: ignore[operator]
            app_totals[month]["volume"] += Decimal(row["total_volume_mn"])  # type: ignore[operator]
            # An app row with no total value is not imputed as zero.
            if row["total_value_crore"]:
                app_totals[month]["value"] += Decimal(row["total_value_crore"])  # type: ignore[operator]

    rbi_upi: dict[str, dict[str, str]] = {}
    with RBI_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["payment_mode"] == "UPI":
                rbi_upi[row["monthly_date"]] = row

    common_months = sorted(set(app_totals) & set(rbi_upi))
    if not common_months:
        raise ValueError("No overlapping UPI months were found")

    comparison_rows: list[dict[str, str]] = []
    material_warnings: list[dict[str, str]] = []
    volume_ratios: list[Decimal] = []
    value_ratios: list[Decimal] = []
    for month in common_months:
        apps = app_totals[month]
        rbi = rbi_upi[month]
        app_volume = apps["volume"]  # type: ignore[assignment]
        app_value = apps["value"]  # type: ignore[assignment]
        rbi_volume = Decimal(rbi["volume_lakh"]) / Decimal("10")
        rbi_value = Decimal(rbi["value_crore"])
        volume_ratio = app_volume / rbi_volume
        value_ratio = app_value / rbi_value
        volume_ratios.append(volume_ratio)
        value_ratios.append(value_ratio)

        # Volumes within 3% are close enough to corroborate a national trend.
        # Values for Jan--Mar 2022 have a large, unexplained mismatch and are
        # deliberately marked as not comparable instead of being corrected.
        if abs(volume_ratio - 1) <= Decimal("0.03") and abs(value_ratio - 1) <= Decimal("0.03"):
            status = "close_match"
        elif abs(volume_ratio - 1) <= Decimal("0.03"):
            status = "volume_matches_value_not_comparable"
            material_warnings.append({
                "month": month,
                "issue": "App-level value total differs materially from the RBI-derived national UPI value.",
                "decision": "Use the app source only for app shares in this month; do not use it as a national value cross-check.",
            })
        else:
            status = "not_comparable"
            material_warnings.append({
                "month": month,
                "issue": "Both the volume and value totals differ materially.",
                "decision": "Do not combine the two sources for this month without further source documentation.",
            })
        comparison_rows.append({
            "month_start_date": month,
            "npci_app_rows": str(apps["rows"]),
            "npci_apps_total_volume_mn": decimal_text(app_volume),
            "idp_rbi_upi_volume_mn": decimal_text(rbi_volume),
            "volume_difference_mn": decimal_text(app_volume - rbi_volume),
            "volume_ratio": decimal_text(volume_ratio),
            "npci_apps_total_value_crore": decimal_text(app_value),
            "idp_rbi_upi_value_crore": decimal_text(rbi_value),
            "value_difference_crore": decimal_text(app_value - rbi_value),
            "value_ratio": decimal_text(value_ratio),
            "idp_days_observed": rbi["days_observed"],
            "idp_calendar_days": rbi["calendar_days"],
            "comparison_status": status,
        })

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(comparison_rows)

    def summary(values: list[Decimal]) -> dict[str, str]:
        return {
            "minimum": decimal_text(min(values)),
            "maximum": decimal_text(max(values)),
            "mean": decimal_text(sum(values) / len(values)),
        }

    report = {
        "purpose": "Reconcile national monthly UPI totals from the NPCI app snapshot and the RBI-derived India Data Portal series.",
        "comparison_window": {"first_month": common_months[0], "last_month": common_months[-1], "months": len(common_months)},
        "unit_note": "RBI-derived volumes are reported in lakh and are divided by 10 here to express millions; both values are in crore rupees.",
        "volume_ratio_summary_app_total_divided_by_rbi_total": summary(volume_ratios),
        "value_ratio_summary_app_total_divided_by_rbi_total": summary(value_ratios),
        "interpretation": [
            "App-level transaction volumes closely match the RBI-derived national UPI series throughout the overlapping period.",
            "Values closely match from April 2022 onward, but January--March 2022 have a large unexplained mismatch.",
            "The cleanest use is therefore: use the app table for app shares, and use the RBI-derived table for national payment totals. Never overwrite one source with the other.",
        ],
        "material_warnings": material_warnings,
        "sources": {
            "app_source": "Official NPCI UPI Ecosystem Statistics, accessed through a locally validated public reference snapshot.",
            "national_source": "RBI Daily Digital Payments data, accessed through the India Data Portal CKAN API and aggregated locally.",
        },
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(comparison_rows)} monthly comparisons; {len(material_warnings)} warning(s)")


if __name__ == "__main__":
    main()
