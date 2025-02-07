import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "restaurant_db"

try:
    # Create a persistent client
    client = MongoClient(DB_URI)
    db = client[DB_NAME]

    # Collections
    reservations_collection = db["reservations"]
    settings_collection = db["settings"]  # Add this if managing restaurant settings

    # Test the connection
    db.command("ping")
    print("✅ Successfully connected to MongoDB!")

except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
