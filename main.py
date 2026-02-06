"""Main script to fetch and process Spotify data."""
from scripts.fetch_data import fetch_data
from scripts.process_data import process_data


def main() -> None:
    """Run the data fetch and process pipeline."""
    data_path: str = "data"

    fetch_data(data_path)
    process_data(data_path)


if __name__ == "__main__":
    main()
