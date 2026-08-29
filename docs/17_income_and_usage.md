# Step 17: Does state income help explain PhonePe usage differences?

## Why this is a useful question

Internet access and merchant availability are not the whole story. A state with
more economic activity may have more smartphones, formal businesses, digital
payment opportunities, and people able to adopt a payment app. So we added one
carefully documented measure of state economic scale: **per capita Net State
Domestic Product (NSDP)**.

This is a descriptive explanation check. It asks whether places that are
economically richer per resident also tend to have more PhonePe activity. It
does **not** claim that income causes PhonePe use.

## What this new data means

The source is the Government of India's *Economic Survey 2025-26 Statistical
Appendix*, Table 1.11A. We use its 2023-24 column.

| Term | Simple meaning |
|---|---|
| NSDP | The value produced by a state's economy after allowing for wear and tear of capital. |
| Per capita | Divided by the number of residents: an amount per person. |
| Current prices | Rupee values in the prices of that time, so they are not adjusted for inflation. |
| FY 2023-24 | The financial year from April 2023 to March 2024. |

This is **not** average salary, household income, or the amount any particular
person earns. It is a broad state-level economic-output measure.

## The data we saved

- `data/raw/economic_survey/economic_survey_2025_26_table_1_11a.pdf` — the
  original official one-page table.
- `data/processed/economic_survey_state_per_capita_nsdp_fy2023_24.csv` — 34
  clean state/UT rows.
- `data/processed/economic_survey_state_per_capita_nsdp_fy2023_24_data_quality_report.json`
  — source, verification, timing, and coverage notes.
- `sql/11_income_and_usage.sql` — the reproducible SQL questions.

The PhonePe project has 36 state/UT geographies. The Economic Survey table
publishes 34 matching estimates. It does not publish State Domestic Product
estimates for **Dadra & Nagar Haveli and Daman & Diu** or **Lakshadweep**. We
leave those two places out of this comparison. We do not guess or fill in their
values.

## Matching the time honestly

FY 2023-24 ends in March 2024. We therefore compare this income snapshot only
with PhonePe **2024 Q1 (January-March 2024)**, the quarter ending in that same
month. This is one cross-state snapshot, not an income time series.

## What we calculated

For each of the 34 matched state/UTs, we compared per-person NSDP with:

- `transactions_per_resident` — how many PhonePe transactions occurred per
  resident in the quarter;
- `registered_users_per_resident` — the number of reported PhonePe
  registrations relative to population;
- `registered_merchants_per_resident` — reported PhonePe merchants relative to
  population; and
- Retail share — the percentage of a state's PhonePe transactions that were
  merchant/shop payments.

Before calculating correlations, we use the **natural logarithm** of income.
That sounds technical, but the idea is simple: raw income values range from
Rs 62,201 per person in Bihar to Rs 587,743 in Sikkim. A log scale treats a
similar *percentage* difference more fairly and stops a few very high-income,
small places from overwhelming the comparison.

## Result

| 2024 Q1 comparison, 34 state/UTs | Correlation | Plain-English reading |
|---|---:|---|
| Log income vs. PhonePe user density | 0.719 | Strong positive association. Higher-income places tended to have more registered PhonePe users per resident. |
| Log income vs. transaction intensity | 0.394 | Moderate positive association. Income explains some, but far from all, of usage intensity. |
| Log income vs. merchant density | 0.366 | Moderate positive association. |
| Log income vs. Retail share | 0.423 | Moderate positive association. |

The most important result is the contrast between **joining** and **using**:

> Income is much more closely associated with how widely PhonePe is registered
> than with how intensely it is used.

Examples show why this matters. Telangana was fairly high income (Rs 347,714
per person) and had very high activity (56.7 transactions per resident).
Karnataka was similar (Rs 339,813; 40.9 transactions). But Sikkim had the
highest income in the matched data (Rs 587,743) and only 8.3 transactions per
resident; Kerala had Rs 281,269 and 5.1 transactions. Income is clearly not a
complete explanation.

## What we can and cannot say

We can say that richer state economies tend to have more reported PhonePe
registrations per resident in this one snapshot. We cannot say that raising
income would cause registrations or transactions to rise by a particular
amount.

Many overlapping factors could be involved: urbanisation, types of local
businesses, merchant acceptance, age structure, smartphone use, network
quality, state payment habits, and PhonePe's own local presence. A high-use
state may also become attractive to merchants, so cause and effect can go in
both directions.

With only 34 places and one income snapshot, a large multi-variable regression
would look more scientific than it really is. We are deliberately keeping this
as a transparent descriptive check for now.

## Reproduce it

```bash
python3 scripts/extract_economic_survey_nsdp_2023_24.py
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/11_income_and_usage.sql
```

## Best next question

We now have three plausible supporting conditions: income, internet
subscriptions, and merchant density. The next sensible step is to build a
simple state-profile table that puts them side by side and looks for meaningful
exceptions (for example, highly connected and high-income states with low
PhonePe use). Those exceptions are often more informative than a single
average correlation.
