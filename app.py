"""Spotify Wrapped - Interactive Streamlit Dashboard with Altair."""
import re
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta
from dashboard import visualizations
from dashboard.tabs import (
    render_overview_tab,
    render_songs_tab,
    render_artists_tab,
    render_patterns_tab,
)
from dashboard.themes import COLORS
from dashboard.utils import get_time_of_day


def _load_css() -> None:
    """Load custom CSS from file."""
    css_path = Path(__file__).parent / "dashboard" / "static" / "style.css"
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styling.")

# Constants
CACHE_REFRESH_HOURS: int = 24
SHEET_ID_PATTERN: re.Pattern = re.compile(r"^[a-zA-Z0-9-_]{10,50}$")

# Configure page first (before any other st calls)
st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load .env for local development (ignored on Streamlit Cloud)
load_dotenv()


def _validate_sheet_id(sheet_id: str) -> bool:
    """
    Validate Google Sheet ID format to prevent injection attacks.

    Args:
        sheet_id: The sheet ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(SHEET_ID_PATTERN.match(sheet_id.strip()))


def fetch_and_process_data(data_path: Path) -> bool:
    """
    Fetch data from Google Sheets and process it.

    Args:
        data_path: Path to the data directory

    Returns:
        True if successful, False otherwise
    """
    # Try st.secrets first (Streamlit Cloud), fallback to .env (local)
    sheet_ids = None
    try:
        sheet_ids = st.secrets.get("SHEET_IDS")
    except Exception:
        sheet_ids = os.getenv("SHEET_IDS")

    if not sheet_ids:
        st.error("SHEET_IDS not found. Add it to .env (local) or Streamlit secrets (cloud).")
        return False

    sheet_ids = sheet_ids.split(",")

    # Validate sheet IDs
    for sheet_id in sheet_ids:
        if not _validate_sheet_id(sheet_id):
            st.error(f"Invalid sheet ID format: {sheet_id}")
            return False

    # Fetch raw data with error handling
    all_data = []
    for sheet_id in sheet_ids:
        try:
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            data = pd.read_csv(url, header=None)
            all_data.append(data)
        except Exception as e:
            st.error(f"Failed to fetch data from sheet {sheet_id}: {e}")
            return False

    if not all_data:
        st.error("No data was fetched from Google Sheets.")
        return False

    try:
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.to_csv(data_path / "raw_data.csv", index=False, header=False)
    except Exception as e:
        st.error(f"Failed to save raw data: {e}")
        return False

    # Process data with error handling
    try:
        raw_data = pd.read_csv(data_path / "raw_data.csv", header=None)
        raw_data.columns = ["date", "title", "artist", "song_id", "link"]

        # Validate required columns exist
        required_cols = ["date", "title", "artist", "song_id"]
        if not all(col in raw_data.columns for col in required_cols):
            st.error("Data is missing required columns.")
            return False

        # Parse dates with error handling
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%B %d, %Y at %I:%M%p").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                return None

        raw_data["date"] = raw_data["date"].apply(parse_date)
        # Remove rows with invalid dates
        raw_data = raw_data[raw_data["date"].notna()]
        raw_data["date"] = pd.to_datetime(raw_data["date"])

        # Add derived columns
        raw_data["day_of_week"] = raw_data["date"].dt.day_of_week
        raw_data["time_of_day"] = raw_data["date"].dt.hour.apply(get_time_of_day)

        raw_data.to_csv(data_path / "processed_data.csv", index=False)
        return True

    except Exception as e:
        st.error(f"Failed to process data: {e}")
        return False


@st.cache_data
def load_data(force_refresh: bool = False) -> pd.DataFrame | None:
    """
    Load and cache the processed Spotify data.

    Args:
        force_refresh: Force re-fetching data from Google Sheets

    Returns:
        DataFrame with listening data, or None if loading failed
    """
    data_path = Path(__file__).parent / "data"
    processed_file = data_path / "processed_data.csv"

    # Create data directory if it doesn't exist
    data_path.mkdir(exist_ok=True)

    # Check if file exists and its age
    should_fetch = force_refresh

    if not processed_file.exists():
        should_fetch = True
    else:
        # Auto-refresh if file is older than configured hours
        file_age = datetime.now() - datetime.fromtimestamp(processed_file.stat().st_mtime)
        if file_age > timedelta(hours=CACHE_REFRESH_HOURS):
            should_fetch = True

    if should_fetch:
        success = fetch_and_process_data(data_path)
        if not success:
            # If we have cached data, return it even if refresh failed
            if processed_file.exists():
                st.warning("Using cached data due to fetch failure.")
            else:
                st.error("No data available. Please check your configuration.")
                return None

    try:
        df = pd.read_csv(processed_file)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None


def render_metrics(df: pd.DataFrame) -> None:
    """Render key metrics cards."""
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-label">Total Listens</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df['artist'].nunique():,}</div>
                <div class="metric-label">Artists</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{df['song_id'].nunique():,}</div>
                <div class="metric-label">Songs</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_per_day = len(df) / df["date"].dt.date.nunique()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_per_day:.1f}</div>
                <div class="metric-label">Per Day</div>
            </div>
        """, unsafe_allow_html=True)


# Load custom CSS
_load_css()

# ============================================================================
# SIDEBAR
# ============================================================================

# Initialize session state for refresh tracking
if "data_refreshed" not in st.session_state:
    st.session_state.data_refreshed = False

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    with st.sidebar:
        with st.spinner("Fetching fresh data from Google Sheets..."):
            load_data(force_refresh=True)
        st.success("Data refreshed successfully!")
        st.session_state.data_refreshed = True

# Data info
data_path = Path(__file__).parent / "data" / "processed_data.csv"
if data_path.exists():
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

if df is None:
    st.error("Failed to load data. Please check your configuration and try again.")
    st.stop()

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

st.sidebar.markdown("---")

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
# Navigation moved to main content as horizontal buttons

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown('<h1 class="main-header">Spotify Listening Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Listening insights</p>', unsafe_allow_html=True)

# Key Metrics
render_metrics(df_filtered)

# Tab Navigation (built-in tabs for smoother switching)
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Artists", "Songs", "Patterns"])

with tab1:
    render_overview_tab(df_filtered)

with tab2:
    with st.spinner("Loading artists..."):
        render_artists_tab(df_filtered)

with tab3:
    with st.spinner("Loading songs..."):
        render_songs_tab(df_filtered)

with tab4:
    with st.spinner("Loading patterns..."):
        render_patterns_tab(df_filtered)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #b76e79; font-size: 0.85rem;'>Made with Streamlit</div>",
    unsafe_allow_html=True,
)
