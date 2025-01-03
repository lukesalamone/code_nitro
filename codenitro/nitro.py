from typing import Union
from PIL import Image
import requests
import argparse

from config import Config
from painter import Painter

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
        file_input: Union[str, None] = None,
        text_input: Union[str, None] = None,
        link_input: Union[str, None] = None,
        line_range: Union[str, None] = None,
        theme: str = 'desert',
        text_style: str = '',
        background: str = '',
        gradient_start: str = '',
        gradient_end: str = '',
        image_path: str = '',
        image_pad: int = -1,
        outpath: str = '',
        save: bool = True):
    """
    Convert code from a file, text input, or GitHub link to an image.

    :param file_input: Path to the source file.
    :param text_input: Code as a string.
    :param link_input: URL of a GitHub repository.
    :param line_range: Range of lines to include in the output (e.g., '1-5').
    :param theme: Pygments theme for syntax highlighting.
    :param text_style: Style for the text color and background.
    :param background: Background style ('gradient', 'image' or 'none').
    :param gradient_start: Start color for gradient.
    :param gradient_end: End color for gradient.
    :param image_path: Path to an image to be added in background (requires background='image').
    :param image_pad: Padding around the code in pixels.
    :param outpath: Output file path. If not specified, defaults to 'default_filename.png' or
        <input path>.png depending on input type.
    :param save: Whether to save the output to a file.
    """
    if len([x for x in [file_input, text_input, link_input] if x]) != 1:
        raise ValueError(
            'Exactly one of file_input, text_input, or link_input must be specified.'
        )

    config = Config({
        'theme':theme,
        'text_style':text_style,
        'background':background,
        'gradient_start':gradient_start,
        'gradient_end':gradient_end,
        'image_path':image_path,
        'image_pad':image_pad
    })

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

    name_part = '.'.join(fname.split('.')[:-1])

    start = 1
    line_count = len(lines)
    if line_range:
        start, end = get_range(line_range)
        print(f'including only lines in range {start} - {end}')
        text = '\n'.join(lines[start-1:end])

    painter = Painter(image_pad=config.image_pad)
    painter.add_code_image(
        text=text,
        line_count=line_count,
        text_style=config.text_style,
        filename=fname,
        line_num_start=start
    )


    if not outpath:
        outpath = f'{name_part}.png'

    if config.background in ('image', 'gradient'):
        if config.background == 'image':
            painter.add_background_image(image_path=config.image_path)
        else:
            painter.add_background_gradient(
                gradient_start=config.gradient_start,
                gradient_end=config.gradient_end
            )
        painter.add_shadow()
        result = painter.squash_layers()

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
    parser.add_argument('--background', type=str, help='image / gradient / none')
    parser.add_argument('--gradient_start', type=str, help='top left color for gradient, hex format')
    parser.add_argument('--gradient_end', type=str, help='bottom right color for gradient, hex format')
    parser.add_argument('--image_path', type=str, help='if background="image", path to background image')
    parser.add_argument('--image_pad', type=int, help='padding around code in pixels')
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
        image_pad=config.image_pad
    )

if __name__ == '__main__':
    main()

__all__ = [
    'code_to_image'
]
