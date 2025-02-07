import streamlit as st
from agents import assistant
from database import reservations_collection, settings_collection

# ---- Page Configuration ----
st.set_page_config(page_title="AI Restaurant Assistant", layout="wide")

# ---- Authentication for Admin ----
def authenticate_admin():
    admin_username = "admin"
    admin_password = "password"  # Change this for security
    username = st.text_input("Admin Username", type="default")
    password = st.text_input("Admin Password", type="password")
    return username == admin_username and password == admin_password

# ---- Load Settings from Database ----
def get_settings():
    settings = settings_collection.find_one({"type": "config"})
    if not settings:
        settings = {"max_reservations_per_slot": 5, "max_guests_per_table": 4}
        settings_collection.insert_one(settings)
    return settings

# ---- Sidebar Navigation ----
st.sidebar.title("🍽️ AI Restaurant Assistant")
page = st.sidebar.selectbox("Navigate to:", ["Customer Chatbot", "Admin Dashboard"])

# ---- Customer Chatbot ----
if page == "Customer Chatbot":
    st.title("🤖 AI-Powered Restaurant Chatbot")
    st.write("Welcome! You can book, modify, or cancel your reservations easily.")

    user_input = st.text_input("💬 How can I assist you today? (e.g., 'I want to book a table')")

    if user_input:
        if "book" in user_input.lower():
            st.subheader("📅 Let's book a table!")
            name = st.text_input("👤 Enter your name:")
            date = st.date_input("📆 Select a date:")
            time = st.time_input("⏰ Select a time:")
            guests = st.number_input("👥 Number of guests:", min_value=1, max_value=20, value=2)
            contact = st.text_input("📞 Enter your contact info:")

            if st.button("✅ Confirm Booking"):
                response = assistant.handle_booking(str(date), str(time), guests, name, contact)
                st.success(response)

        elif "cancel" in user_input.lower():
            st.subheader("🚫 Cancel Your Reservation")
            name = st.text_input("👤 Enter your name:")
            date = st.date_input("📆 Enter your reservation date:")
            time = st.time_input("⏰ Enter your reservation time:")

            if st.button("❌ Cancel Reservation"):
                response = assistant.handle_cancellation(name, str(date), str(time))
                st.warning(response)

        elif "modify" in user_input.lower() or "change" in user_input.lower():
            st.subheader("🔄 Modify Your Reservation")
            name = st.text_input("👤 Enter your name:")
            old_date = st.date_input("📆 Current reservation date:")
            old_time = st.time_input("⏰ Current reservation time:")
            new_date = st.date_input("📆 New reservation date:")
            new_time = st.time_input("⏰ New reservation time:")
            guests = st.number_input("👥 Number of guests:", min_value=1, max_value=20, value=2)

            if st.button("🔄 Update Reservation"):
                response = assistant.modify_reservation(name, str(old_date), str(old_time), str(new_date), str(new_time), guests)
                st.info(response)

    st.write("💬 Type 'book', 'cancel', or 'modify' to interact with the chatbot!")

# ---- Admin Dashboard ----
elif page == "Admin Dashboard":
    st.title("🔧 Restaurant Admin Dashboard")

    if authenticate_admin():
        st.success("✅ Successfully Logged In as Admin!")
        
        reservations = list(reservations_collection.find())
        settings = get_settings()

        if reservations:
            st.subheader("📅 Upcoming Reservations")
            for res in reservations:
                date = res.get("date", "N/A")
                time = res.get("time", "N/A")
                name = res.get("name", "Unknown")
                guests = res.get("guests", "N/A")
                res_id = str(res["_id"]) if "_id" in res else "unknown"

                st.write(f"📌 {date} {time} - {name} ({guests} guests)")

                # Modify Reservation Timing
                new_date = st.date_input(f"📆 Change Date ({name})", value=date, key=f"date_{res_id}")
                new_time = st.time_input(f"⏰ Change Time ({name})", value=time, key=f"time_{res_id}")

                if st.button(f"🔄 Modify {name}'s Booking", key=f"modify_{res_id}"):
                    reservations_collection.update_one(
                        {"_id": res["_id"]},
                        {"$set": {"date": str(new_date), "time": str(new_time)}}
                    )
                    st.success(f"✅ Updated {name}'s booking!")

                # Cancel Reservation
                if "_id" in res and st.button(f"❌ Cancel {name}'s Booking", key=f"cancel_{res_id}"):
                    reservations_collection.delete_one({"_id": res["_id"]})
                    st.warning(f"🚫 Reservation for {name} has been canceled!")

        # ---- Update Restaurant Settings ----
        st.subheader("⚙️ Manage Restaurant Settings")
        max_reservations_per_slot = st.number_input(
            "🔢 Max Reservations per Time Slot", min_value=1, max_value=20,
            value=settings["max_reservations_per_slot"], key="max_reservations"
        )
        max_guests_per_table = st.number_input(
            "👥 Max Guests per Table", min_value=1, max_value=10,
            value=settings["max_guests_per_table"], key="max_guests"
        )

        if st.button("✅ Save Settings", key="update_settings"):
            settings_collection.update_one(
                {"type": "config"},
                {"$set": {"max_reservations_per_slot": max_reservations_per_slot, "max_guests_per_table": max_guests_per_table}},
                upsert=True
            )
            st.success("✅ Settings updated!")

    else:
        st.error("❌ Access Denied! Only admins can view this page.")
