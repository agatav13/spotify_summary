"""Overview tab view for Spotify dashboard."""
import streamlit as st
import pandas as pd
from dashboard import visualizations
from dashboard.themes import COLORS


def render_overview_tab(df: pd.DataFrame) -> None:
    """
    Render the Overview tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    if len(df) == 0:
        st.info("No data available for the selected time period.")
        return

    # Calculate overview stats
    top_artist = df["artist"].value_counts().idxmax()
    top_artist_count = df["artist"].value_counts().max()

    top_song_data = df.groupby(["title", "artist"]).size().reset_index(name="count")
    top_song_idx = top_song_data["count"].idxmax()
    top_song = top_song_data.loc[top_song_idx, "title"]
    top_song_artist = top_song_data.loc[top_song_idx, "artist"]
    top_song_count = top_song_data.loc[top_song_idx, "count"]

    # Peak listening day
    listens_per_day = df.groupby(df["date"].dt.date).size()
    peak_day = listens_per_day.idxmax()
    peak_day_count = listens_per_day.max()

    # Favorite time of day
    time_counts = df["time_of_day"].value_counts()
    favorite_time = time_counts.idxmax()
    favorite_time_count = time_counts.max()

    # Display in a nice grid
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-header">Top Artist</p>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; font-weight: 600; color: #b76e79; margin-bottom: 0.5rem;">
                    {top_artist}
                </div>
                <div style="font-size: 1.1rem; color: #636e72;">
                    {top_artist_count:,} listens
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-header">Top Song</p>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 1.5rem; font-weight: 600; color: #b76e79; margin-bottom: 0.25rem;">
                    {top_song}
                </div>
                <div style="font-size: 1rem; color: #636e72; margin-bottom: 0.5rem;">
                    {top_song_artist}
                </div>
                <div style="font-size: 1.1rem; color: #636e72;">
                    {top_song_count:,} plays
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-header">Peak Listening Day</p>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 1.8rem; font-weight: 600; color: #b76e79; margin-bottom: 0.5rem;">
                    {peak_day.strftime("%B %d, %Y")}
                </div>
                <div style="font-size: 1.1rem; color: #636e72;">
                    {peak_day_count} listens
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown('<p class="section-header">Favorite Time</p>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; font-weight: 600; color: #b76e79; margin-bottom: 0.5rem;">
                    {favorite_time}
                </div>
                <div style="font-size: 1.1rem; color: #636e72;">
                    {favorite_time_count:,} listens
                </div>
            </div>
        """, unsafe_allow_html=True)
