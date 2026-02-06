"""Tab render functions for Spotify dashboard."""
from dashboard.tabs.overview import render_overview_tab
from dashboard.tabs.songs import render_songs_tab
from dashboard.tabs.artists import render_artists_tab
from dashboard.tabs.patterns import render_patterns_tab

__all__ = [
    "render_overview_tab",
    "render_songs_tab",
    "render_artists_tab",
    "render_patterns_tab",
]
