"""Data loading and processing module for Spotify listening data.

This module consolidates all data fetching and processing logic, eliminating
duplication between the main app and standalone scripts.
"""
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from dashboard.config import DATA, SHEET
from dashboard.errors import (
    DashboardError,
    DataLoadError,
    DataProcessingError,
    DataValidationError,
    ErrorSeverity,
    SheetConfigError,
)
from dashboard.utils import get_time_of_day

# Compile regex pattern from config
SHEET_ID_PATTERN: re.Pattern[str] = re.compile(SHEET.id_pattern)


def _validate_sheet_id(sheet_id: str) -> bool:
    """
    Validate Google Sheet ID format to prevent injection attacks.

    Args:
        sheet_id: The sheet ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(SHEET_ID_PATTERN.match(sheet_id.strip()))


def _get_sheet_ids() -> list[str] | None:
    """
    Get sheet IDs from environment or Streamlit secrets.

    Returns:
        List of sheet IDs, or None if not found
    """
    # Try st.secrets first (Streamlit Cloud), fallback to .env (local)
    sheet_ids = None
    try:
        sheet_ids = st.secrets.get("SHEET_IDS")
    except Exception:
        load_dotenv()
        sheet_ids = os.getenv("SHEET_IDS")

    if not sheet_ids:
        return None

    return sheet_ids.split(",")


def _get_sheet_ids_or_raise() -> list[str]:
    """
    Get sheet IDs from environment or Streamlit secrets.

    Returns:
        List of sheet IDs

    Raises:
        SheetConfigError: If sheet IDs are not configured
    """
    sheet_ids = _get_sheet_ids()
    if not sheet_ids:
        raise SheetConfigError(
            "SHEET_IDS not found. Add it to .env (local) or Streamlit secrets (cloud)."
        )
    return sheet_ids


def _parse_date(date_str: str) -> str | None:
    """
    Parse date string from IFTTT format to standard format.

    Args:
        date_str: Date string in format "December 8, 2024 at 07:02PM"

    Returns:
        Formatted date string or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, DATA.date_format).strftime(
            DATA.output_date_format
        )
    except ValueError:
        return None


def fetch_from_sheets(sheet_ids: list[str]) -> pd.DataFrame:
    """
    Fetch and combine data from multiple Google Sheets.

    Args:
        sheet_ids: List of Google Sheet IDs to fetch from

    Returns:
        Combined DataFrame with raw data

    Raises:
        SheetConfigError: If sheet ID is invalid or fetching fails
    """
    all_data: list[pd.DataFrame] = []

    for sheet_id in sheet_ids:
        if not _validate_sheet_id(sheet_id):
            raise SheetConfigError(f"Invalid sheet ID format: {sheet_id}")

        try:
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            data = pd.read_csv(url, header=None)
            all_data.append(data)
        except Exception as e:
            raise DataLoadError(f"Failed to fetch data from sheet {sheet_id}: {e}") from e

    if not all_data:
        raise DataLoadError("No data was fetched from Google Sheets.")

    return pd.concat(all_data, ignore_index=True)


def process_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw Spotify data into a clean, analysis-ready format.

    Args:
        raw_data: Raw DataFrame with columns [date, title, artist, song_id, link]

    Returns:
        Processed DataFrame with additional columns for analysis

    Raises:
        DataValidationError: If required columns are missing
    """
    # Set column names
    raw_data.columns = ["date", "title", "artist", "song_id", "link"]

    # Validate required columns
    if not all(col in raw_data.columns for col in DATA.required_columns):
        raise DataValidationError(
            f"Data is missing required columns: {DATA.required_columns}"
        )

    # Parse dates with error handling
    raw_data["date"] = raw_data["date"].apply(_parse_date)
    # Remove rows with invalid dates
    raw_data = raw_data[raw_data["date"].notna()]
    raw_data["date"] = pd.to_datetime(raw_data["date"])

    # Add derived columns
    raw_data["day_of_week"] = raw_data["date"].dt.day_of_week
    raw_data["time_of_day"] = raw_data["date"].dt.hour.apply(get_time_of_day)

    return raw_data


def fetch_and_process_data(data_path: Path) -> bool:
    """
    Fetch data from Google Sheets and process it.

    This is the main entry point for data loading, used by both the
    Streamlit app and standalone scripts.

    Args:
        data_path: Path to the data directory

    Returns:
        True if successful, False otherwise
    """
    try:
        sheet_ids = _get_sheet_ids_or_raise()

        # Fetch raw data
        raw_data = fetch_from_sheets(sheet_ids)

        # Save raw data (for backup/debugging)
        raw_data.to_csv(data_path / "raw_data.csv", index=False, header=False)

        # Process data directly from memory
        processed_data = process_raw_data(raw_data)
        processed_data.to_csv(data_path / "processed_data.csv", index=False)
        return True

    except (SheetConfigError, DataLoadError, DataValidationError, DataProcessingError) as e:
        _display_error(e)
        return False
    except OSError as e:
        st.error(f"File system error: {e}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False


def _display_error(error: DashboardError) -> None:
    """
    Display an error to the user based on its severity.

    Args:
        error: The error to display
    """
    if error.severity == ErrorSeverity.WARNING:
        st.warning(error.message)
    elif error.severity == ErrorSeverity.INFO:
        st.info(error.message)
    else:
        st.error(error.message)
