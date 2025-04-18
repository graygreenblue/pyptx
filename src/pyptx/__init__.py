"""
pptx_layout
===========

Hierarchical, flex‑box–inspired layout framework on top of **python‑pptx**.

This package resolves a tree of *layout items* (rows, columns, boxes, etc.)
into concrete positions (EMUs) that can be applied to PowerPoint shapes.
"""
from .units import Inch, Centimeter, Ratio, Weight, resolve_length_span
from .core import Rect, LayoutItem, Box, Row, Column, SlideLayout
from .errors import LayoutError, OverflowError
from .debug import draw_rect, draw_layout, test_draw_rects

__all__ = [
    "Inch", "Centimeter", "Ratio", "Weight",
    "Rect", "LayoutItem", "Box", "Row", "Column", "SlideLayout",
    "LayoutError", "OverflowError",
    "resolve_length_span",
    "draw_rect", "draw_layout", "test_draw_rects",
]