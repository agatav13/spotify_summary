"""Error handling utilities for Spotify dashboard.

This module provides custom exceptions and unified error handling
functions for consistent error reporting across the application.
"""
from enum import Enum
from typing import Self


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""

    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class DashboardError(Exception):
    """Base exception for dashboard-related errors."""

    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR) -> None:
        """
        Initialize a dashboard error.

        Args:
            message: Human-readable error message
            severity: Error severity level
        """
        self.message = message
        self.severity = severity
        super().__init__(message)

    @classmethod
    def warning(cls, message: str) -> Self:
        """Create a warning-level error."""
        return cls(message, ErrorSeverity.WARNING)

    @classmethod
    def info(cls, message: str) -> Self:
        """Create an info-level error."""
        return cls(message, ErrorSeverity.INFO)


class DataLoadError(DashboardError):
    """Exception raised when data loading fails."""

    pass


class DataValidationError(DashboardError):
    """Exception raised when data validation fails."""

    pass


class SheetConfigError(DashboardError):
    """Exception raised when sheet configuration is invalid."""

    pass


class DataProcessingError(DashboardError):
    """Exception raised when data processing fails."""

    pass
