# Step 14: Comparing states fairly with population

## The problem with raw totals

Maharashtra will almost always have more transactions than Goa because it has
far more residents. That does not automatically mean a typical person in
Maharashtra uses the app more often.

To make a fair comparison, we divide by population:

```text
transactions per resident = PhonePe transactions in a quarter / state population
```

Example: 100 million transactions in a state of 10 million people is 10
transactions per resident for that quarter. The same 100 million transactions
in a state of 100 million people is 1 transaction per resident.

## Population data added

We downloaded the free official *Population Projections for India and States,
2011-2036* report from the National Health Mission / Ministry of Health and
Family Welfare. We extracted Table 8, which provides annual total population
as of **1 March**, in thousands, and converted it to persons.

New files:

- `data/raw/population/mohfw_population_projections_2011_2036.pdf` - the
  original official report.
- `data/processed/population_state_annual.csv` - 936 rows: 36 states/UTs x 26
  years (2011-2036).
- `data/processed/population_state_data_quality_report.json` - the source,
  file hash and validation results.

### Important geography decision

PhonePe uses one modern label: `Dadra & Nagar Haveli and Daman & Diu`.
The official population table reports those two territories separately. We add
their populations together for every year before joining the data. This makes
the geography consistent instead of quietly comparing a combined PhonePe value
with only one territory's population.

All 36 PhonePe state/UT labels matched a population row. Every one of the
1,224 PhonePe state-quarter records now has a denominator.

## New SQL view

The database now contains:

- `population_state_annual` - the source population table.
- `v_phonepe_state_quarterly_per_capita` - one row per state/UT and quarter,
  with the existing transaction/user/merchant measures plus rates per resident.

The new view's most useful columns are:

| Column | Simple meaning |
|---|---|
| `population_persons` | Official projected population for that state and calendar year. |
| `transactions_per_resident` | Total PhonePe transactions in the quarter divided by population. It is an intensity measure, not a count of unique people. |
| `transaction_value_inr_per_resident` | Rupee value moved in the quarter divided by population. |
| `registered_users_per_resident` | PhonePe registered users divided by population. This is an adoption measure, not the share of active users. |
| `registered_merchants_per_resident` | Registered merchants divided by population. Blank values remain blank where the underlying merchant record is missing. |

The official value is recorded once per calendar year (as of 1 March), so that
same annual denominator is used for Q1 through Q4. This is appropriate for a
state comparison, but we should not pretend it is a quarterly population
estimate.

## First results

### Adoption became less geographically unequal

We used **sigma convergence**, a simple measure of how spread out states are.
It is the standard deviation of the log of a per-resident measure. Lower means
the state values are becoming more alike; it does not mean every state is now
at the same level.

| Measure | 2018 Q1 | 2026 Q2 | Change |
|---|---:|---:|---:|
| Spread of registered PhonePe users per resident | 0.681 | 0.367 | -46% |
| Spread of transactions per resident | 0.768 | 0.798 | +4% |

So the interesting answer is mixed:

> PhonePe registration spread much more evenly across states, but actual
> transaction intensity did not steadily become more equal.

Transaction intensity became particularly uneven in late 2019 (0.768 in 2018
Q1 rose to 1.130 in 2019 Q4), then narrowed again to about 0.80 by 2026. This
is a better and more honest result than simply saying “all states caught up.”

### A concrete 2025 Q1 comparison

At 2025 Q1, the top four transaction intensities were Telangana (76.9),
Karnataka (54.4), Andhra Pradesh (45.3), and Delhi (42.8) transactions per
resident. At the lower end, Manipur was 2.4, Mizoram 2.5 and Nagaland 3.7.

This is not a ranking of who uses *UPI* most. It is a ranking of PhonePe
transactions relative to population, and PhonePe is only one UPI app. It does,
however, show why a state-level explanation needs more than population size.

## How to reproduce it

```bash
python3 scripts/extract_population_projections.py
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/08_per_capita_adoption.sql
```

## The next research question this creates

Registration became more widespread, yet transaction intensity remains highly
different across states. That raises a more useful question than “which state
has the most UPI?”

> Which state characteristics are associated with high **usage intensity**
> after a person has registered: merchant availability, income, urbanisation,
> internet access, or the mix of P2P and merchant payments?

We should answer that first descriptively with reliable state-level inputs,
before attempting a regression or a cash-displacement claim.
