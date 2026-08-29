# Step 15: Does merchant availability line up with PhonePe usage?

## The question

One reasonable explanation for high UPI usage is that people have more places
to pay digitally. We already have one relevant measure: the number of
**registered PhonePe merchants** in each state/UT.

This is not the total number of all UPI merchants in India. It is PhonePe's
registered merchant count. It is still useful for asking a narrower question:

> Across states, does higher PhonePe merchant density go together with more
> PhonePe transactions per resident and a larger Retail payment share?

## Why we start after 2019

Merchant data is incomplete in early 2018: only 18 of 36 state/UT records are
available in 2018 Q1. From 2019 Q3 onward, all 36 are present. We therefore
use 2020 Q1 to 2025 Q1 for the growth comparison and do not turn early missing
records into zeroes.

## What “merchant density” means

```text
registered merchant density = registered PhonePe merchants / population
```

For readability, we often show it as merchants per 100 residents. This is a
relative availability measure. It does **not** tell us whether each listed
merchant was active in that quarter or accepted only PhonePe.

## Result 1: states with more merchants also tend to have more activity

For 2025 Q1, using all 36 states/UTs:

| Comparison | Correlation | Plain meaning |
|---|---:|---|
| Merchant density vs. transactions per resident | 0.698 | Strong positive association. States with more registered PhonePe merchants per resident usually had more PhonePe transactions per resident. |
| User density vs. transactions per resident | 0.809 | An even stronger association. States with more registered users per resident usually had more transactions. |
| Merchant density vs. Retail share | 0.561 | A moderate positive association. Merchant-dense states tended to have a more retail-oriented PhonePe payment mix. |

A correlation of `1` would mean a perfect positive straight-line relationship,
`0` means no straight-line relationship, and `-1` means a perfect negative
relationship. These are all positive, but they are not proof that one variable
caused another.

For example, Delhi had the highest merchant density at 7.84 registered
merchants per 100 residents, but Telangana had the highest transaction
intensity at 76.9 transactions per resident. This is a useful reminder that
merchant count is part of the explanation, not the whole explanation.

## Result 2: growth moved together, but less strongly

From 2020 Q1 to 2025 Q1, states with larger **percentage-like log increases**
in merchant density also tended to show larger increases in transaction
intensity (correlation **0.546**). The equivalent correlation for growth in
registered users was **0.681**.

This suggests a practical working hypothesis:

> Broad user adoption seems more closely connected with usage intensity than
> merchant registration alone, while merchant availability still matters.

It is a hypothesis, not a causal conclusion. High transaction use can itself
attract merchants, and both can be driven by income, city density, internet
access, local business structure, or PhonePe's expansion choices.

## What we can say, and what we cannot

We can say:

- merchant density, user density and transaction intensity move together
  positively across states;
- the relationship is visible both in a single later quarter and in 2020-2025
  growth comparisons; and
- merchant density also lines up positively with the Retail share.

We cannot yet say:

- adding one merchant causes a particular number of transactions;
- PhonePe's merchant count represents all UPI merchant acceptance; or
- higher merchant density displaced cash.

## Reproducibility

Run:

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/09_merchant_density_and_usage.sql
```

The next useful outside data to add is a state-level measure of internet access
or urban/economic activity. That will help us see whether the merchant pattern
remains after accounting for a broader state environment.
