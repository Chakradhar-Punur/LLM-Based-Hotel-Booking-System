import sqlite3
import pandas as pd

# ✅ Function to initialize analytics table in SQLite
def init_analytics():
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS analytics (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )''')
    
    conn.commit()
    conn.close()

init_analytics()

# ✅ Function to update analytics dynamically in the database
def update_analytics():
    df = pd.read_csv("/Users/Chakradhar/Hotel_Booking_System_LLM/data/cleaned_hotel_bookings.csv")

    analytics_data = {
        "total_revenue": f"${df['revenue'].sum():,.2f}",
        "average_lead_time": f"{df['lead_time'].mean():.2f} days",
        "most_common_cancel_date": df[df["is_canceled"] == 1]["reservation_status_date"].mode()[0] if not df[df["is_canceled"] == 1].empty else "N/A",
        "highest_revenue_month": df.groupby("year_month")["revenue"].sum().idxmax(),
        "highest_revenue_value": f"${df.groupby('year_month')['revenue'].sum().max():,.2f}",
        "most_popular_hotel": df["hotel"].mode()[0],
        "most_popular_room_type": df["reserved_room_type"].mode()[0],
        "most_common_country": df["country"].mode()[0],
        "most_common_month": df["arrival_date_month"].mode()[0],
        "top_cancellation_locations": str(df[df["is_canceled"] == 1]["hotel"].value_counts().to_dict()),
        "average_booking_price": f"${df['adr'].mean():.2f}"
    }

    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()

    print("Updating analytics...")  # ✅ Debugging print
    for key, value in analytics_data.items():
        print(f"Inserting: {key} -> {value}")  # ✅ Debugging print
        cursor.execute("INSERT OR REPLACE INTO analytics (key, value) VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()
    print("Analytics update completed.")  # ✅ Debugging print

# ✅ Function to retrieve analytics from the database
def get_analytics():
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM analytics")
    analytics_data = {row[0]: row[1] for row in cursor.fetchall()}

    print("Fetched analytics:", analytics_data)  # ✅ Debugging print

    conn.close()
    return analytics_data if analytics_data else {"error": "No analytics data available"}
