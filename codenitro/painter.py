from typing import List
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageColor
import pygments
from pygments.styles import get_style_by_name
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_for_filename
import io
import math
import os


class Painter:
    def __init__(self, image_pad: int):
        self.pad_x = image_pad
        self.pad_y = image_pad

    def add_code_image(
        self,
        text: str,
        line_count: int,
        text_style: str,
        filename: str,
        line_num_start: int,
    ) -> None:
        line_number_chars = int(math.log10(line_count) + 1)
        style = get_style_by_name(text_style)
        formatter: ImageFormatter = ImageFormatter(
            style=style,
            line_number_chars=line_number_chars,
            line_number_start=line_num_start,
            line_number_bg=style.background_color,
            image_pad=20,
            line_number_separator=False,
            full=True,
        )
        lexer = get_lexer_for_filename(filename)
        image_data = pygments.highlight(text, lexer, formatter)
        code_image = Image.open(io.BytesIO(image_data))
        self.code_image = ImageEnhance.Color(code_image).enhance(2)

    def add_background_image(self, image_path: str) -> None:
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), image_path
        )
        print("image_path", image_path)
        size = self._calc_canvas_size()
        canvas = Image.new("RGBA", size, (255, 255, 255, 0))
        bg_image = Image.open(image_path).convert("RGBA")
        x_offset = (size[0] - bg_image.width) // 2
        y_offset = (size[1] - bg_image.height) // 2
        canvas.paste(bg_image, (x_offset, y_offset), bg_image)
        self.bottom_canvas = canvas

    def add_background_gradient(self, gradient_start: str, gradient_end: str) -> None:
        canvas = Image.new("RGBA", self._calc_canvas_size(), color=0)
        draw = ImageDraw.Draw(canvas)

        start = ImageColor.getcolor(gradient_start, "RGB")
        end = ImageColor.getcolor(gradient_end, "RGB")
        deltas: List[float] = [(b - a) / canvas.width / 2 for a, b in zip(start, end)]
        for i, color in enumerate(range(canvas.width * 2)):
            color = [round(s + d * i) for s, d in zip(start, deltas)]
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
        self.bottom_canvas = canvas

    def add_shadow(self, shadow_offset: tuple[int, int] = (8, 8)) -> Image.Image:
        shadow = Image.new("RGBA", self.code_image.size, (20, 20, 20, 255))
        canvas = Image.new("RGBA", self.bottom_canvas.size, (0, 0, 0, 0))
        offset_x = self.pad_x // 2 + shadow_offset[0]
        offset_y = self.pad_y // 2 + shadow_offset[0]
        canvas.paste(shadow, (offset_x, offset_y))
        canvas = canvas.filter(ImageFilter.GaussianBlur(6))
        self.shadow = canvas

    def squash_layers(self) -> Image.Image:
        self.bottom_canvas.paste(self.shadow, (0, 0), mask=self.shadow)
        self.bottom_canvas.paste(self.code_image, (self.pad_x // 2, self.pad_y // 2))
        return self.bottom_canvas

    def _calc_canvas_size(self) -> tuple[int, int]:
        width, height = self.code_image.size
        return (width + self.pad_x, height + self.pad_y)
