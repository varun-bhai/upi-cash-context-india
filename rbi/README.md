# RBI-derived national payment data

The active source is the free, open-licensed **RBI Daily Digital Payments**
resource on the [India Data Portal](https://ckandev.indiadataportal.com/dataset/reserve-bank-of-india/resource/1f9367ac-01b0-4c82-83a1-4069d4340667).
It is retrieved through the site's public CKAN Data API rather than a paid
catalogue. The downloaded API response is retained unchanged as:

`idp_rbi_daily_digital_payments.json`

It contains national daily observations from 2020-06-01 to 2026-07-10 when we
downloaded it. The project uses three measures, with volume in lakh and value
in INR crore:

- UPI (`upi_vol`, `upi_val`)
- IMPS (`imps_vol`, `imps_val`)
- NFS through ATMs (`nfs_through_atms_vol`, `nfs_through_atms_val`)

Run the transformation from the project root:

```bash
python3 scripts/extract_idp_rbi.py
```

The results are stored under `data/processed/`. The script excludes incomplete
calendar quarters. Crucially, NFS through ATMs is a cash-access proxy; it is
not all ATM withdrawals and not a measure of cash spending.

`extract_rbi.py` remains only as an unused alternative for a future official
monthly workbook download. It is not needed for the current project data.
