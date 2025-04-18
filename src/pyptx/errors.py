"""Custom exceptions for the layout engine."""
class LayoutError(RuntimeError):
    """Base error for layout operations."""


class OverflowError(LayoutError):
    """Raised when children sizes exceed available parent size."""
