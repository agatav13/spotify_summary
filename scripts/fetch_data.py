from dotenv import load_dotenv
import os
import pandas as pd
from progress.bar import Bar


def fetch_data(data_path):
    with Bar("Fetching...", max=4, suffix="%(percent)d%% | Elapsed: %(elapsed)ds") as bar:
        os.makedirs(data_path, exist_ok=True)
        bar.next()

        load_dotenv()  # Load .env
        SHEET_IDS: str | None = os.getenv("SHEET_IDS")
        if not SHEET_IDS:
            raise ValueError("No SHEET_IDS in env.")

        SHEET_IDS: list[str] = SHEET_IDS.split(",")
        bar.next()

        all_data: list[pd.DataFrame] = []
        for sheet_id in SHEET_IDS:
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            
            data: pd.DataFrame = pd.read_csv(url, header=None)

            all_data.append(data)
        bar.next()

        combined_data: pd.DataFrame = pd.concat(all_data, ignore_index=True)
        combined_data.to_csv(f"{data_path}/raw_data.csv", index=False)  # Save to a CSV file
        bar.next()


if __name__ == "__main__":
    fetch_data("data")
