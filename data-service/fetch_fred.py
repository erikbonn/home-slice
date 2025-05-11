import os
from fredapi import Fred
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from db import get_db, Location, MortgageData

# Load environment variables
load_dotenv()

class FredDataFetcher:
    def __init__(self):
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is not set")
        self.fred = Fred(api_key=api_key)

    def fetch_mortgage_rates(self, db: Session, days_back: int = 365) -> bool:
        """
        Fetch mortgage rate data from FRED and store it in the database.
        
        Args:
            db (Session): Database session
            days_back (int): Number of days of historical data to fetch
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Series IDs for different mortgage rates
        series_ids = {
            'MORTGAGE30US': '30-Year Fixed Rate Mortgage Average',
            'MORTGAGE15US': '15-Year Fixed Rate Mortgage Average',
            'MORTGAGE5US': '5/1-Year Adjustable Rate Mortgage Average'
        }
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            # Get or create US location
            location = db.query(Location).filter_by(
                type='country',
                state_code='US'
            ).first()
            
            if not location:
                location = Location(
                    type='country',
                    name='United States',
                    state_code='US'
                )
                db.add(location)
                db.commit()
            
            # Fetch and store data for each series
            for series_id, description in series_ids.items():
                try:
                    series = self.fred.get_series(
                        series_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Store each data point
                    for date, value in series.items():
                        mortgage_data = MortgageData(
                            location_id=location.id,
                            date=date.date(),
                            rate_30yr_fixed=float(value) if series_id == 'MORTGAGE30US' else None,
                            rate_15yr_fixed=float(value) if series_id == 'MORTGAGE15US' else None,
                            rate_5yr_arm=float(value) if series_id == 'MORTGAGE5US' else None
                        )
                        db.add(mortgage_data)
                    
                except Exception as e:
                    print(f"Error fetching {series_id}: {e}")
                    continue
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error in fetch_mortgage_rates: {e}")
            db.rollback()
            return False

def main():
    try:
        fetcher = FredDataFetcher()
        
        # Get database session
        db = next(get_db())
        
        try:
            success = fetcher.fetch_mortgage_rates(db)
            
            if success:
                print("Successfully fetched and stored mortgage rate data")
            else:
                print("Failed to fetch or store mortgage rate data")
                
        except Exception as e:
            print(f"Error in main: {e}")
        finally:
            db.close()
            
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 