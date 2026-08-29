#!/usr/bin/env python3
"""Flatten the local PhonePe Pulse state-level aggregate JSON files into CSVs.

This script deliberately keeps the source category names unchanged.  A later
analysis step can decide how, or whether, to map them to business concepts.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "data/raw/phonepe_pulse"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/processed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def state_display_name(slug: str) -> str:
    """Create a readable label while retaining the original slug as the join key."""
    special_names = {
        "andaman-&-nicobar-islands": "Andaman & Nicobar Islands",
        "dadra-&-nagar-haveli-&-daman-&-diu": "Dadra & Nagar Haveli and Daman & Diu",
        "jammu-&-kashmir": "Jammu & Kashmir",
        "nct-of-delhi": "NCT of Delhi",
    }
    if slug in special_names:
        return special_names[slug]
    return slug.replace("-", " ").title()


def quarter_start(year: int, quarter: int) -> date:
    return date(year, (quarter - 1) * 3 + 1, 1)


def source_files(source_root: Path, dataset: str) -> list[Path]:
    base = source_root / "data/aggregated" / dataset / "country/india/state"
    if not base.is_dir():
        raise FileNotFoundError(f"Expected source folder does not exist: {base}")
    return sorted(base.glob("*/*/*.json"))


def file_parts(path: Path, base: Path) -> tuple[str, int, int]:
    state_slug, year, filename = path.relative_to(base).parts
    quarter = int(path.stem)
    if quarter not in {1, 2, 3, 4}:
        raise ValueError(f"Unexpected quarter in {path}: {quarter}")
    return state_slug, int(year), quarter


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle, parse_float=Decimal)
    if payload.get("success") is not True or payload.get("code") != "SUCCESS":
        raise ValueError(f"Source file does not report SUCCESS: {path}")
    return payload


def decimal_string(value: Any, *, path: Path, field: str) -> str:
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"Invalid {field} in {path}: {value!r}") from error
    if amount < 0:
        raise ValueError(f"Negative {field} in {path}: {amount}")
    return format(amount, "f")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def flatten_transactions(source_root: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    base = source_root / "data/aggregated/transaction/country/india/state"
    rows: list[dict[str, str]] = []
    categories: Counter[str] = Counter()
    missing_categories: list[dict[str, str]] = []
    observed_by_file: dict[tuple[str, int, int], set[str]] = {}

    for path in source_files(source_root, "transaction"):
        state_slug, year, quarter = file_parts(path, base)
        items = load_json(path)["data"].get("transactionData", [])
        if not isinstance(items, list):
            raise ValueError(f"transactionData is not a list: {path}")
        seen: set[str] = set()
        for item in items:
            category = item["name"]
            if category in seen:
                raise ValueError(f"Duplicate category {category!r} in {path}")
            seen.add(category)
            instruments = item.get("paymentInstruments", [])
            total = next((item for item in instruments if item.get("type") == "TOTAL"), None)
            if total is None:
                raise ValueError(f"No TOTAL payment instrument in {path} ({category})")
            count = total["count"]
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Invalid transaction count in {path}: {count!r}")
            rows.append(
                {
                    "state_slug": state_slug,
                    "state_name": state_display_name(state_slug),
                    "year": str(year),
                    "quarter": str(quarter),
                    "quarter_start_date": quarter_start(year, quarter).isoformat(),
                    "source_category": category,
                    "transaction_count": str(count),
                    "transaction_value_inr": decimal_string(
                        total["amount"], path=path, field="transaction value"
                    ),
                    "source_file": str(path.relative_to(source_root)),
                }
            )
            categories[category] += 1
        observed_by_file[(state_slug, year, quarter)] = seen

    all_categories = set(categories)
    for state_slug, year, quarter in sorted(observed_by_file):
        for category in sorted(all_categories - observed_by_file[(state_slug, year, quarter)]):
            missing_categories.append(
                {
                    "state_slug": state_slug,
                    "year": str(year),
                    "quarter": str(quarter),
                    "source_category": category,
                    "note": "Category absent from source file; this is not imputed as zero.",
                }
            )
    return rows, {
        "source_files": len(observed_by_file),
        "output_rows": len(rows),
        "category_file_counts": dict(sorted(categories.items())),
        "missing_category_observations": missing_categories,
    }


def flatten_registered_counts(source_root: Path, dataset: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    base = source_root / f"data/aggregated/{dataset}/country/india/state"
    rows: list[dict[str, str]] = []
    for path in source_files(source_root, dataset):
        state_slug, year, quarter = file_parts(path, base)
        count = load_json(path)["data"].get("aggregated", {}).get("registeredCount")
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid registeredCount in {path}: {count!r}")
        rows.append(
            {
                "state_slug": state_slug,
                "state_name": state_display_name(state_slug),
                "year": str(year),
                "quarter": str(quarter),
                "quarter_start_date": quarter_start(year, quarter).isoformat(),
                "registered_count": str(count),
                "source_file": str(path.relative_to(source_root)),
            }
        )
    return rows, {"source_files": len(rows), "output_rows": len(rows)}


def coverage(rows: list[dict[str, str]]) -> dict[str, Any]:
    periods = sorted({(int(row["year"]), int(row["quarter"])) for row in rows})
    entities = sorted({row["state_slug"] for row in rows})
    return {
        "state_or_ut_entities": len(entities),
        "first_period": f"{periods[0][0]} Q{periods[0][1]}",
        "last_period": f"{periods[-1][0]} Q{periods[-1][1]}",
    }


def missing_entity_quarters(
    reference_rows: list[dict[str, str]], target_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    """List target gaps using transaction coverage as the observed reference."""
    expected = {(row["state_slug"], row["year"], row["quarter"]) for row in reference_rows}
    observed = {(row["state_slug"], row["year"], row["quarter"]) for row in target_rows}
    return [
        {"state_slug": state_slug, "year": year, "quarter": quarter}
        for state_slug, year, quarter in sorted(expected - observed)
    ]


def require_unique(rows: list[dict[str, str]], columns: tuple[str, ...], dataset: str) -> None:
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(row[column] for column in columns)
        if key in seen:
            raise ValueError(f"Duplicate {dataset} output key: {key}")
        seen.add(key)


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    transaction_rows, transaction_summary = flatten_transactions(source_root)
    user_rows, user_summary = flatten_registered_counts(source_root, "user")
    merchant_rows, merchant_summary = flatten_registered_counts(source_root, "merchant")
    require_unique(
        transaction_rows,
        ("state_slug", "year", "quarter", "source_category"),
        "transaction",
    )
    require_unique(user_rows, ("state_slug", "year", "quarter"), "user")
    require_unique(merchant_rows, ("state_slug", "year", "quarter"), "merchant")

    write_csv(
        output_dir / "phonepe_state_transaction_quarterly.csv",
        [
            "state_slug", "state_name", "year", "quarter", "quarter_start_date",
            "source_category", "transaction_count", "transaction_value_inr", "source_file",
        ],
        transaction_rows,
    )
    for filename, rows in [
        ("phonepe_state_user_quarterly.csv", user_rows),
        ("phonepe_state_merchant_quarterly.csv", merchant_rows),
    ]:
        write_csv(
            output_dir / filename,
            [
                "state_slug", "state_name", "year", "quarter", "quarter_start_date",
                "registered_count", "source_file",
            ],
            rows,
        )

    report = {
        "purpose": "Observed source coverage and extraction checks; missing values are never imputed.",
        "source_root": str(source_root),
        "datasets": {
            "transactions": {**coverage(transaction_rows), **transaction_summary},
            "users": {
                **coverage(user_rows),
                **user_summary,
                "missing_entity_quarters_compared_to_transactions": missing_entity_quarters(
                    transaction_rows, user_rows
                ),
            },
            "merchants": {
                **coverage(merchant_rows),
                **merchant_summary,
                "missing_entity_quarters_compared_to_transactions": missing_entity_quarters(
                    transaction_rows, merchant_rows
                ),
            },
        },
    }
    with (output_dir / "phonepe_data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    print("PhonePe extraction complete")
    for dataset, rows in [
        ("transactions", transaction_rows), ("users", user_rows), ("merchants", merchant_rows),
    ]:
        print(f"  {dataset}: {len(rows):,} rows; {coverage(rows)['first_period']} to {coverage(rows)['last_period']}")


if __name__ == "__main__":
    main()
