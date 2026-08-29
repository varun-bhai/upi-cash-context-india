# Step 25: Dashboard data guide

We are preparing the dashboard's **data layer first**. This means every chart
will use a small, reusable CSV exported from the SQLite database, instead of
copying numbers into a visual manually.

Run this whenever the database changes:

```bash
python3 scripts/export_dashboard_data.py
```

It creates four files in `data/dashboard/`.

## 1. National payments context

**File:** `national_quarterly_payments_context.csv`  
**Rows:** 19 quarterly observations, from 2020 Q3 to 2025 Q1.

Use this for the first chart: a two-line indexed chart.

- Horizontal axis: `quarter_start_date`
- Lines: `all_upi_volume_index_first_quarter_100` and
  `nfs_atm_volume_index_first_quarter_100`
- Starting point: both equal 100 in the first available quarter, making the
  different-sized series comparable.

The file also contains actual transaction/withdrawal volumes and average
ticket sizes for tooltip cards. The chart title should say **“National UPI
growth and NFS ATM cash-access context.”**

Never label NFS ATM withdrawals as “cash use” or “all ATM withdrawals.”

## 2. Annual cash-reliance context

**File:** `national_annual_cash_reliance.csv`  
**Rows:** 7 financial years, FY 2017-18 to FY 2023-24.

Use this for a separate line chart:

- Horizontal axis: `financial_year`
- Line: `currency_to_demand_deposits_ratio`
- Optional tooltip: `currency_with_public_crore` and
  `demand_deposits_crore`

Do not put this ratio on the same axis as UPI transaction volume. It is an
annual ratio, while UPI is a quarterly transaction count. The visual should
say: **“Currency relative to immediately spendable bank deposits, not cash
spending.”**

## 3. Merchant-payment mix

**File:** `national_payment_mix_quarterly.csv`  
**Rows:** 34 PhonePe quarters, 2018 Q1 to 2026 Q2. The all-UPI P2M field is
present only where the NPCI series overlaps through 2026 Q1.

Use two linked visuals:

- A 100% stacked area/column chart of `phonepe_p2p_share_pct`,
  `phonepe_retail_share_pct`, and `phonepe_utility_share_pct`.
- A separate line for `all_upi_p2m_share_pct` across its available period.

PhonePe Retail and all-UPI P2M point in the same merchant-payment direction,
but they are not guaranteed to be identical categories. Keep their labels
separate.

## 4. State scale, growth, and business questions

**File:** `state_scale_growth_business_signals.csv`  
**Rows:** 36 state/UT rows for PhonePe 2026 Q2.

This is the dashboard's main state table. It powers three visuals:

1. **Scale versus growth scatter**
   - x-axis: `rolling_4q_transaction_growth_pct`
   - y-axis: `latest_rolling_4q_transactions_mn`
   - bubble size: `latest_quarter_transaction_value_inr_trillion`
   - label/colour: `business_question_to_investigate`

2. **Top-state bar chart**
   - category: `state_name`
   - value: `latest_quarter_transaction_value_inr_trillion`
   - sort descending; display only the top 10.

3. **Business investigation table**
   - `state_name`, `registered_users_per_100_residents`,
     `transactions_per_registered_user`, `merchants_per_100_residents`,
     `retail_share_pct`, `latest_quarter_transactions_mn`, and
     `business_question_to_investigate`.

The signals are based on relative state quartiles in public aggregate data.
They identify where to investigate, not where to spend money.

## Proposed dashboard flow

1. National UPI and cash-access context.
2. Cash-to-demand-deposit context.
3. Merchant-payment mix shift.
4. State scale and growth.
5. Business investigation signals and limitations.

This order tells one coherent story: national payment habits are changing;
cash has not vanished; state markets differ greatly; a business should use
those differences to form better questions, then validate them with internal
product data.
