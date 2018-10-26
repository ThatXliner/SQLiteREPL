#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
# Standard Library
from argparse import ArgumentParser, Namespace
from sqlite3 import Cursor

# 3rd Party
from pygments.styles import STYLE_MAP
from tabulate import tabulate

from .context import Context, SqliteCtxt
# Relative
from .meta_cmds import meta_cmds
from .utils import set_db_con, log, set_prompt_sess, set_toolbar, set_env_vars, set_verbosity


def main() -> None:
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
        '-e',
        '--eval',
        default=False,
        metavar='FILE',
        nargs='?',
        help='eval SQL script before running the REPL')

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
        '--readonly',
        help='open the database is READ-ONLY mode',
        action='store_true',
        default=False)

    parser.add_argument(
        '--no-editor',
        dest='editor',
        help='disable opening in $EDITOR',
        action='store_false',
        default=True)

    parser.add_argument(
        '-t',
        '--table_style',
        help='set table style to <STYLE>, (see https://pypi.org/project/tabulate/) (hint: try "simple", "orgtbl", "pipe", "html" or "latex")',
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
        default='default')

    parser.add_argument(
        '-p',
        '--prompt',
        metavar='STRING',
        help='prompt string',
        default='SQLite >> ')

    args: Namespace = parser.parse_args()

    context: SqliteCtxt = Context.from_namespace(args)

    set_verbosity(context)
    set_db_con(context)
    set_prompt_sess(context)
    set_env_vars(context)

    while True:
        try:
            log.debug(context)
            # refreshes it so that it displays up-to-date info
            set_toolbar(context)
            context.user_input = context.prompt_session.prompt().strip()
            fired = False

            for cmd in meta_cmds:
                if cmd.test(context.user_input):
                    cmd.fire(context)
                    fired = True
                    break

            if fired:
                continue

            elif context.user_input:
                try:
                    with context.con as c:
                        cursor: Cursor = c.cursor()
                        cursor.execute(context.user_input)
                        print(tabulate(cursor.fetchall(), tablefmt=context.table_style))
                        cursor.close()

                except (sqlite3.Error, sqlite3.IntegrityError) as e:
                    print(f"An error occurred: {e.args[0]}")

        except (EOFError, KeyboardInterrupt):
            break
