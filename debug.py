"""
Debug helpers — draw layout rectangles on a slide.
Run `python -m pyptx.debug` to generate demo.pptx.
"""
from __future__ import annotations
from typing import Literal, Optional

from pyptx import Presentation, MSO_SHAPE, RGBColor, Pt
from pyptx.core import Column, Rect, LayoutItem, SlideLayout, Row, Box
from pyptx.units import Inch, Ratio, Unit, Weight

# ------------------------------------------------------------------ #
def draw_rect(slide, rect: Rect, *, fill: Optional[str] = None,
              line: str = "FF0000", line_width: int | Pt = 1) -> None:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, rect.x, rect.y, rect.width, rect.height
    )
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill)
    shape.line.color.rgb = RGBColor.from_string(line)
    shape.line.width = line_width if isinstance(line_width, Pt) else Pt(line_width)


def draw_layout(slide, root: LayoutItem, **kw) -> None:
    for node in root.walk():
        if node.rect:
            draw_rect(slide, node.rect, **kw)


def margins(root: LayoutItem,
    size: Unit = Inch(0.5),
    axis: Literal['horizontal', 'vertical'] = 'horizontal'
) -> LayoutItem:
    if axis == 'horizontal':
        parent = root.add(Row())
    elif axis == 'vertical':
        parent = root.add(Column())

    parent.add(Box(size))
    inner = parent.add(Box())
    parent.add(Box(size))
    return inner

def slide_default(root: LayoutItem) -> LayoutItem:
    center = margins(root,Inch(0.5), 'horizontal')
    content = margins(center,Inch(0.5), 'vertical')
    return content

def test_draw_rects(filename: str = "demo.pptx") -> None:
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    assert isinstance(prs.slide_width,int)
    assert isinstance(prs.slide_height,int)
    root = SlideLayout(prs.slide_width, prs.slide_height)

    content = slide_default(root)

    row = content.add(Row())
    img = row.add(Box(Weight(2)))
    text = row.add(Box(Weight(1)))

    # row.add_box(Ratio(0.3))
    # col = row.add(Column(Ratio(0.5)))
    # col.add(Box(Inch(0.5)))
    # inside = col.add(Row())
    # box1 = inside.add(Box(Weight(2)))
    # box2 = inside.add(Box())
    # col.add(Box(Inch(0.5)))

    # row.add_box()                      # defaults to Weight(1)

    root.resolve()
    draw_layout(slide, root, line="00AAFF")
    prs.save(filename)
    print("saved", filename)


if __name__ == "__main__":
    test_draw_rects()
