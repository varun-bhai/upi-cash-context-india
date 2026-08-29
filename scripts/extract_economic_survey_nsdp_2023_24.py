#!/usr/bin/env python3
"""Create a clean 2023-24 state income snapshot from Economic Survey Table 1.11A.

The values are transcribed from the official one-page PDF after visual
verification.  The Economic Survey does not publish State Domestic Product
estimates for Dadra & Nagar Haveli and Daman & Diu or Lakshadweep, so this
snapshot deliberately has 34, not 36, project geographies.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PDF = PROJECT_ROOT / "data/raw/economic_survey/economic_survey_2025_26_table_1_11a.pdf"
PHONEPE_PATH = PROJECT_ROOT / "data/processed/phonepe_state_user_quarterly.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_PATH = OUTPUT_DIR / "economic_survey_state_per_capita_nsdp_fy2023_24.csv"
REPORT_PATH = OUTPUT_DIR / "economic_survey_state_per_capita_nsdp_fy2023_24_data_quality_report.json"
SOURCE_URL = "https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab1.11a.pdf"

FIELDS = (
    "financial_year", "state_slug", "state_name", "per_capita_nsdp_current_inr",
    "price_basis", "series_base_year", "source_table", "source_url", "availability_note",
)

# state name, FY 2023-24 rupees per person
# Source: Economic Survey 2025-26 Statistical Appendix, Table 1.11A.
SOURCE_ROWS = (
    ("Andhra Pradesh", 237951), ("Arunachal Pradesh", 217325),
    ("Assam", 143852), ("Bihar", 62201), ("Chhattisgarh", 148922),
    ("Goa", 585953), ("Gujarat", 300957), ("Haryana", 319363),
    ("Himachal Pradesh", 234721), ("Jharkhand", 106529),
    ("Karnataka", 339813), ("Kerala", 281269),
    ("Madhya Pradesh", 139713), ("Maharashtra", 278681),
    ("Manipur", 119938), ("Meghalaya", 141195), ("Mizoram", 234996),
    ("Nagaland", 154828), ("Odisha", 150414), ("Punjab", 205374),
    ("Rajasthan", 166647), ("Sikkim", 587743), ("Tamil Nadu", 313329),
    ("Telangana", 347714), ("Tripura", 172299),
    ("Uttar Pradesh", 97364), ("Uttarakhand", 246178),
    ("West Bengal", 149515), ("Andaman & Nicobar Islands", 276000),
    ("Chandigarh", 453457), ("Delhi", 459408), ("Jammu & Kashmir", 140051),
    ("Ladakh", 242360), ("Puducherry", 252164),
)
MISSING_PHONEPE_GEOGRAPHIES = {
    "Dadra & Nagar Haveli and Daman & Diu",
    "Lakshadweep",
}


def main() -> None:
    if not RAW_PDF.is_file():
        raise FileNotFoundError(f"Missing Economic Survey source PDF: {RAW_PDF}")
    with PHONEPE_PATH.open(encoding="utf-8", newline="") as handle:
        phonepe_states = {row["state_name"]: row["state_slug"] for row in csv.DictReader(handle)}

    source_states = {state_name for state_name, _ in SOURCE_ROWS}
    expected_source_states = set(phonepe_states) - MISSING_PHONEPE_GEOGRAPHIES
    if source_states != expected_source_states:
        raise ValueError(
            f"Economic Survey and PhonePe geographies differ. "
            f"Missing={sorted(expected_source_states - source_states)}; "
            f"unexpected={sorted(source_states - expected_source_states)}"
        )

    note = (
        "The Economic Survey table does not publish State Domestic Product estimates for "
        "Dadra & Nagar Haveli and Daman & Diu or Lakshadweep; no values were imputed."
    )
    output_rows = [
        {
            "financial_year": "2023-24",
            "state_slug": phonepe_states[state_name],
            "state_name": state_name,
            "per_capita_nsdp_current_inr": str(value),
            "price_basis": "current prices",
            "series_base_year": "2011-12 series",
            "source_table": "Economic Survey 2025-26 Statistical Appendix, Table 1.11A",
            "source_url": SOURCE_URL,
            "availability_note": note,
        }
        for state_name, value in SOURCE_ROWS
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    report = {
        "source": "Economic Survey 2025-26 Statistical Appendix, Table 1.11A: Per Capita Net State Domestic Product at Current Prices (2011-12 Series).",
        "source_url": SOURCE_URL,
        "raw_file": str(RAW_PDF.relative_to(PROJECT_ROOT)),
        "raw_file_sha256": hashlib.sha256(RAW_PDF.read_bytes()).hexdigest(),
        "financial_year": "2023-24",
        "rows_written": len(output_rows),
        "geography_match_to_phonepe": "passed for 34 published state/UT estimates",
        "missing_phonepe_geographies": sorted(MISSING_PHONEPE_GEOGRAPHIES),
        "missing_reason": note,
        "time_alignment": "FY 2023-24 is compared only with PhonePe 2024 Q1 (January-March 2024), the quarter ending in the same month as the financial year.",
        "interpretation_warning": "Per capita NSDP is state economic output per resident, not household income or average salary. Values are at current prices and are not adjusted for inflation.",
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(output_rows)} Economic Survey state/UT income snapshot rows")


if __name__ == "__main__":
    main()
