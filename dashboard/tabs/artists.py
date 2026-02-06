"""Artists tab view for Spotify dashboard."""
import streamlit as st
import pandas as pd
from dashboard import visualizations


def render_artists_tab(df: pd.DataFrame) -> None:
    """
    Render the Artists tab content.

    Args:
        df: Filtered DataFrame with listening data
    """
    # Artist Details
    st.markdown('<p class="section-header">Top Artists</p>', unsafe_allow_html=True)

    chart = visualizations.plot_top_artists_detail_altair(df, num_artists=20)
    st.altair_chart(chart, width="stretch")

    st.markdown("---")

    # Artist Diversity Score
    st.markdown('<p class="section-header">Artist Diversity</p>', unsafe_allow_html=True)

    diversity = visualizations.calculate_diversity_score(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{diversity['score']:.3f}</div>
                <div class="metric-label">Diversity Score</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{diversity['interpretation']}</div>
                <div class="metric-label">Variety</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{diversity['top_artist_pct']}%</div>
                <div class="metric-label">Top Artist</div>
            </div>
        """, unsafe_allow_html=True)

    st.caption(
        f"💡 {diversity['description']} "
        f"You listened to {diversity['unique_artists']:,} unique artists."
    )
