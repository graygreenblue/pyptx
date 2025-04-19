
from pptx.shapes.shapetree import SlideShapes


class SlideLayout:
    pass

class Slide:
    shapes: SlideShapes

class SlideLayouts:
    def __getitem__(self, idx: int) -> SlideLayout:
        pass
