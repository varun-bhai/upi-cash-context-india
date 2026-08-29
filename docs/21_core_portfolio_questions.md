# Step 21: Core portfolio questions completed

This note completes the remaining foundational, intermediate, and advanced SQL
questions from the original project brief. These are descriptive results from
the public data; the PhonePe state results are not all-UPI state totals.

## 1. Latest state leaders by transaction value

In **2026 Q2**, the top five PhonePe state markets by transaction value were:

| Rank | State | Transaction value | Transaction count |
|---:|---|---:|---:|
| 1 | Maharashtra | Rs 5.47 trillion | 5.06 billion |
| 2 | Karnataka | Rs 5.29 trillion | 4.49 billion |
| 3 | Telangana | Rs 5.13 trillion | 3.88 billion |
| 4 | Andhra Pradesh | Rs 4.62 trillion | 3.25 billion |
| 5 | Uttar Pradesh | Rs 3.94 trillion | 3.67 billion |

Value and count are related but not identical. A state can have fewer payments
than another state but higher-value payments on average.

## 2. Same-quarter year-on-year state growth

Comparing 2026 Q2 with 2025 Q2, all 36 state/UT rows grew in PhonePe
transaction count. The fastest percentage growth included Mizoram (+36.2%),
Sikkim (+34.1%), Assam (+33.1%), Nagaland (+30.7%), and Arunachal Pradesh
(+30.4%).

Small states can have high percentage growth from a small starting level. For
business prioritisation, always pair a growth rate with the transaction base.
For example, Assam grew 33.1% and processed 549.1 million transactions in the
latest quarter, while Mizoram grew 36.2% but processed 4.6 million.

## 3. Rolling four-quarter growth

A rolling four-quarter total smooths out a single quarter's seasonal or
temporary changes. We compare the four quarters ending in 2026 Q2 with the
four quarters ending in 2025 Q2.

The fastest rolling growth was in Manipur (+44.1%), Mizoram (+44.0%),
Meghalaya (+39.1%), Nagaland (+38.8%), Assam (+38.7%), and Sikkim (+38.0%).
Among large markets, Bihar (+31.7% over 8.21 billion rolling transactions),
West Bengal (+31.2% over 6.60 billion), Uttar Pradesh (+27.5% over 13.16
billion), Andhra Pradesh (+27.0% over 11.86 billion), and Maharashtra (+26.6%
over 18.82 billion) are particularly notable.

## 4. Relative adoption-growth tiers

For a simple, interview-friendly segmentation, we place the 36 state/UTs into
four equal growth groups using their rolling four-quarter transaction growth:

- **High growth:** top nine places, from Manipur (+44.1%) through Bihar
  (+31.7%).
- **Low growth:** bottom nine places, from Kerala (+20.1%) through Himachal
  Pradesh (+15.4%).
- **Medium growth:** the other 18 places.

The labels are relative to this dataset, not a judgment that a 20% growth rate
is actually poor. This is a useful SQL `CASE`/window-function segmentation for
a portfolio, but it should never be shown as a company target.

## 5. Do state intensity rankings change?

We rank states by **transactions per resident**, rather than raw total count,
in 2025 Q2 and 2026 Q2. The top four stayed unchanged: Telangana, Karnataka,
Andhra Pradesh, and Delhi. Sikkim made the largest move upward, from rank 18
to rank 14. Most ranks barely changed over one year.

This tells a useful story: the size of PhonePe activity is growing quickly, but
the relative geography of intensive use is fairly persistent over a one-year
period.

## 6. National UPI and cash-access context

The national RBI-derived series has complete quarters through **2025 Q1**.
Over the latest available rolling four-quarter period:

| National measure | Four-quarter total | Year-on-year change |
|---|---:|---:|
| All-UPI transactions | 18.59 billion | +41.7% |
| NFS ATM cash withdrawals | 357.1 million | -8.5% |

This is useful national context: all-UPI grew sharply while this particular
ATM-network withdrawal measure fell. It is **not** a state-level cash result,
not total ATM activity, and not a measure of all cash spending or cash held by
households.

## Reproduce it

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/14_core_portfolio_questions.sql
```
