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

            print(f"Latest DB date: {latest_db_date}")
            print(f"Latest TSV date: {latest_tsv_date}")
            
            # Convert both to date objects for comparison
            if isinstance(latest_db_date, datetime):
                latest_db_date = latest_db_date.date()
            
            return latest_tsv_date > latest_db_date
        except Exception as e:
            print(f"Error checking for new data: {e}")
            return True  # If there's an error checking, assume we need to update

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

            # Process in batches for better performance
            batch_size = 1000
            total_rows = len(df)
            print(f"Starting to process {total_rows} rows...")

            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i + batch_size]
                print(f"Processing rows {i+1} to {min(i+batch_size, total_rows)} of {total_rows}...")
                
                # Process each row in the batch
                for _, row in batch.iterrows():
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
                
                # Commit the batch
                db.commit()
                print(f"Committed batch {i//batch_size + 1} of {(total_rows + batch_size - 1)//batch_size}")

            print("Successfully stored all Redfin state market data in DB.")
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