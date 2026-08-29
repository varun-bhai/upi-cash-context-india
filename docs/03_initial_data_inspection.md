# Step 3: Initial inspection — what the clean data can and cannot tell us

This is an orientation pass, not a conclusion about causality. Its purpose is
to make the dataset understandable before writing analytical SQL.

## Clean datasets now available

| Dataset | Grain | Coverage | Main use |
|---|---|---|---|
| PhonePe transactions | state/UT × quarter × category | 2018 Q1–2026 Q2 | State-level adoption and payment-pattern analysis on the PhonePe platform |
| PhonePe users | state/UT × quarter | 2018 Q1–2026 Q2 | State-level user/adoption context |
| PhonePe merchants | state/UT × quarter | incomplete early coverage | Supplementary merchant context; do not treat missing early records as zero |
| RBI-derived daily payments | national × day × mode | 2020-06-01–2026-07-31, with gaps after 2025-07 | National UPI, IMPS, and NFS-at-ATM context |
| RBI-derived quarterly payments | national × quarter × mode | complete quarters: 2020 Q3–2025 Q1 | National trend comparison aligned to PhonePe quarters |

National and state-level data should not be joined and interpreted as if they
measure the same universe: PhonePe is one payment platform, while the RBI
series is national. We can compare their timing and directions, but not use the
combination to estimate a state-level causal effect.

## First trend check: 2020 Q3 to 2025 Q1

The start and end figures below are sums of daily values in full calendar
quarters. Volume is in lakh; value is in INR crore.

| Measure | Volume: first → last | Change | Value: first → last | Change |
|---|---:|---:|---:|---:|
| UPI | 49,163.48 → 514,037.02 | +945.6% | 917,877.32 → 7,021,740.40 | +665.0% |
| IMPS | 7,478.31 → 13,106.91 | +75.3% | 709,574.03 → 1,837,314.61 | +158.9% |
| NFS through ATMs | 8,881.51 → 8,507.03 | −4.2% | 363,770.96 → 380,551.13 | +4.6% |

This is a useful **question generator**: UPI growth coincides with broadly
flat NFS-at-ATM activity over this window. That is consistent with changing
payment behavior, but it is not proof that UPI displaced cash. Cash use can be
affected by income, inflation, ATM availability, seasonality, policy, and
withdrawals outside the NFS measure.

## Data-quality decisions already applied

- The national source contained 31 duplicate July 2026 records. They were
  identical on all fields we use, so the cleaner keeps one deterministic copy
  and records the count in `idp_rbi_data_quality_report.json`.
- The source has complete months through 2025-05, July 2025, and July 2026,
  but does not provide every intervening month. We therefore keep daily and
  monthly observations, while the quarterly table includes only complete
  calendar quarters.
- NFS through ATMs is labelled as a cash-access proxy throughout. It is not
  total ATM cash withdrawals and is not cash spending.

## Sensible next step

Load the clean CSVs into SQLite and start with descriptive SQL: row counts,
coverage checks, category shares, and state/UT adoption rankings. We should
write those queries before asking any causal question.
