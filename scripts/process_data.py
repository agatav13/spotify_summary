"""Process raw Spotify data into a clean format."""
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from progress.bar import Bar

# Add parent directory to path to import from dashboard
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dashboard.utils import get_time_of_day


def process_data(data_path: str | Path) -> None:
    """
    Process raw Spotify data and save to CSV.

    Args:
        data_path: Path to data directory (contains raw_data.csv)
    """
    with Bar("Processing...", max=7, suffix="%(percent)d%% | Elapsed: %(elapsed)ds") as bar:
        raw_data: pd.DataFrame = pd.read_csv(f"{data_path}/raw_data.csv")
        bar.next()

        # Change the column names
        raw_data.columns = ["date", "title", "artist", "song_id", "link"]
        bar.next()

        # Change the date format from "December 8, 2024 at 07:02PM" to "2024-12-08 19:02"
        DATE_FORMAT: str = "%B %d, %Y at %I:%M%p"
        OUTPUT_DATE_FORMAT: str = "%Y-%m-%d %H:%M"

        raw_data["date"] = raw_data["date"].apply(
            lambda x: datetime.strptime(x, DATE_FORMAT).strftime(OUTPUT_DATE_FORMAT)
        )
        raw_data["date"] = pd.to_datetime(raw_data["date"])
        bar.next()

        # Create new column with the day of week (Monday=0, Sunday=6)
        raw_data["day_of_week"] = raw_data["date"].dt.day_of_week
        bar.next()

        # Create new column with time of the day (Morning, Afternoon, Evening, Night)
        raw_data["time_of_day"] = raw_data["date"].dt.hour.apply(get_time_of_day)
        bar.next()

        os.makedirs(data_path, exist_ok=True)
        bar.next()

        raw_data.to_csv(f"{data_path}/processed_data.csv", index=False)
        bar.next()


if __name__ == "__main__":
    process_data("data")
