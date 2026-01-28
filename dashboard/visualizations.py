"""Visualization functions for Spotify listening data."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import date
from dashboard.themes import (
    COLORS,
    PASTEL_PALETTE,
    get_custom_layout,
    get_color_sequence,
    PINK_SCHEME,
    PASTEL_SCHEME,
    DAY_COLORS,
    TIME_COLORS,
)


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


# ============================================================================
# PLOTLY VISUALIZATIONS
# ============================================================================


def plot_top_artists_plotly(
    df: pd.DataFrame,
    num_artists: int = 6,
    month: int | None = None,
    year: int | None = None,
) -> go.Figure:
    """
    Create an interactive pie chart of top listened artists using Plotly.

    Args:
        df: DataFrame with listening data
        num_artists: Number of top artists to display
        month: Filter by month (1-12), None for all time
        year: Filter by year, None for all time

    Returns:
        Plotly figure with interactive pie chart
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
        .reset_index()
    )

    fig = px.pie(
        artist_counts,
        values="count",
        names="artist",
        hole=0.3,
        color_discrete_sequence=get_color_sequence(num_artists),
        title=f"Top {num_artists} Artists",
    )

    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Listens: %{value}<br>Percent: %{percent}<extra></extra>",
        textposition="inside",
        textinfo="percent+label",
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        **get_custom_layout(),
    )

    return fig


def plot_listens_by_day_plotly(df: pd.DataFrame) -> go.Figure:
    """Create an interactive bar chart of listens by day of week."""
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

    fig = px.bar(
        days_of_week,
        x="day",
        y="count",
        title="Listens by Day of Week",
        color="day",
        color_discrete_sequence=px.colors.sequential.Pinkyl[::-1],
        labels={"day": "Day of Week", "count": "Number of Listens"},
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Listens: %{y}<extra></extra>",
        marker=dict(line=dict(color="white", width=2)),
    )

    fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        **get_custom_layout(),
    )

    return fig


def plot_listens_by_time_plotly(df: pd.DataFrame) -> go.Figure:
    """Create an interactive bar chart of listens by time of day."""
    time_counts = df["time_of_day"].value_counts().reset_index()
    time_counts.columns = ["time", "count"]

    # Order times
    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    time_counts["time"] = pd.Categorical(time_counts["time"], categories=time_order, ordered=True)
    time_counts = time_counts.sort_values("time")

    fig = px.bar(
        time_counts,
        x="time",
        y="count",
        title="Listens by Time of Day",
        color="time",
        color_discrete_map={
            "Morning": COLORS["mint"],
            "Afternoon": COLORS["peach"],
            "Evening": COLORS["secondary"],
            "Night": COLORS["purple"],
        },
        labels={"time": "Time of Day", "count": "Number of Listens"},
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Listens: %{y}<extra></extra>",
        marker=dict(line=dict(color="white", width=2)),
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        **get_custom_layout(),
    )

    return fig


def plot_timeline_plotly(df: pd.DataFrame) -> go.Figure:
    """Create an interactive line plot of listens over time."""
    df_plot = df.copy()
    df_plot["date"] = df_plot["date"].dt.date
    listens_per_day = df_plot.groupby("date").size().reset_index()
    listens_per_day.columns = ["date", "count"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=listens_per_day["date"],
            y=listens_per_day["count"],
            mode="lines",
            fill="tozeroy",
            line=dict(color=COLORS["primary"], width=2),
            hovertemplate="<b>%{x}</b><br>Listens: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Listening Timeline",
        xaxis_title="Date",
        yaxis_title="Number of Listens",
        hovermode="x unified",
        xaxis=dict(
            showgrid=False,
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
        ),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )

    return fig


def plot_heatmap_plotly(df: pd.DataFrame) -> go.Figure:
    """Create an interactive heatmap of listens by hour and day of week."""
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

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="Pinkyl",
        hovertemplate="<b>%{x}</b>, %{y}:00<br>Listens: %{z}<extra></extra>",
    ))

    fig.update_layout(
        title="Listening Patterns: Day of Week vs Hour",
        xaxis_title="Day of Week",
        yaxis_title="Hour",
        **get_custom_layout(),
    )

    return fig


# ============================================================================
# ALTAIR VISUALIZATIONS
# ============================================================================


def plot_top_artists_altair(
    df: pd.DataFrame,
    num_artists: int = 6,
    month: int | None = None,
    year: int | None = None,
) -> alt.Chart:
    """
    Create a donut chart of top listened artists using Altair.

    Args:
        df: DataFrame with listening data
        num_artists: Number of top artists to display
        month: Filter by month (1-12), None for all time
        year: Filter by year, None for all time

    Returns:
        Altair chart with interactive donut chart
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
        .reset_index()
    )

    chart = (
        alt.Chart(artist_counts)
        .mark_arc(
            innerRadius=80,
            cornerRadius=5,
            stroke="#FFFFFF",
            strokeWidth=2,
        )
        .encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color(
                "artist:N",
                legend=alt.Legend(title="Artist", orient="right", labelLimit=150),
                scale=alt.Scale(range=PASTEL_SCHEME),
            ),
            tooltip=[
                alt.Tooltip("artist:N", title="Artist"),
                alt.Tooltip("count:Q", title="Listens", format=","),
                alt.Tooltip("count:Q", title="Percent", format=".1%"),
            ],
        )
        .properties(
            width=400,
            height=400,
            title=f"Top {num_artists} Artists",
        )
        .configure_view(strokeWidth=0)
    )

    return chart


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
        .properties(width="container", height=400, title="Listens by Day of Week")
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
        .properties(width="container", height=400, title="Listens by Time of Day")
    )

    return chart


def plot_timeline_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a line plot of listens over time using Altair."""
    df_plot = df.copy()
    df_plot["date"] = df_plot["date"].dt.date
    listens_per_day = df_plot.groupby("date").size().reset_index()
    listens_per_day.columns = ["date", "count"]

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
        .properties(width="container", height=400, title="Listening Timeline")
        .configure_view(strokeWidth=0)
    )

    return chart


def plot_heatmap_altair(df: pd.DataFrame) -> alt.Chart:
    """Create a heatmap of listens by hour and day of week using Altair."""
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
        .properties(width="container", height=450, title="Listening Patterns Heatmap")
    )

    return chart
