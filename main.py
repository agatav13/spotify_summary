from scripts.fetch_data import fetch_data
from scripts.process_data import process_data

data_path = "data"

fetch_data(data_path)
process_data(data_path)