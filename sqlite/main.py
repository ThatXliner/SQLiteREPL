#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlite3 import Cursor, Connection


def main() -> None:
    # Standard Library
    from os.path import expanduser
    import sqlite3
    from argparse import ArgumentParser, Namespace

    # 3rd Party
    from prompt_toolkit import PromptSession, HTML
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, ThreadedAutoSuggest
    from prompt_toolkit.completion import ThreadedCompleter
    from prompt_toolkit.history import ThreadedHistory, FileHistory
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.styles import style_from_pygments_cls
    from pygments.lexers.sql import SqlLexer
    from pygments.styles import get_style_by_name, STYLE_MAP
    from tabulate import tabulate

    # Relative
    from .completer import SQLiteCompleter
    from .meta_cmds import meta_cmds

    parser: ArgumentParser = ArgumentParser(
        prog='SQLiteREPL',
        description='A dead simple REPL for SQLite',
        epilog='bye!')

    parser.add_argument(
        'database',
        help='path to database',
        nargs='?',
        default='./db.sqlite3')

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
        '-M',
        '--memory',
        help='in memory database',
        action='store_true',
        default=False)

    parser.add_argument(
        '--no-history-search',
        dest='historysearch',
        help='disable history search',
        action='store_false',
        default=True)

    parser.add_argument(
        '--no-complete-while-typing',
        dest='completewhiletyping',
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
        '--tablestyle',
        help='set table style to <STYLE> (hint: try "orgtbl", "pipe" or "simple"',
        metavar='STYLE',
        choices=[
            "plain",
            "simple",
            "grid",
            "fancy_grid",
            "pipe",
            "orgtbl",
            "jira",
            "presto",
            "psql",
            "rst",
            "mediawiki",
            "moinmoin",
            "youtrack",
            "html",
            "latex",
            "latex_raw",
            "latex_booktabs",
            "textile",
        ],
        default='simple')

    parser.add_argument(
        '-s',
        '--style',
        metavar='STYLE',
        help='pygments style (see http://pygments.org/docs/styles/#builtin-styles)',
        nargs='?',
        choices=list(STYLE_MAP.keys()),
        default='monokai')

    parser.add_argument(
        '-p',
        '--prompt',
        metavar='STRING',
        help='prompt string',
        nargs='?',
        default='SQLite >> ')

    args: Namespace = parser.parse_args()

    prompt_session: PromptSession = PromptSession(
        bottom_toolbar=((lambda: HTML("SQLite3 REPL | " + " | ".join([i for i in [
            f"<b><style bg=\"ansiblue\">{i}</style></b> {vars(args)[i]}" for i in dir(args) if i[0] != '_'] if
                                                                      not i.endswith("True") and not i.endswith(
                                                                          "False") and not i.startswith(
                                                                          "prompt")]))) if args.infobar else None),
        message=args.prompt,
        history=ThreadedHistory(FileHistory(expanduser(args.history))),
        auto_suggest=ThreadedAutoSuggest(AutoSuggestFromHistory()),
        include_default_pygments_style=False,
        multiline=args.multiline,
        lexer=PygmentsLexer(SqlLexer),
        style=style_from_pygments_cls(get_style_by_name(args.style)),
        completer=ThreadedCompleter(SQLiteCompleter()),
        enable_history_search=args.historysearch,
        complete_while_typing=args.completewhiletyping,
        enable_open_in_editor=args.editor,
    )

    con: Connection = sqlite3.connect(':memory:' if args.memory else expanduser(args.database))

    while True:
        try:
            user_input: str = prompt_session.prompt().strip()
            fired = False

            for cmd in meta_cmds:
                if cmd.test(user_input):
                    cmd.fire(user_input, prompt_session, con)
                    fired = True
                    break

            if fired:
                continue

            elif user_input:
                try:
                    with con as c:
                        cursor: Cursor = c.cursor()
                        cursor.execute(user_input)
                        print(tabulate(cursor.fetchall(), tablefmt=args.tablestyle))
                        cursor.close()

                except (sqlite3.Error, sqlite3.IntegrityError) as e:
                    print(f"An error occurred: {e.args[0]}")

        except (EOFError, KeyboardInterrupt):
            break
