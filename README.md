# Building an LLM-Powered Booking Analytics & QA System

## Project Overview

This project integrates **LLM (Large Language Model)** for hotel booking analytics and query handling using **Flask, SQLite, and Hugging Face transformers**.

## Features

* Dynamic Revenue Analytics
* RAG-based Answers for General Queries (Retrieval-Augmented Generation)
* Query Logging & History Tracking
* Health Check API (`/health`)

## Tech Stack

* Programming language: Python
* Backend: Flask
* Machine Learning and NLP: Hugging Face Transformer for LLM-based response and FIASS for fast neighbor search retrieval
* Database: SQLite
* Testing: Postman

## Setup Instructions

### 1) Clone the Repository:
```
git clone https://github.com/your-github-username/Hotel_Booking_System_LLM.git
cd Hotel_Booking_System_LLM
```

### 2) Install Dependencies:
```
pip install -r requirements.txt
```

### 3) Generate the data:
```
python notebooks/data_preprocessing.ipynb
```
OR
```
jupyter notebook notebooks/data_preprocessing.ipynb
```

### 4) Run the embedding process:
```
python scripts/embed_data.py
```
This will generate faiss_index.bin and booking_embeddings.npy, used for fast search.

## Running the API

After setting up the transformer model and CSV data, start the API:
```
python api/app.py
```
OR
```
python -m api.app
```

## Testing

After running the API, you will get the url on which the Flask app is running. Go to the URL (eg. http://127.0.0.1:5000) and you should see the message "Hotel Booking LLM API is running!"

To test the various endpoints, the easiest way is to use Postman. Create a new workspace and a new collection. Inside the collection, you can add the requests

Let's start with the simple /ask endpoint that uses LLM and RAG to generate responses based on the question.

Request type: POST

URL: http://127.0.0.1:5000/ask

Click on Body, then chose raw and JSON format

1. Query 1 (Booking related queries):

{
    
    "question": "What is the total revenue in September 2016"

}

{
    
    "answer": "The total revenue in September 2016 is $548,957.70."

}

2. Query 2 (Booking related queries):

{
    
    "question": "Which hotel had the highest revenue in September 2017?"

}

{
    
    "answer": "The hotel with the highest revenue in September 2017 is Resort Hotel with a revenue of $46,851.85."

}

3. Query 3 (Updating database with the precomputed analytics):

Request type: POST

URL: http://127.0.0.1:5000/analytics/update

{
    
    "message": "Analytics updated successfully"
    
}

4. Query 4 (Retrieving all analytics):

Request type: GET

URL: http://127.0.0.1:5000/analytics

{
    
    "average_booking_price": "$101.83",
    "average_lead_time": "104.01 days",
    "highest_revenue_month": "2016-08",
    "highest_revenue_value": "$711,706.32",
    "most_common_cancel_date": "2015-10-21",
    "most_common_country": "PRT",
    "most_common_month": "August",
    "most_popular_hotel": "City Hotel",
    "most_popular_room_type": "A",
    "top_cancellation_locations": "{'City Hotel': 33102, 'Resort Hotel': 11122}",
    "total_revenue": "$11,873,187.94"

}

5. Query 5 (Query from the precomputed analytics):

Request type: POST
URL: http://127.0.0.1:5000/analytics/query

{
    
    "question": "What is the average price of a hotel booking?"
    
}

{
    
    "average_booking_price": "$101.83"
    
}

{
    
    "question": "What is the most popular hotel?"
    
}

{
    
    "most_popular_hotel": "City Hotel"
    
}

6. Query History:

Request type: GET

URL: http://127.0.0.1:5000/query-history

[
  
  {
  
    "question": "what is the average price of a hotel booking?",
    "timestamp": "2025-03-22 14:13:46"
    
  },
  
  {
    
    "question": "what is the most popular hotel?",
    "timestamp": "2025-03-22 14:12:55"
    
  },

  {
        
    "question": "what is the average price of a hotel booking?",
    "timestamp": "2025-03-22 14:10:52"
  
  },

  {
    
    "question": "Which hotel had the highest revenue in September 2017?",
    "timestamp": "2025-03-22 14:07:39"
  
  },
    
  {
        
    "question": "What is the total revenue in September 2016",
    "timestamp": "2025-03-22 14:04:53"
  },

7. Health of the system:

Request type: GET

URL: http://127.0.0.1:5000/health

{
    
    "database": "connected",
    "status": "healthy"

}

## Testing the Database

1) Run the following command to access the database (e.g., hotel_data.db):
```
sqlite3 data/hotel_data.db
```
(Replace data/hotel_data.db with the correct path of the database)

2) Once inside SQLite, check if tables for query history and analytics exist:
```
.tables
```
The expected output should be:
```
analytics  query_history
```

3) To see if user queries are being stored, run:

```
SELECT * FROM query_history ORDER BY timestamp DESC LIMIT 10;
```
The output should show the queries with the timestamps.

4) To verify if analytics data is being stored:

```
SELECT * FROM analytics;
```
The output should show all the precomputed analytics.

##  Implementation Choices & Challenges

* Why SQLite? → Easy to maintain & lightweight for real-time analytics storage.
* Why Hugging Face LLM? → facebook/opt-350m provides a balance of speed & accuracy.
* Challenges Faced:
  - Handling real-time analytics updates efficiently.
  - Optimizing LLM responses for specific financial queries. Used deterministic response generation (`do_sample=False, temperature=1e-5`).
  - Implementing dynamic time period extraction in revenue queries. Used regex-based month/year extraction to filter dataset dynamically.

## Contributing & Future Enhancements

* Improve LLM fine-tuning for specific queries.
* Switch to PostgreSQL for larger datasets.
* Deploy API using Docker & cloud hosting.


### Author: 
Chakradhar
