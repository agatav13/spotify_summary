"""Patterns tab view for Spotify dashboard."""
import pandas as pd
import streamlit as st

from dashboard import visualizations
from dashboard.components import render_empty_state, render_section_header


def render_patterns_tab(df: pd.DataFrame) -> None:
    """
    Render the Patterns tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    if len(df) == 0:
        render_empty_state()
        return

    # Day of Week
    render_section_header("Distribution by Day of Week")
    chart = visualizations.plot_listens_by_day_altair(df)
    st.altair_chart(chart, width="stretch")

    st.markdown("---")

    # Time Patterns
    render_section_header("Time Patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Time of Day")
        chart = visualizations.plot_listens_by_time_altair(df)
        st.altair_chart(chart, width="stretch")

    with col2:
        st.markdown("#### Weekly Patterns Heatmap")
        chart = visualizations.plot_heatmap_altair(df)
        st.altair_chart(chart, width="stretch")

    st.markdown("---")

    # Listening Timeline
    render_section_header("Listening Timeline")
    chart = visualizations.plot_timeline_altair(df)
    st.altair_chart(chart, width="stretch")
