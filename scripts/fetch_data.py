"""Fetch data from Google Sheets."""
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path
from progress.bar import Bar
from typing import Literal


Status = Literal["Fetching", "Reading", "Saving"]


def fetch_data(data_path: str | Path) -> None:
    """
    Fetch data from Google Sheets and save to CSV.

    Args:
        data_path: Path to save the raw data CSV

    Raises:
        ValueError: If SHEET_IDS environment variable is not set
    """
    with Bar("Fetching...", max=4, suffix="%(percent)d%% | Elapsed: %(elapsed)ds") as bar:
        os.makedirs(data_path, exist_ok=True)
        bar.next()

        load_dotenv()
        sheet_ids_env: str | None = os.getenv("SHEET_IDS")
        if not sheet_ids_env:
            raise ValueError("No SHEET_IDS in env.")

        sheet_ids: list[str] = sheet_ids_env.split(",")
        bar.next()

        all_data: list[pd.DataFrame] = []
        for sheet_id in sheet_ids:
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

            data: pd.DataFrame = pd.read_csv(url, header=None)
            all_data.append(data)
        bar.next()

        combined_data: pd.DataFrame = pd.concat(all_data, ignore_index=True)
        combined_data.to_csv(f"{data_path}/raw_data.csv", index=False)
        bar.next()


if __name__ == "__main__":
    fetch_data("data")
