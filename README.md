
# 🚀 Automated End-to-End ELT Crypto Data Pipeline & Live Dashboard

A real-time data pipeline that fetches live cryptocurrency metrics from the CoinGecko API, stores and transforms them in a cloud-hosted PostgreSQL database using an ELT (Extract, Load, Transform) pattern, and visualizes the trends on an auto-refreshing Streamlit dashboard.

---

## 🏗️ How It Works (Data Flow)

Instead of transforming data inside Python, this project dumps the raw API payload straight into a staging table first, and then handles the data cleaning/transformation directly inside PostgreSQL using SQL.

```text
 [ CoinGecko API ] 
         │ (Python requests)
         ▼
 [ PostgreSQL: `crypto_staging` Table ]   <-- Raw API dump
         │ 
         │ (SQL Transformation / Casting)
         ▼
 [ PostgreSQL: `crypto_analytics` Table ] <-- Cleaned & Split Data (Warehouse)
         │ 
         │ (Decoupled Asset Intelligence Tabs)
         ▼
 [ Streamlit Dashboard ]                  <-- Live UI (Auto-refreshes every 10s)
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
📈 Dashboard Features
Asset Intelligence Hub: Decoupled interactive tabs for top crypto tokens (BTC, ETH, SOL, DOGE, ADA).

Watermark Metrics: Computes real-time 24-hour High (Max) and Low (Min) price fluctuations instantly using standard Pandas data structures.

Micro-Trend Analytics: Granular time-series line charts tracked safely using immutable database insertion timestamps (inserted_at).

Production Archive Viewer: Full visual access to the clean, tabular state of the analytical warehouse log with stretched grid handling.

🛠️ Setup & Execution
Prerequisites
Python 3.13+

PostgreSQL Instance (Neon Cloud DB or Local Instance)

1. Configure Environment Secrets
Create a .env file in the root directory (this is securely hidden via .gitignore) and add your database connection string:

Plaintext
DB_URL=postgresql://your_username:your_password@your_host/neondb?sslmode=require
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Run Ingestion Pipeline
To fetch live data, load it to staging, and transform it into the analytics layer, run:

Bash
python pipeline.py
(Note: Run this script 3-4 times initially with brief gaps to populate historical plot points for the trend charts).

4. Start Dashboard
To launch the live dashboard with the 10-second auto-refresh feature:

Bash
streamlit run dashboard.py
📂 Project Structure
pipeline.py - Core ETL/ELT logic (API fetching, secure .env credential loading, DB connection, SQL production macro execution).

dashboard.py - Streamlit application code with auto-refresh mechanism, asset-specific metric tracking, and modern layout formatting.

Dockerfile - Container configuration wrapper.

.gitignore - Prevents local environment files (.env) and cache directories from being pushed.