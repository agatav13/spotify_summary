# Spotify Summary

An interactive dashboard for analyzing Spotify listening habits, built with [Streamlit](https://streamlit.io/).

[**Live Demo**](https://spotifysummary.streamlit.app/) | [Source Code](https://github.com/agatav13/spotify_summary)

## About

Data is collected using an [IFTTT applet](https://ifttt.com/applets/nin7BxVm-keep-a-log-of-your-recently-played-tracks) that logs recently played tracks from Spotify to a Google Sheet.

This project analyzes listening patterns by exploring:

- Top artists and songs
- Listening timeline and trends
- Day-of-week and time-of-day patterns
- Listening heatmaps

## Features

- **Interactive Dashboard**: Filter by time period (all data, this month, this year, or custom range)
- **Visualizations**: Built with Altair for responsive, interactive charts
- **Multiple Data Sources**: Supports multiple Google Sheets as data sources

## Tech Stack

- **Python** for data processing
- **Streamlit** for the web interface
- **Pandas** for data manipulation
- **Altair** for data visualization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/agatav13/spotify_summary.git
cd spotify_summary
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file in the project root
echo "SHEET_IDS=your_sheet_id_1,your_sheet_id_2" > .env
```

4. Run the app:
```bash
streamlit run app.py
```

## Project Structure

```
spotify_wrapped/
├── app.py                 # Main Streamlit application
├── main.py               # Data fetching script
├── dashboard/
│   ├── visualizations.py # Altair chart functions
│   └── themes.py         # Color scheme and styling
├── scripts/
│   ├── fetch_data.py     # Google Sheets fetching
│   └── process_data.py   # Data processing utilities
└── data/                 # Cached data files (auto-created)
```

## Deploy on Streamlit Cloud

1. Fork this repository
2. Connect your repo on [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `SHEET_IDS` as a secret in your app settings
4. Deploy!
