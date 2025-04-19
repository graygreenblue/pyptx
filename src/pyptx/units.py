"""
Unit abstractions for specifying sizes in the layout engine.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence

from .errors import OverflowError

import pptx.util as _pptx_util
from pptx.util import Emu

EMUS_PER_INCH = _pptx_util.Inches(1).emu
EMUS_PER_CM = _pptx_util.Cm(1).emu
EMUS_PER_PT = _pptx_util.Pt(1).emu

class Size(ABC):
    @abstractmethod
    def resolve(
        self,
        parent_size_emu: Emu,
        available_space_emu: Emu,
        total_weights: float,
    ) -> Emu: ...


class Inch(Size):
    def __init__(self, inches: float): self.inches = float(inches)
    def resolve(self, parent_size_emu: Emu, available_space_emu: Emu, total_weights: float) -> Emu:
        return Emu(int(self.inches * EMUS_PER_INCH))
    def __repr__(self): return f"Inch({self.inches})"


class Centimeter(Size):
    def __init__(self, cm: float): self.cm = float(cm)
    def resolve(self, parent_size_emu: Emu, available_space_emu: Emu, total_weights: float) -> Emu:
        return Emu(int(self.cm * EMUS_PER_CM))
    def __repr__(self): return f"Centimeter({self.cm})"


class Ratio(Size):
    def __init__(self, ratio: float):
        if not 0 <= ratio <= 1:
            raise ValueError("Ratio must be between 0 and 1")
        self.ratio = float(ratio)
    def resolve(self, parent_size_emu: Emu, available_space_emu: Emu, total_weights: float) -> Emu:
        return Emu(int(parent_size_emu * self.ratio))
    def __repr__(self): return f"Ratio({self.ratio})"


class Auto(Size):
    def __init__(self, weight: float = 1.0):
        if weight <= 0: raise ValueError
        self.weight = float(weight)
    def resolve(self, parent_size_emu: Emu, available_space_emu: Emu, total_weights: float) -> Emu:
        if total_weights <= 0: raise ValueError("total_weights must be > 0")
        return Emu(int(available_space_emu * (self.weight / total_weights)))
    def __repr__(self): return f"Weight({self.weight})"


def resolve_length_span(specs: Sequence[Size], total_emu: Emu) -> list[Emu]:
    total_fixed = Emu(0)
    total_w = 0.0
    for s in specs:
        if isinstance(s, Auto):
            total_w += s.weight
        else:
            total_fixed += s.resolve(total_emu, Emu(0), Emu(0))

    avail = total_emu - total_fixed
    if avail < 0:
        raise OverflowError("Specified lengths exceed parent size")

    return [s.resolve(total_emu, Emu(avail), total_w) for s in specs]
