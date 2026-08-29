# Step 10: National UPI-app data from NPCI

## Why this matters

PhonePe Pulse gives us state-level detail, but only for PhonePe. This new table
adds a national view of competition between UPI apps: PhonePe, Google Pay,
Paytm, BHIM, Amazon Pay, WhatsApp, bank apps, and others.

It lets us ask app-ecosystem questions such as:

> Did PhonePe gain or lose national share while its state-level Retail mix was
> changing?

## Source and validation

NPCI's public [UPI Ecosystem Statistics](https://www.npci.org.in/product/ecosystem-statistics/upi)
page exposes monthly UPI Applications tables and downloadable reports. Direct
automated download was unreliable, so we used a public reference snapshot that
documents the original NPCI report collection. Before accepting it, we compared
its July 2025 data with the official NPCI table in the browser:

| App | NPCI volume (million) | NPCI value (INR crore) |
|---|---:|---:|
| PhonePe | 8,931.24 | 1,220,140.68 |
| Google Pay | 6,922.92 | 891,297.38 |
| Paytm | 1,366.05 | 143,650.62 |

All three matched exactly. The reference snapshot is retained locally and
ignored by version control; its commit is recorded in the data-quality report.

## What the clean table contains

File: `data/processed/npci_upi_app_monthly.csv`

It has 3,766 app-month rows, covering January 2022 to April 2026. March 2026
is missing from the reference snapshot and is never fabricated.

Each row represents one app's **national** activity in one month. The main
columns are:

| Column | Meaning |
|---|---|
| `month_start_date` | The month, represented by its first day, for example `2025-07-01` |
| `app_name` | Name of the UPI app, for example `PhonePe` or `Google Pay` |
| `customer_initiated_volume_mn` | Customer-initiated transaction count in millions, when supplied by NPCI |
| `customer_initiated_value_crore` | Value of those transactions in INR crore, when supplied |
| `b2c_*`, `b2b_*` | Business-to-customer and business-to-business measures, when supplied |
| `total_volume_mn`, `total_value_crore` | Total transactions for that app in the month |
| `source_reference` | Provenance record: official NPCI source accessed through the validated snapshot |

Some older reports leave B2C/B2B fields blank. Blank means “not reported in
that layout”, not zero. Total volume is available in every row; a few total
value cells are also blank and stay blank.

NPCI attributes an app transaction using its **payer-app** logic: in simple
terms, the app used by the person sending the payment receives the attribution.

## First result

In a like-for-like January comparison:

| App | Jan 2022 volume share | Jan 2026 volume share | Change |
|---|---:|---:|---:|
| PhonePe | 45.46% | 46.60% | +1.15 percentage points |
| Google Pay | 33.65% | 33.98% | +0.34 points |
| Paytm | 15.09% | 7.80% | -7.28 points |

The immediate descriptive takeaway is that PhonePe and Google Pay remained the
two leading apps by transaction volume, while Paytm's share was much lower by
January 2026. This says nothing about state-level market shares and does not
explain why shares changed.

## Important limitation

Do not join an app's national monthly share to a state's PhonePe transaction
row and call that a state app-share result. The levels are different:

- PhonePe Pulse: state/UT level, PhonePe only, quarterly.
- NPCI apps: India-wide, many apps, monthly.

They can be compared as parallel context after being aggregated to the same
time period, but not treated as the same geographic measure.
