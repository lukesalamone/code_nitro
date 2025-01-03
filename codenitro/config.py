from typing import Union
from argparse import Namespace
import json
import os

_SYSTEM_CONFIG_DIR = '~/.config/codenitro'
_DEFAULT_CONFIG = {
    # use default themes or add one to ~/.config/codenitro/themes.json
    'theme':'desert',

    # padding around code portion of image
    'image_pad': 100
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

class BlankNamespace:
    pass

class Config:
    '''
    Configurations will be prioritized in the following order:
        1. command-line arguments (highest)
        2. Configuration file
        3. Defaults (lowest)

    The configuration file is stored at ~/.config/codenitro/settings.json and will
    be created on first run.
    '''

    def __init__(self, command_line_args: Union[Namespace, None] = None):
        self._command_line_args = command_line_args if command_line_args else BlankNamespace()
        self._system_config = self._load_system_config()
        self._themes = self._load_themes()
        self._reconcile_configs()

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

    def _reconcile_configs(self):
        def reconcile_single(name):
            if hasattr(self._command_line_args, name) and getattr(self._command_line_args, name) is not None:
                return getattr(self._command_line_args, name)
            if hasattr(self, name):
                return getattr(self, name)
            elif name in self._system_config:
                return self._system_config[name]
            else:
                return _DEFAULT_CONFIG.get(name, None)

        def apply_theme_conf():
            if self.theme not in self._themes:
                raise ValueError(f'Theme {self.theme} not found in themes! (Available: {list(self._themes.keys())})')
            for k,v in self._themes[self.theme].items():
                setattr(self, k, v)

        self.theme = reconcile_single('theme')
        apply_theme_conf()

        self.text_style = reconcile_single('text_style')
        self.image_path = reconcile_single('image_path')
        self.background = reconcile_single('background')

        self.gradient_start = reconcile_single('gradient_start')
        self.gradient_end = reconcile_single('gradient_end')
        self.image_pad = reconcile_single('image_pad')

    def get_theme_property(self, theme_name, val, key):
        if key == 'text_style':
            return self.text_style if val == '' else val
        elif key == 'image_path':
            return self.image_path if val == '' else val
        elif key == 'background':
            return self.image_path if val == '' else val
        elif key == 'gradient_start':
            return self.image_path if val == '' else val
        elif key == 'gradient_end':
            return self.image_path if val == '' else val
        elif key == 'image_pad':
            return self.image_pad if val == -1 else val
        else:
            raise ValueError(f'Unknown key `{key}`')
