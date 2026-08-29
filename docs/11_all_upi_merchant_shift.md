# Step 11: Is the PhonePe Retail shift part of a wider UPI shift?

## New data

We added the official NPCI monthly national P2P/P2M series, covering January
2022 to March 2026.

- **P2P** means person-to-person payments.
- **P2M** means person-to-merchant payments.

This is different from PhonePe's `Retail` category, but both are useful
indicators of merchant-payment activity. We compare their direction and timing,
not assume they are exactly the same classification.

The August 2025 record matched the official NPCI page exactly: 20,008.31
million total transactions, made up of 7,303.15 million P2P and 12,705.16
million P2M transactions.

## Result

The PhonePe pattern is not PhonePe-only. In the common 2022 Q1–2026 Q1 window:

| Measure | 2022 Q1 | 2026 Q1 | Change |
|---|---:|---:|---:|
| All-UPI P2M share | 41.0% | 62.7% | +21.7 percentage points |
| PhonePe Retail share | 49.1% | 62.5% | +13.5 percentage points |

All-UPI P2M crossed 50% of transaction volume in 2022 Q3. PhonePe's Retail
share was already above 50% in 2022 Q2. By 2023, the two measures were close,
and from then the all-UPI P2M share was slightly higher.

The careful conclusion is:

> PhonePe's growing Retail share appears to be part of a broader national move
> toward merchant payments on UPI, rather than a PhonePe-only change.

This does not show that people stopped using cash because of UPI. It does make
the story more credible: the shift appears in an independent all-UPI source.

## Data-quality note

For September 2023, the published NPCI total volume is 1 million transactions
higher than its P2P and P2M components combined. We preserve the published
values and flag this in the quality report rather than overwrite the source.

## Next research question

Now that the merchant-payment shift is visible both in PhonePe and all UPI, the
next important check is source comparability:

> Do the sum of national app volumes and the separate national UPI series in
> our RBI-derived data broadly agree each month?

That is a data-quality check before we use app shares and cash-access measures
in one combined story.
