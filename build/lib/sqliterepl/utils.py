"""
Many of the functions in this module simply populate the context object with required key-value pairs.
"""

import sqlite3
from logging import Logger, getLogger
from os import getenv
from os.path import expanduser, isfile
from sqlite3 import Cursor
from typing import Dict, Any

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.auto_suggest import ThreadedAutoSuggest, AutoSuggestFromHistory
from prompt_toolkit.history import ThreadedHistory, FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.sql import SqlLexer
from pygments.styles import get_style_by_name
from tabulate import tabulate

from .context import Context, SqliteCtxt
from .completions import SQLiteCompleter

log: Logger = getLogger()


def set_toolbar(context: SqliteCtxt) -> None:
    def custom_toolbar(context: SqliteCtxt) -> HTML:
        s = "SQLite3 REPL"

        def entry(k: str, v: str) -> str:
            return f" | <b><style bg=\"ansiblue\">{k.capitalize()}</style></b> {v}"

        s += entry('database', context.database)
        s += entry('multiline', context.prompt_session.multiline)
        s += entry('directory', context.PWD)
        s += entry('style', context.style)
        s += entry('tables', context.table_style)

        # NOT WORKING
        # s += entry('style', context.prompt_session.style)

        return HTML(s)

    context.prompt_session.bottom_toolbar = lambda: custom_toolbar(context)


def set_db_con(context: SqliteCtxt) -> None:
    if context.readonly:
        if isfile(context.database):
            log.info(f"opening {context.database} in READ-ONLY mode")
            context.database = f'file:{context.database}?mode=ro'
            context.con = sqlite3.connect(context.database, uri=True)
        else:
            raise Exception(f"Database must exist to be opened in READ-ONLY mode.")

    if context.database == ':memory:':
        log.info("opened in-memory database")
        context.con = sqlite3.connect(context.database)

    else:
        if not isfile(context.database):
            print(f"Creating new database in {context.database}.")
        context.con = sqlite3.connect(context.database)


def set_prompt_sess(context: SqliteCtxt) -> None:
    context.prompt_session = PromptSession(
        message=context.prompt,
        history=ThreadedHistory(FileHistory(expanduser(context.history))),
        auto_suggest=ThreadedAutoSuggest(AutoSuggestFromHistory()),
        include_default_pygments_style=False,
        multiline=bool(context.multiline),
        lexer=PygmentsLexer(SqlLexer),
        style=style_from_pygments_cls(get_style_by_name(context.style)),
        completer=SQLiteCompleter(),
        enable_history_search=context.history_search,
        complete_while_typing=context.complete_while_typing,
        enable_open_in_editor=bool(context.editor))

    # bottom_toolbar=((lambda: custom_toolbar(context)) if context.infobar else None),


def set_env_vars(context: SqliteCtxt) -> None:
    for env_var in ['EDITOR', 'PWD', 'PAGER', 'CDPATH', 'PATH', 'BROWSER', 'HOME', 'USER', 'LANG', 'LC_ALL']:
        context[env_var] = getenv(env_var, None)


def set_verbosity(context: SqliteCtxt) -> None:
    if context.verbose:
        import logging

        # initialise logging with sane configuration
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s:%(asctime)s  %(message)s")


def eval_sql_script(context: SqliteCtxt) -> None:
    # evaluate SQL script before entering interactive mode
    if context.eval:
        log.info(f'reading SQL from {context.eval}')
        if isfile(context.eval):
            with context.con as c:
                with open(context.eval, encoding='utf-8') as f:
                    cursor: Cursor = c.cursor()
                    cursor.executescript(f.read())
                    print(tabulate(cursor.fetchall(), tablefmt=context.table_style))
                    cursor.close()
        else:
            raise FileNotFoundError(f'could not read SQL from {context.eval}, not a valid file')
