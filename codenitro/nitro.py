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

def add_shadow_and_gradient(image_data, config, use_gradient=False):
    def add_gradient(size):
        gradient = Image.new('RGBA', size, color=0)
        draw = ImageDraw.Draw(gradient)

        start = ImageColor.getcolor(config.gradient_start, "RGB")
        end = ImageColor.getcolor(config.gradient_end, "RGB")
        deltas = [(b - a) / gradient.width / 2 for a, b in zip(start, end)]
        for i, color in enumerate(range(gradient.width * 2)):
            color = [round(s + d * i) for s,d in zip(start, deltas)]
            draw.line([(i, 0), (0, i)], tuple(color), width=1)
        return gradient
    def add_image(size):
        canvas = Image.new('RGBA', size, (255, 255, 255, 0))
        additional_image = Image.open(config.image_path).convert("RGBA")
        x_offset = (size[0] - additional_image.width) // 2
        y_offset = (size[1] - additional_image.height) // 2
        canvas.paste(additional_image, (x_offset, y_offset), additional_image)
        return canvas
    def make_shadow(code_dims, img_dims, offset_dims):
        shadow = Image.new('RGBA', code_dims, (20, 20, 20, 255))
        shadow_holder = Image.new('RGBA', img_dims, (0,0,0,0))
        shadow_holder.paste(shadow, offset_dims)
        shadow_holder = shadow_holder.filter(ImageFilter.GaussianBlur(6))
        return shadow_holder
    image = Image.open(io.BytesIO(image_data))
    image = ImageEnhance.Color(image).enhance(2)
    pad_x, pad_y = config.image_pad, config.image_pad
    offset_x, offset_y = 8, 8
    width, height = image.size

    if config.background == 'gradient':
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

def load_from_github(url):
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

def load_from_file(fname):
    with open(fname) as f:
        text = f.read()
    return text, fname

def get_range(lines_str):
    scope = lines_str.split('-')
    assert len(scope) == 2, 'incorrect format for lines arg'
    start, end = [int(x) for x in scope]
    return start, end

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

    if 'http://' in args.input or 'https://' in args.input:
        text, fname = load_from_github(args.input)
    else:
        text, fname = load_from_file(args.input)

    start = 1
    lines = text.split('\n')
    line_count = len(lines)
    if args.lines:
        start, end = get_range(args.lines)
        print(f'including only lines in range {start} - {end}')
        text = '\n'.join(lines[start-1:end])

    line_number_chars = int(math.log10(line_count) + 1)
    style = get_style_by_name(config.text_style)
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
    outname = f'{name_part}.png'
    if not config.background == 'none':
        result = add_shadow_and_gradient(result, config)
    with open(outname, 'wb') as f:
        if isinstance(result, Image.Image):
            result.save(f)
        else:
            f.write(result)
        print(f'saved image to {outname}')

if __name__ == '__main__':
    main()
