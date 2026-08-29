#!/usr/bin/env python3
"""Profile the cleaned PhonePe data and reconcile state totals to country totals."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data/processed"
SOURCE_ROOT = PROJECT_ROOT / "data/raw/phonepe_pulse"


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def load_state_totals() -> dict[tuple[int, int, str], dict[str, Decimal | int | str]]:
    totals: dict[tuple[int, int, str], dict[str, Decimal | int | str]] = {}
    with (PROCESSED_DIR / "phonepe_state_transaction_quarterly.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (int(row["year"]), int(row["quarter"]), row["source_category"])
            if key not in totals:
                totals[key] = {
                    "quarter_start_date": row["quarter_start_date"],
                    "transaction_count": 0,
                    "transaction_value_inr": Decimal(0),
                }
            totals[key]["transaction_count"] += int(row["transaction_count"])
            totals[key]["transaction_value_inr"] += Decimal(row["transaction_value_inr"])
    return totals


def load_country_totals(year: int, quarter: int) -> dict[str, tuple[int, Decimal]]:
    path = SOURCE_ROOT / f"data/aggregated/transaction/country/india/{year}/{quarter}.json"
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle, parse_float=Decimal)
    return {
        item["name"]: (
            item["paymentInstruments"][0]["count"],
            item["paymentInstruments"][0]["amount"],
        )
        for item in payload["data"]["transactionData"]
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    fields = [
        "year", "quarter", "quarter_start_date", "source_category",
        "state_sum_transaction_count", "state_sum_transaction_value_inr",
        "country_transaction_count", "country_transaction_value_inr",
        "count_difference", "value_difference_inr",
    ]
    with (PROCESSED_DIR / "phonepe_national_reconciliation_quarterly.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    state_totals = load_state_totals()
    rows: list[dict[str, str]] = []
    count_differences: list[int] = []
    value_differences: list[Decimal] = []

    for (year, quarter, category), values in sorted(state_totals.items()):
        country = load_country_totals(year, quarter)
        if category not in country:
            raise ValueError(f"Country total lacks category {category!r} in {year} Q{quarter}")
        country_count, country_value = country[category]
        count_difference = int(values["transaction_count"]) - country_count
        value_difference = Decimal(values["transaction_value_inr"]) - country_value
        count_differences.append(count_difference)
        value_differences.append(value_difference)
        rows.append(
            {
                "year": str(year),
                "quarter": str(quarter),
                "quarter_start_date": str(values["quarter_start_date"]),
                "source_category": category,
                "state_sum_transaction_count": str(values["transaction_count"]),
                "state_sum_transaction_value_inr": decimal_string(
                    Decimal(values["transaction_value_inr"])
                ),
                "country_transaction_count": str(country_count),
                "country_transaction_value_inr": decimal_string(country_value),
                "count_difference": str(count_difference),
                "value_difference_inr": decimal_string(value_difference),
            }
        )
    write_csv(rows)

    profile = {
        "purpose": "Validate that quarterly state totals reconcile to PhonePe country totals.",
        "comparisons": len(rows),
        "all_transaction_counts_reconcile_exactly": all(value == 0 for value in count_differences),
        "maximum_absolute_value_difference_inr": decimal_string(
            max(abs(value) for value in value_differences)
        ),
        "interpretation": (
            "Small value differences are floating-point aggregation artefacts in the JSON source; "
            "the largest observed difference should be interpreted against multi-billion-rupee totals."
        ),
    }
    with (PROCESSED_DIR / "phonepe_reconciliation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2)
        handle.write("\n")

    print(f"Reconciled {len(rows)} quarter-category totals")
    print(f"Transaction counts reconcile exactly: {profile['all_transaction_counts_reconcile_exactly']}")
    print(f"Largest absolute value difference: ₹{profile['maximum_absolute_value_difference_inr']}")


if __name__ == "__main__":
    main()
