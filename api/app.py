from flask import Flask, request, jsonify
from api.rag import generate_answer
from api.analytics import get_analytics, update_analytics
import sqlite3

app = Flask(__name__)

# Initialize Database
def init_db():
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()

    # Table for storing query history
    cursor.execute('''CREATE TABLE IF NOT EXISTS query_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')

    # Table for real-time analytics storage
    cursor.execute('''CREATE TABLE IF NOT EXISTS analytics (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )''')

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Hotel Booking LLM API is running!"

@app.route("/ask", methods=["POST"])
def ask():
    """Handles booking-related questions and logs query history"""
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Store query in history
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO query_history (question) VALUES (?)", (question,))
    conn.commit()
    conn.close()
    
    answer = generate_answer(question)
    
    return jsonify({"answer": answer})

@app.route("/analytics/query", methods=["POST"])
def analytics_query():
    """Returns specific precomputed analytics based on the user's query and logs the query"""
    data = request.json
    question = data.get("question", "").lower()

    # Store query in history
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO query_history (question) VALUES (?)", (question,))
    conn.commit()
    conn.close()

    analytics_data = get_analytics()

    # Mapping keywords to analytics data
    keyword_mapping = {
        "total revenue": "total_revenue",
        "average lead time": "average_lead_time",
        "most common cancellation date": "most_common_cancel_date",
        "highest revenue month": "highest_revenue_month",
        "highest revenue value": "highest_revenue_value",
        "most popular hotel": "most_popular_hotel",
        "most popular room type": "most_popular_room_type",
        "most common country": "most_common_country",
        "most common month": "most_common_month",
        "highest booking cancellations": "top_cancellation_locations",
        "average price of a hotel booking": "average_booking_price"
    }

    # Finding the best match for the question
    for keyword, key in keyword_mapping.items():
        if keyword in question:
            return jsonify({key: analytics_data.get(key, "Data not available")})

    return jsonify({"error": "Query not recognized. Please try a different question."}), 400

@app.route("/analytics", methods=["GET"])
def analytics():
    """Returns real-time precomputed analytics"""
    return jsonify(get_analytics())

@app.route("/analytics/update", methods=["POST"])
def update_analytics_route():
    """Manually triggers an update for analytics data"""
    update_analytics()
    return jsonify({"message": "Analytics updated successfully"})

@app.route("/query-history", methods=["GET"])
def query_history():
    """Retrieves the history of queries asked"""
    conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, timestamp FROM query_history ORDER BY timestamp DESC")
    history = [{"question": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(history)

@app.route("/health", methods=["GET"])
def health_check():
    """Checks system health, including database connectivity"""
    try:
        conn = sqlite3.connect("/Users/Chakradhar/Hotel_Booking_System_LLM/data/hotel_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
