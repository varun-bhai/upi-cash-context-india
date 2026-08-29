# Step 2: Free national payment indicators

## Purpose

This source provides a free national context series for UPI, IMPS, and NFS
through ATMs. It cannot support state-level cash-displacement claims.

The unit of analysis starts as a national daily payment mode. We retain that
grain, then create monthly sums and complete-calendar-quarter sums that align
with PhonePe’s quarterly state data.

## Source decision

The active source is the India Data Portal's open-licensed [RBI Daily Digital
Payments resource](https://ckandev.indiadataportal.com/dataset/reserve-bank-of-india/resource/1f9367ac-01b0-4c82-83a1-4069d4340667).
It makes RBI-derived national daily payment measures available through a free
public API. The snapshot currently covers 2020-06-01 to 2026-07-10, so the
first usable full calendar quarter is 2020 Q3.

The source reports volume in lakh and value in INR crore. We preserve those
units instead of making silent unit conversions.

## What we saved and created

The unmodified API response is stored locally at
`data/raw/rbi/idp_rbi_daily_digital_payments.json`. The extraction script
creates three cleaned files:

- `idp_rbi_national_payment_indicators_daily.csv`
- `idp_rbi_national_payment_indicators_monthly.csv`
- `idp_rbi_national_payment_indicators_quarterly.csv`

Run:

```bash
python3 scripts/extract_idp_rbi.py
```

## Validation rules and limitations

The extractor stops if the API response is incomplete, duplicate dates conflict
on the selected measures, or a selected value is negative. The downloaded
snapshot contains 31 identical duplicate records for July 2026; it retains one
deterministic copy of each and records that decision in the quality report. It
emits a quarter only when all three months and every calendar day in those
months are represented, and records skipped partial periods.

## Interpretation rule

Compare series as national trends and describe them as an association. **NFS
through ATMs** is a cash-access proxy, not a measure of all ATM withdrawals or
cash spending. It cannot prove that UPI caused cash use to fall.
