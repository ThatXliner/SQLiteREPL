#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import getcwd
from sqlite3 import Cursor
from typing import Dict, Any

from .utils import custom_prompt_sess, custom_toolbar
from .log import log


def main() -> None:
    # Standard Library
    from os.path import expanduser
    import sqlite3
    from argparse import ArgumentParser, Namespace

    # 3rd Party
    from pygments.styles import STYLE_MAP
    from tabulate import tabulate

    # Relative
    from .meta_cmds import meta_cmds

    parser: ArgumentParser = ArgumentParser(
        prog='SQLiteREPL',
        description='A dead simple REPL for SQLite',
        epilog='bye!')

    parser.add_argument(
        'database',
        help='path to database',
        nargs='?',
        default=':memory:')

    parser.add_argument(
        '-H',
        '--history',
        metavar='PATH',
        help='path to history file',
        nargs='?',
        default='~/.SqliteREPL_history')

    parser.add_argument(
        '-m',
        '--multiline',
        help='enable multiline mode (useful for creating tables)',
        action='store_true',
        default=False)

    parser.add_argument(
        '-v',
        '--verbose',
        help='enable verbose logging',
        action='store_true',
        default=False)

    parser.add_argument(
        '-M',
        '--memory',
        help='in memory database',
        action='store_true',
        default=False)

    parser.add_argument(
        '--no-history-search',
        dest='history_search',
        help='disable history search',
        action='store_false',
        default=True)

    parser.add_argument(
        '--no-complete-while-typing',
        dest='complete_while_typing',
        help='disable completion while typing',
        action='store_false',
        default=True)

    parser.add_argument(
        '--no-infobar',
        dest='infobar',
        help='disable info bar at the bottom of the screen',
        action='store_false',
        default=True)

    parser.add_argument(
        '--no-editor',
        dest='editor',
        help='disable opening in $EDITOR',
        action='store_false',
        default=True)

    parser.add_argument(
        '-t',
        '--table_style',
        help='set table style to <STYLE> (hint: try "orgtbl", "pipe" or "simple")',
        metavar='STYLE',
        choices=[
            "fancy_grid",
            "grid",
            "html",
            "jira",
            "latex",
            "latex_booktabs",
            "latex_raw",
            "mediawiki",
            "moinmoin",
            "orgtbl",
            "pipe",
            "plain",
            "presto",
            "psql",
            "rst",
            "simple",
            "textile",
            "youtrack",
        ],
        default='simple')

    parser.add_argument(
        '-s',
        '--style',
        metavar='STYLE',
        help='pygments style (see http://pygments.org/docs/styles/#builtin-styles)',
        choices=list(STYLE_MAP.keys()),
        default='monokai')

    parser.add_argument(
        '-p',
        '--prompt',
        metavar='STRING',
        help='prompt string',
        default='SQLite >> ')

    args: Namespace = parser.parse_args()

    if args.verbose:
        import logging

        # initialise logging with sane configuration
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s:%(asctime)s  %(message)s"
        )

    context: Dict[str, Any] = dict()

    for k, v in vars(args).items():
        context[k] = v

    context['database'] = expanduser(args.database) if args.database != ':memory:' else args.database
    context['con'] = sqlite3.connect(context['database'])
    context['prompt_session'] = custom_prompt_sess(context)
    context['cwd'] = getcwd()

    while True:
        try:
            log.info(context)
            context['user_input'] = context['prompt_session'].prompt(
                bottom_toolbar=(lambda: custom_toolbar(context))).strip()
            fired = False

            for cmd in meta_cmds:
                if cmd.test(context['user_input']):
                    cmd.fire(context)
                    fired = True
                    break

            if fired:
                continue

            elif context['user_input']:
                try:
                    with context['con'] as c:
                        cursor: Cursor = c.cursor()
                        cursor.execute(context['user_input'])
                        print(tabulate(cursor.fetchall(), tablefmt=context['table_style']))
                        cursor.close()

                except (sqlite3.Error, sqlite3.IntegrityError) as e:
                    print(f"An error occurred: {e.args[0]}")

        except (EOFError, KeyboardInterrupt):
            break
