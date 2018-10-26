from argparse import Namespace
from functools import reduce
from os.path import expanduser
from typing import Any, Optional, Dict


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
