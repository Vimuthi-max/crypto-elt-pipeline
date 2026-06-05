import streamlit as st
import psycopg2
import pandas as pd
import time  
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Page Configuration
st.set_page_config(page_title="Advanced Crypto Analytics Dashboard", layout="wide", page_icon="📈")

# Dashboard Header
st.title("🚀 Real-Time Crypto Data Pipeline Dashboard")
st.info("💡 **Pipeline Status:** Live-sync active. Fetching structural micro-batches from Neon Cloud Warehouse.")

# Define Data Fetching Function
def load_analytics_data():
    conn = psycopg2.connect(DB_URL)
    query = """
    SELECT coin_name, price_usd, change_24h, extracted_date, extracted_time, inserted_at 
    FROM crypto_analytics 
    ORDER BY inserted_at DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    if not DB_URL:
        st.error("Engine Error: DB_URL environment variable is missing. Check your .env file!")
    else:
        df = load_analytics_data()

        if not df.empty:
            
            # --- INTERACTIVE COIN TABS (5 COINS) ---
            st.subheader("📊 Asset Intelligence Hub")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🪙 BITCOIN (BTC)", 
                "🔷 ETHEREUM (ETH)", 
                "☀️ SOLANA (SOL)", 
                "🐶 DOGECOIN (DOGE)", 
                "₳ CARDANO (ADA)"
            ])
            
            coins = ["BITCOIN", "ETHEREUM", "SOLANA", "DOGE COIN", "CARDANO"]
            tabs = [tab1, tab2, tab3, tab4, tab5]
            
            for coin, tab in zip(coins, tabs):
                with tab:
                    coin_df = df[df['coin_name'] == coin]
                    if not coin_df.empty:
                        latest_record = coin_df.iloc[0]
                        current_price = latest_record['price_usd']
                        change_24h = latest_record['change_24h']
                        max_price = coin_df['price_usd'].max()
                        min_price = coin_df['price_usd'].min()
                        
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric(label="Current Spot Price", value=f"${current_price:,.4f}" if current_price < 1 else f"${current_price:,.2f}", delta=f"{change_24h}%")
                        m_col2.metric(label="24h High (Max)", value=f"${max_price:,.4f}" if max_price < 1 else f"${max_price:,.2f}")
                        m_col3.metric(label="24h Low (Min)", value=f"${min_price:,.4f}" if min_price < 1 else f"${min_price:,.2f}")
                        
                        st.caption(f"📈 {coin} Specific Price Micro-Trend")
                        st.line_chart(coin_df.set_index('inserted_at')['price_usd'])
                    else:
                        st.warning(f"No records found for {coin}. Please run pipeline.py a few times to log data.")

            st.markdown("---")

            # --- COMBINED MARKET HISTORICAL TREND ---
            st.subheader("📉 Cross-Asset Comparison Trend")
            chart_df = df.pivot_table(index='inserted_at', columns='coin_name', values='price_usd').sort_index()
            st.line_chart(chart_df)

            st.markdown("---")

            # --- PRODUCTION ARCHIVE LOGS ---
            st.subheader("📋 Production Analytical Warehouse Log (`crypto_analytics`)")
            st.dataframe(df, width="stretch")
            
        else:
            st.warning("No data found in the analytics layer. Please trigger the data ingestion pipeline.")

except Exception as e:
    st.error(f"Engine Failure: Unable to stream analytical components: {e}")

# --- Auto-Refresh Orchestration ---
time.sleep(10)
st.rerun()