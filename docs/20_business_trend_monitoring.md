# Step 20: Business monitoring — are the state signals changing?

## The business question

The first business snapshot told us where to investigate user activation,
merchant acceptance, or core-market experience. A single snapshot can be
misleading, so the next analyst question is:

> Compared with the same quarter a year earlier, are usage, user reach,
> merchant reach, and the Retail payment mix improving or weakening?

We compare **2025 Q2 (April-June 2025)** with **2026 Q2 (April-June 2026)**.
Using the same quarter avoids confusing normal seasonal patterns with growth.

## Measures monitored

| Measure | What it tells us |
|---|---|
| Transaction growth | Whether total payment activity grew in the state/UT. |
| User-density growth | Whether reported registrations grew faster than population. |
| Transactions per registered user | A rough usage-intensity measure. It is not an active-user or retention measure. |
| Merchant-density growth | Whether reported merchant reach grew faster than population. |
| Retail-share change | Whether shop/merchant-style payments became a larger or smaller part of PhonePe activity. |

## Overall result across the 36 PhonePe state/UT rows

| 2025 Q2 to 2026 Q2 change | Result |
|---|---:|
| PhonePe transactions | +24.2% |
| Reported registered users | +11.7% |
| Reported registered merchants | +10.2% |
| Transaction-weighted Retail share | +1.9 percentage points |

In simple words, transaction activity grew about twice as quickly as the
reported user base. The merchant base also grew, and Retail payments took a
larger share. This is a strong descriptive sign of deeper use of the platform;
it does not tell us why use deepened or whether it was profitable.

## Examples a business team would investigate

- **Gujarat:** transactions grew 25.9% and transactions per registered user
  grew 12.6%, even though it remained an activation signal in the latest
  cross-state snapshot. The priority is not “the market is failing”; it is
  “what keeps its usage-per-registration relatively low, and can the improving
  trend continue?”
- **Tamil Nadu:** transactions grew 19.2%, while transactions per registered
  user rose 7.5% and Retail share rose 2.2 percentage points. This suggests a
  different investigation from Gujarat even though both were activation
  signals.
- **Arunachal Pradesh:** merchant density grew 31.0% and Retail share rose
  3.3 points. Its merchant-acceptance signal deserves a follow-up check to see
  whether the growth comes from genuine merchant use or a change in registered
  coverage.
- **Maharashtra, Karnataka, Telangana:** very large transaction markets also
  grew 25.5%, 20.4%, and 27.4%, respectively. For a product team, this keeps
  reliability and capacity in the foreground, rather than only acquisition.

## How to read this correctly

This is a monitoring table, not a growth-target model. Public aggregate data
cannot distinguish new active users from reactivated users, measure revenue or
cost, or show what specific feature, campaign, competitor, or local event
caused growth. It gives a concise and defensible answer to: **where should we
look next?**

## Reproduce it

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/13_business_trend_monitoring.sql
```
