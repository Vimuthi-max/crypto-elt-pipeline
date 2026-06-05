# Crypto Data Pipeline (ELT) & Live Dashboard

A real-time data pipeline that fetches live cryptocurrency metrics from the CoinGecko API, stores them in a local PostgreSQL database using an ELT (Extract, Load, Transform) pattern, and visualizes the trends on an auto-refreshing Streamlit dashboard.

---

## 🏗️ How It Works (Data Flow)

Instead of transforming data inside Python, this project dumps the raw API payload straight into a staging table first, and then handles the data cleaning/transformation directly inside PostgreSQL using SQL.

```text
 [ CoinGecko API ] 
         │ (Python requests)
         ▼
 [ PostgreSQL: `crypto_staging` Table ]  <-- Raw API dump
         │ 
         │ (SQL Transformation / Casting)
         ▼
 [ PostgreSQL: `crypto_analytics` Table ] <-- Cleaned & Split Data
         │ 
         ▼
 [ Streamlit Dashboard ]                 <-- Live UI (Auto-refreshes every 10s)
Why this approach?
ELT Pattern: Ingesting raw data first ensures that if an API payload format changes or network lags, we don't lose data during a mid-flight Python transformation.

Database-Level Casting: Used Postgres SQL casting (::DATE and ::TIME) to split the raw ISO timestamps into separate date and time columns. This makes time-series querying much faster.

Idempotency: The staging table (crypto_staging) is automatically truncated after the transformation layer executes. This ensures no duplicate rows are inserted if the script runs multiple times.

📊 Database Schema
1. Staging Table
Acts as a temporary buffer for raw incoming data.

SQL
CREATE TABLE crypto_staging (
    id SERIAL PRIMARY KEY,
    coin_name VARCHAR(50) NOT NULL,
    price_usd NUMERIC(20, 4) NOT NULL,
    change_24h NUMERIC(10, 4),
    extracted_at TIMESTAMP NOT NULL
);
2. Analytics Table (Warehouse Layer)
Structured for optimal dashboard querying and historical trend analysis.

SQL
CREATE TABLE crypto_analytics (
    fact_id SERIAL PRIMARY KEY,
    coin_name VARCHAR(50) NOT NULL,
    price_usd NUMERIC(20, 4) NOT NULL,
    change_24h NUMERIC(10, 4),
    extracted_date DATE NOT NULL,
    extracted_time TIME NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
🚀 Setup & Execution
Prerequisites
Python 3.10+

PostgreSQL instance running locally (configured via pgAdmin)

1. Install Dependencies
Bash
pip install -r requirements.txt
2. Run Ingestion Pipeline
To fetch live data, load it to staging, and transform it into the analytics layer, run:

Bash
python pipeline.py
3. Start Dashboard
To launch the live dashboard with the 10-second auto-refresh feature:

Bash
streamlit run dashboard.py
📂 Project Structure
pipeline.py - Core ETL/ELT logic (API fetching, DB connection, SQL execution).

dashboard.py - Streamlit application code with auto-refresh mechanism.

Dockerfile - Container configuration wrapper.

.gitignore - Prevents local environment files and DB passwords from being pushed.