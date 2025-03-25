from dotenv import load_dotenv
import os
import pandas as pd

def fetch_data(data_path):
    load_dotenv()  # Load .env
    SHEET_ID = os.getenv("SHEET_ID")

    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

    data = pd.read_csv(url)

    os.makedirs(data_path, exist_ok=True)
    data.to_csv(f"{data_path}/raw_data.csv", index=False)  # Save to a CSV file

if __name__ == "__main__":
    fetch_data("data")