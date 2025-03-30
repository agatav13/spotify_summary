# Spotify summary

Data collected with a [IFTTT applet](https://ifttt.com/applets/nin7BxVm-keep-a-log-of-your-recently-played-tracks), that logs recently played tracks on Spotify.

This project explores listening habits by analyzing song titles, artists, and listening times.

The project was created to practice:
1. Data processing
   - loading raw data
   - transforming raw data into a usable format
   - adding new information based on existing data
2. Data analysis
   - using **Python** and **Jupyter Notebooks**
3. Data visualization
   - using libraries like **Matplotlib** and **Seaborn**


### Instructions

Packages and their versions are specified in `requirments.txt`. Install with:
```bash
pip install -r requirements.txt
```

Put `SHEET_ID` for Google Spreadsheet with logged songs in the `.env` file. Then run `main.py` to fetch and process data, that will be saved in `raw_data.csv` and `processed_data.csv` files in the path specified in `main.py`.