#!/usr/bin/env python3
"""Create a clean state/UT internet-access snapshot from TRAI Table 1.33.

The source table is a June 2024 snapshot. Values are transcribed from the
official PDF after visual verification because its state names and multi-line
UT labels are not a machine-readable table. The script validates the complete
set of project geographies and the published national total.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PDF = PROJECT_ROOT / "data/raw/trai/trai_qpir_june_2024.pdf"
PHONEPE_PATH = PROJECT_ROOT / "data/processed/phonepe_state_user_quarterly.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_PATH = OUTPUT_DIR / "trai_state_internet_subscribers_june_2024.csv"
REPORT_PATH = OUTPUT_DIR / "trai_state_internet_subscribers_june_2024_data_quality_report.json"
SOURCE_URL = "https://www.trai.gov.in/sites/default/files/2024-11/QPIR_09102024_0.pdf"

FIELDS = (
    "as_of_date", "state_slug", "state_name", "rural_subscribers_mn",
    "urban_subscribers_mn", "total_subscribers_mn",
    "rural_subscribers_per_100_population", "urban_subscribers_per_100_population",
    "total_subscribers_per_100_population", "source_table", "source_url",
    "interpretation_note",
)

# state name, rural mn, urban mn, total mn, rural per 100, urban per 100, total per 100
# Source: TRAI QPIR, Table 1.33, end of June 2024. None represents a published dash.
SOURCE_ROWS = (
    ("Andhra Pradesh", 18.04, 17.90, 35.94, 53.87, 89.92, 67.31),
    ("Arunachal Pradesh", 0.55, 0.38, 0.94, 47.39, 93.35, 59.32),
    ("Assam", 13.21, 7.03, 20.24, 43.35, 123.66, 55.98),
    ("Bihar", 37.74, 17.46, 55.21, 33.34, 109.14, 42.73),
    ("Chhattisgarh", 8.62, 8.90, 17.52, 38.85, 105.47, 57.20),
    ("Goa", 0.83, 1.62, 2.45, 229.51, 132.36, 154.54),
    ("Gujarat", 19.03, 37.34, 56.38, 51.76, 104.08, 77.60),
    ("Haryana", 10.08, 19.97, 30.05, 57.46, 151.76, 97.89),
    ("Himachal Pradesh", 4.07, 2.62, 6.68, 60.38, 336.26, 88.92),
    ("Jharkhand", 11.17, 8.78, 19.95, 37.82, 82.86, 49.71),
    ("Karnataka", 21.00, 37.70, 58.70, 55.98, 122.60, 85.99),
    ("Kerala", 16.65, 18.10, 34.75, 211.12, 64.45, 96.61),
    ("Madhya Pradesh", 20.76, 28.89, 49.65, 33.32, 112.72, 56.46),
    ("Maharashtra", 34.39, 76.39, 110.79, 52.70, 122.37, 86.77),
    ("Manipur", 0.98, 1.35, 2.32, 44.53, 126.06, 71.25),
    ("Meghalaya", 1.36, 0.76, 2.13, 50.69, 108.98, 62.76),
    ("Mizoram", 0.54, 0.72, 1.25, 96.05, 103.36, 100.10),
    ("Nagaland", 1.00, 0.69, 1.69, 84.31, 64.09, 74.66),
    ("Odisha", 16.75, 8.49, 25.24, 46.58, 99.81, 56.77),
    ("Punjab", 9.88, 17.82, 27.69, 55.24, 135.87, 89.35),
    ("Rajasthan", 26.47, 26.74, 53.21, 44.00, 121.40, 64.74),
    ("Sikkim", 0.37, 0.29, 0.67, 111.27, 80.59, 95.39),
    ("Tamil Nadu", 17.43, 44.88, 62.31, 49.39, 107.16, 80.75),
    ("Telangana", 13.17, 22.99, 36.16, 67.20, 122.71, 94.33),
    ("Tripura", 1.09, 1.15, 2.24, 43.99, 67.04, 53.37),
    ("Uttar Pradesh", 65.51, 66.46, 131.98, 36.19, 114.89, 55.25),
    ("Uttarakhand", 4.96, 5.06, 10.02, 66.27, 117.40, 84.94),
    ("West Bengal", 25.59, 38.24, 63.82, 40.95, 102.67, 64.00),
    ("Andaman & Nicobar Islands", 0.21, 0.21, 0.42, 95.48, 115.86, 104.61),
    ("Chandigarh", 0.04, 1.30, 1.34, None, None, 107.11),
    ("Dadra & Nagar Haveli and Daman & Diu", 0.29, 0.55, 0.85, 122.44, 48.08, 60.96),
    ("Delhi", 0.29, 35.18, 35.47, None, None, 162.09),
    ("Jammu & Kashmir", 4.50, 5.36, 9.87, 47.45, 126.41, 71.84),
    ("Ladakh", 0.31, 0.11, 0.42, 150.99, 114.08, 139.20),
    ("Lakshadweep", 0.05, 0.00, 0.06, None, None, 83.63),
    ("Puducherry", 0.39, 0.82, 1.21, 77.92, 68.65, 71.39),
)


def text(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def main() -> None:
    if not RAW_PDF.is_file():
        raise FileNotFoundError(f"Missing TRAI source PDF: {RAW_PDF}")
    with PHONEPE_PATH.open(encoding="utf-8", newline="") as handle:
        phonepe_states = {row["state_name"]: row["state_slug"] for row in csv.DictReader(handle)}
    source_states = {row[0] for row in SOURCE_ROWS}
    if source_states != set(phonepe_states):
        raise ValueError(
            f"TRAI and PhonePe geographies differ. Missing={sorted(set(phonepe_states) - source_states)}; "
            f"unexpected={sorted(source_states - set(phonepe_states))}"
        )
    published_national_total_mn = 969.60
    extracted_total_mn = round(sum(row[3] for row in SOURCE_ROWS), 2)
    if abs(extracted_total_mn - published_national_total_mn) > 0.10:
        raise ValueError(f"TRAI total validation failed: {extracted_total_mn} vs {published_national_total_mn}")

    output_rows: list[dict[str, str]] = []
    note = (
        "This is the number of internet subscriptions per 100 population, not unique people with internet access. "
        "A person may hold more than one subscription, so values can exceed 100."
    )
    for state_name, rural_mn, urban_mn, total_mn, rural_per100, urban_per100, total_per100 in SOURCE_ROWS:
        output_rows.append({
            "as_of_date": "2024-06-30",
            "state_slug": phonepe_states[state_name],
            "state_name": state_name,
            "rural_subscribers_mn": text(rural_mn),
            "urban_subscribers_mn": text(urban_mn),
            "total_subscribers_mn": text(total_mn),
            "rural_subscribers_per_100_population": text(rural_per100),
            "urban_subscribers_per_100_population": text(urban_per100),
            "total_subscribers_per_100_population": text(total_per100),
            "source_table": "TRAI QPIR June 2024, Table 1.33",
            "source_url": SOURCE_URL,
            "interpretation_note": note,
        })
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    report = {
        "source": "Telecom Regulatory Authority of India, Quarterly Performance Indicators Report, June 2024, Table 1.33.",
        "source_url": SOURCE_URL,
        "raw_file": str(RAW_PDF.relative_to(PROJECT_ROOT)),
        "raw_file_sha256": hashlib.sha256(RAW_PDF.read_bytes()).hexdigest(),
        "snapshot_date": "2024-06-30",
        "rows_written": len(output_rows),
        "geography_match_to_phonepe": "passed: 36 states/UTs",
        "published_national_total_subscribers_mn": published_national_total_mn,
        "sum_of_rounded_state_ut_totals_mn": extracted_total_mn,
        "interpretation_warning": note,
        "time_alignment": "The snapshot is at the end of June 2024 and will be compared only with PhonePe 2024 Q2 (April-June 2024), not treated as a time series.",
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(output_rows)} TRAI state/UT internet-subscriber snapshot rows")


if __name__ == "__main__":
    main()
