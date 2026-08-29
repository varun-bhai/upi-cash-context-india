# Analysis question register

This is our working checklist. The goal is to complete the useful questions in
the original project brief before we write a final portfolio story. A question
can be **complete**, **next**, or **not possible with our public data**. This
keeps the project organised without pretending every interesting question has
an answer.

## Scope decision

We formally chose the original brief's option **(a)** for cash analysis:

> We show state-level PhonePe/UPI adoption patterns separately, and use the
> national UPI-versus-NFS ATM series as national cash-access context. We do not
> claim a state-level cash-displacement result because we do not have a vetted,
> comparable state cash-withdrawal series.

## Original analysis questions

| Area | Question | Status | Where it is or will be answered |
|---|---|---|---|
| Foundational | PhonePe transaction volume and value by state and quarter | Complete | Clean PhonePe tables and `sql/02_initial_inspection.sql` |
| Foundational | National UPI versus NFS ATM withdrawal trend | Complete, with cash-access limitation | `sql/03_exploratory_patterns.sql`, `docs/05_first_research_leads.md` |
| Foundational | Did cash become smaller relative to demand deposits as UPI scaled? | Complete, national descriptive context | `sql/15_cash_reliance_scorecard.sql`, `docs/23_cash_reliance_scorecard.md` |
| Foundational | Top states by latest-quarter transaction value | Complete | `sql/14_core_portfolio_questions.sql`, `docs/21_core_portfolio_questions.md` |
| Foundational | National and state year-on-year transaction growth | Complete | `sql/14_core_portfolio_questions.sql`, `docs/21_core_portfolio_questions.md` |
| Intermediate | Four-quarter rolling state growth | Complete | `sql/14_core_portfolio_questions.sql`, `docs/21_core_portfolio_questions.md` |
| Intermediate | Do state rankings change over time? | Complete | `sql/08_per_capita_adoption.sql`, `sql/14_core_portfolio_questions.sql` |
| Intermediate | Is ATM withdrawal flat, falling, or rising more slowly than UPI? | Complete | `sql/03_exploratory_patterns.sql`, `sql/14_core_portfolio_questions.sql` |
| Advanced | Adoption tiers: high/medium/low state growth | Complete | `sql/14_core_portfolio_questions.sql`, `docs/21_core_portfolio_questions.md` |
| Advanced | Is the payment mix moving toward merchant/Retail payments? | Complete | `sql/04_retail_shift_deep_dive.sql`, `sql/07_all_upi_merchant_shift.sql` |
| Advanced | Does income, internet, or merchant density line up with use? | Complete as descriptive checks | `sql/09`, `sql/10`, `sql/11` and docs 15--17 |
| Advanced | Does a financial-inclusion beneficiary snapshot line up with PhonePe use? | Complete; no simple relationship found | `sql/16_financial_inclusion_context.sql`, `docs/24_financial_inclusion_context.md` |

## Business-analysis questions

| Question | Status | Current evidence |
|---|---|---|
| Which states merit an activation investigation? | Initial snapshot complete | `sql/12_business_opportunity_signals.sql` |
| Which states merit a merchant-acceptance investigation? | Initial snapshot complete | `sql/12_business_opportunity_signals.sql` |
| Which markets are high-use, high-scale core markets? | Initial snapshot complete | `sql/12_business_opportunity_signals.sql` |
| Are those business signals improving or weakening over time? | Complete | `sql/13_business_trend_monitoring.sql`, `docs/20_business_trend_monitoring.md` |

## Deliberately not claimed

- UPI caused cash use to fall in a particular state.
- UPI caused the national cash-to-demand-deposit ratio to fall. The series are
  descriptive national context, not a causal experiment.
- A state should receive marketing spend based only on this public data.
- A registered PhonePe user is an active, retained customer.
- A registered PhonePe merchant is an active, revenue-generating merchant.
- A PMJDY beneficiary count is a count of unique banked people, active
  debit-card users, or active UPI users.

## Delivery order

1. Finish the remaining SQL questions in the register.
2. Check every result against source coverage and definitions.
3. Select the small set of strongest findings.
4. Write the final portfolio story, dashboard plan, and interview-ready
   explanation of each decision.
