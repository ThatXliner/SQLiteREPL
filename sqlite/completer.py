# Standard Library
from shlex import split
# 3rd Party
from typing import Generator, List

from prompt_toolkit.completion import Completer, CompleteEvent, Completion
from prompt_toolkit.document import Document

# Relative Imports
from completions import sql_completions


class SQLiteCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:
        try:
            args: List[str] = split(doc.current_line.strip())
            if len(args) == 0: return None
            curr_word = doc.get_word_under_cursor(WORD=True)
            yield from (i for i in sql_completions(doc) if
                        i.text.startswith(curr_word.upper()) or i.text.startswith(curr_word))
        except (ValueError, NameError):
            pass
