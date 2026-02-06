"""Songs tab view for Spotify dashboard."""
import streamlit as st
import pandas as pd
from dashboard import visualizations


def render_songs_tab(df: pd.DataFrame) -> None:
    """
    Render the Songs tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    st.markdown('<p class="section-header">Top Songs</p>', unsafe_allow_html=True)

    # Get chart
    chart = visualizations.plot_top_songs_altair(df, num_songs=20)
    st.altair_chart(chart, width="stretch")
