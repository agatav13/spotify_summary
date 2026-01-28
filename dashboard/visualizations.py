"""Visualization functions for Spotify listening data."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date


def plot_top_artists(
    df: pd.DataFrame,
    num_artists: int = 6,
    month: int | None = None,
    year: int | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Create a pie chart of top listened artists.

    Args:
        df: DataFrame with listening data
        num_artists: Number of top artists to display
        month: Filter by month (1-12), None for all time
        year: Filter by year, None for all time
        ax: Matplotlib axis to plot on

    Returns:
        Matplotlib axis with the plot
    """
    df_filtered = df.copy()

    if month is not None and year is not None:
        df_filtered = df_filtered[
            (df_filtered["date"].dt.month == month)
            & (df_filtered["date"].dt.year == year)
        ]

    # Group by artist and count
    artist_counts = (
        df_filtered[["artist", "title"]]
        .groupby(by="artist")
        .count()
        .rename(columns={"title": "count"})
        .sort_values(by="count", ascending=False)
        .head(num_artists)
    )

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    ax.pie(
        artist_counts["count"],
        labels=artist_counts.index,
        textprops={"fontsize": 10},
        colors=sns.color_palette("Pastel1"),
    )

    date_range = f"{month:02}-{year}" if (month and year) else "all data"
    ax.set_title(
        f"Most listened artists ({date_range})",
        fontdict={"fontsize": 14, "fontweight": "bold"},
        pad=20,
    )

    return ax


def plot_listens_by_day(df: pd.DataFrame) -> plt.Figure:
    """Create a bar chart of listens by day of week."""
    day_labels = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    days_of_week = df["day_of_week"].value_counts().sort_index()
    days_of_week.index = days_of_week.index.map(day_labels)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(days_of_week.index, days_of_week, color=sns.color_palette("Pastel1"))

    ax.set_title(
        "Number of listens per day of week",
        fontdict={"fontsize": 14, "fontweight": "bold"},
        pad=20,
    )
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.set_xlabel("Day of week", fontsize=10, labelpad=10)
    ax.set_ylabel("Number of listens", fontsize=10, labelpad=10)
    ax.grid(axis="y")

    plt.tight_layout()
    return fig


def plot_listens_by_time(df: pd.DataFrame) -> plt.Figure:
    """Create a bar chart of listens by time of day."""
    time_of_day = df["time_of_day"].value_counts()

    time_of_day.index = pd.Categorical(
        time_of_day.index, ["Morning", "Afternoon", "Evening", "Night"]
    )
    time_of_day = time_of_day.sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(time_of_day.index, time_of_day, color=sns.color_palette("Pastel1"))

    ax.set_title(
        "Number of listens by time of day",
        fontdict={"fontsize": 14, "fontweight": "bold"},
        pad=20,
    )
    ax.set_xlabel("Time of day", fontsize=10, labelpad=10)
    ax.set_ylabel("Number of listens", fontsize=10, labelpad=10)
    ax.grid(axis="y")

    plt.tight_layout()
    return fig


def plot_listens_over_time(df: pd.DataFrame) -> plt.Figure:
    """Create a line plot of listens per day."""
    df_plot = df.copy()
    df_plot["date"] = df_plot["date"].dt.date
    listens_per_day = df_plot.groupby("date").count()["song_id"]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(listens_per_day, color="palevioletred")

    ax.set_title(
        "Number of listens per day",
        fontdict={"fontsize": 14, "fontweight": "bold"},
        pad=20,
    )
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.set_xlabel("Date", fontsize=11, labelpad=10)
    ax.set_ylabel("Number of listens", fontsize=11, labelpad=10)
    ax.grid()

    plt.tight_layout()
    return fig


def plot_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Create a heatmap of listens by hour and day of week."""
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
        .unstack(fill_value=0)
        .reindex(columns=list(day_labels.values()))
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        pivot,
        cmap=sns.cubehelix_palette(as_cmap=True),
        linewidths=0.2,
        linecolor="white",
        ax=ax,
    )

    ax.set_title(
        "Number of listens: Day of week vs Hour",
        fontdict={"fontsize": 14, "fontweight": "bold"},
        pad=20,
    )
    ax.tick_params(axis="y", rotation=0)
    ax.set_xlabel("Day of week", fontsize=11, labelpad=10)
    ax.set_ylabel("Hour", fontsize=11, labelpad=10)

    plt.tight_layout()
    return fig
