# Step 6: Follow-up on the Retail-share shift

We followed the first pattern instead of assuming its explanation.

## What survived the checks

The PhonePe source uses the same visible labels—`P2P`, `Retail`, and
`Utility`—throughout the 2018 Q1–2026 Q2 transaction series. `P2P` and
`Retail` appear for every state/UT-quarter; one `Utility` record is missing for
Lakshadweep in 2018 Q1. This supports label continuity, but it cannot prove
that PhonePe never changed the underlying category definitions. We should make
that limitation explicit in any final report.

The Retail-share increase is broad: 35 of 36 state/UT entities increased their
Retail share between 2020 Q3 and 2025 Q1, by 14.6 percentage points on average.
That makes it less plausible that the national result is caused only by a few
large states.

## Merchant context: useful, but not an explanation yet

Merchant records are complete for every state/UT in the 2020 Q3–2025 Q1
comparison window. That lets us explore merchant levels without treating gaps
as zero.

However, the correlation across states between a state's increase in Retail
share and its **absolute** increase in registered PhonePe merchants is only
`0.118`—a weak positive relationship. This tells us that, in this simple
state-level comparison, merchant additions alone do not explain much of the
variation in the Retail-share shift.

We deliberately use absolute additions rather than percentage merchant growth:
percentage growth from a small starting base can be huge and misleading. The
simple percentage-growth version even gave a negative correlation, illustrating
why denominator choices matter.

This is still not a causal test. Other factors—state size, customer adoption,
merchant activity rather than registration, category definitions, time trends,
and local conditions—could all matter.

## Best next question

Instead of asking whether merchant *counts* explain the share shift, examine
whether states that begin with a lower Retail share catch up faster. If so, the
pattern may be convergence in PhonePe's transaction mix rather than a direct
merchant-registration effect. That question needs no new dataset and is a good
next SQL exercise.

Run the reproducible queries with:

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/04_retail_shift_deep_dive.sql
```
