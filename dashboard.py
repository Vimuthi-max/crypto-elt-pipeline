import streamlit as st
import psycopg2
import pandas as pd
import time  

# Database විස්තර
DB_HOST = "localhost"
DB_NAME = "crypto_db"
DB_USER = "postgres"
DB_PASS = "16455"  
DB_PORT = "5432"

st.set_page_config(page_title="Live Crypto Analytics", layout="wide")

# Dashboard එකේ ප්‍රධාන Title එක
st.title("🚀 Real-Time Crypto Data Pipeline Dashboard")
st.write("This dashboard reads live data directly from our PostgreSQL production warehouse.")

# --- Auto Refresh සෙටප් එක ---

REFRESH_INTERVAL = 10 

def load_analytics_data():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
    query = "SELECT coin_name, price_usd, change_24h, extracted_date, extracted_time, inserted_at FROM crypto_analytics ORDER BY inserted_at DESC;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    df = load_analytics_data()

    if not df.empty:
        # --- 1. TOP METRICS SECTION ---
        st.subheader("💰 Latest Market Prices")
        col1, col2, col3 = st.columns(3)
        
        for coin, col in zip(["BITCOIN", "ETHEREUM", "SOLANA"], [col1, col2, col3]):
            coin_df = df[df['coin_name'] == coin]
            if not coin_df.empty:
                latest_record = coin_df.iloc[0]
                price = latest_record['price_usd']
                change = latest_record['change_24h']
                col.metric(label=f"{coin} (USD)", value=f"${price:,.2f}", delta=f"{change}%")

        st.markdown("---")

        # --- 2. CHART SECTION ---
        st.subheader("📈 Price Trend Over Time")
        chart_df = df.pivot_table(index='extracted_time', columns='coin_name', values='price_usd').sort_index()
        st.line_chart(chart_df)

        st.markdown("---")

        # --- 3. DATA TABLE SECTION ---
        st.subheader("📋 Raw Analytical Warehouse Data (`crypto_analytics`)")
        st.dataframe(df, width="stretch")
        
        
    else:
        st.warning("No data found in 'crypto_analytics' table. Run your pipeline.py first!")

except Exception as e:
    st.error(f" Failed to load dashboard: {e}")

# --- Auto Refresh Countdown එක පෙන්වීම සහ Rerun කිරීම ---
st.caption(f"🔄 Automatically refreshing from database every {REFRESH_INTERVAL} seconds...")
time.sleep(REFRESH_INTERVAL)
st.rerun()  # මුළු පිටුවම නැවත ක්‍රියාත්මක කර ඩේටා අප්ඩේට් කිරීම