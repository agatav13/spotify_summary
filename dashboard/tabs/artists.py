"""Artists tab view for Spotify dashboard."""
import pandas as pd
import streamlit as st

from dashboard import visualizations
from dashboard.components import render_empty_state, render_metric_card, render_section_header
from dashboard.config import CHART


def render_artists_tab(df: pd.DataFrame) -> None:
    """
    Render the Artists tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    if len(df) == 0:
        render_empty_state()
        return

    # Artist Details
    render_section_header("Top Artists")

    chart = visualizations.plot_top_artists_detail_altair(df, num_artists=CHART.default_num_artists)
    st.altair_chart(chart, width="stretch")

    st.markdown("---")

    # Artist Diversity Score
    render_section_header("Artist Diversity")

    diversity = visualizations.calculate_diversity_score(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card(f"{diversity['score']:.3f}", "Diversity Score")

    with col2:
        render_metric_card(diversity['interpretation'], "Variety")

    with col3:
        render_metric_card(f"{diversity['top_artist_pct']}%", "Top Artist")

    st.caption(
        f"💡 {diversity['description']} "
        f"You listened to {diversity['unique_artists']:,} unique artists."
    )
