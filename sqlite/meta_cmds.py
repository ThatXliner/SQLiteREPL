import sqlite3
from shlex import split
from sqlite3 import Connection, Cursor
from subprocess import run, PIPE
from typing import List
from tabulate import tabulate

from prompt_toolkit import PromptSession


class MetaCmd:
    def __init__(self, *patterns, **kwargs):
        self._patterns = list(patterns)

    def test(self, cmdline: str) -> bool:
        cmdline = cmdline.strip()
        for pat in self.patterns:
            if cmdline.startswith(pat):
                return True
        return False

    def fire(self, cmdline: str, sess: PromptSession, con) -> None:
        pass

    def sanitise(self, cmdline: str) -> str:
        cmdline = cmdline.strip()
        for pat in self.patterns:
            if cmdline.startswith(pat):
                return cmdline.replace(pat, '').strip()
        return cmdline

    @property
    def patterns(self) -> List[str]:
        return self._patterns


class ExitCmd(MetaCmd):
    def __init__(self):
        super().__init__(".exit", ".quit")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        exit(0)


class HelpCmd(MetaCmd):
    def __init__(self):
        super().__init__(".help")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        print('''
.cd DIRECTORY          Change the working directory to DIRECTORY
.dump                  Dump the database in an SQL text format
.exit                  Exit this program
.help                  Show this message
.output ?FILE?         Send output to FILE or stdout
.print STRING...       Print literal STRING
.prompt MAIN           Replace the prompt
.quit                  Exit this program
.read FILENAME         Execute SQL in FILENAME
.shell CMD ARGS...     Run CMD ARGS... in a system shell
.show                  Show the current values for various settings
.system CMD ARGS...    Run CMD ARGS... in a system shell
.tables                List names of tables'''.strip())


class TablesCmd(MetaCmd):
    def __init__(self):
        super().__init__(".tables")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        with con as c:
            cursor: Cursor = c.cursor()
            cursor.execute("SELECT * FROM sqlite_master where type='table'")
            print(tabulate(cursor.fetchall()))
            cursor.close()


class ShowCmd(MetaCmd):
    def __init__(self):
        super().__init__(".show")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        print(f'''
sqlite                  {sqlite3.sqlite_version}

style                   {sess.style}
prompt                  {sess.message}        
editing mode            {sess.editing_mode}        
color depth             {sess.color_depth}        
multiline               {sess.multiline}        
history search          {sess.enable_history_search}        
search case sensitivity {sess.search_ignore_case}        
complete while typing   {sess.complete_while_typing}        
complete style          {sess.complete_style}        
open in editor          {sess.enable_open_in_editor}        
''')


class DumpCmd(MetaCmd):
    def __init__(self):
        super().__init__(".dump")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        for line in con.iterdump():
            print(line)


class PrintCmd(MetaCmd):
    def __init__(self):
        super().__init__(".print")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        s = self.sanitise(cmdline)
        if s:
            print(s)


class ShellCmd(MetaCmd):
    def __init__(self):
        super().__init__(".shell", ".system")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        print(run(split(self.sanitise(cmdline)), stdout=PIPE, encoding='utf-8').stdout, end='')


class PromptCmd(MetaCmd):
    def __init__(self):
        super().__init__(".prompt")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        sess.message = self.sanitise(cmdline) + " "


class ReadCmd(MetaCmd):
    def __init__(self):
        super().__init__(".read")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        file_name: str = self.sanitise(cmdline)
        if file_name:
            with open(file_name, encoding='utf-8') as f:
                with con as c:
                    cursor: Cursor = c.cursor()
                    cursor.execute(f.read())
                    print(tabulate(cursor.fetchall()))
                    cursor.close()
        else:
            print("please provide file name")


class OutputCmd(MetaCmd):
    def __init__(self):
        super().__init__(".output")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        import sys
        file_name: str = self.sanitise(cmdline)
        if file_name:
            sys.stdout = open(file_name, encoding='utf-8', mode='a+')
        else:
            print("please provide file name")


class CdCmd(MetaCmd):
    def __init__(self):
        super().__init__(".cd")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        from os import chdir
        path: str = self.sanitise(cmdline)
        if path:
            try:
                chdir(path)
                return
            except FileNotFoundError:
                pass
        print('print provide a valid destination path')


class BackupCmd(MetaCmd):
    def __init__(self):
        super().__init__(".backup")

    def fire(self, cmdline: str, sess: PromptSession, con: Connection) -> None:
        target_file = self.sanitise(cmdline)
        if target_file:
            def progress(status, remaining, total):
                print(f'Copied {total-remaining} of {total} pages...')

            with sqlite3.connect(target_file) as backup:
                con.backup(target=backup, progress=progress)
        else:
            print('please provide output path')


meta_cmds: List[MetaCmd] = [
    ExitCmd(),
    HelpCmd(),
    CdCmd(),
    PromptCmd(),
    ReadCmd(),
    ShellCmd(),
    DumpCmd(),
    OutputCmd(),
    TablesCmd(),
    PrintCmd(),
]
