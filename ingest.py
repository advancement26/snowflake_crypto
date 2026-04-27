# Crypto data ingestion script
# TODO: Add your ingestion logic here
import os
import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_CONFIG = {
    "account":   os.getenv("SNOWFLAKE_ACCOUNT"),
    "user":      os.getenv("SNOWFLAKE_USER"),
    "password":  os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database":  os.getenv("SNOWFLAKE_DATABASE"),
    "schema":    os.getenv("SNOWFLAKE_SCHEMA"),
}

INGESTED_AT = datetime.now(timezone.utc).isoformat()

def get_connection():
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    conn.cursor().execute("USE DATABASE CRYPTO_DB")
    conn.cursor().execute("USE SCHEMA ANALYTICS")
    conn.cursor().execute("USE WAREHOUSE CRYPTO_WH")
    return conn

def load_to_snowflake(df, table_name):
    df.columns = [col.upper() for col in df.columns]
    conn = get_connection()
    success, nchunks, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name.upper(),
        auto_create_table=True,
        overwrite=True
    )
    conn.close()
    print(f"✅ Loaded {nrows} rows → {table_name.upper()}")

def ingest_coingecko_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1, "sparkline": False}
    df = pd.DataFrame(requests.get(url, params=params).json())
    df["ingested_at"] = INGESTED_AT
    load_to_snowflake(df, "raw_coingecko_markets")

def ingest_fear_greed():
    df = pd.DataFrame(requests.get("https://api.alternative.me/fng/?limit=30").json()["data"])
    df["ingested_at"] = INGESTED_AT
    load_to_snowflake(df, "raw_fear_greed_index")

def ingest_exchange_rates():
    data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
    df = pd.DataFrame([{"base_currency": "USD", "target_currency": c, "rate": data["rates"].get(c), "date": data["date"], "ingested_at": INGESTED_AT} for c in ["ZAR", "GBP", "EUR", "AUD"]])
    load_to_snowflake(df, "raw_exchange_rates")

def ingest_global_market():
    data = requests.get("https://api.coingecko.com/api/v3/global").json()["data"]
    df = pd.DataFrame([{"active_cryptocurrencies": data["active_cryptocurrencies"], "total_market_cap_usd": data["total_market_cap"]["usd"], "total_volume_usd": data["total_volume"]["usd"], "market_cap_percentage_btc": data["market_cap_percentage"]["btc"], "market_cap_percentage_eth": data["market_cap_percentage"]["eth"], "market_cap_change_percentage_24h": data["market_cap_change_percentage_24h_usd"], "ingested_at": INGESTED_AT}])
    load_to_snowflake(df, "raw_global_market")

if __name__ == "__main__":
    print("🚀 Starting ingestion pipeline...")
    ingest_coingecko_markets()
    ingest_fear_greed()
    ingest_exchange_rates()
    ingest_global_market()
    print("✅ All sources ingested successfully!")