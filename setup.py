#!/usr/bin/env python3

"""
SQLite REPL written in python3
"""

# Standard Library
# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os.path import dirname, abspath, join

# 3rd Party
from setuptools import find_packages, setup

# Get the long description from the README file
with open(join(abspath(dirname(__file__)), 'README.rst'), encoding='utf-8') as readme:
    setup(name='sqlite',

          # Versions should comply with PEP440.  For a discussion on single-sourcing
          # the version across setup.py and the project code, see
          # https://packaging.python.org/en/latest/single_source_version.html
          version='1.0.0',

          description='SQLite REPL written in python3',

          long_description=readme.read(),

          # The project's main homepage.
          url='https://github.com/nl253/SQLiteREPL',

          # Author details
          author='Norbert Logiewa',

          author_email='norbertlogiewa96@gmail.com',

          # Choose your license
          license='MIT',

          classifiers=[
              'Intended Audience :: Developers',
              'Topic :: Database :: Front-Ends',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7',
          ],

          keywords='database sqlite3 sqlite REPL SQLite prompt-toolkit prompt_toolkit',

          packages=find_packages(),

          # List run-time dependencies here.  These will be installed by pip when
          # your project is installed. For an analysis of "install_requires" vs pip's
          # requirements files see:
          # https://packaging.python.org/en/latest/requirements.html

          install_requires=['prompt_toolkit>=2.0', 'tabulate>=0.8.1', 'pygments>=2.2.0'],

          entry_points={
              'console_scripts': ['sqlite = sqlite.main:main']
          })
