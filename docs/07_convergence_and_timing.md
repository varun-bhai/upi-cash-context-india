# Step 7: We tested convergence, then inspected timing

## The convergence idea is not strongly supported

If states with a low initial Retail share were simply catching up, we would
expect a clearly negative relationship between their Retail share in 2020 Q3
and the share increase by 2025 Q1. The observed Pearson correlation is `-0.153`.
That is weak, so it does not support a strong, systematic catch-up story.

This is a valuable result. It prevents us from turning a plausible narrative
into a claim the data do not support.

## The shift looks gradual, with a few larger moves

The national PhonePe Retail share rose over the whole period, rather than in
one single jump. The largest quarter-to-quarter increase was 5.9 percentage
points in 2021 Q3 (from 37.3% in 2021 Q2 to 43.2%). The next largest rises
were 3.8 points in 2021 Q4 and 2.5 points in 2022 Q2.

The unusually low 2021 Q2 share and the recovery afterwards could reflect the
COVID-period mix of transactions, seasonal effects, platform behaviour, or
classification/reporting differences. Our current data cannot distinguish
those explanations.

## What this changes in our research plan

So far, our internal checks suggest:

- the Retail-share change is broad across states/UTs;
- it is not explained simply by merchant additions;
- it is not strongly explained as lower-share states catching up;
- its timing makes the 2021 period worth contextual investigation.

The next useful addition should be one source that supplies context—such as
official monthly national UPI statistics or a documented timeline of relevant
payment-policy and COVID restrictions—not a large collection of unrelated
datasets. We would use it to describe timing, not to assert causality.

Run the queries with:

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/05_convergence_and_timing.sql
```
