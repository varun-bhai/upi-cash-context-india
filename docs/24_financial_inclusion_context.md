# Step 24: Testing financial-inclusion context at the state level

This step answers a sensible follow-up question: could a state-level banking or
financial-inclusion measure make our PhonePe analysis more useful? We tested a
free, official source rather than assuming that it would help.

## The data we added

The Ministry of Finance's PMJDY website publishes a state-wise account-opening
report. We saved the **19 August 2026** page and extracted its 36 state/UT
rows. The cleaned file is
`data/processed/pmjdy_state_financial_inclusion_2026_08_19.csv`.

It contains:

- **Rural/semi-urban beneficiaries** and **urban/metro beneficiaries** — the
  PMJDY beneficiary counts reported at bank branches in each location type.
- **Total beneficiaries** — the reported total of those two components.
- **Balance in beneficiary accounts** — the reported amount held in these
  accounts, in rupees crore.
- **RuPay debit cards issued** — cards issued to PMJDY beneficiaries.

We divide total beneficiaries by the 2026 population estimate only to compare
different-sized states fairly. For example, 71 PMJDY beneficiaries per 100
residents in Assam does **not** mean that 71% of residents are uniquely banked
or actively using a payment app. A reported beneficiary/account count and a
count of people are not the same thing.

The snapshot is 50 days after the end of PhonePe 2026 Q2 (April--June). That is
close enough for a one-time descriptive comparison, but not exact time
alignment and not a quarterly PMJDY trend.

## The test result

We checked whether a state with more PMJDY beneficiaries per resident also had
more PhonePe use in 2026 Q2. Across all 36 states/UTs:

| Comparison | Pearson correlation |
|---|---:|
| PMJDY beneficiaries per resident vs. registered PhonePe users per resident | -0.184 |
| PMJDY beneficiaries per resident vs. PhonePe transactions per resident | +0.080 |

Both values are close to zero. In plain language: this one PMJDY snapshot does
**not** line up in a simple, useful way with either broader registered PhonePe
coverage or more intensive PhonePe payments across states.

That is an important data-analysis result. It prevents us from making a weak
business claim such as “states with more financial inclusion should be the next
UPI-app targets.” PMJDY was designed to reach people who were financially
excluded, so its beneficiary density can reflect many things at once: the
starting level of financial inclusion, state demographics, migration, account
history, and programme coverage. It is not a direct measure of app-ready bank
customers.

## What we keep, and what we do not claim

We keep the PMJDY snapshot in the database because it is clean, documented,
and useful for asking better questions. We do **not** put it in the main
dashboard story or use it to score markets.

The final query lists states that are in the top half of PMJDY beneficiary
density but bottom half of PhonePe registered-user density. That list is an
interview-style diagnostic prompt only:

> “What local friction—device access, language, onboarding, merchant
> acceptance, or something else—might explain this pattern?”

To answer it, a real payments company would need privacy-safe internal data on
active accounts, app installs, onboarding completion, payment success rates,
merchant availability, and costs. The public data cannot tell us whether the
PMJDY beneficiaries and PhonePe users are even the same people.

## Reproduce it

```bash
python3 scripts/extract_pmjdy_state_snapshot.py
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/16_financial_inclusion_context.sql
```

The extraction script verifies all 36 PMJDY state/UT rows against the PhonePe
geography and records the saved source page's SHA-256 fingerprint in the data-
quality report.
