"""Spotify Wrapped - Interactive Streamlit Dashboard."""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dashboard import visualizations


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the processed Spotify data."""
    data_path = "data/processed_data.csv"
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


st.set_page_config(
    page_title="Spotify Wrapped",
    page_icon="🎵",
    layout="wide",
)


# Load data
with st.spinner("Loading data..."):
    df = load_data()

# Title and description
st.title("🎵 Spotify Listening Analysis")
st.markdown(f"**Total listens:** {len(df):,}")
st.markdown(f"**Date range:** {df['date'].dt.date.min()} to {df['date'].dt.date.max()}")

# Sidebar controls
st.sidebar.header("Controls")

# Date range filter
date_range = st.sidebar.radio(
    "Time period",
    ["All data", "This month", "This year", "Custom range"],
)

if date_range == "All data":
    df_filtered = df
elif date_range == "This month":
    today = pd.Timestamp.now()
    df_filtered = df[
        (df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)
    ]
elif date_range == "This year":
    today = pd.Timestamp.now()
    df_filtered = df[df["date"].dt.year == today.year]
else:  # Custom range
    min_date = df["date"].dt.date.min()
    max_date = df["date"].dt.date.max()
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    df_filtered = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    ]

# Show filtered data info
if len(df_filtered) < len(df):
    st.sidebar.markdown(f"**Filtered listens:** {len(df_filtered):,}")
else:
    st.sidebar.markdown(f"**Showing all:** {len(df_filtered):,} listens")

# Top artists section
st.header("Most Listened Artists")

col1, col2 = st.columns(2)

with col1:
    st.subheader("All Time")
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    visualizations.plot_top_artists(df_filtered, num_artists=6, ax=ax1)
    st.pyplot(fig1)
    plt.close()

with col2:
    st.subheader("This Month")
    today = pd.Timestamp.now()
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    visualizations.plot_top_artists(
        df_filtered,
        num_artists=6,
        month=today.month,
        year=today.year,
        ax=ax2,
    )
    st.pyplot(fig2)
    plt.close()

# Day of week analysis
st.header("Listening Patterns by Day")

with st.container():
    fig3 = visualizations.plot_listens_by_day(df_filtered)
    st.pyplot(fig3)
    plt.close()

# Time of day analysis
st.header("Listening Patterns by Time of Day")

col3, col4 = st.columns(2)

with col3:
    fig4 = visualizations.plot_listens_by_time(df_filtered)
    st.pyplot(fig4)
    plt.close()

with col4:
    st.subheader("Time of Day Heatmap")
    fig5 = visualizations.plot_heatmap(df_filtered)
    st.pyplot(fig5)
    plt.close()

# Timeline
st.header("Listens Over Time")

with st.container():
    fig6 = visualizations.plot_listens_over_time(df_filtered)
    st.pyplot(fig6)
    plt.close()
