"""Patterns tab view for Spotify dashboard."""
import streamlit as st
import pandas as pd
from dashboard import visualizations


def render_patterns_tab(df: pd.DataFrame) -> None:
    """
    Render the Patterns tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    # Day of Week
    st.markdown('<p class="section-header">Distribution by Day of Week</p>', unsafe_allow_html=True)
    chart = visualizations.plot_listens_by_day_altair(df)
    st.altair_chart(chart, width="stretch")

    st.markdown("---")

    # Time Patterns
    st.markdown('<p class="section-header">Time Patterns</p>', unsafe_allow_html=True)

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
    st.markdown('<p class="section-header">Listening Timeline</p>', unsafe_allow_html=True)
    chart = visualizations.plot_timeline_altair(df)
    st.altair_chart(chart, width="stretch")
