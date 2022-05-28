from cx_Freeze import setup, Executable
from setuptools import find_packages

options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress'
        ],
        'excludes': ['tkinter']
    }
}

executables = [
    Executable('app.py',
               base='console',
               targetName='ThousandSunsServer.exe')
]

setup(
    name='ThousandSuns',
    packages=find_packages(),
    version='0.4.2',
    description='rig',
    executables=executables,
    options=options
)
