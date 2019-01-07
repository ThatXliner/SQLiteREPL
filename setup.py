#!/usr/bin/env python3

"""
SQLite REPL written in python3
"""

# Standard Library
# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os.path import abspath, dirname, join

# 3rd Party
from setuptools import find_packages, setup

# Get the long description from the README file
with open(join(abspath(dirname(__file__)), 'README.md'), encoding='utf-8') as readme:
    setup(name='sqliterepl',

          # Versions should comply with PEP440.  For a discussion on single-sourcing
          # the version across setup.py and the project code, see
          # https://packaging.python.org/en/latest/single_source_version.html
          version='2.0.0a1',

          description='SQLite REPL written in python3',

          long_description=readme.read(),
          long_description_content_type='text/markdown',

          python_requires='>=3.6',

          # The project's main homepage.
          url='https://github.com/nl253/SQLiteREPL',
          project_urls={
              "Bug Tracker": "https://github.com/nl253/SQLiteREPL/issues",
              "Source Code": "https://github.com/nl253/SQLiteREPL",
          },

          # Author details
          author='Norbert Logiewa',
          author_email='norbertlogiewa96@gmail.com',

          # Choose your license
          license='MIT',

          classifiers=[
              'Intended Audience :: Developers',
              'Topic :: Database :: Front-Ends',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3.7',
          ],

          keywords='database sqlite3 sqlite sqliterepl REPL SQLite prompt-toolkit prompt_toolkit',

          packages=find_packages(),

          # List run-time dependencies here.  These will be installed by pip when
          # your project is installed. For an analysis of "install_requires" vs pip's
          # requirements files see:
          # https://packaging.python.org/en/latest/requirements.html

          install_requires=[
              'prompt_toolkit>=2.0',
              'tabulate>=0.8.1', 
              'pygments>=2.2.0',
          ],
          entry_points={
              'console_scripts': ['sqliterepl = sqliterepl.main:main']
          })
