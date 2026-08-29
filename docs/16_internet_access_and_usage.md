# Step 16: Does internet access explain PhonePe usage differences?

## Why add internet data?

UPI needs an internet-connected device, so it is reasonable to ask whether
states with more internet access also have more PhonePe activity. This is an
explanation check, not a causal test.

We added the Telecom Regulatory Authority of India's (TRAI) **June 2024**
state/UT snapshot of internet subscribers.

New files:

- `data/raw/trai/trai_qpir_june_2024.pdf` - original TRAI report.
- `data/processed/trai_state_internet_subscribers_june_2024.csv` - 36 clean
  state/UT rows from Table 1.33.
- `data/processed/trai_state_internet_subscribers_june_2024_data_quality_report.json`
  - source and validation record.

## What the internet measure means

The central field is `total_subscribers_per_100_population`:

```text
internet subscription density = internet subscriptions / 100 residents
```

It is **not** the percentage of unique people who use the internet. One person
may have several SIMs or data connections. That is why Delhi's value is 162.1
and Goa's is 154.5: more than 100 subscriptions per 100 residents is possible.

## Matching time carefully

The TRAI figure is measured at the **end of June 2024**. We compare it only
with PhonePe's **2024 Q2 (April-June)** state data. We do not pretend a single
June snapshot is a complete quarterly internet time series.

All 36 TRAI state/UT rows matched all 36 PhonePe state/UT rows for that
quarter.

## Result

| Comparison in 2024 Q2 | Correlation | Interpretation |
|---|---:|---|
| Internet subscription density vs. PhonePe user density | 0.665 | Moderately strong positive association. Better-connected states tended to have more PhonePe registrations per resident. |
| Internet subscription density vs. PhonePe transaction intensity | 0.302 | Weak positive association. Internet density alone does not explain how many transactions occur. |
| Internet subscription density vs. PhonePe merchant density | 0.319 | Weak positive association. |
| Internet subscription density vs. PhonePe Retail share | 0.270 | Weak positive association. |

The main learning is:

> Internet connectivity appears more closely related to **joining PhonePe**
> than to **how intensively people transact after joining**.

The examples make this easy to see. Telangana had both high internet density
(94.3 subscriptions per 100 residents) and very high transaction intensity
(62.8 transactions per resident). But Kerala had similarly high internet
density (96.6) and much lower PhonePe transaction intensity (5.4). Mizoram had
100.1 subscriptions per 100 residents and only 1.7 PhonePe transactions per
resident.

So internet access is likely a necessary supporting condition, but it is not a
complete explanation. Merchant acceptance, local payment habits, incomes,
urbanisation, and app preferences can still matter.

## What this does **not** prove

This is a one-time comparison across 36 places. It cannot prove that more
internet subscriptions caused more PhonePe users or transactions. A richer,
more urban state might have both high connectivity and high payment use for
other reasons.

It also measures all internet subscriptions, not PhonePe users' connection
quality and not unique people. We should never turn this into a claim like
“a 1-point increase in internet access causes X transactions.”

## Reproducibility

```bash
python3 scripts/extract_trai_internet_june_2024.py
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/10_internet_access_and_usage.sql
```

## Next research direction

The next outside factor should be a comparable state-level measure of economic
activity or income. It may help explain why two similarly connected states,
such as Telangana and Kerala, can have very different transaction intensity.
