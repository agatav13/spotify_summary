"""Songs tab view for Spotify dashboard."""
import pandas as pd
import streamlit as st

from dashboard import visualizations
from dashboard.components import render_empty_state, render_section_header
from dashboard.config import CHART


def render_songs_tab(df: pd.DataFrame) -> None:
    """
    Render the Songs tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    if len(df) == 0:
        render_empty_state()
        return

    render_section_header("Top Songs")

    chart = visualizations.plot_top_songs_altair(df, num_songs=CHART.default_num_songs)
    st.altair_chart(chart, width="stretch")
