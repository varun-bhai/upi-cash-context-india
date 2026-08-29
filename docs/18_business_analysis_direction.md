# Step 18: Turning the project into a business data-analysis portfolio

## A change in emphasis

This project should be a **data-analysis project**, not a research paper.

Research papers helped us learn good habits: check sources, match dates fairly,
and avoid claiming causes that the data cannot prove. But the work we produce
from here should look more like the work a business data analyst does:

> Use data to identify a decision worth investigating, explain the evidence,
> and state what additional information is needed before taking action.

We will keep the academic sources in the background as references. We will not
add advanced statistical models simply to make the project look complicated.

## The business setting we can simulate

Imagine we are analysts for a UPI payment app. At the state/UT level, a product
or growth team might ask:

1. **Activation:** Where do we have many registered users but comparatively
   little transaction activity per registered user?
2. **Merchant acceptance:** Where do we have a user base but relatively few
   registered merchants and a low share of Retail/shop payments?
3. **Core-market protection:** Which high-volume, high-use markets deserve
   close attention to payment reliability, support, and merchant experience?

These are useful *questions to investigate*. They are not orders to run a
marketing campaign, because our public data does not include campaign cost,
revenue, profit, active users, customer complaints, or competitor presence.

## What we used

We use the latest complete PhonePe state/UT quarter in the project: **2026 Q2
(April-June 2026)**. All 36 states/UTs have users, merchants, transactions,
and population for this period.

For each state/UT we calculate:

| Measure | Plain meaning | Why it helps a business question |
|---|---|---|
| Registered users per 100 residents | Breadth of reported PhonePe registration | Shows where the potential user base is relatively broad. |
| Transactions per registered user | Quarter's transactions divided by reported registered users | A rough usage-intensity signal. It does **not** mean active users or retention. |
| Merchants per 100 residents | Reported merchants relative to population | A rough acceptance-network signal. |
| Retail share | Share of PhonePe transactions labelled `Retail` | A rough signal of shop/merchant payment mix. |
| Quarterly transactions | Total PhonePe transaction count | A scale signal: a small state and a large state should not be prioritised in the same way. |

To avoid arbitrary cut-offs, the SQL sorts all 36 places into four equal-sized
comparison groups (called **quartiles**) for each measure. For example,
“high user density” means a place lies in the upper half of this particular
36-place comparison. It does not mean the level is objectively good.

## The first business signals

| Signal from 2026 Q2 | State/UTs flagged | Sensible next business question |
|---|---|---|
| Activation of existing users | Gujarat, Tamil Nadu, Uttarakhand, Himachal Pradesh, Chandigarh, Andaman & Nicobar Islands | Are people registering but not finding a frequent payment use case, or does the registration count include inactive old accounts? |
| Activation + merchant acceptance | Sikkim, Ladakh | Is merchant availability a bottleneck? The small transaction scale means first validate the local market before prioritising investment. |
| Merchant acceptance/onboarding | Arunachal Pradesh | Are there geographic, merchant-category, onboarding, or connectivity constraints? |
| Protect high-use core experience | 15 state/UTs, including Maharashtra, Karnataka, Telangana, Uttar Pradesh, Andhra Pradesh, Rajasthan, Bihar, Delhi | Are success rate, support, fraud controls, and merchant experience keeping up with a very large transaction base? |

Two useful examples:

- **Gujarat** had about **1.16 billion** PhonePe transactions in the quarter and
  Tamil Nadu about **1.05 billion**. Both have a relatively broad registered
  base but are in the lower half of this cross-state comparison for
  transactions per registered user. That makes activation a high-impact
  question to investigate.
- **Sikkim** and **Ladakh** meet both the low-use and low-merchant signals,
  but have only about **15.0 million** and **9.3 million** quarterly
  transactions, respectively. A business team would first check the likely
  payoff and operating constraints—not treat an interesting pattern as an
  automatic priority.

## What this analysis does not know

Public PhonePe Pulse data is excellent for learning SQL and seeing geographic
patterns, but it cannot tell us:

- whether a registered user is active, retained, or a duplicate;
- why a person did not transact;
- transaction success/failure rate, customer support contacts, fraud, or app
  performance;
- merchant category, onboarding cost, revenue, or profitability; and
- what Google Pay, Paytm, bank apps, or cash are doing in the same state.

Therefore the proper analyst recommendation is usually:

> “This is a priority **for investigation**. Combine it with internal product,
> merchant, and cost data before choosing an intervention.”

That is strong analysis, not a weakness.

## The SQL work

The whole segmentation is reproducible in
`sql/12_business_opportunity_signals.sql`. It produces a detailed state list
and a count of places in each signal group.

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/12_business_opportunity_signals.sql
```

## Good next business-analysis step

Next, we can examine **change over time** for these business signals. For
example: did Gujarat's transactions per registered user improve or weaken from
2025 Q2 to 2026 Q2? This would make the project feel even more like routine
business monitoring rather than one-off research.
