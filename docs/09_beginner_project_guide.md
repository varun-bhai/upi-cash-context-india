# Beginner guide: what we have built and why

## 1. The project in one sentence

We are studying how digital payments grew in India, especially on PhonePe, and
whether that growth happened alongside changes in one measure of cash access:
cash withdrawals through the National Financial Switch (NFS) ATM network.

We are **not** trying to claim, without evidence, that “UPI killed cash”. A
better question is:

> As UPI and PhonePe activity grew, what happened to cash-access indicators and
> to the kinds of payments people made?

## 2. A few words you will see often

| Word | Simple meaning | Example in this project |
|---|---|---|
| Dataset | A collection of data arranged in rows and columns | The PhonePe transactions CSV |
| Row | One record in a dataset | PhonePe Retail activity in Maharashtra in 2025 Q1 |
| Column | One type of information repeated for every row | `transaction_count` |
| Column header | The name at the top of a column | `state_name` |
| Raw data | Original source data, kept unchanged | PhonePe's original JSON files |
| Cleaned data | Data made consistent and easy to analyse | Our CSV files in `data/processed/` |
| Database | A structured place to store and query data | `upi_cash_displacement.sqlite` |
| SQL | A language for asking questions of a database | “Which state had the most transactions?” |
| `NULL` / missing | “We do not have a value”; it is not the same as zero | A missing merchant record does not mean zero merchants |

## 3. The three layers of data we have

We deliberately use three layers because no single free source gives every
answer.

### Layer A: PhonePe data by state/UT

This is the detailed geographic dataset. It covers 36 states and Union
Territories (UTs), such as Maharashtra, Karnataka, Delhi, Ladakh, and Andaman
& Nicobar Islands.

It comes from the open PhonePe Pulse dataset and covers 34 quarters from 2018
Q1 to 2026 Q2. A quarter is a three-month period:

- Q1: January to March
- Q2: April to June
- Q3: July to September
- Q4: October to December

This data describes **PhonePe activity only**. It does not include every UPI
payment made on Google Pay, Paytm, BHIM, a bank app, or any other UPI app.

Why do we still use it? It is free, detailed, state-level, and includes users,
merchants, and payment categories. The RBI study reviewed below also used
PhonePe Pulse as a state-level proxy for UPI because its national growth closely
tracked total UPI. But “proxy” means a useful stand-in, not an exact copy.

### Layer B: national UPI, IMPS, and ATM-network data

This is India-wide data from an open India Data Portal resource derived from
RBI payment data. It covers every payment provider together, not PhonePe alone.

We use it to ask national questions such as:

> When total UPI volume grew across India, did NFS-at-ATM withdrawal activity
> grow, fall, or remain similar?

The data has daily observations from 2020-06-01 to 2026-07-31, but some later
months are absent. For fair quarter-to-quarter analysis, we created a separate
quarterly table containing only complete calendar quarters: 2020 Q3 to 2025 Q1.

### Layer C: our SQLite database

The database does not add new facts. It is simply a well-organised copy of the
cleaned tables that lets us ask questions with SQL.

It is stored at `data/upi_cash_displacement.sqlite` and contains several main
tables:

| Table | What one row represents | Number of rows |
|---|---|---:|
| `phonepe_state_transactions` | One PhonePe state/UT + quarter + transaction category | 3,671 |
| `phonepe_state_users` | One PhonePe state/UT + quarter | 1,224 |
| `phonepe_state_merchants` | One PhonePe state/UT + quarter, when supplied by source | 1,178 |
| `national_payment_quarterly` | One India-wide quarter + payment method | 57 |
| `state_per_capita_nsdp_snapshot` | One state/UT + financial-year income snapshot, where published | 34 |

## 4. The PhonePe transaction table, explained column by column

File: `data/processed/phonepe_state_transaction_quarterly.csv`

It has 3,671 rows. Each row says:

> “In this state/UT, during this quarter, in this PhonePe payment category,
> this many transactions occurred and their total value was this many rupees.”

An early example row is:

```text
andaman-&-nicobar-islands, Andaman & Nicobar Islands, 2018, 1, 2018-01-01,
P2P, 2297, 15513455.551771518, ...
```

In plain English, it means that PhonePe recorded 2,297 P2P transactions in
Andaman & Nicobar Islands in 2018 Q1, worth about Rs 15.5 million in total.

| Header | What it means | Example |
|---|---|---|
| `state_slug` | Technical, stable version of the state name used for matching tables | `andaman-&-nicobar-islands` |
| `state_name` | Human-readable state/UT name | `Andaman & Nicobar Islands` |
| `year` | Calendar year | `2018` |
| `quarter` | Original PhonePe quarter number, `1` to `4` | `1` |
| `quarter_start_date` | First day of the quarter; useful for sorting and joining | `2018-01-01` |
| `source_category` | PhonePe transaction category | `P2P`, `Retail`, or `Utility` |
| `transaction_count` | Number of transactions | `2297` |
| `transaction_value_inr` | Total value of those transactions, in Indian rupees | `15513455.55...` |
| `source_file` | Original raw JSON file used to create this row | A file path, used for traceability |

The categories are copied exactly from PhonePe:

- `P2P`: person-to-person payments, such as sending money to a friend or family
  member.
- `Retail`: payments to a merchant or shop.
- `Utility`: bill and utility-style payments.

## 5. The PhonePe user and merchant tables

### Users

File: `data/processed/phonepe_state_user_quarterly.csv`

It has the same state and time columns, plus:

| Header | Meaning |
|---|---|
| `registered_count` | Number of PhonePe registered users reported for that state/UT and quarter |

Example: `9292` for Andaman & Nicobar Islands in 2018 Q1 means 9,292
registered PhonePe users were reported in that quarter.

This is a **level**, not something we add through time. If a state has 10
million users in Q1 and 11 million in Q2, it does not have 21 million users.
Instead we say it grew by 1 million users.

### Merchants

File: `data/processed/phonepe_state_merchant_quarterly.csv`

Its `registered_count` means registered PhonePe merchants rather than users.
It has 1,178 rows rather than 1,224, so 46 state-quarter records are missing.

This matters:

- `0` merchants would mean the source explicitly says there were none.
- a missing row means the source did not provide the number.

We preserve missing records as missing. We do not turn them into zero just to
make a spreadsheet look complete.

## 6. The national payment tables

### Daily national table

File: `data/processed/idp_rbi_national_payment_indicators_daily.csv`

It has 5,664 rows: 1,888 unique days multiplied by three payment methods.
Each row says:

> “Across India, on this day, this payment method had this transaction volume
> and this total value.”

Example:

```text
2020-06-01, 2020, 6, Q2, IMPS, 76.81, 9072.55, ...
```

This means IMPS handled 76.81 lakh transactions worth Rs 9,072.55 crore on
2020-06-01.

| Header | Meaning |
|---|---|
| `date` | The exact day |
| `year`, `month`, `quarter` | Time labels derived from the date |
| `payment_mode` | `UPI`, `IMPS`, or `NFS_ATM_CASH_WITHDRAWAL` |
| `volume_lakh` | Number of transactions in lakh; 1 lakh = 100,000 |
| `value_crore` | Total value in INR crore; 1 crore = 10,000,000 rupees |
| `source_resource_id` | Technical ID of the India Data Portal resource, kept for traceability |

`IMPS` is Immediate Payment Service, another instant bank-transfer method.

`NFS_ATM_CASH_WITHDRAWAL` is activity through the National Financial Switch at
ATMs. It is a **cash-access proxy**. It is not all ATM withdrawals in India,
not cash held in wallets, and not total cash spending. This is why we avoid the
oversimplified sentence “UPI replaced all cash”.

### Quarterly national table

File: `data/processed/idp_rbi_national_payment_indicators_quarterly.csv`

This table has 57 rows: 19 complete quarters multiplied by three payment
methods. We built it by adding daily observations within a quarter, but only
when all three calendar months are present.

| Extra header | Meaning |
|---|---|
| `months_included` | Always `3` in this table: a full quarter |
| `days_observed` | Number of daily records added, such as `92` for a 92-day quarter |

This protects us from comparing a full three-month quarter with a partial month
and accidentally calling it a decline.

## 7. What “cleaning the data” meant here

Cleaning does not mean changing inconvenient numbers. It means making the data
safe and understandable without changing its meaning.

We did the following:

1. Kept raw source files unchanged.
2. Converted nested PhonePe JSON files into simple row-and-column CSV files.
3. Added a quarter-start date to make dates easy to sort and join.
4. Kept PhonePe's original category labels instead of renaming them based on
   guesses.
5. Preserved missing merchant data as missing.
6. Checked PhonePe state totals against PhonePe's country totals. All 102
   available quarter-category transaction-count comparisons matched exactly.
7. Found 31 duplicated source records in the national daily data. The duplicate
   values were identical for the measures we use, so we retained one copy in a
   documented, repeatable way.
8. Excluded partial or incomplete quarters from the quarterly national table.
9. Standardised quarter labels inside SQLite to `Q1`, `Q2`, `Q3`, `Q4`. The
   original CSVs remain unchanged.

## 8. What we found so far

These are descriptions of the data, not final proof about why something
happened.

1. **National UPI volume rose sharply.** From 2020 Q3 to 2025 Q1, it rose from
   49,163 lakh to 514,037 lakh transactions, a 945.6% increase.

2. **NFS-at-ATM volume was broadly flat in the same comparison.** It moved from
   8,882 lakh to 8,507 lakh transactions, a go 4.2% decrease. This is consistent
   with less reliance on some cash withdrawals, but it does not prove UPI
   caused the change.

3. **PhonePe's Retail category became more important.** Its share of PhonePe
   transactions rose from 44.5% in 2020 Q3 to 60.5% in 2025 Q1. P2P's share
   fell from 44.8% to 33.0%.

4. **The Retail-share change was broad.** It increased in 35 of 36 state/UT
   entities. Large states contributed much of the extra number of Retail
   payments, but the pattern was not only a Maharashtra/Karnataka story.

5. **Two simple explanations were not strongly supported.** Differences in
   merchant additions did not explain much of the variation in Retail-share
   change across states. Nor did states with low initial Retail shares show a
   strong, systematic catch-up pattern.

6. **2021 deserves closer attention.** The largest change in PhonePe's national
   Retail share was a 5.9 percentage-point rise in 2021 Q3, following a low
   2021 Q2 share. This could reflect the COVID period, seasonal effects,
   platform behaviour, or other changes. Our current data cannot choose among
   those explanations.

## 9. What the RBI research adds

The RBI Bulletin paper, *Impact of UPI on Cash Demand - Evidence from National
and Subnational Levels* (September 2025), is more advanced than our current
project. It is useful as a benchmark, not as a result we should copy.

The study:

- uses Currency in Circulation (CIC) as a national cash-demand proxy;
- uses state currency-chest withdrawals as a state-level cash-use proxy because
  granular state ATM-withdrawal data are not available;
- uses PhonePe Pulse as a state-level UPI proxy and reports that PhonePe's
  growth closely tracked total UPI growth nationally;
- divides by state population to compare a large state and a small state fairly;
- controls for factors such as economic activity, ATM density, formalisation,
  education, internet access, year effects, and seasonal quarter effects;
- finds an association between higher UPI adoption and lower cash demand, while
  explicitly warning that regression estimates do not automatically prove
  causation.

This tells us two important things:

1. Our use of PhonePe for state-level **digital-adoption patterns** is
   reasonable when clearly labelled as a proxy.
2. We should not pretend our present data can reproduce the RBI causal-style
   analysis. We now have a consistent state population denominator, but still
   lack state currency-chest withdrawals, ATM density, economic activity, and
   the other controls used by the RBI paper.

## 10. What we will do next, in order

### Next step 1: official NPCI app-level data - completed

We added NPCI national monthly app data for PhonePe, Google Pay, Paytm, BHIM,
Amazon Pay, WhatsApp and others. This adds the competition/ecosystem view that
PhonePe Pulse cannot provide. The clean table covers January 2022 to April 2026
with a documented March 2026 gap.

Question it will answer:

> While PhonePe's Retail share was rising, was PhonePe gaining, stable, or
> losing national market share compared with Google Pay and Paytm?

It is national only. We will never present it as state-by-state app data.

### Next step 2: compare PhonePe with all-UPI state totals when available

NPCI also publishes state-wide totals for all UPI apps combined. If we can
obtain a reliable historical series, we can calculate a useful ratio:

```text
PhonePe transactions in a state / total UPI transactions in that state
```

That would show PhonePe's coverage of total state UPI activity. It would not
show Google Pay's or Paytm's state shares.

### Added national merchant-payment context

We also added NPCI's all-UPI P2P/P2M series. It confirms that the rising
merchant-payment pattern is broader than PhonePe: all-UPI P2M share rose from
41.0% in 2022 Q1 to 62.4% in 2025 Q1 (a 21.5-point rise), while PhonePe Retail share rose from
49.1% to 60.5%. This is strong descriptive context, but still not proof about
cash displacement.

### Added population-adjusted state comparisons

We added the official Ministry of Health & Family Welfare annual population
projections (2011-2036) and matched every PhonePe state-quarter to its state
population. This lets us compare rates rather than totals, for example,
transactions per resident and registered PhonePe users per resident.

The first result is nuanced: registered-user intensity became much less unequal
across states, while transaction intensity remains highly different by state.
The detailed setup and result are in `docs/14_population_and_per_capita_analysis.md`.

### First explanation check: merchant density

Using the PhonePe merchant series, we checked whether states with more
registered PhonePe merchants per resident also had more transactions per
resident. In 2025 Q1 the relationship was positive and fairly strong (a
correlation of 0.698). User density had an even stronger relationship with
transaction intensity (0.809). This is a useful clue, not a causal result: a
high-usage state may attract more merchants, and both may be affected by income
or internet access. The exact query and explanation are in
`docs/15_merchant_density_and_usage.md`.

### Second explanation check: internet subscriptions

We added the official TRAI state/UT internet-subscriber snapshot for June 2024
and aligned it only with the PhonePe April-June 2024 quarter. Internet
subscription density had a stronger relationship with PhonePe user density
(0.665) than with transaction intensity (0.302). In simple words: connectivity
seems linked with joining the app, but does not on its own explain how much the
app is used. The full explanation is in
`docs/16_internet_access_and_usage.md`.

### Third explanation check: state income

We added the official Economic Survey's 2023-24 per-person state income
(per-capita NSDP at current prices) and matched it only with PhonePe 2024 Q1,
which ends when that financial year ends. It covers 34 of 36 PhonePe
geographies; the table does not publish estimates for Dadra & Nagar Haveli and
Daman & Diu or Lakshadweep, and we did not fill them in.

Income was strongly related to PhonePe user density (correlation 0.719), but
only moderately related to transaction intensity (0.394). In plain words:
higher-income states tended to have more people registered on PhonePe, but
income did not fully explain how much people transacted. The full explanation
is in `docs/17_income_and_usage.md`.

### Business-analysis direction

We are now using the data in a more practical, portfolio-style way. Instead
of trying to prove a broad academic claim, we ask decision-support questions
for a hypothetical UPI app: where should it investigate user activation,
merchant acceptance, or protecting high-use core markets? The public data can
flag patterns, but it cannot reveal costs, revenue, active users, or the exact
reason behind a pattern. The detailed business framing and the SQL output are
in `docs/18_business_analysis_direction.md` and
`sql/12_business_opportunity_signals.sql`.

We also compared the latest business signals with the same quarter one year
earlier. PhonePe transactions across the 36 state/UT rows grew 24.2% from 2025
Q2 to 2026 Q2, faster than the 11.7% growth in reported registrations. The
business-monitoring explanation is in `docs/20_business_trend_monitoring.md`.

The remaining core portfolio SQL questions—latest state leaders, same-quarter
growth, rolling four-quarter growth, relative growth tiers, ranking changes,
and national UPI versus NFS ATM context—are now complete in
`sql/14_core_portfolio_questions.sql`. The plain-language results are in
`docs/21_core_portfolio_questions.md`.

### Next step 3: add one stronger cash-demand measure

Inspired by the RBI study, we can look for a reproducible national series for
currency in circulation or ATM withdrawals relative to GDP. We add it only if
we can document the source and units clearly.

### Next step 4: build the final SQL portfolio story

The final project should have a modest, honest title, such as:

> UPI Growth, PhonePe Payment Mix, and Cash-Access Trends in India

It will include the data sources, cleaning decisions, SQL questions, charts,
findings, limitations, and ideas for future work. It will say what the data
shows and equally clearly what it cannot show.

## 11. The most important rule

When analysing data, there is a big difference between these statements:

- **Description:** “UPI rose while NFS ATM volume was broadly flat.”
- **Association:** “Higher UPI and lower cash access moved together.”
- **Causation:** “UPI caused people to use less cash.”

We can safely make the first statement. We can investigate the second. The
third needs much stronger data and research design, like the RBI study.

## Sources used in this guide

- PhonePe Pulse: <https://www.phonepe.com/pulse/data/>
- India Data Portal, RBI Daily Digital Payments: <https://ckandev.indiadataportal.com/dataset/reserve-bank-of-india/resource/1f9367ac-01b0-4c82-83a1-4069d4340667>
- NPCI UPI Ecosystem Statistics: <https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics>
- RBI Bulletin study: <https://rbidocs.rbi.org.in/rdocs/Bulletin/PDFs/05ARTICLES24092025634FBBE941344543801EDCF305753C94.PDF>
- MoHFW population projections: <https://nhm.gov.in/New_Updates_2018/Report_Population_Projection_2019.pdf>
- Economic Survey state income table: <https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab1.11a.pdf>
- Zerodha Daily Brief explanation: <https://thedailybrief.zerodha.com/p/how-upi-is-changing-cash-use-in-india>
