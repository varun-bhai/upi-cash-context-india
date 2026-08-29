#!/usr/bin/env python3
"""Create clean national payment indicators from India Data Portal's RBI daily API snapshot.

The raw JSON is downloaded unchanged from the public CKAN API.  This script
keeps the source grain (one national observation per day and payment mode) and
then creates monthly and complete-quarter sums for analysis alongside PhonePe's
quarterly state data.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/rbi/idp_rbi_daily_digital_payments.json"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
RESOURCE_ID = "1f9367ac-01b0-4c82-83a1-4069d4340667"
MODES = {
    "UPI": ("upi_vol", "upi_val"),
    "IMPS": ("imps_vol", "imps_val"),
    "NFS_ATM_CASH_WITHDRAWAL": ("nfs_through_atms_vol", "nfs_through_atms_val"),
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-path", type=Path, default=RAW_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def decimal_or_none(value: object, field: str, day: str) -> Decimal | None:
    if value is None or value == "":
        return None
    result = Decimal(str(value))
    if result < 0:
        raise ValueError(f"{day}: {field} is negative ({value!r})")
    return result


def display(value: Decimal) -> str:
    return format(value, "f")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_records(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle, parse_float=Decimal)
    if payload.get("success") is not True:
        raise ValueError("The raw JSON does not contain a successful CKAN API response")
    result = payload.get("result", {})
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("The raw JSON does not contain result.records")
    total = result.get("total")
    if total != len(records):
        raise ValueError(f"Raw response is incomplete: API reported {total} records but contains {len(records)}")
    return records


def main() -> None:
    args = arguments()
    records = load_records(args.raw_path.resolve())
    records_by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        records_by_day[str(record.get("date", ""))].append(record)
    duplicate_records_removed = 0
    canonical_records: list[dict[str, object]] = []
    for raw_day, candidates in records_by_day.items():
        selected_values = {
            tuple(candidate.get(field) for fields in MODES.values() for field in fields)
            for candidate in candidates
        }
        if len(selected_values) != 1:
            raise ValueError(f"Conflicting duplicate daily records for {raw_day}")
        # The portal has 31 duplicate records for July 2026.  They agree on all
        # fields used here, so keeping the lowest API row id is deterministic.
        canonical_records.append(min(candidates, key=lambda candidate: int(candidate.get("_id", 0))))
        duplicate_records_removed += len(candidates) - 1

    seen_dates: set[date] = set()
    daily: list[dict[str, str]] = []
    null_counts: dict[str, int] = defaultdict(int)

    for record in canonical_records:
        raw_day = str(record.get("date", ""))
        try:
            day = datetime.strptime(raw_day, "%Y-%m-%d").date()
        except ValueError as error:
            raise ValueError(f"Invalid date in raw data: {raw_day!r}") from error
        seen_dates.add(day)
        for mode, (volume_field, value_field) in MODES.items():
            volume = decimal_or_none(record.get(volume_field), volume_field, raw_day)
            value = decimal_or_none(record.get(value_field), value_field, raw_day)
            if volume is None or value is None:
                null_counts[mode] += 1
                continue
            daily.append({
                "date": day.isoformat(),
                "year": str(day.year),
                "month": str(day.month),
                "quarter": f"Q{(day.month - 1) // 3 + 1}",
                "payment_mode": mode,
                "volume_lakh": display(volume),
                "value_crore": display(value),
                "source_resource_id": RESOURCE_ID,
            })

    daily.sort(key=lambda row: (row["date"], row["payment_mode"]))
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in daily:
        grouped[(row["date"][:7], row["payment_mode"])].append(row)

    monthly: list[dict[str, str]] = []
    for (month_key, mode), rows in sorted(grouped.items()):
        year, month = map(int, month_key.split("-"))
        observed_days = {row["date"] for row in rows}
        monthly.append({
            "monthly_date": f"{month_key}-01",
            "year": str(year),
            "month": str(month),
            "quarter": f"Q{(month - 1) // 3 + 1}",
            "payment_mode": mode,
            "days_observed": str(len(observed_days)),
            "calendar_days": str(calendar.monthrange(year, month)[1]),
            "volume_lakh": display(sum(Decimal(row["volume_lakh"]) for row in rows)),
            "value_crore": display(sum(Decimal(row["value_crore"]) for row in rows)),
        })

    quarterly_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in monthly:
        quarterly_groups[(f"{row['year']}-{row['quarter']}", row["payment_mode"])].append(row)
    quarterly: list[dict[str, str]] = []
    skipped_quarters: list[dict[str, object]] = []
    for (period, mode), rows in sorted(quarterly_groups.items()):
        year, quarter = period.split("-")
        expected_months = {1, 2, 3} if quarter == "Q1" else {4, 5, 6} if quarter == "Q2" else {7, 8, 9} if quarter == "Q3" else {10, 11, 12}
        months_present = {int(row["month"]) for row in rows}
        full_months = all(row["days_observed"] == row["calendar_days"] for row in rows)
        if months_present != expected_months or not full_months:
            skipped_quarters.append({"period": period, "payment_mode": mode, "months_present": sorted(months_present), "all_calendar_days_observed": full_months})
            continue
        quarter_start = min(row["monthly_date"] for row in rows)
        quarterly.append({
            "year": year,
            "quarter": quarter,
            "quarter_start_date": quarter_start,
            "payment_mode": mode,
            "months_included": "3",
            "days_observed": str(sum(int(row["days_observed"]) for row in rows)),
            "volume_lakh": display(sum(Decimal(row["volume_lakh"]) for row in rows)),
            "value_crore": display(sum(Decimal(row["value_crore"]) for row in rows)),
        })

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "idp_rbi_national_payment_indicators_daily.csv", list(daily[0]), daily)
    write_csv(output_dir / "idp_rbi_national_payment_indicators_monthly.csv", list(monthly[0]), monthly)
    write_csv(output_dir / "idp_rbi_national_payment_indicators_quarterly.csv", list(quarterly[0]), quarterly)
    report = {
        "source": "India Data Portal, RBI Daily Digital Payments, queried through public CKAN Data API",
        "source_resource_id": RESOURCE_ID,
        "raw_records": len(records),
        "duplicate_source_records_removed": duplicate_records_removed,
        "unique_daily_source_records": len(canonical_records),
        "daily_date_range": {"start": min(seen_dates).isoformat(), "end": max(seen_dates).isoformat()},
        "modes": {mode: {"volume_field": fields[0], "value_field": fields[1]} for mode, fields in MODES.items()},
        "units": {"volume": "lakh", "value": "INR crore"},
        "missing_or_null_mode_days": dict(null_counts),
        "daily_rows_written": len(daily),
        "monthly_rows_written": len(monthly),
        "complete_quarterly_rows_written": len(quarterly),
        "skipped_incomplete_quarter_mode_combinations": skipped_quarters,
        "interpretation_note": "NFS_ATM_CASH_WITHDRAWAL is National Financial Switch throughput at ATMs. It is a cash-access proxy, not total ATM withdrawals or cash spending.",
    }
    with (output_dir / "idp_rbi_data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(daily):,} daily, {len(monthly):,} monthly, and {len(quarterly):,} complete-quarter rows")


if __name__ == "__main__":
    main()
