from dotenv import load_dotenv
import os
import pandas as pd
from progress.bar import Bar


def fetch_data(data_path):
    with Bar("Fetching...", max=4, suffix="%(percent)d%% | Elapsed: %(elapsed)ds") as bar:
        load_dotenv()  # Load .env
        bar.next()

        SHEET_ID = os.getenv("SHEET_ID")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        data = pd.read_csv(url)
        bar.next()

        os.makedirs(data_path, exist_ok=True)
        bar.next()

        data.to_csv(f"{data_path}/raw_data.csv", index=False)  # Save to a CSV file
        bar.next()


if __name__ == "__main__":
    fetch_data("data")
