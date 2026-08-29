# Dashboard storyboard: the final portfolio story

This is a design brief for a Power BI or Tableau dashboard. The dashboard is
the presentation layer; all calculations should come from the cleaned SQLite
database and the saved SQL, not from hand-edited spreadsheet totals.

## Page 1: National context — digital growth and cash access

**Question:** What happened nationally as UPI scaled?

- Line chart: quarterly all-UPI transaction volume and NFS ATM withdrawal
  volume, indexed to 100 at the first common quarter. Indexing lets two very
  different scales be shown fairly.
- Supporting cards: latest available rolling four-quarter growth: UPI +41.7%,
  NFS ATM withdrawals -8.5%; FY 2021-22 to FY 2023-24 cash-to-demand-deposit
  ratio: 1.445 to 1.347.
- Add a separate small line for the annual cash-to-demand-deposit ratio. Do
  not overlay it with transaction counts because it has a different unit and
  annual frequency.
- Source: `v_national_payment_quarterly_pivot`,
  `v_national_cash_reliance_with_upi`, `sql/14_core_portfolio_questions.sql`,
  and `sql/15_cash_reliance_scorecard.sql`.
- Mandatory subtitle: “NFS ATM withdrawals are a national cash-access proxy;
  the cash/deposit ratio is a national monetary-context measure. Neither is
  total cash use or causal proof that UPI replaced cash.”

## Page 2: State scale and growth

**Question:** Which PhonePe markets are large, and which are growing?

- Bubble/scatter chart: x = latest rolling four-quarter growth, y = latest
  rolling four-quarter transaction volume, bubble size = transaction value.
- Bar chart: top 10 states/UTs by latest-quarter transaction value.
- Use a log scale for volume if the tool supports it; otherwise annotate that
  small states can show high percentage growth from small bases.
- Source: `sql/14_core_portfolio_questions.sql`.

## Page 3: Merchant-payment mix

**Question:** Are payments becoming more merchant-oriented?

- Stacked area or 100% stacked column chart: national PhonePe P2P, Retail, and
  Utility shares over time.
- Supporting line: national NPCI all-UPI P2M share where the data overlaps.
- Source: `phonepe_state_transactions` aggregated by quarter and
  `national_upi_p2p_p2m_monthly` aggregated to quarter.
- Do not label PhonePe `Retail` and NPCI P2M as the same field; show them as
  parallel supporting measures.

## Page 4: Business monitoring signals

**Question:** Where should a hypothetical UPI app investigate next?

- Table with state/UT, transactions per registered user, merchants per 100
  residents, Retail share, total transactions, and the business signal.
- Optional scatter: x = registered users per 100 residents; y = transactions
  per registered user; bubble size = quarterly transaction count; colour =
  business signal.
- Use a small callout for Gujarat and Tamil Nadu (activation investigation),
  and the high-scale core markets.
- Source: `sql/12_business_opportunity_signals.sql` and
  `sql/13_business_trend_monitoring.sql`.
- Mandatory note: “Public aggregate data flags questions for investigation;
  it does not include active users, cost, revenue, or product performance.”

## Page 5: Methods and limits

Keep this page short and interview-friendly:

- PhonePe is a state-level UPI proxy, not all UPI apps.
- National UPI/cash comparison is not state-level.
- Registered users and merchants are not the same as active users or active
  merchants.
- Per-resident measures use official population projections.
- Income and internet checks are single snapshots and descriptive only.
- The PMJDY financial-inclusion snapshot was tested as context but was not a
  useful standalone predictor of PhonePe use, so it is intentionally excluded
  from the main dashboard pages.

## Suggested opening sentence for a presentation

> “The data shows broad digital-payment growth and a growing merchant-payment
> mix. It also shows that payment intensity remains geographically different,
> so the best business questions are about local activation, merchant
> acceptance, and protecting high-scale markets—not a blanket claim that UPI
> has replaced cash everywhere.”
