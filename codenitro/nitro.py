import pygments
from pygments.styles import get_style_by_name
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_for_filename
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageColor
import requests
import argparse
import math
import io

from config import Config

def add_shadow_and_gradient(
        image_data,
        background=None,
        gradient_start='#fff',
        gradient_end='#000',
        image_path='',
        image_pad=0):
    def add_gradient(size):
        gradient = Image.new('RGBA', size, color=0)
        draw = ImageDraw.Draw(gradient)

        start: tuple[int, ...] = ImageColor.getcolor(gradient_start, "RGB")
        end: tuple[int, ...] = ImageColor.getcolor(gradient_end, "RGB")
        deltas = [(b - a) / gradient.width / 2 for a, b in zip(start, end)]
        for i, color in enumerate(range(gradient.width * 2)):
            color = [round(s + d * i) for s,d in zip(start, deltas)]
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
        return gradient
    def add_image(size):
        canvas = Image.new('RGBA', size, (255, 255, 255, 0))
        bg_image = Image.open(image_path).convert("RGBA")
        x_offset = (size[0] - bg_image.width) // 2
        y_offset = (size[1] - bg_image.height) // 2
        canvas.paste(bg_image, (x_offset, y_offset), bg_image)
        return canvas
    def make_shadow(code_dims, img_dims, offset_dims):
        shadow = Image.new('RGBA', code_dims, (20, 20, 20, 255))
        shadow_holder = Image.new('RGBA', img_dims, (0,0,0,0))
        shadow_holder.paste(shadow, offset_dims)
        shadow_holder = shadow_holder.filter(ImageFilter.GaussianBlur(6))
        return shadow_holder
    image = Image.open(io.BytesIO(image_data))
    image = ImageEnhance.Color(image).enhance(2)
    pad_x, pad_y = image_pad, image_pad
    offset_x, offset_y = 8, 8
    width, height = image.size

    if background == 'gradient':
        bottom_canvas = add_gradient((width+pad_x, height+pad_y))
    else:
        bottom_canvas = add_image((width+pad_x, height+pad_y))

    shadow = make_shadow(
        code_dims=(width, height),
        img_dims=(width+pad_x, height+pad_y),
        offset_dims=(pad_x//2+offset_x, pad_y//2+offset_y)
    )
    bottom_canvas.paste(shadow, (0, 0), mask=shadow)
    bottom_canvas.paste(image, (pad_x//2, pad_y//2))
    return bottom_canvas

def load_from_github(url) -> tuple[str, str]:
    def convert_url(url):
        return '/'.join(url.split('/blob/')).replace('github.com/', 'raw.githubusercontent.com/')

    assert 'github.com' in url, 'input url is not from github'
    url = convert_url(url)
    try:
        response = requests.get(url)
        fname = url.split('/')[-1]
        return response.text, fname
    except:
        print(f'failed to download from url {url}')
        return '', ''

def load_from_file(fname) -> tuple[str, str]:
    with open(fname) as f:
        text = f.read()
    return text, fname

def get_range(lines_str) -> tuple[int, int]:
    scope = lines_str.split('-')
    assert len(scope) == 2, 'incorrect format for lines arg'
    start, end = [int(x) for x in scope]
    return start, end

def code_to_image(
        file_input=None,
        text_input=None,
        link_input=None,
        line_range=None,
        theme='desert',
        text_style='',
        background='',
        gradient_start='',
        gradient_end='',
        image_path='',
        image_pad=-1,
        outpath=None,
        save=True):
    if len([x for x in [file_input, text_input, link_input] if x]) != 1:
        raise ValueError(
            'Exactly one of file_input, text_input, or link_input must be specified.'
        )

    # user-specified theme will override sub-properties
    if theme:
        config = Config()
        text_style = config.get_theme_property(theme, text_style, 'text_style')
        background = config.get_theme_property(theme, background, 'background')
        gradient_start = config.get_theme_property(theme, gradient_start, 'gradient_start')
        gradient_end = config.get_theme_property(theme, gradient_end, 'gradient_end')
        image_path = config.get_theme_property(theme, image_path, 'image_path')
        image_pad = config.get_theme_property(theme, image_pad, 'image_pad')

    fname = 'default_filename.py'
    if text_input:
        text = text_input
        lines = text_input.split('\n')
    else:
        if link_input != None:
            text, fname = load_from_github(link_input)
        else:
            text, fname = load_from_file(file_input)
        lines = text.split('\n')
    start = 1
    line_count = len(lines)
    if line_range:
        start, end = get_range(line_range)
        print(f'including only lines in range {start} - {end}')
        text = '\n'.join(lines[start-1:end])

    line_number_chars = int(math.log10(line_count) + 1)
    style = get_style_by_name(text_style)
    formatter = ImageFormatter(
        style=style,
        line_number_chars=line_number_chars,
        line_number_start=start,
        line_number_bg=style.background_color,
        image_pad=20,
        line_number_separator=False,
        full=True)

    lexer = get_lexer_for_filename(fname)
    result = pygments.highlight(text, lexer, formatter)
    name_part = '.'.join(fname.split('.')[:-1])

    if not outpath:
        outpath = f'{name_part}.png'

    if background != 'none':
        result = add_shadow_and_gradient(
            image_data=result,
            background=background,
            gradient_start=gradient_start,
            gradient_end=gradient_end,
            image_path=image_path,
            image_pad=image_pad)

    if not save:
        return result

    with open(outpath, 'wb') as f:
        if isinstance(result, Image.Image):
            result.save(f)
        else:
            f.write(result)
        print(f'saved image to {outpath}')

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='the file to use')
    parser.add_argument('--lines', type=str, help='range of lines to print (defaults to all)')
    parser.add_argument('--theme', type=str, help='theme to use')
    parser.add_argument('--text_style', type=str, help='text color scheme')
    parser.add_argument('--image_pad', type=int, help='padding around code in pixels')
    parser.add_argument('--background', type=str, help='gradient / none')
    args = parser.parse_args()

    config = Config(command_line_args=args)
    text_input, link_input, file_input = None, None, None

    if 'http://' in args.input or 'https://' in args.input:
        link_input = args.input
    else:
        file_input = args.input

    code_to_image(
        file_input=file_input,
        text_input=text_input,
        link_input=link_input,
        line_range=args.lines,
        theme=config.theme,
        text_style=config.text_style,
        background=config.background,
        gradient_start=config.gradient_start,
        gradient_end=config.gradient_end,
        image_path=config.image_path,
        image_pad=config.image_pad,
        outpath=None,
        save=True
    )

if __name__ == '__main__':
    main()

__all__ = [
    'code_to_image'
]
