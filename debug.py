"""
Debug helpers — draw layout rectangles on a slide.
Run `python -m pyptx.debug` to generate demo.pptx.
"""
from __future__ import annotations

from pptx import Presentation
from pyptx import  SlideRoot # type: ignore
from pyptx.units import Inch, Auto # type: ignore


# def margins(root: Area,
#     size: Size = Inch(0.5),
#     axis: Literal['horizontal', 'vertical'] = 'horizontal'
# ) -> LayoutItem:
#     if axis == 'horizontal':
#         parent = root.add(Row())
#     elif axis == 'vertical':
#         parent = root.add(Column())

#     parent.add(Box(size))
#     inner = parent.add(Box())
#     parent.add(Box(size))
#     return inner

# def slide_default(root: LayoutItem) -> LayoutItem:
#     center = margins(root,Inch(0.5), 'horizontal')
#     content = margins(center,Inch(0.5), 'vertical')
#     return content

def test_draw_rects(filename: str = "demo.pptx") -> None:
    prs = Presentation()
    root = SlideRoot(prs)

    #Margins
    _,content,_ = root.split_horizontal([Inch(0.75), Auto(), Inch(0.75)])
    _,content,_ = content.split_vertical([Inch(0.75), Auto(), Inch(0.75)])

    # Plots in 4 corners
    row1,_,row2 = content.split_vertical([Auto(), Inch(0.75), Auto()])
    box1,_,box2 = row1.split_horizontal([Auto(), Inch(0.75), Auto()])
    box3,_,box4 = row2.split_horizontal([Auto(), Inch(0.75), Auto()])

    root.resolve()

    row1.debug_rect("row1")
    row2.debug_rect("row2")

    box1.debug_rect("box1")
    box2.debug_rect("box2")
    box3.debug_rect("box3")
    box4.debug_rect("box4")


    root[[0]].debug_rect("Left")
    root[[1,0]].debug_rect("Top")
    root[[1,2]].debug_rect("Bottom")


    # content = slide_default(root)
    # col = content.add(Column())
    # col.add(Box(Ratio(0.1)))
    # row = col.add(Row())
    # img = row.add(Box(Weight(2)))
    # text = row.add(Box(Weight(1)))

    # row.add_box(Ratio(0.3))
    # col = row.add(Column(Ratio(0.5)))
    # col.add(Box(Inch(0.5)))
    # inside = col.add(Row())
    # box1 = inside.add(Box(Weight(2)))
    # box2 = inside.add(Box())
    # col.add(Box(Inch(0.5)))

    # row.add_box()                      # defaults to Weight(1)


    root.prs.save(filename)
    print("saved", filename)


if __name__ == "__main__":
    test_draw_rects()
