# Step 5: First research leads from exploratory SQL

These are patterns worth investigating, not final findings. We have used the
same complete-quarter window—2020 Q3 to 2025 Q1—whenever national RBI-derived
data and PhonePe data are compared.

## Lead 1: UPI rose while NFS-at-ATM volume did not

National UPI volume rose from 49,163 lakh to 514,037 lakh transactions
(+945.6%). Over the same first-to-last quarter comparison, NFS-through-ATM
volume moved from 8,882 lakh to 8,507 lakh (−4.2%).

That makes the question interesting, but not settled: does rising UPI mainly
replace small, frequent cash-like payments while cash withdrawals remain useful
for other purposes? The available ATM measure is only NFS-through-ATM activity,
not every cash withdrawal and not cash spending. We cannot infer causation.

## Lead 2: PhonePe's mix shifted toward retail payments

At the national PhonePe-platform level, the Retail category increased from
44.5% of transactions in 2020 Q3 to 60.5% in 2025 Q1. P2P fell from 44.8% to
33.0%; Utility fell from 10.7% to 6.5%.

This raises a stronger follow-up question than simply “did UPI grow?”:

> Is the apparent retail shift broad across states, or concentrated in a few
> large states and merchants?

Before interpreting it as an economic change, we should check whether PhonePe's
category definitions were stable across time. The current project deliberately
preserves the source labels rather than relabelling them.

### Follow-up result: the Retail-share increase is widespread

We tested the obvious alternative explanation—that the national shift is mostly
one or two large states. Retail's transaction share increased in **35 of 36**
state/UT entities between 2020 Q3 and 2025 Q1, with an average increase of
14.6 percentage points. The largest share increases were in Jammu & Kashmir
(+25.9 points), Dadra & Nagar Haveli and Daman & Diu (+21.7), Ladakh (+20.5),
Odisha (+20.2), and Goa (+20.1).

Large states still account for much of the added Retail volume: Maharashtra,
Karnataka, Telangana, Uttar Pradesh, and Andhra Pradesh together contributed
about 54% of the increase. So the pattern is both **broad** (most places show
it) and **volume-concentrated** (large states account for much of its size).

This is evidence about PhonePe's platform mix only. It remains possible that a
change in source categorisation contributed to the result, so documenting or
validating the category definitions is a sensible future check.

## Lead 3: Size and growth are different stories

In 2025 Q1, the largest PhonePe transaction volumes came from Maharashtra,
Karnataka, Telangana, Uttar Pradesh, and Andhra Pradesh. But ranking states by
percentage growth from 2020 Q3 produces a different list: Jammu & Kashmir,
Assam, Bihar, Goa, and several smaller state/UT entities rise near the top.

Small starting bases can make a growth rate look dramatic, so later analysis
should always show the starting and ending transaction levels alongside the
percentage. The exploratory SQL applies a minimum starting-volume threshold,
but even that is only a first safeguard.

## Lead 4: Platform activity per registered user varies substantially

For states with at least one million registered PhonePe users in 2025 Q1,
Telangana, Andhra Pradesh, and Karnataka have the highest transactions per
registered user in this dataset. This does **not** mean their residents use UPI
the most: it is an activity ratio inside the PhonePe platform, and registered
users are not the state's population.

It does suggest an investigable question: what distinguishes high-activity
PhonePe states from low-activity ones? Potential future data could include
population, internet access, urbanisation, income, bank/ATM availability, or
merchant density—added one source at a time and with a clear reason.

## Proposed next query

Start with Lead 2. Calculate each state/UT's Retail share in 2020 Q3 and 2025
Q1, rank the changes, and inspect whether the national change is widespread or
driven by a small set of places. That is a focused SQL task our existing data
can answer directly.

Run all exploratory queries with:

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/03_exploratory_patterns.sql
```
