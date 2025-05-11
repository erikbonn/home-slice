import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from db import get_db, Location, HousingData
import gzip
import io

# Load environment variables
load_dotenv()

REDFIN_STATE_CSV_URL = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/state_market_tracker.tsv000.gz"

class RedfinDataFetcher:
    def __init__(self):
        self.csv_url = REDFIN_STATE_CSV_URL

    def is_new_data_available(self, db: Session) -> bool:
        """
        Check if new data is available by comparing the latest date in the database with the latest date in the downloaded TSV.
        Args:
            db (Session): SQLAlchemy DB session
        Returns:
            bool: True if new data is available, False otherwise
        """
        try:
            # Get the latest date from the database
            latest_db_date = db.query(HousingData.date).order_by(HousingData.date.desc()).first()
            if not latest_db_date:
                return True  # No data in DB, so new data is available
            latest_db_date = latest_db_date[0]

            # Download and parse the TSV to get the latest date
            resp = requests.get(self.csv_url)
            resp.raise_for_status()
            with gzip.open(io.BytesIO(resp.content), 'rt') as f:
                df = pd.read_csv(f, sep='\t')
            latest_tsv_date = pd.to_datetime(df['PERIOD_END']).max().date()

            return latest_tsv_date > latest_db_date
        except Exception as e:
            print(f"Error checking for new data: {e}")
            return False

    def fetch_and_store_state_data(self, db: Session, state_filter=None) -> bool:
        """
        Download the Redfin state-level housing market TSV, parse, and store in DB.
        Args:
            db (Session): SQLAlchemy DB session
            state_filter (list[str] or None): If provided, only process these state codes
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_new_data_available(db):
            print("No new data available. Skipping ingestion.")
            return True

        try:
            print(f"Downloading Redfin state market data from {self.csv_url} ...")
            resp = requests.get(self.csv_url)
            resp.raise_for_status()
            print("Download complete. Decompressing...")
            with gzip.open(io.BytesIO(resp.content), 'rt') as f:
                df = pd.read_csv(f, sep='\t')
            print(f"Loaded {len(df)} rows from Redfin TSV.")

            # Optionally filter by state
            if state_filter:
                df = df[df['STATE_CODE'].isin(state_filter)]
                print(f"Filtered to {len(df)} rows for states: {state_filter}")

            # Iterate and store
            for _, row in df.iterrows():
                # Get or create location
                location = db.query(Location).filter_by(
                    type='state',
                    state_code=row['STATE_CODE']
                ).first()
                if not location:
                    location = Location(
                        type='state',
                        name=row['STATE'],
                        state_code=row['STATE_CODE']
                    )
                    db.add(location)
                    db.commit()
                # Store housing data
                housing_data = HousingData(
                    location_id=location.id,
                    date=pd.to_datetime(row['PERIOD_END']).date(),
                    median_price=float(row['MEDIAN_SALE_PRICE']) if not pd.isna(row['MEDIAN_SALE_PRICE']) else None,
                    median_price_sqft=float(row['MEDIAN_PPSF']) if not pd.isna(row['MEDIAN_PPSF']) else None,
                    median_dom=int(row['MEDIAN_DOM']) if not pd.isna(row['MEDIAN_DOM']) else None,
                    inventory=int(row['INVENTORY']) if not pd.isna(row['INVENTORY']) else None,
                    new_listings=int(row['NEW_LISTINGS']) if not pd.isna(row['NEW_LISTINGS']) else None,
                    price_reduced=int(row['PRICE_DROPS']) if not pd.isna(row['PRICE_DROPS']) else None
                )
                db.add(housing_data)
            db.commit()
            print("Successfully stored Redfin state market data in DB.")
            return True
        except Exception as e:
            print(f"Error in fetch_and_store_state_data: {e}")
            db.rollback()
            return False

def main():
    fetcher = RedfinDataFetcher()
    db = next(get_db())
    try:
        # You can filter for specific states, e.g. ['CA', 'TX']
        success = fetcher.fetch_and_store_state_data(db, state_filter=None)
        if success:
            print("Redfin state data fetch and store complete.")
        else:
            print("Redfin state data fetch/store failed.")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 