import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Meta access token and Ad Account ID
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("AD_ACCOUNT_ID")

# PostgreSQL credentials
DB_HOST = os.getenv("DATABASE_HOSTNAME")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")
DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")

# Meta Graph API base
GRAPH_API_URL = "https://graph.facebook.com/v17.0"

# Table name
TABLE_NAME = "meta_ads_campaign_insights"

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Ensure the table exists
def ensure_table_exists():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            campaign_id VARCHAR(50),
            campaign_name TEXT,
            spend NUMERIC(12,2),
            impressions BIGINT,
            clicks BIGINT,
            account_id VARCHAR(50),
            date_start DATE,
            date_stop DATE,
            date_added TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Table '{TABLE_NAME}' is ready.")

# Get campaigns from the ad account
def get_campaigns():
    url = f"{GRAPH_API_URL}/{AD_ACCOUNT_ID}/campaigns"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "fields": "id,name"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])

# Get insights for a campaign
def get_campaign_insights(campaign_id):
    url = f"{GRAPH_API_URL}/{campaign_id}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "fields": "campaign_id,campaign_name,date_start,date_stop,spend,impressions,clicks",
        "date_preset": "maximum"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    insights = data.get("data")
    if insights and len(insights) > 0:
        return insights[0]
    return None

# Insert campaigns into Postgres
def insert_campaigns(campaigns):
    if not campaigns:
        print("No campaigns to insert.")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    sql = f"""
    INSERT INTO {TABLE_NAME} (
        campaign_id, campaign_name, spend, impressions, clicks, account_id, date_start, date_stop, date_added
    ) VALUES %s
    """

    values = []
    now = datetime.utcnow().isoformat()
    for c in campaigns:
        values.append((
            c["campaign_id"],
            c["campaign_name"],
            c.get("spend"),
            c.get("impressions"),
            c.get("clicks"),
            f"Run Using Python - {AD_ACCOUNT_ID.strip('act_')}",
            c.get("date_start"),
            c.get("date_stop"),
            now
        ))

    execute_values(cur, sql, values)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(values)} campaigns.")

def main():
    # Ensure the table exists first
    ensure_table_exists()

    print("Fetching campaigns...")
    campaigns = get_campaigns()
    print(f"Found {len(campaigns)} campaigns.")

    cleaned_campaigns = []

    for campaign in campaigns:
        campaign_id = campaign["id"]
        campaign_name = campaign.get("name")
        insights = get_campaign_insights(campaign_id)

        # Skip if date_start is null or insights are empty
        if not insights or insights.get("date_start") is None:
            print(f"Skipping campaign {campaign_name} ({campaign_id}) due to null insights.")
            continue

        cleaned_campaigns.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "spend": insights.get("spend"),
            "impressions": insights.get("impressions"),
            "clicks": insights.get("clicks"),
            "date_start": insights.get("date_start"),
            "date_stop": insights.get("date_stop")
        })

    # Insert into Postgres
    insert_campaigns(cleaned_campaigns)

if __name__ == "__main__":
    main()
