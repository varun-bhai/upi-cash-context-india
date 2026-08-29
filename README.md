## Live dashboard

[Open the interactive dashboard](https://varun-bhai.github.io/upi-cash-context-india/dashboard_site/)

# UPI Growth, PhonePe Payment Mix, and Cash-Access Trends in India

## The project in one sentence

This is a SQL/data-analysis portfolio project that examines how PhonePe payment
activity grew across Indian states and Union Territories, how merchant-payment
mix changed, and how national all-UPI growth moved alongside cash-access and
cash-reliance context measures.

It is designed to answer practical analyst questions, not to claim that UPI
“killed cash.”

## Questions answered

### Payments and adoption

- Which state/UT markets are largest by PhonePe transaction value and volume?
- Which markets are growing fastest, and how does their scale differ?
- Did the mix shift from person-to-person payments toward merchant/Retail
  payments?
- Did state transaction-intensity rankings change over time?

### National cash-access context

- As national all-UPI activity rose, what happened to NFS ATM-withdrawal
  activity?
- Did currency held by the public become smaller relative to demand deposits?

### Business-style questions for a hypothetical UPI app

- Where should a team investigate activation of existing registered users?
- Where should it investigate merchant acceptance/onboarding?
- Which high-scale, high-use markets should be monitored for reliability and
  experience?
- Are those signals improving or weakening year over year?

## The short story

1. **Merchant-style digital payments became more important.** PhonePe Retail
   share rose from 44.5% in 2020 Q3 to 60.5% in 2025 Q1. NPCI's all-UPI P2M
   share also rose from 41.0% in 2022 Q1 to 62.4% in 2025 Q1. The pattern is
   therefore broader than one app, although PhonePe categories and NPCI P2M
   are not identical measures.

2. **The national evidence shows changing payment context, not cash
   disappearance.** In the latest comparable four-quarter national window
   ending 2025 Q1, all-UPI transaction volume was up 41.7% year over year
   while NFS ATM withdrawals were down 8.5%. Separately, the RBI's annual
   cash-to-demand-deposits ratio declined from 1.445 in FY 2021-22 to 1.347 in
   FY 2023-24 even though currency with the public rose in rupee terms. This
   is descriptive context, not causal proof or a measure of all cash use.

3. **Large markets and fast-growth markets are different.** In 2026 Q2,
   Maharashtra led PhonePe transaction value (Rs 5.47 trillion), followed by
   Karnataka and Telangana. The fastest rolling growth was in Manipur,
   Mizoram, Meghalaya, Nagaland, Assam, and Sikkim—many from much smaller
   bases. Bihar, Uttar Pradesh, Andhra Pradesh, Maharashtra, and Telangana
   combined large scale with meaningful rolling growth.

4. **Usage intensity remains geographically persistent.** In transactions per
   resident, Telangana, Karnataka, Andhra Pradesh, and Delhi stayed the top
   four from 2025 Q2 to 2026 Q2. Growth is widespread, but the relative
   geography of intensive use did not change much in one year.

5. **A practical business lens creates useful follow-up questions.** Gujarat
   and Tamil Nadu have broad registered-user bases but comparatively lower
   transactions per registered user, making user activation worth
   investigating. Maharashtra, Karnataka, Telangana, Uttar Pradesh, Andhra
   Pradesh, and other high-scale markets call for attention to reliability and
   customer/merchant experience. These are investigation signals, not direct
   investment recommendations.

6. **Not every plausible external dataset improves the story.** A 36-state
   PMJDY financial-inclusion snapshot had no simple relationship with PhonePe
   registered-user density or transaction intensity, so it is retained as
   documented context rather than turned into a market-targeting score.

## Scope and the most important limitation

PhonePe Pulse supplies detailed quarterly state/UT data, but the cash-access
series available in this project is national. We therefore make this explicit
choice:

> State-level PhonePe adoption is analysed on its own. National UPI and NFS ATM
> withdrawals are shown as national context. The project does **not** claim a
> state-level cash-displacement result.

NFS ATM withdrawals are only a cash-access proxy. They are not all ATM
withdrawals, cash held by households, or cash spending at shops. The
cash-to-demand-deposits ratio is a national annual monetary measure, not cash
spending; it also cannot tell us whether UPI caused any change.

## Data sources

| Source | Geography and time | Used for |
|---|---|---|
| [PhonePe Pulse](https://www.phonepe.com/pulse/data/) | 36 states/UTs, quarterly, 2018 Q1--2026 Q2 | Transactions, users, merchants, and payment mix |
| [NPCI UPI ecosystem statistics](https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics) | National, monthly | App context and all-UPI P2P/P2M mix |
| [India Data Portal RBI payment indicators](https://ckandev.indiadataportal.com/dataset/reserve-bank-of-india/resource/1f9367ac-01b0-4c82-83a1-4069d4340667) | National, complete quarters 2020 Q3--2025 Q1 | All-UPI, IMPS, and NFS ATM withdrawal context |
| [RBI Table 41: Average Monetary Aggregates](https://systemhealth.rbi.org.in/Scripts/PublicationsView.aspx_id%3D22515%281%29.html) | National, annual averages FY 2017-18--FY 2023-24 | Currency with public, demand deposits, and their ratio |
| [MoHFW population projections](https://nhm.gov.in/New_Updates_2018/Report_Population_Projection_2019.pdf) | States/UTs, annual | Per-resident comparisons |
| [TRAI QPIR](https://www.trai.gov.in/sites/default/files/2024-11/QPIR_09102024_0.pdf) | States/UTs, June 2024 snapshot | Internet-subscription comparison |
| [Economic Survey state-income table](https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab1.11a.pdf) | 34 published state/UT estimates, FY 2023-24 | Income comparison |
| [PMJDY state-wise account report](https://pmjdy.gov.in/account-statistics-state.aspx/scheme) | 36 states/UTs, 19 Aug 2026 snapshot | Financial-inclusion context test |

## What is in the project

```text
data/raw/        Original downloaded or cloned source files
data/processed/  Clean analysis-ready CSVs and data-quality reports
data/upi_cash_displacement.sqlite
                 Reproducible SQLite analysis database
scripts/         Python extraction and database-loading scripts
sql/             Commented SQL questions
docs/             Plain-language decisions, findings, and limitations
```

Start with these files:

- `docs/09_beginner_project_guide.md` — plain-language walkthrough of the data.
- `docs/19_analysis_question_register.md` — every project question and its
  status.
- `docs/21_core_portfolio_questions.md` — core SQL findings.
- `docs/23_cash_reliance_scorecard.md` — the strengthened national
  cash-reliance conclusion and its limits.
- `docs/24_financial_inclusion_context.md` — why a plausible state-level
  financial-inclusion measure was kept as context, not a targeting score.
- `docs/18_business_analysis_direction.md` and
  `docs/20_business_trend_monitoring.md` — business-style analysis.

## Rebuild the database

```bash
python3 scripts/load_sqlite.py
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/14_core_portfolio_questions.sql
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/15_cash_reliance_scorecard.sql
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/16_financial_inclusion_context.sql
```

The SQL files are deliberately written as readable, standalone questions. The
project uses SQLite because it is simple to run locally and fully supports the
joins, CTEs, window functions, and views used here.

## Dashboard-ready views

The recommended dashboard design and source queries are in
`docs/22_dashboard_storyboard.md`. The dashboard should tell the story in this
order: national context, state scale and growth, payment mix, then business
signals and limitations.

For ready-to-import dashboard tables, run `python3
scripts/export_dashboard_data.py`; the fields, chart roles, and limitations are
explained in `docs/25_dashboard_data_guide.md`.

The local interactive dashboard is in `dashboard_site/index.html`. Rebuild its
embedded data after refreshing the database with `python3
scripts/build_dashboard_site.py`.

The deliberately editorial visual direction—and the choices made to avoid a
generic AI-generated dashboard look—are recorded in
`docs/26_dashboard_design_decisions.md`.

## Future work

- Add a vetted state-level cash-withdrawal or currency-chest series before
  making state-level cash-displacement claims.
- Add internal-style data (active users, success rates, merchant categories,
  cost, revenue, support contacts) before turning business signals into real
  prioritisation decisions.
- Add district analysis only as a separate version; it is deliberately out of
  scope here.
- Extend the national cash-access series when a complete, free, and documented
  official quarterly source is available.
