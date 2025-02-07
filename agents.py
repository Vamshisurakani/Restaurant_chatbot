import openai
from crewai import Agent
from database import reservations_collection
from availability import check_availability
from openai import OpenAI

# ✅ Initialize OpenAI Client (Replace with your actual API key)
client = OpenAI(
    api_key="your_api_key"
)  # Use your valid API key


class RestaurantAssistant:
    def process_message(self, message):
        print(f"Processing message: {message}")  # Debugging
        return self.ask_gpt(message)

    def ask_gpt(self, prompt):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a restaurant assistant helping users book tables.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")  # Debugging
            return "Sorry, I encountered an error while processing your request."

    def handle_booking(self, date, time, guests, name, contact):
        print(
            f"Handling booking for {name} on {date} at {time} for {guests} guests."
        )  # Debugging
        if check_availability(
            date, time, guests
        ):  # Ensure check_availability() is working
            booking_data = {
                "date": date,
                "time": time,
                "guests": guests,
                "name": name,
                "contact": contact,
            }
            reservations_collection.insert_one(
                booking_data
            )  # Ensure MongoDB is connected
            return (
                f"Booking confirmed for {name} on {date} at {time} for {guests} guests."
            )
        else:
            return "Sorry, no tables are available at that time."

    def handle_cancellation(self, name, date, time):
        """Handles reservation cancellations."""
        result = reservations_collection.delete_one(
            {"name": name, "date": date, "time": time}
        )
        return (
            "✅ Reservation canceled."
            if result.deleted_count > 0
            else "❌ No reservation found."
        )

    def modify_reservation(self, name, old_date, old_time, new_date, new_time, guests):
        """Handles reservation modifications."""
        existing_res = reservations_collection.find_one(
            {"name": name, "date": old_date, "time": old_time}
        )
        if existing_res:
            if check_availability(new_date, new_time, guests):
                reservations_collection.update_one(
                    {"name": name, "date": old_date, "time": old_time},
                    {"$set": {"date": new_date, "time": new_time, "guests": guests}},
                )
                return f"✅ Reservation updated to {new_date} at {new_time}."
            return "❌ No availability for the new time."
        return "❌ No existing reservation found."


assistant = RestaurantAssistant()
