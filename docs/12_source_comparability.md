# Step 12: Do our two national UPI sources agree?

## Why do this check?

We now have two separate ways to describe national UPI activity:

1. **NPCI app data**: monthly transactions attributed to individual apps, such
   as PhonePe, Google Pay, and Paytm. Adding all apps gives a national-looking
   total.
2. **RBI-derived UPI data**: a national UPI total from the RBI Daily Digital
   Payments series, collected through the free India Data Portal API and summed
   to months.

They should be broadly similar, but they are not automatically the same dataset
or definition. This is a reconciliation check, not a reason to overwrite either
source.

## What we compared

The new file
`data/processed/national_upi_source_comparison_monthly.csv` compares every
overlapping month. Its important columns are:

- `npci_apps_total_volume_mn`: all app transactions added together, in
  millions.
- `idp_rbi_upi_volume_mn`: the independent RBI-derived national UPI total,
  converted from lakh to millions. (10 lakh = 1 million.)
- `volume_ratio`: app total divided by RBI-derived total. A value near `1`
  means close agreement.
- Equivalent `value_*` columns for money moved, in crore rupees.
- `comparison_status`: a plain-language quality flag.

## Result

There are 42 overlapping months, from January 2022 through July 2025.

- The app-total **volume** ratio ranges from **0.9816 to 1.0197**, with an
  average of **1.0040**. In everyday language: the two transaction-count series
  differ by no more than about 2% in either direction. That is strong agreement.
- From **April 2022 onward**, transaction **values** also differ by no more than
  about 2%.
- January--March 2022 are an exception: their app-value totals are only about
  17% of the RBI-derived value. We have not guessed why. Those three values are
  flagged and must not be used as a national-value cross-check.

## Decision we will follow

| Question | Preferred source | Reason |
|---|---|---|
| How large is UPI overall? | RBI-derived national series | It is a direct national payment indicator. |
| Which app has what share? | NPCI app series | It is app-level by design. |
| Do the two tell the same volume trend? | Both, after checking this file | Their volume totals closely corroborate each other. |
| What happened to app-level money value in Jan--Mar 2022? | Do not compare it with the national value total | The mismatch is unresolved. |

This lets us say that the app-share story is grounded in an app-level source,
while national UPI totals come from a separate source. It does **not** mean that
either source proves a change in cash use.

## Reproducibility

Run this check again with:

```bash
python3 scripts/compare_national_upi_sources.py
```

It writes the comparison CSV and
`data/processed/national_upi_source_comparison_report.json`. The report retains
the three warnings instead of hiding them.
