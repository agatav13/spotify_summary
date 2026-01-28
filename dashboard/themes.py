"""Theme and color palette for Spotify dashboard - Altair version."""
import altair as alt


COLORS = {
    "primary": "#E91E63",      # Pink (main accent)
    "secondary": "#F48FB1",    # Light Pink
    "accent": "#CE93D8",       # Purple accent
    "teal": "#26A69A",         # Teal (professional)
    "blue": "#42A5F5",         # Blue (professional)
    "coral": "#FF7043",        # Coral (warmth)
    "grey_light": "#F5F5F5",   # Light grey background
    "grey_dark": "#424242",    # Dark grey text
    "white": "#FFFFFF",
}

# Categorical schemes (for bar charts, pie charts)
PINK_SCHEME = ["#E91E63", "#F48FB1", "#CE93D8", "#AB47BC", "#9FA8DA", "#90CAF9"]
PASTEL_SCHEME = ["#F8BBD0", "#F48FB1", "#CE93D8", "#B39DDB", "#9FA8DA", "#90CAF9"]
PROFESSIONAL_SCHEME = ["#E91E63", "#26A69A", "#42A5F5", "#FFA726", "#AB47BC", "#78909C"]

# Day of week specific colors (pink gradient)
DAY_COLORS = {
    "Monday": "#F48FB1",
    "Tuesday": "#F06292",
    "Wednesday": "#E91E63",
    "Thursday": "#CE93D8",
    "Friday": "#AB47BC",
    "Saturday": "#9FA8DA",
    "Sunday": "#90CAF9",
}

# Time of day colors
TIME_COLORS = {
    "Morning": "#90CAF9",
    "Afternoon": "#FFCC80",
    "Evening": "#F48FB1",
    "Night": "#CE93D8",
}


def get_chart_config() -> dict:
    """Get default Altair chart configuration."""
    return {
        "background": "#FFFFFF",
        "view": {"stroke": "transparent"},
        "axis": {
            "labelFontSize": 12,
            "titleFontSize": 14,
            "labelColor": "#424242",
            "titleColor": "#424242",
        },
        "legend": {
            "labelFontSize": 12,
            "titleFontSize": 14,
            "labelColor": "#424242",
            "titleColor": "#424242",
        },
        "header": {
            "titleFontSize": 18,
            "titleColor": "#E91E63",
        },
    }


PASTEL_PALETTE = ["#F8BBD0", "#F48FB1", "#CE93D8", "#B39DDB", "#9FA8DA", "#90CAF9"]


def get_custom_layout() -> dict:
    """Get custom Plotly layout for backwards compatibility."""
    return {
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "font": {"color": "#424242", "family": "sans-serif"},
        "margin": dict(l=20, r=20, t=40, b=20),
        "title": {"x": 0.5, "xanchor": "center"},
    }


def get_color_sequence(n: int) -> list:
    """Get a color sequence of length n from PASTEL_PALETTE."""
    return [PASTEL_PALETTE[i % len(PASTEL_PALETTE)] for i in range(n)]
