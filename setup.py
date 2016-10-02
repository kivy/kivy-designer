#!/usr/bin/env python
import codecs
import os

import re

import io
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def find_version(*file_paths):
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'utf-8') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

curdir = os.path.dirname(__file__)
with io.open(os.path.join(curdir, "README.md"), encoding="utf-8") as fd:
    readme = fd.read()


setup(
    name='kivy-designer',
    version=find_version('designer', '__init__.py'),
    url='https://github.com/kivy/kivy-designer',
    description='UI designer for Kivy',
    long_description=readme,
    author='Kivy\'s Developers and Contributors.',
    packages=find_packages(exclude=('tests', 'tests.*')),
    package_data={'designer': ['*.rst', '*.kv', '*.ini', 'data/icons/*',
                               'data/new_templates/*',
                               'data/new_templates/images/*',
                               'data/profiles/*',
                               'data/settings/*',
                               'tools/ssh-agent/*']},
    license='MIT',
    install_requires=[
        'kivy >= 1.9.1',
        'pygments >= 2.1',
        'docutils >= 0.12',
        'watchdog >= 0.8',
        'jedi >= 0.9',
        'gitpython >= 1.0',
        'six >= 1.10.0',
        'kivy-garden'],

    entry_points={
        'gui_scripts': [
            'kivydesigner=designer.__main__:main',
        ]
    }
)
