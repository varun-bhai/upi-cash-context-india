# Step 4: Load the clean data into SQLite

## Why SQLite now?

We have separated raw data from cleaned CSVs. SQLite gives us a real relational
database without installing a server or paying for a service. It lets us learn
the workflow used in larger databases: define a schema, load tables, query
them, and keep SQL scripts reproducible.

## What is in the database

The loader creates `data/upi_cash_displacement.sqlite` with four base tables:

| Table | Meaning | Rows after this load |
|---|---|---:|
| `phonepe_state_transactions` | PhonePe state/UT × quarter × category transactions | 3,671 |
| `phonepe_state_users` | PhonePe registered users by state/UT × quarter | 1,224 |
| `phonepe_state_merchants` | PhonePe registered merchants by state/UT × quarter | 1,178 |
| `national_payment_quarterly` | Complete national quarters for UPI, IMPS, and NFS-at-ATM | 57 |

It also creates two views:

- `v_phonepe_state_quarterly` aggregates PhonePe categories to one state/UT
  quarter and attaches users and merchants. A missing merchant value remains
  `NULL`, not zero.
- `v_national_payment_quarterly_pivot` places national UPI, IMPS, and
  NFS-at-ATM measures side-by-side for each complete quarter.

The PhonePe source labels quarters as `1`–`4`; the database loader normalises
those labels to `Q1`–`Q4` to match the national table. The processed CSVs stay
unchanged, so the original source representation remains available.

## Rebuild it

Run this whenever a cleaned CSV changes:

```bash
python3 scripts/load_sqlite.py
```

The loader rebuilds the project database from the processed CSVs. It does not
modify raw source files.

## First SQL inspection

Run the starter queries with:

```bash
sqlite3 -header -column data/upi_cash_displacement.sqlite < sql/02_initial_inspection.sql
```

Read [the query file](/Users/varun/Desktop/sql_upi_project/sql/02_initial_inspection.sql)
as you run it. Each query answers a narrow quality or coverage question before
we move to rankings, growth rates, or relationships between series.
