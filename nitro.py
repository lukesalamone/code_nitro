import pygments
from pygments.styles import get_style_by_name
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_for_filename
import requests
import argparse
import math

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

def main(args):
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
    style = get_style_by_name('monokai')
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
    name_part = '.'.join(args.input.split('.')[:-1])
    outname = f'{name_part}.png'
    with open(outname, 'wb') as f:
        f.write(result)
        print(f'saved image to {outname}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='the file to use')
    parser.add_argument('--lines', type=str, help='range of lines to print (defaults to all)')
    args = parser.parse_args()
    main(args)
