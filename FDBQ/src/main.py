#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os.path
from pprint import pprint

db_path = os.path.expanduser("~/.db")
conn = sqlite3.connect(db_path)
curr = conn.cursor()
query = curr.execute

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from completer import MyCustomCompleter
# from styling import custom_style, SqliteConsoleLexer, PygmentsLexer

# initialise variables
user_input = ""

# used for fish-like history completion
history = InMemoryHistory()

while user_input != 'exit':
    # offer suggestions from history from history
    user_input = prompt('SQLite >> ',
                        history=history,
                        multiline=False,
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=MyCustomCompleter())
                        # style=custom_style,
                        # lexer=PygmentsLexer(SqliteConsoleLexer),
    try:
        q = query(user_input)
        for i in q:
            pprint(i)

    except sqlite3.Error as e:
        print("An error occurred:", e.args[0])

conn.commit()
curr.close()
conn.close()
