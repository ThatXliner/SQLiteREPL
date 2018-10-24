from os.path import expanduser
from typing import Dict, Any

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.auto_suggest import ThreadedAutoSuggest, AutoSuggestFromHistory
from prompt_toolkit.history import ThreadedHistory, FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.sql import SqlLexer
from pygments.styles import get_style_by_name

from .completions import SQLiteCompleter


def custom_toolbar(context: Dict[str, Any]) -> HTML:
    s = "SQLite3 REPL"

    def entry(k: str, v: str) -> str:
        return f" | <b><style bg=\"ansiblue\">{k.capitalize()}</style></b> {v}"

    s += entry('database', context['database'])
    s += entry('multiline', context['prompt_session'].multiline)
    s += entry('directory', context['cwd'])
    s += entry('tables', context['table_style'])

    # NOT WORKING
    # s += entry('style', context['prompt_session'].style)

    return HTML(s)


def custom_prompt_sess(context: Dict[str, Any]) -> PromptSession:
    return PromptSession(
        bottom_toolbar=((lambda: custom_toolbar(context)) if context.get('infobar') else None),
        message=context['prompt'],
        history=ThreadedHistory(FileHistory(expanduser(context['history']))),
        auto_suggest=ThreadedAutoSuggest(AutoSuggestFromHistory()),
        include_default_pygments_style=False,
        multiline=bool(context['multiline']),
        lexer=PygmentsLexer(SqlLexer),
        style=style_from_pygments_cls(get_style_by_name(context['style'])),
        completer=SQLiteCompleter(),
        enable_history_search=context['history_search'],
        complete_while_typing=context['complete_while_typing'],
        enable_open_in_editor=bool(context['editor']),
    )
