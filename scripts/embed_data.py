import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

df = pd.read_csv("/Users/Chakradhar/Hotel_Booking_System_LLM/data/cleaned_hotel_bookings.csv")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
df["text"] = df.apply(lambda row: f"Hotel: {row['hotel']}, Date: {row['reservation_status_date']}, Revenue: {row['adr']}", axis=1)
embeddings = embedding_model.encode(df["text"].tolist(), convert_to_numpy=True)

# Store embeddings in FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save files
faiss.write_index(index, "data/faiss_index.bin")
np.save("data/booking_embeddings.npy", embeddings)