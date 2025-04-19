from pptx.dml.fill import FillFormat
from pptx.dml.line import LineFormat
from pptx.text.text import TextFrame


class Shape:
    fill: FillFormat
    line: LineFormat
    text: str
    text_frame: TextFrame
