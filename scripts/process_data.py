import os
import pandas as pd
from datetime import datetime, date

def process_data(data_path):
    raw_data = pd.read_csv(f"{data_path}/raw_data.csv")

    # Change the column names
    raw_data.columns = ["date", "title", "artist", "song_id", "link"]

    # Change the date format from "December 8, 2024 at 07:02PM" to "2024-12-08 19:02"
    raw_data["date"] = raw_data["date"].apply(lambda x: datetime.strptime(x, "%B %d, %Y at %I:%M%p").strftime("%Y-%m-%d %H:%M"))
    raw_data["date"] = pd.to_datetime(raw_data["date"])

    # Create new column with the day od week (Monday=0, Sunday=6)
    raw_data["day_of_week"] = raw_data["date"].dt.day_of_week

    os.makedirs(data_path, exist_ok=True)
    raw_data.to_csv(f"{data_path}/processed_data.csv", index=False)  # Save to a CSV file

if __name__ == "__main__":
    process_data("data")