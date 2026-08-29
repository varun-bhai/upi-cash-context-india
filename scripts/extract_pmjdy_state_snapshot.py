#!/usr/bin/env python3
"""Create a clean PMJDY state financial-inclusion snapshot.

PMJDY publishes a live state-wise beneficiary table.  This script extracts the
preserved 19 August 2026 page and aligns its 36 geographic rows to PhonePe's
36 states/UTs.  It intentionally treats PMJDY beneficiary counts as a
financial-inclusion context measure, not as unique banked people, active debit
cards, active UPI users, or a direct measure of a state's bank access.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/pmjdy/pmjdy_statewise_accounts_2026_08_19.html"
PHONEPE_PATH = PROJECT_ROOT / "data/processed/phonepe_state_user_quarterly.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_PATH = OUTPUT_DIR / "pmjdy_state_financial_inclusion_2026_08_19.csv"
REPORT_PATH = OUTPUT_DIR / "pmjdy_state_financial_inclusion_2026_08_19_data_quality_report.json"
SOURCE_URL = "https://pmjdy.gov.in/account-statistics-state.aspx/scheme"
SOURCE_TABLE = "PMJDY Statewise account opening Report"

FIELDS = (
    "as_of_date",
    "state_slug",
    "state_name",
    "beneficiaries_rural_semiurban_count",
    "beneficiaries_urban_metro_count",
    "total_beneficiaries_count",
    "balance_in_beneficiary_accounts_crore",
    "rupay_debit_cards_issued_count",
    "source_table",
    "source_url",
    "interpretation_note",
)

PMJDY_TO_PHONEPE = {
    "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",
    "Jammu And Kashmir": "Jammu & Kashmir",
    "The Dadra And Nagar Haveli And Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",
}


class RowParser(HTMLParser):
    """Small standard-library parser for the rows of a saved HTML table."""

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
            self._current_row.append(" ".join("".join(self._cell_parts).split()))
            self._cell_parts = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = None


def whole_number(value: str) -> int:
    return int(value.replace(",", ""))


def main() -> None:
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Missing PMJDY source page: {RAW_PATH}")
    raw_html = RAW_PATH.read_text(encoding="utf-8")
    date_match = re.search(r"Statewise account opening Report as on\s*(\d{2}/\d{2}/\d{4})", raw_html)
    if date_match is None:
        raise ValueError("Could not find the PMJDY report date")
    as_of_date = datetime.strptime(date_match.group(1), "%d/%m/%Y").date().isoformat()
    table_match = re.search(
        r'<table[^>]*id="ContentPlaceHolder1_gridstateacnt"[^>]*>(.*?)</table>',
        raw_html,
        flags=re.DOTALL,
    )
    if table_match is None:
        raise ValueError("Could not locate the PMJDY state account table")
    parser = RowParser()
    parser.feed(table_match.group(1))
    source_rows = [row for row in parser.rows if len(row) == 7 and row[0].isdigit() and row[1] != "Total"]
    total_rows = [row for row in parser.rows if len(row) == 7 and row[1] == "Total"]
    if [int(row[0]) for row in source_rows] != list(range(1, 37)):
        raise ValueError("The PMJDY table does not contain exactly the expected 36 numbered state/UT rows")
    if len(total_rows) != 1:
        raise ValueError("The PMJDY table does not contain exactly one total row")
    total_row = total_rows[0]
    expected_totals = (
        sum(whole_number(row[2]) for row in source_rows),
        sum(whole_number(row[3]) for row in source_rows),
        sum(whole_number(row[4]) for row in source_rows),
        sum(Decimal(row[5].replace(",", "")) for row in source_rows),
        sum(whole_number(row[6]) for row in source_rows),
    )
    reported_totals = (
        whole_number(total_row[2]),
        whole_number(total_row[3]),
        whole_number(total_row[4]),
        Decimal(total_row[5].replace(",", "")),
        whole_number(total_row[6]),
    )
    if expected_totals != reported_totals:
        raise ValueError(
            f"PMJDY state totals do not reconcile: expected {expected_totals}, reported {reported_totals}"
        )

    with PHONEPE_PATH.open(encoding="utf-8", newline="") as handle:
        phonepe_states = {row["state_name"]: row["state_slug"] for row in csv.DictReader(handle)}

    note = (
        "PMJDY beneficiary counts are a state-level financial-inclusion context measure. "
        "They are not verified unique people, active bank-account users, active debit-card users, "
        "or active UPI users; the data are not a direct measure of bank branches or ATM access."
    )
    output_rows: list[dict[str, str]] = []
    for row in source_rows:
        source_name = row[1]
        state_name = PMJDY_TO_PHONEPE.get(source_name, source_name)
        if state_name not in phonepe_states:
            raise ValueError(f"PMJDY state cannot be mapped to PhonePe geography: {source_name!r}")
        rural_count = whole_number(row[2])
        urban_count = whole_number(row[3])
        total_count = whole_number(row[4])
        if rural_count + urban_count != total_count:
            raise ValueError(f"PMJDY beneficiary components do not equal total for {source_name}")
        output_rows.append({
            "as_of_date": as_of_date,
            "state_slug": phonepe_states[state_name],
            "state_name": state_name,
            "beneficiaries_rural_semiurban_count": str(rural_count),
            "beneficiaries_urban_metro_count": str(urban_count),
            "total_beneficiaries_count": str(total_count),
            "balance_in_beneficiary_accounts_crore": row[5].replace(",", ""),
            "rupay_debit_cards_issued_count": str(whole_number(row[6])),
            "source_table": SOURCE_TABLE,
            "source_url": SOURCE_URL,
            "interpretation_note": note,
        })
    output_rows.sort(key=lambda row: row["state_name"])
    output_states = {row["state_name"] for row in output_rows}
    if output_states != set(phonepe_states):
        raise ValueError(
            "PMJDY/PhonePe geography mismatch: "
            f"missing={sorted(set(phonepe_states) - output_states)}; "
            f"unexpected={sorted(output_states - set(phonepe_states))}"
        )

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
        "as_of_date": as_of_date,
        "rows_written": len(output_rows),
        "geography_match_to_phonepe": "passed for all 36 PhonePe state/UT geographies",
        "state_totals_reconcile_to_source_total": "passed",
        "name_mappings": PMJDY_TO_PHONEPE,
        "time_alignment": "PMJDY is a 19 August 2026 snapshot. It is compared only with PhonePe 2026 Q2 (April-June 2026) as near-in-time descriptive context, not as a same-day series.",
        "interpretation_warning": note,
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(output_rows)} PMJDY state financial-inclusion snapshot rows")


if __name__ == "__main__":
    main()
