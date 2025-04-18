"""
Core layout primitives (Rect, LayoutItem, Box/Row/Column).
Only minimal behaviour is implemented – the engine is expected to be
extended iteratively.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .units import Unit, resolve_length_span
from .errors import OverflowError


# ------------------------------------------------------------------ #
# Geometry helpers
# ------------------------------------------------------------------ #
@dataclass(slots=True)
class Rect:
    """Axis‑aligned rectangle in EMUs."""

    x: int
    y: int
    width: int
    height: int

    def split_vertical(self, specs: Sequence[Unit]) -> List["Rect"]:
        """Divide the rectangle **horizontally** into columns."""
        widths = resolve_length_span(specs, self.width)
        rects: List[Rect] = []
        cursor = self.x
        for w in widths:
            rects.append(Rect(cursor, self.y, w, self.height))
            cursor += w
        return rects

    def split_horizontal(self, specs: Sequence[Unit]) -> List["Rect"]:
        """Divide the rectangle **vertically** into rows."""
        heights = resolve_length_span(specs, self.height)
        rects: List[Rect] = []
        cursor = self.y
        for h in heights:
            rects.append(Rect(self.x, cursor, self.width, h))
            cursor += h
        return rects


# ------------------------------------------------------------------ #
# Layout tree
# ------------------------------------------------------------------ #
class LayoutItem:
    """
    Base node in the layout tree.

    Subclasses implement :meth:`_layout_children` to position child items
    within *self.rect*.
    """

    def __init__(self):
        self.children: list["LayoutItem"] = []
        self.rect: Optional[Rect] = None

    # ---------------------------------------------------------------- #
    # Public API
    # ---------------------------------------------------------------- #
    def add(self, item: "LayoutItem") -> "LayoutItem":
        """Append *item* as a child and return it (for fluent calls)."""
        self.children.append(item)
        return item

    def layout(self, rect: Rect):
        """
        Resolve positions of *self* and its descendants.

        Subclasses should **not** override – implement
        :meth:`_layout_children` instead.
        """
        self.rect = rect
        self._layout_children()

    # ---------------------------------------------------------------- #
    # Internal helpers
    # ---------------------------------------------------------------- #
    def _layout_children(self):
    def walk(self):

        """Yield *self* and all descendants."""

        yield self

        for _child in self.children:

            yield from _child.walk()


        """Position children inside *self.rect* (override in subclass)."""
        # Default: if children exist, that's an error (no strategy).
        if self.children:
            raise NotImplementedError(
                f"{self.__class__.__name__} cannot contain children"
            )


# ------------------------------------------------------------------ #
# Concrete containers
# ------------------------------------------------------------------ #
class Box(LayoutItem):
    """
    Generic flex container.

    Currently simply forwards full *rect* to the single child (if any).
    """

    def _layout_children(self):
        if not self.children:
            return
        if len(self.children) > 1:
            raise LayoutError("Box supports 0 or 1 child for now")
        self.children[0].layout(self.rect)  # type: ignore[arg-type]


class Row(LayoutItem):
    """
    Lay out children **horizontally** according to the *specs* list.

    Each child is associated with a :class:`Unit`. A one‑to‑one mapping
    must be provided up‑front.
    """

    def __init__(self, specs: Sequence[Unit]):
        super().__init__()
        self.specs: List[Unit] = list(specs)

    # API sugar
    def add_box(self, unit: Unit) -> Box:
        box = Box()
        self.specs.append(unit)
        self.add(box)
        return box

    # ---------------------------------------------------------------- #
    # Layout algorithm
    # ---------------------------------------------------------------- #
    def _layout_children(self):
        if len(self.specs) != len(self.children):
            raise LayoutError(
                f"Row expects {len(self.specs)} children, "
                f"got {len(self.children)}"
            )
        columns = self.rect.split_vertical(self.specs)
        for child, rect in zip(self.children, columns, strict=False):
            child.layout(rect)


class Column(LayoutItem):
    """
    Lay out children **vertically** according to the *specs* list.
    Equivalent to :class:`Row` but splits on the Y‑axis.
    """

    def __init__(self, specs: Sequence[Unit]):
        super().__init__()
        self.specs: List[Unit] = list(specs)

    def add_box(self, unit: Unit) -> Box:
        box = Box()
        self.specs.append(unit)
        self.add(box)
        return box

    def _layout_children(self):
        if len(self.specs) != len(self.children):
            raise LayoutError(
                f"Column expects {len(self.specs)} children, "
                f"got {len(self.children)}"
            )
        rows = self.rect.split_horizontal(self.specs)
        for child, rect in zip(self.children, rows, strict=False):
            child.layout(rect)


# ------------------------------------------------------------------ #
# Slide root
# ------------------------------------------------------------------ #
class SlideLayout(Box):
    """
    Root container representing an entire slide.

    The `pptx.Slide` instance is *not* referenced directly – this class
    merely resolves geometry for client code to apply to shapes.
    """

    def __init__(self, slide_width: int, slide_height: int):
        """
        Parameters
        ----------
        slide_width, slide_height : int
            Slide dimensions in EMUs (see `pptx.util.Inches.to_emu`).
        """
        super().__init__()
        self.slide_width = slide_width
        self.slide_height = slide_height

    def resolve(self):
        """Resolve the full layout tree."""
        super().layout(Rect(0, 0, self.slide_width, self.slide_height))