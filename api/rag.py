from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from scripts.retrieve import retrieve_similar_records as retrieve
import re

model_name = "facebook/opt-350m"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

qa_model = pipeline("text-generation", model=model, tokenizer=tokenizer, device="cpu")

def extract_time_period(question):
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    
    month_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
    year_pattern = r"\b(20\d{2})\b"

    month_match = re.search(month_pattern, question, re.IGNORECASE)
    year_match = re.search(year_pattern, question)

    month = month_map[month_match.group(0).lower()] if month_match else None
    year = year_match.group(0) if year_match else None

    return month, year

def generate_answer(question):
    """Retrieves relevant data and generates an AI-generated answer"""
    retrieved_data = retrieve(question, top_k=3)
    
    print("Retrieved Data Columns:", retrieved_data.columns)
    print("Retrieved Data Sample:\n", retrieved_data.head())
    
    if retrieved_data.empty:
        return "No relevant data found."
    
    if "text" not in retrieved_data.columns:
        return "Error: 'text' column is missing in retrieved data."

    # Handling Non-Revenue Queries
    if "room type" in question.lower():
        most_common_room = retrieved_data["reserved_room_type"].mode()[0]
        return f"The most commonly booked room type is {most_common_room}."

    if "most guests" in question.lower() or "top country" in question.lower():
        top_guest_country = retrieved_data["country"].mode()[0]
        return f"The country with the most guests is {top_guest_country}."

    if "repeat customers" in question.lower():
        repeat_guests_count = retrieved_data["is_repeated_guest"].sum()
        return f"There are {repeat_guests_count} repeat guests in the dataset."

    # Handling Revenue Queries
    if "revenue" in question.lower():
        if "revenue" not in retrieved_data.columns or "hotel" not in retrieved_data.columns or "year_month" not in retrieved_data.columns:
            return "Error: Required columns ('revenue', 'hotel', 'year_month') are missing in retrieved data."

        # Extract time period from question
        month, year = extract_time_period(question)
        
        month_map_reverse = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        
        if month and year:
            retrieved_data = retrieved_data[retrieved_data["year_month"] == f"{year}-{month}"]
        elif year:
            retrieved_data = retrieved_data[retrieved_data["year_month"].str.startswith(year)]
        
        if retrieved_data.empty:
            return f"No revenue data found for {month_map_reverse.get(month, month)} {year if year else ''}."
        
        if "total revenue" in question.lower():
            total_revenue = retrieved_data["revenue"].sum()
            return f"The total revenue in {month_map_reverse.get(month, month)} {year} is ${total_revenue:,.2f}."

        # Group by hotel and sum revenue
        hotel_revenue = retrieved_data.groupby("hotel")["revenue"].sum()

        # Find the hotel with the highest revenue
        highest_revenue_hotel = hotel_revenue.idxmax()
        highest_revenue = hotel_revenue.max()

        return f"The hotel with the highest revenue in {month_map_reverse.get(month, month)} {year if year else 'the given period'} is {highest_revenue_hotel} with a revenue of ${highest_revenue:,.2f}."

    # Default RAG-based Response for Unmatched Queries
    context = " ".join(retrieved_data["text"].tolist())

    prompt = f"""
    Context: {context}

    Question: {question}

    Provide a precise and factual response.
    """

    response = qa_model(
        prompt,
        max_length=100,
        do_sample=False,
        temperature=1e-5,
        truncation=True,
        return_full_text=False
    )
    
    return response[0]['generated_text'].strip()
