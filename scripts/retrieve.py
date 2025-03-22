import re
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

df = pd.read_csv("/Users/Chakradhar/Hotel_Booking_System_LLM/data/cleaned_hotel_bookings.csv")

if "text" not in df.columns:
    df["text"] = df.apply(lambda row: f"Hotel: {row['hotel']}, Date: {row['year_month']}, Revenue: {row['adr']}", axis=1)

index = faiss.read_index("/Users/Chakradhar/Hotel_Booking_System_LLM/data/faiss_index.bin")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_month_year(query):
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    
    match = re.search(r"(\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b)\s(\d{4})", query, re.IGNORECASE)
    
    if match:
        month = months[match.group(1).lower()]
        year = match.group(2)
        return f"{year}-{month}"
    
    return None

def retrieve_similar_records(query, top_k=20):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    results = df.iloc[indices[0]]
    
    year_month = extract_month_year(query)
    if year_month:
        filtered_results = results[results["year_month"] == year_month]
        if filtered_results.empty:
            filtered_results = df[df["year_month"] == year_month]
        return filtered_results
    
    return results
