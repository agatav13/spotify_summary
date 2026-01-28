"""Spotify Wrapped - Interactive Streamlit Dashboard with Altair."""
import streamlit as st
import pandas as pd
from dashboard import visualizations
from dashboard.themes import COLORS


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the processed Spotify data."""
    data_path = "data/processed_data.csv"
    df = pd.read_csv(data_path)
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
        font-size: 2.5rem;
        font-weight: bold;
        color: #E91E63;
        text-align: center;
        margin-bottom: 1rem;
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
</style>
""",
    unsafe_allow_html=True,
)

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("🎛️ Time Period")

# Time period selector
period = st.sidebar.radio(
    "Time Period",
    ["All Data", "This Month", "This Year", "Custom Range"],
)

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
st.markdown('<p class="main-header">🎵 Spotify Listening Dashboard</p>', unsafe_allow_html=True)

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

col1, col2 = st.columns([4, 1])
with col2:
    st.info("📊")
    top_n = st.slider("Number of Artists", min_value=3, max_value=15, value=6)

with col1:
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
