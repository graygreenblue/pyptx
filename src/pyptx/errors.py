"""Custom exceptions for the layout engine."""

from loguru import logger

class PyptxError(Exception):
    """Base error for pyptx operations."""
    def __init__(self, message: str):
        logger.error(f"{self.__class__.__name__} - {message}")
        super().__init__(message)

class LayoutError(PyptxError):
    """Base error for layout operations."""

class OverflowError(LayoutError):
    """Raised when children sizes exceed available parent size."""

class LayoutStateError(LayoutError):
    """Rect has not been assigned before attempting layout operations."""

class SpecMismatchError(LayoutError):
    """Number of Unit specs does not match number of child items."""
