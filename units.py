"""
Unit abstractions for specifying sizes in the layout engine.

Resolution order (two‑pass):

1. **First pass** – walk the spec list, summing:
   • *total_fixed*  := absolute + ratio lengths (in EMUs)
   • *total_weights* := sum of `Weight.weight` values

2. **Second pass** – compute *available* := parent − total_fixed
   then resolve every spec via `Unit.resolve(parent, available, total_weights)`.

This lets every `Unit` decide its final size in one call during the second pass.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

import pptx.

EMUS_PER_INCH = 914400
EMUS_PER_CM = int(EMUS_PER_INCH / 2.54)


# ------------------------------------------------------------------------- #
# Abstract base
# ------------------------------------------------------------------------- #
class Unit(ABC):
    """Abstract base for all length/width units."""

    @abstractmethod
    def resolve(
        self,
        parent_size_emu: int,
        available_space_emu: int,
        total_weights: float,
    ) -> int:
        """
        Return size in EMUs.

        Parameters
        ----------
        parent_size_emu
            Total size of the parent container.
        available_space_emu
            Parent minus *total_fixed* (≥ 0). Only meaningful for `Weight`.
        total_weights
            Sum of all `Weight.weight` values in the sibling list.
        """


# ------------------------------------------------------------------------- #
# Absolute units
# ------------------------------------------------------------------------- #
class Inch(Unit):
    """Absolute length specified in inches."""

    def __init__(self, inches: float):
        self.inches = float(inches)

    def resolve(self, parent_size_emu: int, available_space_emu: int, total_weights: float) -> int:  # noqa: N803,E501
        return int(self.inches * EMUS_PER_INCH)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Inch({self.inches})"


class Centimeter(Unit):
    """Absolute length specified in centimeters."""

    def __init__(self, cm: float):
        self.cm = float(cm)

    def resolve(self, parent_size_emu: int, available_space_emu: int, total_weights: float) -> int:  # noqa: N803,E501
        return int(self.cm * EMUS_PER_CM)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Centimeter({self.cm})"


# ------------------------------------------------------------------------- #
# Relative units
# ------------------------------------------------------------------------- #
class Ratio(Unit):
    """Fraction of the *parent* size (0 ≤ ratio ≤ 1)."""

    def __init__(self, ratio: float):
        if not (0.0 <= ratio <= 1.0):
            raise ValueError("Ratio must be in range [0, 1]")
        self.ratio = float(ratio)

    def resolve(self, parent_size_emu: int, available_space_emu: int, total_weights: float) -> int:  # noqa: N803,E501
        return int(parent_size_emu * self.ratio)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Ratio({self.ratio})"


class Weight(Unit):
    """
    Weighted portion of *available* space.
    Resolved after absolutes & ratios, based on `weight / total_weights`.
    """

    def __init__(self, weight: float = 1.0):
        if weight <= 0:
            raise ValueError("Weight must be positive")
        self.weight = float(weight)

    def resolve(self, parent_size_emu: int, available_space_emu: int, total_weights: float) -> int:  # noqa: N803,E501
        if total_weights == 0:
            raise ValueError("total_weights must be > 0 when Weight units present")
        share = available_space_emu * (self.weight / total_weights)
        return int(share)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Weight({self.weight})"


# ------------------------------------------------------------------------- #
# Utility
# ------------------------------------------------------------------------- #
def resolve_length_span(
    specs: Sequence[Unit],
    total_emu: int,
) -> list[int]:
    """
    Resolve a sequence of *Unit* specs into absolute EMU sizes.

    Two‑pass algorithm (see module docstring).

    Raises
    ------
    OverflowError
        If the specified absolute/ratio units exceed *total_emu*.
    """
    from .errors import OverflowError
    total_fixed = 0
    total_weights = 0.0

    # First pass – gather totals
    for spec in specs:
        if isinstance(spec, Weight):
            total_weights += spec.weight
        else:
            total_fixed += spec.resolve(total_emu, 0, 0)

    available = total_emu - total_fixed
    if available < 0:
        raise OverflowError(
            f"Layout overspecified by {-available} EMUs "
            f"(parent size: {total_emu}, specs: {specs!r})"
        )

    # Second pass – final resolution
    resolved: list[int] = [
        spec.resolve(total_emu, available, total_weights) for spec in specs
    ]
    return resolved
