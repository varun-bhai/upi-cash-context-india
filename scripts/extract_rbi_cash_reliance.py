#!/usr/bin/env python3
"""Create an annual national cash-reliance context series from RBI Table 41.

RBI Table 41 reports *annual average* monetary aggregates in INR crore.  This
script extracts the table directly from the preserved RBI webpage, rather than
typing values into a CSV.  The resulting ratio is a contextual measure:
currency with the public divided by demand deposits.  It is not a measurement
of cash spending, cash withdrawals, or a causal effect of UPI.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/rbi/cash_reliance/rbi_table41_average_monetary_aggregates_fy2023_24.html"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_PATH = OUTPUT_DIR / "rbi_annual_cash_reliance.csv"
REPORT_PATH = OUTPUT_DIR / "rbi_annual_cash_reliance_data_quality_report.json"
SOURCE_URL = "https://systemhealth.rbi.org.in/Scripts/PublicationsView.aspx_id%3D22515%281%29.html"
SOURCE_TABLE = "RBI Table 41: Average Monetary Aggregates"
FINANCIAL_YEAR = re.compile(r"^20(1[7-9]|2[0-3])-\d{2}$")

FIELDS = (
    "financial_year",
    "currency_with_public_crore",
    "demand_deposits_crore",
    "currency_to_demand_deposits_ratio",
    "source_table",
    "source_url",
    "time_basis",
    "interpretation_note",
)


class TableRowParser(HTMLParser):
    """Collect text cells from every HTML table row without external packages."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._cell_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell_parts is not None and self._current_row is not None:
            value = " ".join("".join(self._cell_parts).split())
            self._current_row.append(value)
            self._cell_parts = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = None


def parse_rbi_rows(raw_html: str) -> list[dict[str, str]]:
    parser = TableRowParser()
    parser.feed(raw_html)
    extracted: list[dict[str, str]] = []
    for row in parser.rows:
        if len(row) != 13 or not FINANCIAL_YEAR.fullmatch(row[0]):
            continue
        currency_with_public = int(row[1].replace(",", ""))
        demand_deposits = int(row[2].replace(",", ""))
        if currency_with_public <= 0 or demand_deposits <= 0:
            raise ValueError(f"Invalid monetary aggregate values for {row[0]}")
        extracted.append({
            "financial_year": row[0],
            "currency_with_public_crore": str(currency_with_public),
            "demand_deposits_crore": str(demand_deposits),
            "currency_to_demand_deposits_ratio": f"{currency_with_public / demand_deposits:.9f}",
            "source_table": SOURCE_TABLE,
            "source_url": SOURCE_URL,
            "time_basis": "annual average (financial year)",
            "interpretation_note": (
                "Currency with the public divided by demand deposits. This is a monetary-"
                "aggregate context measure, not cash spending, cash withdrawals, or proof that UPI caused cash use to change."
            ),
        })
    extracted.sort(key=lambda row: row["financial_year"])
    expected_years = [f"{year}-{str(year + 1)[-2:]}" for year in range(2017, 2024)]
    found_years = [row["financial_year"] for row in extracted]
    if found_years != expected_years:
        raise ValueError(f"Expected Table 41 rows for {expected_years}, found {found_years}")
    return extracted


def main() -> None:
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Missing RBI source page: {RAW_PATH}")
    raw_html = RAW_PATH.read_text(encoding="utf-8")
    if "Table 41 : Average Monetary Aggregates" not in raw_html:
        raise ValueError("The preserved page does not contain the expected RBI Table 41 title")
    output_rows = parse_rbi_rows(raw_html)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    report = {
        "source": SOURCE_TABLE,
        "source_url": SOURCE_URL,
        "raw_file": str(RAW_PATH.relative_to(PROJECT_ROOT)),
        "raw_file_sha256": hashlib.sha256(RAW_PATH.read_bytes()).hexdigest(),
        "table_date": "2024-09-13",
        "rows_written": len(output_rows),
        "financial_year_range": {"start": output_rows[0]["financial_year"], "end": output_rows[-1]["financial_year"]},
        "units": "INR crore",
        "time_basis": "annual averages for the financial year, not end-of-year balances",
        "derivation": "currency_to_demand_deposits_ratio = currency_with_public_crore / demand_deposits_crore",
        "interpretation_warning": "The ratio offers national monetary context only. It cannot measure cash spending or establish that UPI caused cash use to change.",
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(output_rows)} RBI annual cash-reliance rows")


if __name__ == "__main__":
    main()
