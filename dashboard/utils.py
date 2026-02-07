"""Utility functions for data processing."""
from typing import Literal

TimeOfDay = Literal["Morning", "Afternoon", "Evening", "Night"]


def get_time_of_day(hour: int) -> TimeOfDay:
    """
    Get time of day label from hour.

    Morning: 6:00 - 11:59
    Afternoon: 12:00 - 17:59
    Evening: 18:00 - 22:59
    Night: 23:00 - 5:59

    Args:
        hour: Hour of day (0-23)

    Returns:
        Time of day label
    """
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 17:
        return "Afternoon"
    elif 18 <= hour <= 22:
        return "Evening"
    else:
        return "Night"
