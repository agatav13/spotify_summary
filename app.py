"""Spotify Wrapped - Interactive Streamlit Dashboard with Altair."""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from dashboard import visualizations
from dashboard.themes import COLORS

# Load .env for local development (ignored on Streamlit Cloud)
load_dotenv()


def fetch_and_process_data(data_path: Path) -> None:
    """Fetch data from Google Sheets and process it."""
    # Try st.secrets first (Streamlit Cloud), fallback to .env (local)
    sheet_ids = None
    try:
        sheet_ids = st.secrets.get("SHEET_IDS")
    except Exception:
        sheet_ids = os.getenv("SHEET_IDS")

    if not sheet_ids:
        st.error("SHEET_IDS not found. Add it to .env (local) or Streamlit secrets (cloud).")
        st.stop()

    sheet_ids = sheet_ids.split(",")

    # Fetch raw data
    all_data = []
    for sheet_id in sheet_ids:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        data = pd.read_csv(url, header=None)
        all_data.append(data)

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data.to_csv(data_path / "raw_data.csv", index=False, header=False)

    # Process data
    raw_data = pd.read_csv(data_path / "raw_data.csv", header=None)
    raw_data.columns = ["date", "title", "artist", "song_id", "link"]

    # Parse dates
    raw_data["date"] = raw_data["date"].apply(
        lambda x: datetime.strptime(x, "%B %d, %Y at %I:%M%p").strftime("%Y-%m-%d %H:%M")
    )
    raw_data["date"] = pd.to_datetime(raw_data["date"])

    # Add derived columns
    raw_data["day_of_week"] = raw_data["date"].dt.day_of_week

    def get_time_of_day(hour):
        if 6 <= hour <= 11:
            return "Morning"
        elif 12 <= hour <= 17:
            return "Afternoon"
        elif 18 <= hour <= 22:
            return "Evening"
        else:
            return "Night"

    raw_data["time_of_day"] = raw_data["date"].dt.hour.apply(get_time_of_day)

    raw_data.to_csv(data_path / "processed_data.csv", index=False)


@st.cache_data
def load_data(force_refresh: bool = False) -> pd.DataFrame:
    """Load and cache the processed Spotify data."""
    data_path = Path(__file__).parent / "data"
    processed_file = data_path / "processed_data.csv"

    # Create data directory if it doesn't exist
    data_path.mkdir(exist_ok=True)

    # Check if file exists and its age
    should_fetch = force_refresh

    if not processed_file.exists():
        should_fetch = True
    else:
        # Auto-refresh if file is older than 24 hours
        file_age = datetime.now() - datetime.fromtimestamp(processed_file.stat().st_mtime)
        if file_age > timedelta(hours=24):
            should_fetch = True

    if should_fetch:
        with st.spinner("Fetching and processing data from Google Sheets..."):
            fetch_and_process_data(data_path)
            st.rerun()

    df = pd.read_csv(processed_file)
    df["date"] = pd.to_datetime(df["date"])
    return df


# Page config
st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - Sage Rose Design
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap');

    * {
        font-family: 'Source Sans Pro', -apple-system, sans-serif;
    }

    .main {
        background-color: #f7f6f3;
    }

    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 600;
        color: #2d3436;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.01em;
    }

    .subtitle {
        font-family: 'Source Sans Pro', sans-serif;
        text-align: center;
        color: #b76e79;
        font-size: 0.9rem;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.05em;
    }

    h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 3rem !important;
        font-weight: 600 !important;
        color: #2d3436 !important;
    }

    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(183, 110, 121, 0.06);
        border: 1px solid #e8e6e1;
        transition: all 0.2s ease;
    }

    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(183, 110, 121, 0.12);
    }

    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.25rem;
        font-weight: 600;
        color: #b76e79;
        letter-spacing: -0.02em;
    }

    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #636e72;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }

    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.35rem;
        font-weight: 500;
        color: #2d3436;
        margin-top: 1.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #b76e79;
        display: inline-block;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 8% !important;
        padding-right: 8% !important;
        max-width: 1400px !important;
    }

    hr {
        border: none;
        border-top: 1px solid #e0ddd5;
        margin: 2rem 0;
    }

    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e8e6e1;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    h3 {
        color: #2d3436 !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.sidebar.info("Fetching fresh data from Google Sheets...")
    df = load_data(force_refresh=True)

# Data info
data_path = Path(__file__).parent / "data" / "processed_data.csv"
if data_path.exists():
    from datetime import datetime
    file_age = datetime.now() - datetime.fromtimestamp(data_path.stat().st_mtime)
    hours_ago = int(file_age.total_seconds() / 3600)
    st.sidebar.caption(f"Data updated {hours_ago}h ago")

st.sidebar.markdown("---")

# Time Period
st.sidebar.header("Time Period")

# Time period selector
period = st.sidebar.radio(
    "Time Period",
    ["All Data", "This Month", "This Year", "Custom Range"],
)

# Load data
df = load_data()

if period == "All Data":
    df_filtered = df
elif period == "This Month":
    today = pd.Timestamp.now()
    df_filtered = df[
        (df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)
    ]
elif period == "This Year":
    today = pd.Timestamp.now()
    df_filtered = df[df["date"].dt.year == today.year]
else:  # Custom Range
    min_date = df["date"].dt.date.min()
    max_date = df["date"].dt.date.max()
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    df_filtered = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    ]

# Show filtered info
st.sidebar.markdown(f"**Showing:** {len(df_filtered):,} listens")

# Header
st.markdown('<h1 class="main-header">Spotify Listening Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Listening insights</p>', unsafe_allow_html=True)

# Key Metrics
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df_filtered):,}</div>
            <div class="metric-label">Total Listens</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df_filtered['artist'].nunique():,}</div>
            <div class="metric-label">Artists</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df_filtered['song_id'].nunique():,}</div>
            <div class="metric-label">Songs</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    avg_per_day = len(df_filtered) / df_filtered["date"].dt.date.nunique()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_per_day:.1f}</div>
            <div class="metric-label">Per Day</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# TOP ARTISTS SECTION
# ============================================================================
st.markdown('<p class="section-header">Top Artists</p>', unsafe_allow_html=True)

# Slider above chart, left-aligned
col1, col2 = st.columns([1, 4])
with col1:
    top_n = st.slider("n", min_value=3, max_value=15, value=6, key="top_n", label_visibility="collapsed")

chart = visualizations.plot_top_artists_altair(df_filtered, num_artists=top_n)
st.altair_chart(chart, width="stretch")

st.markdown("---")

# ============================================================================
# TIMELINE SECTION
# ============================================================================
st.markdown('<p class="section-header">Listening Timeline</p>', unsafe_allow_html=True)
chart = visualizations.plot_timeline_altair(df_filtered)
st.altair_chart(chart, width="stretch")

st.markdown("---")

# ============================================================================
# DAY OF WEEK SECTION
# ============================================================================
st.markdown('<p class="section-header">Distribution by Day of Week</p>', unsafe_allow_html=True)
chart = visualizations.plot_listens_by_day_altair(df_filtered)
st.altair_chart(chart, width="stretch")

st.markdown("---")

# ============================================================================
# TIME PATTERNS SECTION
# ============================================================================
st.markdown('<p class="section-header">Time Patterns</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Time of Day")
    chart = visualizations.plot_listens_by_time_altair(df_filtered)
    st.altair_chart(chart, width="stretch")

with col2:
    st.markdown("#### Weekly Patterns Heatmap")
    chart = visualizations.plot_heatmap_altair(df_filtered)
    st.altair_chart(chart, width="stretch")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #b76e79; font-size: 0.85rem;'>Made with Streamlit</div>",
    unsafe_allow_html=True,
)
