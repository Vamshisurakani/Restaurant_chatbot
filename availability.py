from database import reservations_collection, settings_collection

def check_availability(date, time, guests):
    """Check if there are available tables for the given date, time, and guests count."""

    # Fetch restaurant settings
    settings = settings_collection.find_one({"_id": "restaurant_settings"})  
    if not settings:
        print("⚠️ Warning: No settings found in the database. Using defaults.")
        settings = {"total_tables": 10, "max_guests_per_table": 4}  # Fallback defaults
    
    total_tables = settings.get("total_tables", 10)
    max_guests_per_table = settings.get("max_guests_per_table", 4)

    # Check if guests exceed max allowed per table
    if guests > max_guests_per_table:
        print(f"❌ Booking failed: Maximum guests per table is {max_guests_per_table}.")
        return False  

    # Count booked slots
    booked_slots = reservations_collection.count_documents({"date": date, "time": time})

    # Check if tables are available
    if booked_slots >= total_tables:
        print("❌ Booking failed: No tables available.")
        return False  

    return True  
