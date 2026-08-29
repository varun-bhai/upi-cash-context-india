# Step 13: What existing research teaches us

## Scope

This is a **curated review**, not a claim that we found every paper ever
written about UPI. I prioritised work that is (a) about India or fast payments,
(b) uses real data rather than opinion alone, and (c) can teach us a useful
method or a useful caution for this project.

Our project question is deliberately narrower than many of these studies:

> As UPI becomes more merchant-oriented, what patterns are visible in state
> and national payment data, and what can we responsibly say about possible
> changes in reliance on cash?

## The most useful studies

| Study | Main question and data | Technique | What we borrow | What we do **not** claim |
|---|---|---|---|---|
| [Awasthy & Seet, RBI Bulletin (2025)](https://rbidocs.rbi.org.in/rdocs/Bulletin/PDFs/05ARTICLES24092025634FBBE941344543801EDCF305753C94.PDF) | Does UPI relate to cash demand nationally and across states? Uses currency in circulation, state currency-chest withdrawals, PhonePe Pulse, population, nighttime lights, ATM density, EPFO, education and internet data. | National ARDL time-series model; state fixed-effects panel quantile regressions. | Treat cash access as an imperfect proxy; work per capita; include time effects and controls; allow relationships to differ by state. | A correlation in our much smaller dataset is not causal proof. |
| [Reddy, Kedia & Shukla, ICRIER (2024)](https://icrier.org/pdf/IPCIDE-wp1.pdf) | How has digital-payment adoption diffused across states and districts? Uses PhonePe Pulse plus population, income, poverty, literacy, phone/internet access and financial-inclusion indicators. | Descriptive trends; sigma and gamma convergence; cross-sectional regression with robust standard errors. | Measure adoption in several ways: users per person, transactions per person, value per person and ticket size. Check whether states are converging, not just growing. | Registered users are not necessarily active users; cross-sectional associations are not causal. |
| [Dubey & Purnanandam (2023 working paper)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4373602) | Can cashless payments improve household income and small-business activity? Uses district differences after UPI and bank participation timing. | An instrumental-variable style design: timing of a district's main bank joining UPI supplies variation in adoption. | A credible causal question needs an external event or rule that changes payment adoption for some places sooner than others. | We do not have that bank-timing design, so we cannot reproduce its causal income result. |
| [RBI Annual Report 2022-23, currency-demand discussion](https://www.rbi.org.in/scripts/AnnualReportPublications.aspx?Id=1373) | Why can currency and digital payments rise at the same time? Uses macro currency and payment indicators. | Decomposes motives for holding cash and models currency demand. | Do not use currency in circulation alone as “cash spending.” Cash can be held for precaution or savings, while small everyday cash payments decline. | A rising currency total does not disprove a shift away from cash at shops. |
| [BIS, fast-payments design and adoption (2024)](https://www.bis.org/publ/qtrpdf/r_qt2403c.htm) | What features and country conditions help fast payments grow? Uses international payment-system data. | Cross-country analysis of system design and adoption conditions. | Merchant acceptance, interoperability, smartphones, internet and digital literacy are plausible drivers—not just the existence of an app. | An international correlation is not a state-level result for India. |
| [BIS, digital payments, informality and growth (2024)](https://www.bis.org/publ/work1196.htm) | How are digital payments, growth and informal employment related across 101 economies? | Panel regressions with lagged outcomes and controls for endogeneity. | If we later examine formalisation or economic outcomes, put pre-existing levels and broader digitalisation controls in the model. | Its country-level estimates cannot be pasted onto Indian states. |
| [NPCI–PRICE, Digital Payment Adoption in India (2020)](https://www.npci.org.in/PDF/npci/knowledge-center/Digital-Payment-Adoption-in-India-2020.pdf) | Which households use or want to use digital payments, and what differs by income group? | Household adoption report. | Adoption is not only about technology: ability, trust, income, perceived usefulness and merchant acceptance matter. | This is context for interpretation, not a time series to merge with our transactions. |

## Practical lessons for our project

### 1. Start with measurement, not regression

Our strongest immediate work is descriptive but valuable:

- all-UPI P2M share rose from 41.0% in 2022 Q1 to 62.4% in 2025 Q1;
- PhonePe Retail share rose from 49.1% to 60.5% in the same period;
- the independent app and RBI-derived national UPI volume sources broadly agree.

That is already a defensible finding about the *composition* of UPI payments.
It is not yet a finding about cash displacement.

### 2. Use rates as well as totals

A transaction total is naturally larger in Maharashtra than in a small state.
The ICRIER and RBI studies therefore divide by population. When we add a
consistent state-population source, we should calculate:

- transactions per resident;
- registered PhonePe users per resident;
- merchants per resident; and
- transaction value per resident.

Example: 100 million transactions in a 10 million-person state means roughly
10 transactions per resident for that quarter. The same 100 million in a
100 million-person state means roughly 1 per resident. Totals alone hide that
difference.

### 3. Separate person-to-person from merchant activity

P2P transfers can include sending money to family or moving money between a
person's own accounts. P2M transactions are much closer to an everyday shop or
service payment. Our all-UPI P2P/P2M series is therefore a better bridge to the
cash-use question than raw UPI totals. PhonePe `Retail` is useful too, but it is
not exactly the same definition as all-UPI P2M.

### 4. Cash needs a precise proxy

The RBI paper uses state currency-chest withdrawals. Our current national
dataset has NFS/ATM transaction data, which is a **cash-access proxy**, not a
complete measure of cash demand or cash spending. A fall in ATM withdrawals can
mean less cash use, but could also reflect people withdrawing less often and
taking out more each time. Every later chart and query must keep this caveat.

### 5. Control for obvious alternative explanations before modelling

Suppose a state has more UPI and fewer ATM withdrawals. That could reflect UPI,
but it could also reflect urbanisation, income, better internet, merchant
acceptance, COVID-period behaviour or seasonal festivals. If we later build a
state-by-quarter model, the minimum sensible controls are:

- state fixed effects (each state's stable character);
- quarter/year effects (nationwide shocks and seasonality);
- population-normalised outcomes;
- an economic-activity proxy; and
- ATM and internet availability if consistent state data are available.

### 6. Choose a technique that our data can actually support

The RBI national ARDL model has more than 60 quarters, beginning in 2009. Our
clean national UPI/cash-access overlap is only 19 complete quarters. An ARDL
model now would look sophisticated but be fragile. We should not run it yet.

Likewise, a difference-in-differences study needs a believable intervention and
a comparison group. “COVID happened” is not enough because it affected every
state in many ways. The bank-entry timing in Dubey and Purnanandam is the kind
of outside variation that a causal design needs; we do not currently have it.

## Recommended next steps, in order

1. **Create per-capita state measures.** Add one documented population series,
   match state names carefully, and keep unmatched states visible.
2. **Run a convergence analysis.** Use the standard deviation of log
   transactions-per-resident and users-per-resident by quarter. This directly
   follows the ICRIER approach and answers whether adoption became less uneven.
3. **Build a transparent descriptive cash-access dashboard/query.** Align
   national UPI, all-UPI P2M share and NFS/ATM volume, with no causal wording.
4. **Look for state cash-withdrawal data.** If a lawful, reproducible series of
   currency-chest withdrawals becomes available, that unlocks a properly scoped
   state panel study resembling the RBI paper.
5. **Only then consider regression.** Write the question, outcome, comparison,
   controls and limitations first; then decide whether the available data really
   supports it.

## Research position at this point

We have moved beyond “PhonePe alone seems to be changing.” Independent national
P2M data show the same broad merchant-payment direction, and app totals agree
closely with a separate national UPI volume series. The next rigorous question
is not “did UPI kill cash?” It is:

> Which states and periods show the largest move toward merchant payments per
> resident, and does that change line up with a carefully defined cash-access
> indicator after accounting for the things that could also drive both?
