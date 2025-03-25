from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

load_dotenv()  # Load .env
SHEET_ID = os.getenv("SHEET_ID")

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

data = pd.read_csv(url)
data.columns = ["date", "title", "artist", "song_id", "link"]  # Change the column names

# Change the date format from "December 8, 2024 at 07:02PM" to "2024-12-08 19:02"
data["date"] = data["date"].apply(lambda x: datetime.strptime(x, "%B %d, %Y at %I:%M%p").strftime("%Y-%m-%d %H:%M"))

os.makedirs("data", exist_ok=True)
data.to_csv("data/data.csv", index=False)  # Save to a CSV file