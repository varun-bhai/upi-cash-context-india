# Expanding the project beyond PhonePe

## Short answer

Yes, but the available public data has different levels of detail:

| Source | Apps covered | Geography | Time grain | What it can answer |
|---|---|---|---|---|
| PhonePe Pulse | PhonePe only | State/UT | Quarter | Adoption, users, merchants, and transaction mix within PhonePe |
| NPCI UPI Ecosystem Statistics | PhonePe, Google Pay, Paytm, BHIM, Amazon Pay, WhatsApp, bank apps, and others | India total | Month | App competition, market shares, volumes, and average ticket size |
| NPCI State-wise UPI Product Statistics | All UPI apps together | State/UT | Month | Total UPI adoption by state, but not which app was used |
| India Data Portal RBI-derived series | All payment providers together | India total | Day / month / quarter | National UPI, IMPS, and NFS-through-ATM trend context |

## The important limitation

We have not found an equivalent open, historical **state-by-state** dataset for
Google Pay, Paytm, or other individual apps. Their companies do not publish a
PhonePe-Pulse-style public dataset that we can verify and load. We should not
invent state app comparisons from national totals.

This is not a weakness if we structure the project correctly. It gives us a
useful three-layer design:

1. **National UPI ecosystem:** NPCI app-level data lets us see whether PhonePe,
   Google Pay, Paytm, and other apps gained or lost national share.
2. **State-level digital adoption:** PhonePe Pulse gives geographic and
   category-level detail, clearly labelled as PhonePe-platform activity.
3. **National cash context:** RBI-derived national measures let us describe the
   relationship between all-UPI growth and cash-access indicators.

## What the Zerodha article contributes

The Zerodha article is a readable explanation of an RBI Bulletin study,
*Impact of UPI on Cash Demand – Evidence from National and Subnational Levels*
(September 2025). It is useful for ideas, but it should not be our primary
data source. The underlying RBI study asks about national and state-level UPI
adoption, cash demand, and income differences.

The best things to borrow are its research discipline:

- distinguish cash **demand** from cash merely existing in circulation;
- use more than one cash indicator where possible;
- compare states carefully, accounting for different levels of development;
- avoid claiming that an observed correlation proves causation.

The article describes cash-in-circulation growth, currency relative to demand
deposits, ATM withdrawals relative to GDP, and UPI average ticket size. Those
are future candidate measures; we should add one at a time only when we can
obtain a reliable, reproducible source.

## Recommended next addition

Add the official NPCI app-level monthly table first. It would give the project
an India-wide ecosystem view that includes Google Pay, Paytm, BHIM, Amazon Pay,
WhatsApp, and bank apps. We can ask:

> Did PhonePe's state-level Retail shift occur while PhonePe was gaining,
> stable, or losing national UPI-app market share relative to Google Pay and
> Paytm?

This will not prove why the shift happened, but it is a strong, answerable
descriptive question. Only after that should we seek an additional cash-demand
measure inspired by the RBI study.

## Sources

- NPCI, [UPI Ecosystem Statistics](https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics)
- NPCI, [UPI Product Statistics](https://www.npci.org.in/product/upi/product-statistics)
- PhonePe, [Pulse Dataset](https://www.phonepe.com/pulse/data/)
- RBI Bulletin study, [Impact of UPI on Cash Demand – Evidence from National and Subnational Levels](https://rbidocs.rbi.org.in/rdocs/Bulletin/PDFs/05ARTICLES24092025634FBBE941344543801EDCF305753C94.PDF)
- Zerodha Daily Brief, [How UPI is Changing Cash Use in India](https://thedailybrief.zerodha.com/p/how-upi-is-changing-cash-use-in-india)
