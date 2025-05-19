from db import get_db, Location, HousingData, MortgageData
from sqlalchemy import func
import pandas as pd

def verify_data():
    db = next(get_db())
    try:
        # Check locations
        print("\n=== Locations ===")
        locations = db.query(Location).all()
        print(f"Total locations: {len(locations)}")
        print("\nSample locations:")
        for loc in locations[:5]:  # Show first 5 locations
            print(f"- {loc.name} ({loc.state_code})")

        # Check housing data
        print("\n=== Housing Data ===")
        total_records = db.query(func.count(HousingData.id)).scalar()
        print(f"Total housing data records: {total_records}")

        # Get date range
        min_date = db.query(func.min(HousingData.date)).scalar()
        max_date = db.query(func.max(HousingData.date)).scalar()
        print(f"Date range: {min_date} to {max_date}")

        # Get sample data for a specific state
        print("\n=== Sample Data for California ===")
        ca_location = db.query(Location).filter_by(state_code='CA').first()
        if ca_location:
            ca_data = db.query(HousingData).filter_by(location_id=ca_location.id)\
                .order_by(HousingData.date.desc())\
                .limit(5).all()
            
            print("\nLatest 5 records for California:")
            for record in ca_data:
                print(f"Date: {record.date}")
                print(f"  Median Price: ${record.median_price:,.2f}" if record.median_price else "  Median Price: N/A")
                print(f"  Inventory: {record.inventory:,}" if record.inventory else "  Inventory: N/A")
                print(f"  New Listings: {record.new_listings:,}" if record.new_listings else "  New Listings: N/A")
                print(f"  Price Reduced: {record.price_reduced:,}" if record.price_reduced else "  Price Reduced: N/A")
                print()

        # Check mortgage rate data
        print("\n=== Mortgage Rate Data ===")
        us_location = db.query(Location).filter_by(state_code='US').first()
        if us_location:
            mortgage_data = db.query(MortgageData).filter_by(location_id=us_location.id)\
                .order_by(MortgageData.date.desc())\
                .limit(5).all()
            
            print("\nLatest 5 mortgage rate records:")
            for record in mortgage_data:
                print(f"Date: {record.date}")
                print(f"  30-Year Fixed: {record.rate_30yr_fixed:.2f}%" if record.rate_30yr_fixed else "  30-Year Fixed: N/A")
                print(f"  15-Year Fixed: {record.rate_15yr_fixed:.2f}%" if record.rate_15yr_fixed else "  15-Year Fixed: N/A")
                print(f"  5/1 ARM: {record.rate_5yr_arm:.2f}%" if record.rate_5yr_arm else "  5/1 ARM: N/A")
                print()

            # Get date range for mortgage data
            min_mortgage_date = db.query(func.min(MortgageData.date)).scalar()
            max_mortgage_date = db.query(func.max(MortgageData.date)).scalar()
            print(f"Mortgage data date range: {min_mortgage_date} to {max_mortgage_date}")

        # Check for any null values
        print("\n=== Data Quality Check ===")
        null_counts = {
            'median_price': db.query(func.count(HousingData.id)).filter(HousingData.median_price.is_(None)).scalar(),
            'median_price_sqft': db.query(func.count(HousingData.id)).filter(HousingData.median_price_sqft.is_(None)).scalar(),
            'median_dom': db.query(func.count(HousingData.id)).filter(HousingData.median_dom.is_(None)).scalar(),
            'inventory': db.query(func.count(HousingData.id)).filter(HousingData.inventory.is_(None)).scalar(),
            'new_listings': db.query(func.count(HousingData.id)).filter(HousingData.new_listings.is_(None)).scalar(),
            'price_reduced': db.query(func.count(HousingData.id)).filter(HousingData.price_reduced.is_(None)).scalar()
        }
        
        print("Null value counts:")
        for field, count in null_counts.items():
            print(f"- {field}: {count:,} null values")

    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_data() 