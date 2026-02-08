"""Spotify Wrapped - Interactive Streamlit Dashboard with Altair."""
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.components import render_footer, render_metric_card
from dashboard.config import CACHE
from dashboard.data_loader import fetch_and_process_data
from dashboard.tabs import (
    render_artists_tab,
    render_overview_tab,
    render_patterns_tab,
    render_songs_tab,
)


def _load_css() -> None:
    """Load custom CSS from file."""
    css_path = Path(__file__).parent / "dashboard" / "static" / "style.css"
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styling.")

# Configure page first (before any other st calls)
st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
        if file_age > timedelta(hours=CACHE.refresh_hours):
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


@st.cache_data
def filter_data_by_period(
    df: pd.DataFrame,
    period: str,
    start_date: datetime | None | pd.Timestamp = None,
    end_date: datetime | None | pd.Timestamp = None,
) -> pd.DataFrame:
    """
    Filter data by time period with caching.

    Args:
        df: Full DataFrame to filter
        period: Time period filter ("All Data", "This Month", "This Year", "Custom Range")
        start_date: Start date for custom range
        end_date: End date for custom range

    Returns:
        Filtered DataFrame
    """
    if period == "All Data":
        return df
    elif period == "This Month":
        today = pd.Timestamp.now()
        return df[
            (df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)
        ]
    elif period == "This Year":
        today = pd.Timestamp.now()
        return df[df["date"].dt.year == today.year]
    else:  # Custom Range
        if start_date is None or end_date is None:
            return df
        return df[
            (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
        ]


def render_metrics(df: pd.DataFrame) -> None:
    """Render key metrics cards."""
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        render_metric_card(f"{len(df):,}", "Total Listens")

    with col2:
        render_metric_card(f"{df['artist'].nunique():,}", "Artists")

    with col3:
        render_metric_card(f"{df['song_id'].nunique():,}", "Songs")

    with col4:
        avg_per_day = len(df) / df["date"].dt.date.nunique()
        render_metric_card(f"{avg_per_day:.1f}", "Per Day")


# Load custom CSS
_load_css()

# ============================================================================
# SIDEBAR
# ============================================================================

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    # Clear the cached data so load_data() will fetch fresh data
    load_data.clear()
    with st.sidebar:
        with st.spinner("Fetching fresh data from Google Sheets..."):
            df_new = load_data(force_refresh=True)
        if df_new is not None:
            st.success("Data refreshed successfully!")
        else:
            st.error("Failed to refresh data.")

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

if period == "Custom Range":
    min_date = df["date"].dt.date.min()
    max_date = df["date"].dt.date.max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    # Handle both tuple and single date return types
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date
    df_filtered = filter_data_by_period(df, period, start_date, end_date)
else:
    df_filtered = filter_data_by_period(df, period)

# Show filtered info
st.sidebar.markdown(f"**Showing:** {len(df_filtered):,} listens")

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
render_footer()
