# Step 1: PhonePe data acquisition and cleaning

## Why this is our first step

Before writing SQL, we need an auditable local dataset. The PhonePe Pulse source
provides quarterly, state/UT-level activity; it does **not** represent all UPI
transactions in a state. We will therefore call it PhonePe activity throughout
the project until a validated all-UPI state-level source is available.

## What is stored locally

- `data/raw/phonepe_pulse/` — a shallow clone of the public PhonePe Pulse Git
  repository. Keep it unchanged: it is our source snapshot.
- `scripts/extract_phonepe.py` — repeatable transformation from raw JSON to
  clean CSVs. It uses only the Python standard library.
- `data/processed/` — generated analysis-ready files and the quality report.

The source snapshot used for this run is commit
`f9bdd6b6eec3eb39fce5524c60b65ebe373b9652` (downloaded 2026-08-29).

## Observed source structure

The extractor reads these raw folders:

- `data/aggregated/transaction/country/india/state/<state>/<year>/<quarter>.json`
- `data/aggregated/user/country/india/state/<state>/<year>/<quarter>.json`
- `data/aggregated/merchant/country/india/state/<state>/<year>/<quarter>.json`

We preserve two state fields:

- `state_slug` is the source’s stable folder name and will be the eventual join key.
- `state_name` is only a readable display label.

## Cleaning decisions

1. Raw JSON is never edited.
2. Each value is attached to a quarter-start date to make time joins explicit.
3. Transaction categories are copied exactly as supplied. We do not silently
   rename `Retail` to `Business`, because that would be an analytical
   assumption that needs documentation and validation.
4. Transaction values are retained as decimal rupee values, without conversion
   to lakhs or crores. Unit conversion, if needed, happens only in a derived
   SQL query.
5. A missing source file or missing category is recorded as missing—not as zero.
   This distinction matters most for the early merchant data.

## Run it

From the project root:

```bash
python3 scripts/extract_phonepe.py
python3 scripts/profile_phonepe.py
```

The next step is to inspect the generated quality report and profiles together.
Only after that will we decide which tables and questions to build in SQL.

## Results of the first extraction

- Transactions: 36 state/UT entities, every quarter from 2018 Q1 to 2026 Q2,
  with 3,671 category-level records.
- Users: the same 36 entities and all 34 quarters, with 1,224 records.
- Merchants: 1,178 records. Early quarters are absent for some entities; the
  exact 46 missing entity-quarter observations are recorded in the quality
  report and must remain missing in later analysis.
- One category is absent in one source file: `Utility` for Lakshadweep in 2018
  Q1. It is recorded as missing rather than changed to zero.

## Reconciliation check

For every available quarter and category, `profile_phonepe.py` sums the state/UT
records and compares that sum with PhonePe's separate country-level JSON file.
All 102 transaction-count comparisons reconcile exactly. The largest rupee-value
difference is ₹24.12162438, a negligible floating-point aggregation difference
against totals measured in billions or trillions of rupees. This gives us a
useful check that the JSON parser has neither dropped nor duplicated records.

The resulting `phonepe_national_reconciliation_quarterly.csv` is a validation
artifact, not a substitute for the RBI or NPCI national payment series.

## Important interpretation rule

`registered_count` is a level reported for a quarter, not a quarterly flow.
It is meaningful to compare its level or quarter-to-quarter change; it is not
meaningful to add registered-user or registered-merchant counts across quarters.
