import os
from fredapi import Fred
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FredDataFetcher:
    def __init__(self):
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable is not set")
        self.fred = Fred(api_key=api_key)

    def fetch_mortgage_rates(self, days_back=365):
        """
        Fetch mortgage rate data from FRED.
        
        Args:
            days_back (int): Number of days of historical data to fetch
            
        Returns:
            dict: Dictionary containing mortgage rate data
        """
        # Series IDs for different mortgage rates
        series_ids = {
            'MORTGAGE30US': '30-Year Fixed Rate Mortgage Average',
            'MORTGAGE15US': '15-Year Fixed Rate Mortgage Average',
            'MORTGAGE5US': '5/1-Year Adjustable Rate Mortgage Average'
        }
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        data = {}
        for series_id, description in series_ids.items():
            try:
                series = self.fred.get_series(
                    series_id,
                    start_date=start_date,
                    end_date=end_date
                )
                data[series_id] = {
                    'description': description,
                    'data': series.to_dict()
                }
            except Exception as e:
                print(f"Error fetching {series_id}: {e}")
                data[series_id] = None
        
        return data

def main():
    try:
        fetcher = FredDataFetcher()
        mortgage_data = fetcher.fetch_mortgage_rates()
        
        # Print summary of fetched data
        for series_id, data in mortgage_data.items():
            if data:
                print(f"\n{data['description']}:")
                print(f"Number of data points: {len(data['data'])}")
                print(f"Latest value: {list(data['data'].values())[-1]}")
            else:
                print(f"\nFailed to fetch {series_id}")
                
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main() 