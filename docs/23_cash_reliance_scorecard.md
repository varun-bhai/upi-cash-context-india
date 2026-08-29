# Step 23: A stronger national cash-reliance scorecard

This step adds a second national lens alongside the existing NFS ATM
cash-access proxy. It is deliberately national, because the project still does
not have a comparable, vetted state-level cash-withdrawal series.

## What we added

The new clean file is
`data/processed/rbi_annual_cash_reliance.csv`. It comes from the RBI's
**Table 41: Average Monetary Aggregates**, whose saved source page is in
`data/raw/rbi/cash_reliance/`.

For each financial year, the table supplies two money measures in rupees crore:

- **Currency with the public** — physical currency held outside RBI/banks in
  the public's hands. It is about currency outstanding, not cash spent at
  shops.
- **Demand deposits** — bank deposits that can be used on demand, such as
  balances in current and savings accounts.

We divide the first by the second:

```text
cash-to-demand-deposits ratio = currency with the public / demand deposits
```

For example, a ratio of 1.347 means there was about Rs 135 of currency with
the public for every Rs 100 of demand deposits in the annual-average figures.
This is the same kind of *relative cash reliance* idea discussed in the
Zerodha article and the RBI research, but it is a transparent project metric
with its own saved source and definition.

## What the matched three-year window shows

RBI Table 41 is annual, while our national payment data has complete quarters
from 2020 Q3 through 2025 Q1. The clean overlap is three whole financial years:
FY 2021-22, FY 2022-23, and FY 2023-24.

| Financial year | Currency with public | Demand deposits | Cash-to-demand-deposits ratio | All-UPI transactions | UPI average payment | NFS ATM withdrawals |
|---|---:|---:|---:|---:|---:|---:|
| 2021-22 | Rs 28.81 lakh crore | Rs 19.94 lakh crore | 1.445 | 45.96 billion | Rs 1,831 | 3.79 billion |
| 2022-23 | Rs 31.22 lakh crore | Rs 22.02 lakh crore | 1.417 | 83.71 billion | Rs 1,662 | 4.02 billion |
| 2023-24 | Rs 32.82 lakh crore | Rs 24.37 lakh crore | 1.347 | 131.13 billion | Rs 1,525 | 3.90 billion |

From FY 2021-22 to FY 2023-24:

- Currency with the public **still rose 13.9%**. This is why “UPI killed
  cash” would be false.
- Demand deposits rose faster, by **22.2%**.
- Therefore the ratio fell **6.8%**, from 1.445 to 1.347.
- All-UPI transaction volume grew **185.3%**, and the average UPI payment
  became **16.7% smaller** (Rs 1,831 to Rs 1,525). This is consistent with
  UPI expanding into smaller, more routine payments.
- NFS ATM withdrawal volume moved only **2.9%** over this particular
  three-financial-year window. It should not be described as total ATM
  withdrawals or total cash use.

The longer RBI-only series also gives useful context. Its ratio rose to a
post-pandemic high of **1.548 in FY 2020-21**, then fell to **1.347 in FY
2023-24** (a 13.0% decline from that peak). That pattern says cash became less
large relative to immediately spendable bank deposits after the pandemic high;
it does not say people stopped using cash.

## The careful conclusion

We now have three mutually reinforcing national observations:

1. UPI transaction volume expanded extremely quickly.
2. Its average payment became smaller, which supports the idea that it reached
   more everyday transactions.
3. Cash did not disappear: currency with the public increased in rupee terms.
   But demand deposits increased faster, so the cash-to-demand-deposits ratio
   declined; the NFS ATM proxy later also declined in the latest rolling
   four-quarter window available to the project.

The responsible portfolio conclusion is:

> National evidence is consistent with UPI taking a bigger role in smaller,
> everyday digital payments and with cash becoming less important *relative to
> demand deposits*. It does not establish that UPI caused a fall in cash use,
> and it says nothing directly about individual states.

## What this helps a business ask

This scorecard is not a marketing-targeting table. It can support a product or
payments strategy discussion:

- If average UPI payments are getting smaller, should the product make tiny
  merchant payments faster and more reliable?
- In a market that still uses ATMs heavily, are low-value merchant payments a
  better opportunity than a blanket “replace cash” campaign?
- Do internal data show that UPI users make a first small merchant payment,
  then repeat it? Public data cannot answer that, but it tells us why to test
  it.

## Reproduce it

```bash
python3 scripts/extract_rbi_cash_reliance.py
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/15_cash_reliance_scorecard.sql
```

The first command re-extracts from the saved RBI page. The data-quality report
records the source file's SHA-256 fingerprint and keeps the definition visible.
