"""Spotify Wrapped - Interactive Streamlit Dashboard with Altair."""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from dashboard import visualizations
from dashboard.themes import COLORS


def fetch_and_process_data(data_path: Path) -> None:
    """Fetch data from Google Sheets and process it."""
    sheet_ids = st.secrets.get("SHEET_IDS")
    if not sheet_ids:
        st.error("SHEET_IDS not found in Streamlit secrets. Please add it in app settings.")
        st.stop()

    sheet_ids = sheet_ids.split(",")

    # Fetch raw data
    all_data = []
    for sheet_id in sheet_ids:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        data = pd.read_csv(url, header=None)
        all_data.append(data)

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data.to_csv(data_path / "raw_data.csv", index=False)

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

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        color: #E91E63;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
    }
    h1 {
        font-size: 4rem !important;
        font-weight: 800 !important;
    }
    .metric-card {
        background-color: #FFF0F5;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #F48FB1;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #E91E63;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #F48FB1;
        padding-bottom: 0.25rem;
    }
    .chart-container {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #F0F0F0;
    }
    /* Reduce padding at top and bottom of page */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-right: 15% !important;
    }
    /* Hide sidebar collapse button */
    [data-testid="stSidebarCollapseButton"] {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.header("🎛️ Controls")

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
    st.sidebar.caption(f"📊 Data updated {hours_ago}h ago")

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

# Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Listens", value=f"{len(df_filtered):,}")
with col2:
    st.metric(label="Unique Artists", value=f"{df_filtered['artist'].nunique():,}")
with col3:
    st.metric(label="Unique Songs", value=f"{df_filtered['song_id'].nunique():,}")
with col4:
    avg_per_day = len(df_filtered) / df_filtered["date"].dt.date.nunique()
    st.metric(label="Avg per Day", value=f"{avg_per_day:.1f}")

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
    f"<div style='text-align: center; color: {COLORS['secondary']};'>Made with 💖 and Streamlit</div>",
    unsafe_allow_html=True,
)
