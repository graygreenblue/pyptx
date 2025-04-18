"""
Core layout engine – per‑child units, one shared add_box().
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, TypeVar, Union

from loguru import logger

from .errors import LayoutStateError, SpecMismatchError
from .units import Unit, Weight, resolve_length_span

# ------------------------------------------------------------------ #
@dataclass(slots=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    # helpers --------------------------------------------------------
    def split_vertical(self, specs: List[Unit]) -> List["Rect"]:
        widths, cursor, out = resolve_length_span(specs, self.width), self.x, []
        for w in widths:
            out.append(Rect(cursor, self.y, w, self.height))
            cursor += w
        return out

    def split_horizontal(self, specs: List[Unit]) -> List["Rect"]:
        heights, cursor, out = resolve_length_span(specs, self.height), self.y, []
        for h in heights:
            out.append(Rect(self.x, cursor, self.width, h))
            cursor += h
        return out


# ------------------------------------------------------------------ #
ChildT = TypeVar("ChildT", bound="LayoutItem")

class LayoutItem:
    """Base node; can contain any LayoutItem subclass as a child."""

    def __init__(self, unit: Unit|None = None) -> None:
        self.children: List["LayoutItem"] = []
        self.rect: Optional[Rect] = None
        self.unit: Optional[Unit] = unit          # size relative to parent

    # public --------------------------------------------------------
    def add(self, item: ChildT) -> ChildT:
        self.children.append(item)
        return item

    def add_box(self, unit: Unit | None = None) -> "Box":
        """
        Convenience: create a Box, set its *unit*, add it, and return it.

        If *unit* is omitted, Weight(1) is used so you don't have to specify
        sizes up‑front.
        """
        box = Box()
        box.unit = unit or Weight(1)      # set size before adding
        self.add(box)
        return box

    def with_unit(self, unit: Unit) -> "LayoutItem":
        """Fluent helper to set this item's unit and return self."""
        self.unit = unit
        return self

    def __getitem__(self, idx: Union[int, tuple[int, ...]]) -> ChildT:
        node: LayoutItem = self
        if isinstance(idx, int):
            return node.children[idx]          # type: ignore[return-value]
        for i in idx:
            node = node.children[i]
        return node                             # type: ignore[return-value]

    def walk(self) -> Iterable["LayoutItem"]:
        yield self
        for c in self.children:
            yield from c.walk()

    # layout helpers -----------------------------------------------
    def _rect(self) -> Rect:
        if self.rect is None:
            raise LayoutStateError("LayoutItem has no rect; call resolve() first")
        return self.rect

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        logger.debug(f"{self.__class__.__name__}.layout -> {rect}")
        self._layout_children()

    # subclasses override ------------------------------------------
    def _layout_children(self) -> None: ...


# ------------------------------------------------------------------ #
class Box(LayoutItem):
    def _layout_children(self) -> None:
        self._rect()
        if not self.children:
            return
        if len(self.children) != 1:
            raise SpecMismatchError("Box supports exactly one child")
        self.children[0].layout(self._rect())


class Row(LayoutItem):
    """Horizontal splitter (children laid out in columns)."""

    def _layout_children(self) -> None:
        units = [c.unit or Weight(1) for c in self.children]
        for child, rect in zip(self.children, self._rect().split_vertical(units)):
            child.layout(rect)


class Column(LayoutItem):
    """Vertical splitter (children stacked in rows)."""

    def _layout_children(self) -> None:
        units = [c.unit or Weight(1) for c in self.children]
        for child, rect in zip(self.children, self._rect().split_horizontal(units)):
            child.layout(rect)


class Folds(LayoutItem):
    """Generic splitter – choose axis='horizontal' or 'vertical'."""

    def __init__(self, axis: str) -> None:
        super().__init__()
        if axis not in ("horizontal", "vertical"):
            raise ValueError("axis must be 'horizontal' or 'vertical'")
        self.axis = axis

    def _layout_children(self) -> None:
        units = [c.unit or Weight(1) for c in self.children]
        parts = (
            self._rect().split_horizontal(units)
            if self.axis == "horizontal"
            else self._rect().split_vertical(units)
        )
        for child, rect in zip(self.children, parts):
            child.layout(rect)


# Root container ----------------------------------------------------
class SlideLayout(Box):
    def __init__(self, width: int, height: int) -> None:
        super().__init__()
        self.slide_width, self.slide_height = width, height

    def resolve(self) -> None:
        super().layout(Rect(0, 0, self.slide_width, self.slide_height))
