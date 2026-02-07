"""Configuration constants for Spotify dashboard.

This module centralizes all configuration values to make it easier
to maintain and modify dashboard behavior.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheConfig:
    """Cache-related configuration."""

    refresh_hours: int = 24


@dataclass(frozen=True)
class TimeOfDayConfig:
    """Time of day categorization configuration."""

    morning_start: int = 6
    morning_end: int = 11
    afternoon_start: int = 12
    afternoon_end: int = 17
    evening_start: int = 18
    evening_end: int = 22


@dataclass(frozen=True)
class ChartConfig:
    """Chart visualization configuration."""

    default_num_songs: int = 10
    default_num_artists: int = 10
    timeline_width: int = 400
    timeline_height: int = 400
    heatmap_height: int = 450
    bar_height_songs: int = 30
    bar_height_artists: int = 28


@dataclass(frozen=True)
class DataConfig:
    """Data processing configuration."""

    date_format: str = "%B %d, %Y at %I:%M%p"
    output_date_format: str = "%Y-%m-%d %H:%M"
    required_columns: tuple[str, ...] = ("date", "title", "artist", "song_id")


@dataclass(frozen=True)
class SheetConfig:
    """Google Sheets configuration."""

    id_pattern: str = r"^[a-zA-Z0-9-_]{10,50}$"
    export_format: str = "csv"


# Singleton instances for easy importing
CACHE = CacheConfig()
TIME_OF_DAY = TimeOfDayConfig()
CHART = ChartConfig()
DATA = DataConfig()
SHEET = SheetConfig()
