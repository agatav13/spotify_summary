"""Reusable UI components for the Spotify dashboard.

This module provides common UI components used across multiple tabs
to ensure consistency and reduce code duplication.
"""
import streamlit as st

from dashboard.themes import COLORS


def render_metric_card(value: str | int | float, label: str) -> None:
    """
    Render a metric card with a value and label.

    Args:
        value: The metric value to display
        label: The metric label
    """
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str) -> None:
    """
    Render a section header with the Sage Rose theme.

    Args:
        title: The section title
    """
    st.markdown(f'<p class="section-header">{title}</p>', unsafe_allow_html=True)


def render_stat_card(
    title: str,
    value: str,
    subtitle: str | None = None,
) -> None:
    """
    Render a stat card with title, value, and optional subtitle.

    Args:
        title: The card title (shown as section header)
        value: The main value to display
        subtitle: Optional subtitle to display below the value
    """
    render_section_header(title)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; font-weight: 600; color: {COLORS['sage_rose']};
                       margin-bottom: 0.5rem;">
                {value}
            </div>
            {f'<div style="font-size: 1.1rem; color: {COLORS["grey_medium"]};">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str = "No data available for the selected time period.") -> None:
    """
    Render an empty state message.

    Args:
        message: The message to display
    """
    st.info(message)


def render_footer(text: str = "Made with Streamlit") -> None:
    """
    Render the footer with consistent styling.

    Args:
        text: The footer text
    """
    st.markdown("---")
    footer_html = (
        f"<div style='text-align: center; color: {COLORS['sage_rose']}; font-size: 0.85rem;'>"
        f"{text}</div>"
    )
    st.markdown(footer_html, unsafe_allow_html=True)
