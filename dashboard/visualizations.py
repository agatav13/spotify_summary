"""Visualization functions for Spotify listening data."""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from dashboard.themes import (
    COLORS,
    PINK_SCHEME,
    DAY_COLORS,
    TIME_COLORS,
)


def plot_listens_by_day_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a bar chart of listens by day of week using Altair."""
    day_labels = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    days_of_week = df["day_of_week"].value_counts().sort_index().reset_index()
    days_of_week.columns = ["day", "count"]
    days_of_week["day"] = days_of_week["day"].map(day_labels)

    # Ensure proper ordering
    days_of_week["day"] = pd.Categorical(
        days_of_week["day"],
        categories=list(day_labels.values()),
        ordered=True,
    )
    days_of_week = days_of_week.sort_values("day")

    chart = (
        alt.Chart(days_of_week)
        .mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            width=50,
        )
        .encode(
            x=alt.X(
                "day:N",
                title="Day of Week",
                axis=alt.Axis(labelAngle=-45),
                sort=list(day_labels.values()),  # Explicitly set sort order
            ),
            y=alt.Y("count:Q", title="Number of Listens"),
            color=alt.Color(
                "day:N",
                scale=alt.Scale(domain=list(day_labels.values()), range=list(DAY_COLORS.values())),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("day:N", title="Day"),
                alt.Tooltip("count:Q", title="Listens", format=","),
            ],
        )
        .properties(width="container", height=400)
    )

    return chart


def plot_listens_by_time_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a bar chart of listens by time of day using Altair."""
    time_counts = df["time_of_day"].value_counts().reset_index()
    time_counts.columns = ["time", "count"]

    # Order times
    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    time_counts["time"] = pd.Categorical(time_counts["time"], categories=time_order, ordered=True)
    time_counts = time_counts.sort_values("time")

    chart = (
        alt.Chart(time_counts)
        .mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8,
            width=60,
        )
        .encode(
            x=alt.X(
                "time:N",
                title="Time of Day",
                sort=time_order,  # Explicitly set sort order
            ),
            y=alt.Y("count:Q", title="Number of Listens"),
            color=alt.Color(
                "time:N",
                scale=alt.Scale(domain=time_order, range=list(TIME_COLORS.values())),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("time:N", title="Time"),
                alt.Tooltip("count:Q", title="Listens", format=","),
            ],
        )
        .properties(width="container", height=400)
    )

    return chart


@st.cache_data
def _prepare_timeline_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and cache timeline data."""
    df_plot = df.copy()
    df_plot["date"] = df_plot["date"].dt.date
    listens_per_day = df_plot.groupby("date").size().reset_index()
    listens_per_day.columns = ["date", "count"]
    return listens_per_day


def plot_timeline_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a line plot of listens over time using Altair."""
    # Use cached data preparation
    listens_per_day = _prepare_timeline_data(df)

    # Create base chart
    base = (
        alt.Chart(listens_per_day)
        .encode(
            x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %Y")),
            y=alt.Y("count:Q", title="Number of Listens"),
        )
    )

    # Area fill
    area = base.mark_area(opacity=0.3, color=COLORS["primary"]).encode(
        y=alt.Y("count:Q", title="Number of Listens"),
        y2=alt.value(0),
    )

    # Line
    line = base.mark_line(color=COLORS["primary"], strokeWidth=2)

    # Points with tooltip
    points = base.mark_circle(color=COLORS["primary"], size=30, opacity=0.5).encode(
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
            alt.Tooltip("count:Q", title="Listens", format=","),
        ]
    )

    chart = (
        (area + line + points)
        .properties(width="container", height=400)
        .configure_view(strokeWidth=0)
    )

    return chart


@st.cache_data
def _prepare_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and cache heatmap data."""
    day_labels = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    df_plot = df.copy()
    df_plot["hour"] = df_plot["date"].dt.hour
    df_plot["day_of_week"] = df_plot["day_of_week"].map(day_labels)

    pivot = (
        df_plot.groupby(["hour", "day_of_week"])
        .size()
        .reset_index()
        .rename(columns={0: "count"})
    )

    # Order days properly
    pivot["day_of_week"] = pd.Categorical(
        pivot["day_of_week"],
        categories=list(day_labels.values()),
        ordered=True,
    )

    return pivot


def plot_heatmap_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a heatmap of listens by hour and day of week using Altair."""
    # Use cached data preparation
    pivot = _prepare_heatmap_data(df)

    day_labels = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    # Custom pink gradient for heatmap
    pink_gradient = ["#FFF5F8", "#FFDEE9", "#F8BBD0", "#F48FB1", "#F06292", "#E91E63", "#AD1457"]

    chart = (
        alt.Chart(pivot)
        .mark_rect(stroke="#FFFFFF", strokeWidth=1, cornerRadius=3)
        .encode(
            x=alt.X(
                "day_of_week:N",
                title="Day of Week",
                sort=list(day_labels.values()),  # Explicitly set sort order
            ),
            y=alt.Y("hour:O", title="Hour"),
            color=alt.Color(
                "count:Q",
                scale=alt.Scale(
                    range=pink_gradient,
                    type="sqrt"
                ),
                legend=alt.Legend(title="Listens", orient="right"),
            ),
            tooltip=[
                alt.Tooltip("day_of_week:N", title="Day"),
                alt.Tooltip("hour:O", title="Hour"),
                alt.Tooltip("count:Q", title="Listens", format=","),
            ],
        )
        .properties(width="container", height=450)
    )

    return chart


# ============================================================================
# NEW VISUALIZATIONS FOR MULTI-TAB DASHBOARD
# ============================================================================


def _truncate_text(text: str, max_length: int = 40) -> str:
    """Truncate text to max_length and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


@st.cache_data
def _prepare_top_songs_data(df: pd.DataFrame, num_songs: int = 10) -> pd.DataFrame:
    """Prepare and cache top songs data."""
    song_counts = (
        df.groupby(["title", "artist"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(num_songs)
    )

    song_counts["title_truncated"] = song_counts["title"].apply(lambda x: _truncate_text(x, 20))
    song_counts["artist_truncated"] = song_counts["artist"].apply(lambda x: _truncate_text(x, 25))
    song_counts["song_label"] = song_counts["title_truncated"] + " — " + song_counts["artist_truncated"]

    total_listens = df.shape[0]
    song_counts["percent"] = (song_counts["count"] / total_listens * 100).round(1)

    return song_counts


def plot_top_songs_altair(df: pd.DataFrame, num_songs: int = 10) -> alt.Chart:
    """
    Create a horizontal bar chart of most played songs using Altair.

    Args:
        df: DataFrame with listening data (must have title, artist columns)
        num_songs: Number of top songs to display

    Returns:
        Altair chart with horizontal bar chart
    """
    # Use cached data preparation
    song_counts = _prepare_top_songs_data(df, num_songs)

    chart = (
        alt.Chart(song_counts)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, height=30)
        .encode(
            y=alt.Y(
                "song_label:N",
                title="Song",
                sort="-x",  # Sort by count descending
                axis=alt.Axis(labelLimit=400),
            ),
            x=alt.X("count:Q", title="Number of Listens"),
            color=alt.Color(
                "count:Q",
                scale=alt.Scale(
                    scheme="reds",
                    range=["#F8BBD0", "#F48FB1", "#F06292", "#E91E63", "#C2185B"]
                ),
                legend=alt.Legend(title="Listens", orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("title:N", title="Song"),
                alt.Tooltip("artist:N", title="Artist"),
                alt.Tooltip("count:Q", title="Listens", format=","),
                alt.Tooltip("percent:Q", title="% of Total", format=".1f"),
            ],
        )
        .properties(width="container", height=max(400, 50 + num_songs * 35))
        .configure_view(strokeWidth=0)
    )

    return chart


@st.cache_data
def _prepare_top_artists_data(df: pd.DataFrame, num_artists: int = 10) -> pd.DataFrame:
    """Prepare and cache top artists data."""
    artist_counts = (
        df.groupby("artist")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(num_artists)
    )

    artist_counts["artist_truncated"] = artist_counts["artist"].apply(lambda x: _truncate_text(x, 40))

    total_listens = df.shape[0]
    artist_counts["percent"] = (artist_counts["count"] / total_listens * 100).round(1)

    return artist_counts


def plot_top_artists_detail_altair(
    df: pd.DataFrame,
    num_artists: int = 10,
) -> alt.Chart:
    """
    Create an enhanced horizontal bar chart of top artists using Altair.
    More intuitive than donut chart for comparisons.

    Args:
        df: DataFrame with listening data
        num_artists: Number of top artists to display

    Returns:
        Altair chart with horizontal bar chart showing artist and listen count
    """
    # Use cached data preparation
    artist_counts = _prepare_top_artists_data(df, num_artists)

    chart = (
        alt.Chart(artist_counts)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, height=28)
        .encode(
            y=alt.Y(
                "artist_truncated:N",
                title="Artist",
                sort="-x",  # Sort by count descending
                axis=alt.Axis(labelLimit=300),
            ),
            x=alt.X("count:Q", title="Number of Listens"),
            color=alt.Color(
                "count:Q",
                scale=alt.Scale(
                    scheme="purples",
                    range=["#E1BEE7", "#CE93D8", "#AB47BC", "#9C27B0", "#7B1FA2"]
                ),
                legend=alt.Legend(title="Listens", orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("artist:N", title="Artist"),
                alt.Tooltip("count:Q", title="Listens", format=","),
                alt.Tooltip("percent:Q", title="% of Total", format=".1f"),
            ],
        )
        .properties(width="container", height=max(400, 50 + num_artists * 30))
        .configure_view(strokeWidth=0)
    )

    return chart


def calculate_diversity_score(df: pd.DataFrame) -> dict:
    """
    Calculate Artist Diversity Score using Simpson's Diversity Index.

    Measures the variety of artists in your listening history.
    - Higher score (closer to 1) = More diverse listening across many artists
    - Lower score (closer to 0) = More focused on fewer artists

    Args:
        df: DataFrame with listening data

    Returns:
        Dictionary with diversity score and interpretation
    """
    # Get artist listen counts
    artist_counts = df["artist"].value_counts()
    total_listens = len(df)

    # Simpson's Diversity Index: D = 1 - sum(p_i^2)
    # where p_i is the proportion of listens to artist i
    proportions = artist_counts / total_listens
    simpson_index = 1 - (proportions ** 2).sum()

    # Determine interpretation
    if simpson_index >= 0.8:
        interpretation = "Very Diverse"
        description = "You explore a wide variety of artists!"
    elif simpson_index >= 0.6:
        interpretation = "Diverse"
        description = "You have a good mix of favorite and new artists."
    elif simpson_index >= 0.4:
        interpretation = "Moderate"
        description = "You tend to focus on certain artists but explore others."
    else:
        interpretation = "Focused"
        description = "You strongly prefer your favorite artists."

    return {
        "score": float(round(simpson_index, 3)),
        "interpretation": interpretation,
        "description": description,
        "unique_artists": int(len(artist_counts)),
        "top_artist_pct": float(round((artist_counts.iloc[0] / total_listens) * 100, 1)),
    }
