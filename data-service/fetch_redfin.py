import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedfinDataFetcher:
    def __init__(self):
        self.base_url = "https://www.redfin.com/stingray/api/gis-csv"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_state_data(self, state_code):
        """
        Fetch housing market data for a specific state.
        
        Args:
            state_code (str): Two-letter state code (e.g., 'CA' for California)
            
        Returns:
            pd.DataFrame: DataFrame containing the housing market data
        """
        params = {
            "al": 1,
            "market": "realestate",
            "num_homes": 500,
            "ord": "redfin-recommended-asc",
            "page_number": 1,
            "region_id": state_code,
            "region_type": 2,
            "sf": 1,
            "status": 1,
            "uipt": 1,
            "v": 8
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            # Parse CSV data
            df = pd.read_csv(pd.StringIO(response.text))
            
            # Add timestamp
            df['fetched_at'] = datetime.now()
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for state {state_code}: {e}")
            return None

def main():
    fetcher = RedfinDataFetcher()
    
    # Example: Fetch data for California
    ca_data = fetcher.fetch_state_data('CA')
    
    if ca_data is not None:
        print(f"Successfully fetched {len(ca_data)} records for California")
        # TODO: Save to database
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main() 