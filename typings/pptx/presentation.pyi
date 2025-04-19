from typing import IO
from pptx.slide import Slide, SlideLayout, SlideLayouts


class Length(int):
    pass

class Presentation:
    slide_width: Length | None
    slide_height: Length | None
    slides: Slides
    slide_layouts: SlideLayouts
    def save(self, file: str | IO[bytes]) -> None:
        pass

class Slides:
    def add_slide(self, layout: SlideLayout) -> Slide:
        pass
