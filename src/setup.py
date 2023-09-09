from setuptools import setup

setup(
    name='codenitro',
    version='1.0',
    packages=['codenitro'],
    install_requires=[
        'Pillow>=10.0.0',
        'Pygments>=2.15.1',
        'requests>=2.31.0'
    ],
    entry_points={
        'console_scripts': [
            'nitro = nitro.nitro:main',
        ],
    },
)
