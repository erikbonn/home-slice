import os
from dotenv import load_dotenv
import sys

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Load environment variables and print them for debugging
env_path = os.path.join(os.getcwd(), '.env')
print(f"Looking for .env file at: {env_path}")
print(f".env file exists: {os.path.exists(env_path)}")

load_dotenv(env_path)
print("\nEnvironment variables:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"PUBLIC_DATA_SERVICE_DB_CONNECTION_STRING: {os.getenv('PUBLIC_DATA_SERVICE_DB_CONNECTION_STRING')}")

# Only try to import and test connection if we have the environment variables
if os.getenv('DATABASE_URL') or os.getenv('PUBLIC_DATA_SERVICE_DB_CONNECTION_STRING'):
    from db.connection import engine

    def test_connection():
        try:
            # Try to connect to the database
            with engine.connect() as connection:
                print("✅ Successfully connected to the database!")
                return True
        except Exception as e:
            print("❌ Failed to connect to the database:")
            print(f"Error: {str(e)}")
            return False

    if __name__ == "__main__":
        test_connection()
else:
    print("\n❌ No database connection variables found!")
    sys.exit(1) 