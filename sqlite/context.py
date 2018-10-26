from argparse import Namespace
from functools import reduce
from os.path import expanduser
from sqlite3 import Connection
from typing import Any, Optional, Dict

from prompt_toolkit import PromptSession


class Context(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    def __getattr__(self, item: str) -> Optional[Any]:
        return eval(f'self["{item}"]', globals(), locals()) if item in self.keys() else None

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __str__(self):
        s: str = self.__class__.__name__
        s += '\n' + (len(s) * '-')

        size: int = len(reduce(lambda k1, k2: k1 if len(k2) <= len(k1) else k2, self.keys()))

        for k, v in self.items():
            s += f'  %-{size + 2}s %s\n' % (k, str(v))

        s += '\n'

        return s

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_namespace(namespace: Namespace) -> Dict[str, Any]:
        context = Context()
        for k, v in vars(namespace).items():
            context[k] = expanduser(v) if isinstance(v, str) and '~' in v else v
        return context


class SqliteCtxt(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.BROWSER: str = None
        self.CDPATH: str = None
        self.EDITOR: str = None
        self.HOME: str = None
        self.LANG: str = None
        self.LC_ALL: str = None
        self.PAGER: str = None
        self.PATH: str = None
        self.PWD: str = None
        self.complete_while_typing: bool = None
        self.con: Connection = None
        self.database: str = None
        self.editor: bool = None
        self.eval: str = None
        self.history: str = None
        self.history_search: bool = None
        self.infobar: bool = None
        self.memory: bool = None
        self.multiline: bool = None
        self.prompt: str = None
        self.prompt_session: PromptSession = None
        self.readonly: bool = None
        self.style: Any = None
        self.table_style: str = None
        self.user_input: str = None
        self.verbose: bool = None
