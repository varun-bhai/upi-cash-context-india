#!/usr/bin/env python3
"""Standardise RBI monthly UPI, IMPS, and ATM-withdrawal indicators.

Input files are downloaded CSVs stored unchanged in data/raw/rbi.  The script
supports the two public Dataful/RBI layouts and refuses ambiguous selections.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data/raw/rbi"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}
MODES = ("UPI", "IMPS", "ATM_WITHDRAWAL")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def clean(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def decimal(value: str | None, field: str, row_number: int) -> Decimal:
    try:
        result = Decimal((value or "").strip())
    except InvalidOperation as error:
        raise ValueError(f"Row {row_number}: invalid {field}: {value!r}") from error
    if result < 0:
        raise ValueError(f"Row {row_number}: negative {field}: {value!r}")
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path.name}: CSV has no header row")
        return list(reader)


def source_mode_new(row: dict[str, str]) -> str | None:
    labels = [clean(row.get(column)) for column in ("category", "category_major", "category_minor", "sub_category")]
    joined = " | ".join(labels)
    if any(label == "upi" for label in labels):
        return "UPI"
    if any(label == "imps" for label in labels):
        return "IMPS"
    if "cash withdrawal at atms" in joined:
        return "ATM_WITHDRAWAL"
    return None


def source_mode_old(row: dict[str, str]) -> str | None:
    labels = [clean(row.get(column)) for column in ("category", "sub_category", "sub_category_major")]
    joined = " | ".join(labels)
    if any(label == "upi" for label in labels):
        return "UPI"
    if any(label == "imps" for label in labels):
        return "IMPS"
    if "cash withdrawal at atms" in joined or "cash withdrawals at atms" in joined:
        return "ATM_WITHDRAWAL"
    return None


def standardise(path: Path, layout: str) -> list[dict[str, str]]:
    rows = read_csv(path)
    needed = {"year", "month", "volume", "value"}
    if not rows or not needed.issubset(rows[0]):
        raise ValueError(f"{path.name}: expected columns {sorted(needed)}; found {sorted(rows[0]) if rows else []}")
    mode_lookup = source_mode_new if layout == "new" else source_mode_old
    output: list[dict[str, str]] = []
    for position, row in enumerate(rows, start=2):
        mode = mode_lookup(row)
        if mode is None:
            continue
        month_name = clean(row["month"])
        if month_name not in MONTHS:
            raise ValueError(f"Row {position}: unrecognised month {row['month']!r}")
        year = int(row["year"])
        monthly_date = date(year, MONTHS[month_name], 1)
        output.append({
            "monthly_date": monthly_date.isoformat(),
            "year": str(year),
            "month": str(monthly_date.month),
            "quarter": str((monthly_date.month - 1) // 3 + 1),
            "payment_mode": mode,
            "volume_lakh": format(decimal(row["volume"], "volume", position), "f"),
            "value_crore": format(decimal(row["value"], "value", position), "f"),
            "source_layout": layout,
            "source_file": path.name,
        })
    return output


def validate_unique(rows: list[dict[str, str]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["monthly_date"], row["payment_mode"])].append(row)
    duplicates = {key: values for key, values in grouped.items() if len(values) != 1}
    if duplicates:
        examples = ", ".join(f"{period} {mode} ({len(values)} rows)" for (period, mode), values in list(duplicates.items())[:8])
        raise ValueError(
            "The label mapping is ambiguous. Expected exactly one record per month and mode; "
            f"examples: {examples}. Inspect source labels before changing the script."
        )


def select_source_rows(old_rows: list[dict[str, str]], new_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Use old layout through Sep 2019 and new layout from Oct 2019 onward."""
    cutoff = "2019-10-01"
    selected = [row for row in old_rows if row["monthly_date"] < cutoff]
    selected.extend(row for row in new_rows if row["monthly_date"] >= cutoff)
    validate_unique(selected)
    return sorted(selected, key=lambda row: (row["monthly_date"], row["payment_mode"]))


def complete_months(rows: list[dict[str, str]]) -> list[str]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        grouped[row["monthly_date"]].add(row["payment_mode"])
    return sorted(period for period, modes in grouped.items() if modes == set(MODES))


def quarterly_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["year"], row["quarter"], row["payment_mode"])].append(row)
    output: list[dict[str, str]] = []
    for (year, quarter, mode), values in sorted(grouped.items()):
        if len(values) != 3:
            continue
        output.append({
            "year": year,
            "quarter": quarter,
            "quarter_start_date": date(int(year), (int(quarter) - 1) * 3 + 1, 1).isoformat(),
            "payment_mode": mode,
            "months_included": "3",
            "volume_lakh": format(sum(Decimal(row["volume_lakh"]) for row in values), "f"),
            "value_crore": format(sum(Decimal(row["value_crore"]) for row in values), "f"),
        })
    return output


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = arguments()
    raw_dir, output_dir = args.raw_dir.resolve(), args.output_dir.resolve()
    old_path = raw_dir / "rbi_payment_indicators_old_format.csv"
    new_path = raw_dir / "rbi_payment_indicators_new_format.csv"
    missing = [str(path) for path in (old_path, new_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required RBI input file(s): " + ", ".join(missing))
    old_rows = standardise(old_path, "old")
    new_rows = standardise(new_path, "new")
    validate_unique(old_rows)
    validate_unique(new_rows)
    selected = select_source_rows(old_rows, new_rows)
    quarters = quarterly_rows(selected)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "rbi_national_payment_indicators_monthly.csv",
        ["monthly_date", "year", "month", "quarter", "payment_mode", "volume_lakh", "value_crore", "source_layout", "source_file"],
        selected,
    )
    write_csv(
        output_dir / "rbi_national_payment_indicators_quarterly.csv",
        ["year", "quarter", "quarter_start_date", "payment_mode", "months_included", "volume_lakh", "value_crore"],
        quarters,
    )
    report = {
        "purpose": "RBI source-layout validation and monthly-to-quarterly aggregation.",
        "source_cutover": "old format through 2019-09; new format from 2019-10",
        "modes": list(MODES),
        "monthly_rows": len(selected),
        "complete_months": complete_months(selected),
        "quarterly_rows_with_all_three_months": len(quarters),
        "unit_note": "Volume remains in lakh; value remains in rupees crore. No raw-unit conversion is performed in this stage.",
    }
    with (output_dir / "rbi_data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(selected):,} monthly rows and {len(quarters):,} complete-quarter rows")


if __name__ == "__main__":
    main()
