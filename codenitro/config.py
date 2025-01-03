from typing import Union
from argparse import Namespace
import json
import os

_SYSTEM_CONFIG_DIR = '~/.config/codenitro'
_DEFAULT_CONFIG = {
    # use default themes or add one to ~/.config/codenitro/themes.json
    'theme':'desert',

    # padding around code portion of image
    'image_pad': 100,

    # these properties will be overridden by "theme" if it is set
    'text_style':'coffee',
    'image_path':'images/desert.png',
    'background': 'image',
    'gradient_start': '#09afd4',
    'gradient_end': '#341a6e'
}

_DEFAULT_THEMES = {
    'desert':{
        # text styles can be found on https://pygments.org/styles
        'text_style':'coffee',

        # path to background image
        'image_path':'images/desert.png',

        # valid values are "gradient" or "none"
        'background':'image'
    },
    'blue': {
        # linear gradient from top left to bottom right
        'background': 'gradient',

        'text_style':'monokai',

        # hex color format of top-left corner of gradient
        'gradient_start': '#09afd4',

        # hex color format of bottom-right corner of gradient
        'gradient_end': '#341a6e'
    },
    'moon':{
        'background':'image',
        'text_style':'dracula',
        'image_path':'images/moon.png',
    },
    'forest':{
        'background':'image',
        'text_style':'gruvbox-dark',
        'image_path':'images/forest.png',
    },
    'cool':{
        'background': 'gradient',
        'text_style':'monokai',
        'gradient_start': '#1faf98',
        'gradient_end': '#dab4ff'
    }
}

class Config:
    '''
    Configurations will be prioritized in the following order:
        1. command-line arguments (highest)
        2. Configuration file
        3. Defaults (lowest)

    The configuration file is stored at ~/.config/codenitro/settings.json and will
    be created on first run.
    '''

    def __init__(self, command_line_args: Union[Namespace, dict] = {}):
        self._themes = self._load_themes()
        self._parse_default_config()
        self._parse_system_config(self._load_system_config())
        self._parse_command_line_args(command_line_args)

    def _parse_config(self, conf):
        '''
        Properties from the theme will be overridden if they are directly specified.
        '''
        if 'theme' in conf:
            theme = conf['theme']
            if theme not in self._themes:
                raise ValueError(
                    f'Theme {theme} not found in themes! (Available: {list(self._themes.keys())})'
                )
            for k,v in self._themes[theme].items():
                setattr(self, k, v)
        for k,v in conf.items():
            setattr(self, k, v)

    def _parse_default_config(self):
        self._parse_config(_DEFAULT_CONFIG)

    def _parse_system_config(self, config):
        self._parse_config(config)

    def _parse_command_line_args(self, args):
        args = args if type(args) == dict else vars(args)
        args = {k:v for k,v in args.items() if v not in (None, '', -1)}
        self._parse_config(args)

    def _load_system_config(self):
        system_config_dir = os.path.expanduser(_SYSTEM_CONFIG_DIR)
        system_config_path = os.path.join(system_config_dir, 'settings.json')
        os.makedirs(system_config_dir, exist_ok=True)

        if not os.path.exists(system_config_path):
            with open(system_config_path, 'w') as f:
                json.dump(_DEFAULT_CONFIG, f, indent=4)
        with open(system_config_path) as f:
            return json.load(f)

    def _load_themes(self):
        system_config_dir = os.path.expanduser(_SYSTEM_CONFIG_DIR)
        system_themes_path = os.path.join(system_config_dir, 'themes.json')

        if not os.path.exists(system_themes_path):
            with open(system_themes_path, 'w') as f:
                json.dump(_DEFAULT_THEMES, f, indent=4)
        with open(system_themes_path) as f:
            return json.load(f)

__all__ = [
    'Config'
]
