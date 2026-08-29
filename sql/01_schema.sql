-- SQLite schema for analysis-ready tables only.
-- Raw JSON and CSV files remain unchanged under data/raw and data/processed.

DROP VIEW IF EXISTS v_phonepe_state_quarterly;
DROP VIEW IF EXISTS v_phonepe_state_quarterly_per_capita;
DROP VIEW IF EXISTS v_phonepe_state_q2_2024_with_internet;
DROP VIEW IF EXISTS v_phonepe_state_q1_2024_with_nsdp;
DROP VIEW IF EXISTS v_phonepe_state_q2_2026_with_pmjdy;
DROP VIEW IF EXISTS v_national_payment_quarterly_pivot;
DROP VIEW IF EXISTS v_national_cash_reliance_with_upi;
DROP VIEW IF EXISTS v_national_upi_app_monthly;
DROP TABLE IF EXISTS national_upi_p2p_p2m_monthly;
DROP TABLE IF EXISTS national_cash_reliance_annual;
DROP TABLE IF EXISTS phonepe_state_transactions;
DROP TABLE IF EXISTS phonepe_state_users;
DROP TABLE IF EXISTS phonepe_state_merchants;
DROP TABLE IF EXISTS national_payment_quarterly;
DROP TABLE IF EXISTS national_upi_app_monthly;
DROP TABLE IF EXISTS population_state_annual;
DROP TABLE IF EXISTS state_internet_subscribers_snapshot;
DROP TABLE IF EXISTS state_per_capita_nsdp_snapshot;
DROP TABLE IF EXISTS state_pmjdy_financial_inclusion_snapshot;

CREATE TABLE phonepe_state_transactions (
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    quarter TEXT NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    quarter_start_date TEXT NOT NULL,
    source_category TEXT NOT NULL,
    transaction_count INTEGER NOT NULL CHECK (transaction_count >= 0),
    transaction_value_inr REAL NOT NULL CHECK (transaction_value_inr >= 0),
    source_file TEXT NOT NULL,
    PRIMARY KEY (state_slug, quarter_start_date, source_category)
);

CREATE TABLE phonepe_state_users (
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    quarter TEXT NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    quarter_start_date TEXT NOT NULL,
    registered_count INTEGER NOT NULL CHECK (registered_count >= 0),
    source_file TEXT NOT NULL,
    PRIMARY KEY (state_slug, quarter_start_date)
);

CREATE TABLE phonepe_state_merchants (
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    quarter TEXT NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    quarter_start_date TEXT NOT NULL,
    registered_count INTEGER NOT NULL CHECK (registered_count >= 0),
    source_file TEXT NOT NULL,
    PRIMARY KEY (state_slug, quarter_start_date)
);

CREATE TABLE population_state_annual (
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2011 AND 2036),
    population_persons INTEGER NOT NULL CHECK (population_persons > 0),
    source_state_or_aggregation TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_date_basis TEXT NOT NULL,
    source_url TEXT NOT NULL,
    method_note TEXT NOT NULL,
    PRIMARY KEY (state_slug, year)
);

CREATE TABLE state_internet_subscribers_snapshot (
    as_of_date TEXT NOT NULL,
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    rural_subscribers_mn REAL NOT NULL CHECK (rural_subscribers_mn >= 0),
    urban_subscribers_mn REAL NOT NULL CHECK (urban_subscribers_mn >= 0),
    total_subscribers_mn REAL NOT NULL CHECK (total_subscribers_mn >= 0),
    rural_subscribers_per_100_population REAL CHECK (rural_subscribers_per_100_population >= 0),
    urban_subscribers_per_100_population REAL CHECK (urban_subscribers_per_100_population >= 0),
    total_subscribers_per_100_population REAL NOT NULL CHECK (total_subscribers_per_100_population >= 0),
    source_table TEXT NOT NULL,
    source_url TEXT NOT NULL,
    interpretation_note TEXT NOT NULL,
    PRIMARY KEY (as_of_date, state_slug)
);

CREATE TABLE state_per_capita_nsdp_snapshot (
    financial_year TEXT NOT NULL,
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    per_capita_nsdp_current_inr INTEGER NOT NULL CHECK (per_capita_nsdp_current_inr > 0),
    price_basis TEXT NOT NULL,
    series_base_year TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_url TEXT NOT NULL,
    availability_note TEXT NOT NULL,
    PRIMARY KEY (financial_year, state_slug)
);

-- PMJDY is a one-time beneficiary-account snapshot, not a count of verified
-- unique banked people or active UPI customers.
CREATE TABLE state_pmjdy_financial_inclusion_snapshot (
    as_of_date TEXT NOT NULL,
    state_slug TEXT NOT NULL,
    state_name TEXT NOT NULL,
    beneficiaries_rural_semiurban_count INTEGER NOT NULL CHECK (beneficiaries_rural_semiurban_count >= 0),
    beneficiaries_urban_metro_count INTEGER NOT NULL CHECK (beneficiaries_urban_metro_count >= 0),
    total_beneficiaries_count INTEGER NOT NULL CHECK (total_beneficiaries_count >= 0),
    balance_in_beneficiary_accounts_crore REAL NOT NULL CHECK (balance_in_beneficiary_accounts_crore >= 0),
    rupay_debit_cards_issued_count INTEGER NOT NULL CHECK (rupay_debit_cards_issued_count >= 0),
    source_table TEXT NOT NULL,
    source_url TEXT NOT NULL,
    interpretation_note TEXT NOT NULL,
    PRIMARY KEY (as_of_date, state_slug),
    CHECK (beneficiaries_rural_semiurban_count + beneficiaries_urban_metro_count = total_beneficiaries_count)
);

CREATE TABLE national_payment_quarterly (
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    quarter TEXT NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    quarter_start_date TEXT NOT NULL,
    payment_mode TEXT NOT NULL CHECK (payment_mode IN ('UPI', 'IMPS', 'NFS_ATM_CASH_WITHDRAWAL')),
    months_included INTEGER NOT NULL CHECK (months_included = 3),
    days_observed INTEGER NOT NULL CHECK (days_observed > 0),
    volume_lakh REAL NOT NULL CHECK (volume_lakh >= 0),
    value_crore REAL NOT NULL CHECK (value_crore >= 0),
    PRIMARY KEY (quarter_start_date, payment_mode)
);

-- RBI Table 41 provides annual *average* monetary aggregates.  The ratio is
-- a national context measure; it does not represent total cash use.
CREATE TABLE national_cash_reliance_annual (
    financial_year TEXT NOT NULL PRIMARY KEY,
    currency_with_public_crore REAL NOT NULL CHECK (currency_with_public_crore > 0),
    demand_deposits_crore REAL NOT NULL CHECK (demand_deposits_crore > 0),
    currency_to_demand_deposits_ratio REAL NOT NULL CHECK (currency_to_demand_deposits_ratio > 0),
    source_table TEXT NOT NULL,
    source_url TEXT NOT NULL,
    time_basis TEXT NOT NULL,
    interpretation_note TEXT NOT NULL
);

CREATE TABLE national_upi_app_monthly (
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_start_date TEXT NOT NULL,
    app_name TEXT NOT NULL,
    customer_initiated_volume_mn REAL CHECK (customer_initiated_volume_mn >= 0),
    customer_initiated_value_crore REAL CHECK (customer_initiated_value_crore >= 0),
    b2c_volume_mn REAL CHECK (b2c_volume_mn >= 0),
    b2c_value_crore REAL CHECK (b2c_value_crore >= 0),
    b2b_volume_mn REAL CHECK (b2b_volume_mn >= 0),
    b2b_value_crore REAL CHECK (b2b_value_crore >= 0),
    total_volume_mn REAL NOT NULL CHECK (total_volume_mn >= 0),
    total_value_crore REAL CHECK (total_value_crore >= 0),
    source_reference TEXT NOT NULL,
    PRIMARY KEY (month_start_date, app_name)
);

CREATE TABLE national_upi_p2p_p2m_monthly (
    year INTEGER NOT NULL CHECK (year BETWEEN 2018 AND 2100),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_start_date TEXT NOT NULL PRIMARY KEY,
    total_volume_mn REAL NOT NULL CHECK (total_volume_mn >= 0),
    total_value_crore REAL NOT NULL CHECK (total_value_crore >= 0),
    p2p_volume_mn REAL NOT NULL CHECK (p2p_volume_mn >= 0),
    p2p_value_crore REAL NOT NULL CHECK (p2p_value_crore >= 0),
    p2m_volume_mn REAL NOT NULL CHECK (p2m_volume_mn >= 0),
    p2m_value_crore REAL NOT NULL CHECK (p2m_value_crore >= 0),
    source_p2p_share_pct REAL NOT NULL CHECK (source_p2p_share_pct >= 0),
    source_p2m_share_pct REAL NOT NULL CHECK (source_p2m_share_pct >= 0),
    source_reference TEXT NOT NULL
);

CREATE INDEX idx_phonepe_transactions_period ON phonepe_state_transactions (quarter_start_date);
CREATE INDEX idx_phonepe_transactions_state ON phonepe_state_transactions (state_slug);
CREATE INDEX idx_phonepe_users_period ON phonepe_state_users (quarter_start_date);
CREATE INDEX idx_phonepe_merchants_period ON phonepe_state_merchants (quarter_start_date);
CREATE INDEX idx_population_state_year ON population_state_annual (state_slug, year);
CREATE INDEX idx_internet_snapshot_state ON state_internet_subscribers_snapshot (state_slug, as_of_date);
CREATE INDEX idx_nsdp_snapshot_state ON state_per_capita_nsdp_snapshot (state_slug, financial_year);
CREATE INDEX idx_pmjdy_snapshot_state ON state_pmjdy_financial_inclusion_snapshot (state_slug, as_of_date);
CREATE INDEX idx_upi_app_monthly_period ON national_upi_app_monthly (month_start_date);
CREATE INDEX idx_cash_reliance_financial_year ON national_cash_reliance_annual (financial_year);

-- One row per state/UT and quarter. Category records are aggregated here;
-- registered users are a level, never summed across time.
CREATE VIEW v_phonepe_state_quarterly AS
SELECT
    t.state_slug,
    t.state_name,
    t.year,
    t.quarter,
    t.quarter_start_date,
    SUM(t.transaction_count) AS transaction_count,
    SUM(t.transaction_value_inr) AS transaction_value_inr,
    u.registered_count AS registered_users,
    m.registered_count AS registered_merchants
FROM phonepe_state_transactions AS t
LEFT JOIN phonepe_state_users AS u
    ON u.state_slug = t.state_slug
   AND u.quarter_start_date = t.quarter_start_date
LEFT JOIN phonepe_state_merchants AS m
    ON m.state_slug = t.state_slug
   AND m.quarter_start_date = t.quarter_start_date
GROUP BY t.state_slug, t.state_name, t.year, t.quarter, t.quarter_start_date;

-- The population figure is the official annual projection as on 1 March of
-- the same calendar year. It is a denominator for fair state comparisons, not
-- an estimate of active PhonePe users.
CREATE VIEW v_phonepe_state_quarterly_per_capita AS
SELECT
    q.state_slug,
    q.state_name,
    q.year,
    q.quarter,
    q.quarter_start_date,
    p.population_persons,
    q.transaction_count,
    q.transaction_value_inr,
    q.registered_users,
    q.registered_merchants,
    1.0 * q.transaction_count / p.population_persons AS transactions_per_resident,
    1.0 * q.transaction_value_inr / p.population_persons AS transaction_value_inr_per_resident,
    1.0 * q.registered_users / p.population_persons AS registered_users_per_resident,
    1.0 * q.registered_merchants / p.population_persons AS registered_merchants_per_resident
FROM v_phonepe_state_quarterly AS q
JOIN population_state_annual AS p
    ON p.state_slug = q.state_slug
   AND p.year = q.year;

-- The TRAI value is a one-time snapshot at the end of June 2024, aligned only
-- to PhonePe's April-June 2024 quarter. It must not be read as a quarterly
-- internet-access series.
CREATE VIEW v_phonepe_state_q2_2024_with_internet AS
SELECT
    p.*,
    i.total_subscribers_per_100_population AS internet_subscribers_per_100_population,
    i.total_subscribers_mn AS internet_subscribers_mn
FROM v_phonepe_state_quarterly_per_capita AS p
JOIN state_internet_subscribers_snapshot AS i
    ON i.state_slug = p.state_slug
   AND i.as_of_date = '2024-06-30'
WHERE p.quarter_start_date = '2024-04-01';

-- FY 2023-24 ends in March 2024. This is therefore a one-time alignment to
-- PhonePe's January-March 2024 quarter, not an annual PhonePe series.
CREATE VIEW v_phonepe_state_q1_2024_with_nsdp AS
SELECT
    p.*,
    n.per_capita_nsdp_current_inr,
    n.price_basis AS nsdp_price_basis,
    n.series_base_year AS nsdp_series_base_year
FROM v_phonepe_state_quarterly_per_capita AS p
JOIN state_per_capita_nsdp_snapshot AS n
    ON n.state_slug = p.state_slug
   AND n.financial_year = '2023-24'
WHERE p.quarter_start_date = '2024-01-01';

-- PMJDY's 19 August 2026 snapshot is close to, but not exactly aligned with,
-- PhonePe's April-June 2026 quarter. It is descriptive inclusion context.
CREATE VIEW v_phonepe_state_q2_2026_with_pmjdy AS
SELECT
    p.*,
    j.total_beneficiaries_count AS pmjdy_beneficiaries,
    j.beneficiaries_rural_semiurban_count AS pmjdy_rural_semiurban_beneficiaries,
    j.beneficiaries_urban_metro_count AS pmjdy_urban_metro_beneficiaries,
    j.balance_in_beneficiary_accounts_crore AS pmjdy_balance_crore,
    j.rupay_debit_cards_issued_count AS pmjdy_rupay_cards_issued,
    1.0 * j.total_beneficiaries_count / p.population_persons AS pmjdy_beneficiaries_per_resident,
    1.0 * j.rupay_debit_cards_issued_count / j.total_beneficiaries_count AS pmjdy_rupay_cards_per_beneficiary,
    10000000.0 * j.balance_in_beneficiary_accounts_crore / j.total_beneficiaries_count AS pmjdy_balance_inr_per_beneficiary
FROM v_phonepe_state_quarterly_per_capita AS p
JOIN state_pmjdy_financial_inclusion_snapshot AS j
    ON j.state_slug = p.state_slug
   AND j.as_of_date = '2026-08-19'
WHERE p.quarter_start_date = '2026-04-01';

-- National modes aligned on the same complete calendar quarter.
CREATE VIEW v_national_payment_quarterly_pivot AS
SELECT
    quarter_start_date,
    year,
    quarter,
    MAX(CASE WHEN payment_mode = 'UPI' THEN volume_lakh END) AS upi_volume_lakh,
    MAX(CASE WHEN payment_mode = 'UPI' THEN value_crore END) AS upi_value_crore,
    MAX(CASE WHEN payment_mode = 'IMPS' THEN volume_lakh END) AS imps_volume_lakh,
    MAX(CASE WHEN payment_mode = 'IMPS' THEN value_crore END) AS imps_value_crore,
    MAX(CASE WHEN payment_mode = 'NFS_ATM_CASH_WITHDRAWAL' THEN volume_lakh END) AS nfs_atm_volume_lakh,
    MAX(CASE WHEN payment_mode = 'NFS_ATM_CASH_WITHDRAWAL' THEN value_crore END) AS nfs_atm_value_crore
FROM national_payment_quarterly
GROUP BY quarter_start_date, year, quarter;

-- The RBI money series and the payment data are brought together only on
-- financial years with four complete payment quarters.  All payment values
-- below are fiscal-year totals; the cash/deposit fields are fiscal-year
-- averages, so the comparison is descriptive context, not a causal test.
CREATE VIEW v_national_cash_reliance_with_upi AS
WITH fiscal_payment_totals AS (
    SELECT
        CASE
            WHEN CAST(strftime('%m', quarter_start_date) AS INTEGER) >= 4
                THEN printf('%d-%02d', year, (year + 1) % 100)
            ELSE printf('%d-%02d', year - 1, year % 100)
        END AS financial_year,
        COUNT(*) AS complete_quarters,
        SUM(upi_volume_lakh) AS upi_volume_lakh,
        SUM(upi_value_crore) AS upi_value_crore,
        SUM(nfs_atm_volume_lakh) AS nfs_atm_volume_lakh,
        SUM(nfs_atm_value_crore) AS nfs_atm_value_crore
    FROM v_national_payment_quarterly_pivot
    GROUP BY financial_year
)
SELECT
    c.financial_year,
    c.currency_with_public_crore,
    c.demand_deposits_crore,
    c.currency_to_demand_deposits_ratio,
    p.complete_quarters,
    p.upi_volume_lakh,
    p.upi_value_crore,
    100.0 * p.upi_value_crore / p.upi_volume_lakh AS upi_average_ticket_inr,
    p.nfs_atm_volume_lakh,
    p.nfs_atm_value_crore,
    100.0 * p.nfs_atm_value_crore / p.nfs_atm_volume_lakh AS nfs_atm_average_withdrawal_inr,
    c.time_basis,
    c.interpretation_note
FROM national_cash_reliance_annual AS c
JOIN fiscal_payment_totals AS p
    ON p.financial_year = c.financial_year
WHERE p.complete_quarters = 4;

-- App-level national monthly market share. NPCI assigns each transaction to the
-- payer app; this is not a state-level app market-share measure.
CREATE VIEW v_national_upi_app_monthly AS
SELECT
    year,
    month,
    month_start_date,
    app_name,
    total_volume_mn,
    total_value_crore,
    100.0 * total_volume_mn / SUM(total_volume_mn) OVER (PARTITION BY month_start_date) AS volume_market_share_pct,
    100.0 * total_value_crore / SUM(total_value_crore) OVER (PARTITION BY month_start_date) AS value_market_share_pct
FROM national_upi_app_monthly;
