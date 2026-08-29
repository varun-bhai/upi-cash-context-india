#!/usr/bin/env python3
"""Extract annual state/UT population projections from the official MoHFW PDF.

The source table reports people as on 1 March, in thousands.  We retain its
annual values and aggregate Dadra & Nagar Haveli with Daman & Diu so the
geography matches the PhonePe Pulse state series.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "data/raw/population/mohfw_population_projections_2011_2036.pdf"
PHONEPE_PATH = PROJECT_ROOT / "data/processed/phonepe_state_user_quarterly.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/processed"
OUTPUT_PATH = OUTPUT_DIR / "population_state_annual.csv"
REPORT_PATH = OUTPUT_DIR / "population_state_data_quality_report.json"
SOURCE_URL = "https://nhm.gov.in/New_Updates_2018/Report_Population_Projection_2019.pdf"

FIELDS = (
    "state_slug", "state_name", "year", "population_persons",
    "source_state_or_aggregation", "source_table", "source_date_basis",
    "source_url", "method_note",
)

# Table 8 is arranged across pages in this order. The first element is India,
# which is used only as a validation check, not an analytical state row.
TABLE_GROUPS = (
    ("INDIA", "JAMMU & KASHMIR", "HIMACHAL PRADESH"),
    ("PUNJAB", "HARYANA", "NCT OF DELHI"),
    ("RAJASTHAN", "UTTAR PRADESH", "BIHAR"),
    ("ASSAM", "WEST BENGAL", "JHARKHAND"),
    ("ODISHA", "CHHATTISGARH", "MADHYA PRADESH"),
    ("GUJARAT", "MAHARASHTRA", "ANDHRA PRADESH"),
    ("KARNATAKA", "KERALA", "TAMIL NADU"),
    ("CHANDIGARH", "UTTARAKHAND", "SIKKIM"),
    ("ARUNACHAL PRADESH", "NAGALAND", "MANIPUR"),
    ("MIZORAM", "TRIPURA", "MEGHALAYA"),
    ("DAMAN & DIU", "DADRA & NAGAR", "GOA"),
    ("LAKSHADWEEP", "PUDUCHERRY", "ANDAMAN & NICOBAR"),
    ("TELANGANA", "LADAKH"),
)

SOURCE_TO_PROJECT_STATE = {
    "JAMMU & KASHMIR": "Jammu & Kashmir",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "PUNJAB": "Punjab",
    "HARYANA": "Haryana",
    "NCT OF DELHI": "Delhi",
    "RAJASTHAN": "Rajasthan",
    "UTTAR PRADESH": "Uttar Pradesh",
    "BIHAR": "Bihar",
    "ASSAM": "Assam",
    "WEST BENGAL": "West Bengal",
    "JHARKHAND": "Jharkhand",
    "ODISHA": "Odisha",
    "CHHATTISGARH": "Chhattisgarh",
    "MADHYA PRADESH": "Madhya Pradesh",
    "GUJARAT": "Gujarat",
    "MAHARASHTRA": "Maharashtra",
    "ANDHRA PRADESH": "Andhra Pradesh",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "TAMIL NADU": "Tamil Nadu",
    "CHANDIGARH": "Chandigarh",
    "UTTARAKHAND": "Uttarakhand",
    "SIKKIM": "Sikkim",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "NAGALAND": "Nagaland",
    "MANIPUR": "Manipur",
    "MIZORAM": "Mizoram",
    "TRIPURA": "Tripura",
    "MEGHALAYA": "Meghalaya",
    "GOA": "Goa",
    "LAKSHADWEEP": "Lakshadweep",
    "PUDUCHERRY": "Puducherry",
    "ANDAMAN & NICOBAR": "Andaman & Nicobar Islands",
    "TELANGANA": "Telangana",
    "LADAKH": "Ladakh",
}


def read_pdf_text(path: Path) -> str:
    command = ["pdftotext", "-layout", str(path), "-"]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def parse_group_page(page: str, group: tuple[str, ...]) -> dict[str, dict[int, int]]:
    """Read the Persons column for each state on one Table 8 page."""
    lines = page.splitlines()
    rows: list[tuple[int, list[int]]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.fullmatch(r"\s*20(?:1\d|2\d|3[0-6])\s*", line):
            line = f"{line} {lines[index + 1] if index + 1 < len(lines) else ''}"
            index += 1
        values = re.findall(r"\d[\d,]*", line)
        if values and re.fullmatch(r"20(?:1\d|2\d|3[0-6])", values[0]):
            expected_values = 1 + 3 * len(group)
            if len(values) == expected_values:
                rows.append((int(values[0]), [int(value.replace(",", "")) for value in values[1:]]))
        index += 1
    if len(rows) != 26 or {year for year, _ in rows} != set(range(2011, 2037)):
        raise ValueError(f"Could not read all 2011-2036 rows for Table 8 group {group!r}")
    result: dict[str, dict[int, int]] = {state: {} for state in group}
    for year, values in rows:
        for position, state in enumerate(group):
            result[state][year] = values[position * 3] * 1_000
    return result


def main() -> None:
    if not PDF_PATH.is_file():
        raise FileNotFoundError(f"Missing official population PDF: {PDF_PATH}")
    text = read_pdf_text(PDF_PATH)
    pages = text.split("\f")
    parsed: dict[str, dict[int, int]] = {}
    for group in TABLE_GROUPS:
        matches = [page for page in pages if all(marker in page for marker in group) and "Projected Total Population by Sex as on 1st March" in page]
        if len(matches) != 1:
            raise ValueError(f"Expected one Table 8 page for {group!r}, found {len(matches)}")
        parsed.update(parse_group_page(matches[0], group))

    # The official India total is a convenient extraction check. It is not a
    # sum of the analytical regions after the PhonePe geography mapping.
    if parsed["INDIA"][2024] != 1_398_598_000:
        raise ValueError("Official India total validation failed for 2024")

    project_values: dict[str, dict[int, int]] = {}
    project_source: dict[str, str] = {}
    for source_name, project_name in SOURCE_TO_PROJECT_STATE.items():
        project_values[project_name] = parsed[source_name]
        project_source[project_name] = source_name.title()
    combined_name = "Dadra & Nagar Haveli and Daman & Diu"
    project_values[combined_name] = {
        year: parsed["DAMAN & DIU"][year] + parsed["DADRA & NAGAR"][year]
        for year in range(2011, 2037)
    }
    project_source[combined_name] = "Daman & Diu + Dadra & Nagar Haveli"

    with PHONEPE_PATH.open(encoding="utf-8", newline="") as handle:
        phonepe_states = {row["state_name"]: row["state_slug"] for row in csv.DictReader(handle)}
    missing_from_population = sorted(set(phonepe_states) - set(project_values))
    unexpected_population = sorted(set(project_values) - set(phonepe_states))
    if missing_from_population or unexpected_population:
        raise ValueError(
            f"State geography did not match PhonePe. Missing={missing_from_population}; unexpected={unexpected_population}"
        )

    output_rows: list[dict[str, str]] = []
    for state_name in sorted(project_values):
        for year in range(2011, 2037):
            output_rows.append({
                "state_slug": phonepe_states[state_name],
                "state_name": state_name,
                "year": str(year),
                "population_persons": str(project_values[state_name][year]),
                "source_state_or_aggregation": project_source[state_name],
                "source_table": "Table 8: projected total population by sex as on 1 March",
                "source_date_basis": "1 March of each calendar year",
                "source_url": SOURCE_URL,
                "method_note": "Dadra & Nagar Haveli and Daman & Diu are summed to match the merged PhonePe geography.",
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    report = {
        "source": "National Commission on Population, Ministry of Health & Family Welfare, Population Projections for India and States 2011-2036 (July 2020).",
        "source_url": SOURCE_URL,
        "raw_file": str(PDF_PATH.relative_to(PROJECT_ROOT)),
        "raw_file_sha256": hashlib.sha256(PDF_PATH.read_bytes()).hexdigest(),
        "source_table": "Table 8, projected total population as on 1 March; source unit is thousands of persons.",
        "rows_written": len(output_rows),
        "coverage": {"states_uts": len(project_values), "first_year": 2011, "last_year": 2036},
        "geography_decision": "Daman & Diu and Dadra & Nagar Haveli are summed in every year to match PhonePe's merged state/UT label.",
        "validations": {
            "phonepe_state_geography_match": "passed",
            "official_india_total_2024_persons": parsed["INDIA"][2024],
            "expected_official_india_total_2024_persons": 1_398_598_000,
        },
    }
    with REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(f"Created {len(output_rows):,} annual population rows for {len(project_values)} states/UTs")


if __name__ == "__main__":
    main()
