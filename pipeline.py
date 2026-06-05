import requests
import json
from datetime import datetime
import psycopg2

# Database විස්තර
DB_HOST = "localhost"
DB_NAME = "crypto_db"
DB_USER = "postgres"
DB_PASS = "16455"  
DB_PORT = "5432"

def fetch_crypto_data():
    URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
    try:
        print("🔄 [1/3] Fetching live data from CoinGecko API...")
        response = requests.get(URL)
        if response.status_code == 200:
            raw_data = response.json()
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            flattened_data = []
            for coin_id, details in raw_data.items():
                flattened_data.append({
                    "coin_name": coin_id.upper(),
                    "price_usd": details["usd"],
                    "change_24h": round(details["usd_24h_change"], 4),
                    "extracted_at": current_timestamp
                })
            return flattened_data
    except Exception as e:
        print(f"❌ Extraction Error: {e}")
    return None

def run_complete_pipeline(data_list):
    if not data_list:
        print("⚠️ No data to process.")
        return

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
        cursor = connection.cursor()

        # --- STEP 1: LOAD TO STAGING ---
        print("📥 [2/3] Loading raw data into 'crypto_staging'...")
        insert_staging_query = """
        INSERT INTO crypto_staging (coin_name, price_usd, change_24h, extracted_at)
        VALUES (%s, %s, %s, %s);
        """
        for record in data_list:
            cursor.execute(insert_staging_query, (record["coin_name"], record["price_usd"], record["change_24h"], record["extracted_at"]))

        # --- STEP 2: TRANSFORM & LOAD TO PRODUCTION ---
        print("🔄 [3/3] Transforming and moving data to 'crypto_analytics'...")
        transform_query = """
        INSERT INTO crypto_analytics (coin_name, price_usd, change_24h, extracted_date, extracted_time)
        SELECT coin_name, price_usd, change_24h, extracted_at::DATE, extracted_at::TIME
        FROM crypto_staging;
        """
        cursor.execute(transform_query)

        # --- STEP 3: TRUNCATE STAGING (ඩේටා Clean කිරීම) ---
        print("🧹 Cleaning up Staging Table for the next run...")
        cursor.execute("TRUNCATE TABLE crypto_staging;")

        # හැමදේම සාර්ථක නම් Commit කිරීම
        connection.commit()
        print("\n🏆 [SUCCESS] End-to-End ELT Pipeline Completed Successfully!")

    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

if __name__ == "__main__":
    live_data = fetch_crypto_data()
    run_complete_pipeline(live_data)