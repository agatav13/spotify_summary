import os
import pandas as pd
from datetime import datetime
from progress.bar import Bar


def get_time_of_day(hour):
    '''
    Morning: 6:00 - 11:59
    Afternoon: 12:00 - 17:59
    Evening: 18:00 - 22:59
    Night: 23:00 - 5:59
    Returns label for time of the day based on the hour
    '''
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 17:
        return "Afternoon"
    elif 18 <= hour <= 22:
        return "Evening"
    else:
        return "Night"


def process_data(data_path):
    with Bar("Processing...", max=7, suffix="%(percent)d%% | Elapsed: %(elapsed)ds") as bar:
        raw_data = pd.read_csv(f"{data_path}/raw_data.csv")
        bar.next()

        # Change the column names
        raw_data.columns = ["date", "title", "artist", "song_id", "link"]
        bar.next()

        # Change the date format from "December 8, 2024 at 07:02PM" to "2024-12-08 19:02"
        raw_data["date"] = raw_data["date"].apply(lambda x: datetime.strptime(
            x, "%B %d, %Y at %I:%M%p").strftime("%Y-%m-%d %H:%M"))
        raw_data["date"] = pd.to_datetime(raw_data["date"])
        bar.next()

        # Create new column with the day od week (Monday=0, Sunday=6)
        raw_data["day_of_week"] = raw_data["date"].dt.day_of_week
        bar.next()

        # Create new column with time of the day (Morning, Afternoon, Evening, Night)
        raw_data["time_of_day"] = raw_data["date"].dt.hour.apply(
            get_time_of_day)
        bar.next()

        os.makedirs(data_path, exist_ok=True)
        bar.next()

        raw_data.to_csv(f"{data_path}/processed_data.csv",
                        index=False)  # Save to a CSV file
        bar.next()


if __name__ == "__main__":
    process_data("data")
