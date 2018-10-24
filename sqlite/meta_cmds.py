"""NOTE: commands in sqlite3 are designed to behave in a similar but not the same way as implemented in the official
sqlite3 client. """

# Standard Library
import sqlite3
import sys
from os import getcwd, getenv, remove
from os.path import expanduser, isfile, abspath
from shlex import split
from sqlite3 import Cursor
from subprocess import PIPE, run
from tempfile import NamedTemporaryFile
from typing import List, Optional, Dict, Any

# 3rd Party
from tabulate import tabulate

from .completions import _MetaCmdCompleter
from .log import log
from .utils import custom_prompt_sess


class MetaCmd:
    def __init__(self, *patterns):
        self._patterns = list(patterns)

    def test(self, cmdline: str) -> bool:
        """Check if this command matches the text inserted on the cmdline.
        """
        cmdline = cmdline.strip()
        for pat in self.patterns:
            if cmdline.startswith(pat):
                log.debug(f'running {pat} meta command')
                return True
        return False

    def fire(self, context: Dict[str, Any]) -> None:
        """To be overridden by implementors.
        """
        pass

    def sanitise(self, cmdline: str) -> str:
        """Remove spaces and the command itself from the cmdline and return the result.
        """
        cmdline = cmdline.strip()
        if len(cmdline) == 0:
            return ''
        for pat in self.patterns:
            if cmdline.startswith(pat):
                return cmdline.replace(pat, '').strip()
        return cmdline

    @property
    def patterns(self) -> List[str]:
        """List of patterns that may trigger this command.
        """
        return self._patterns


class ExitCmd(MetaCmd):
    def __init__(self):
        super().__init__(".exit", ".quit")

    def fire(self, context: Dict[str, Any]) -> None:
        log.debug('quitting')
        exit(0)


class HelpCmd(MetaCmd):
    HELP_MSG: str = '\n'.join(
        ["%-10s %-20s %s" % (cmd, pair[0], pair[1]) for cmd, pair in _MetaCmdCompleter.META.items()])

    def __init__(self):
        super().__init__(".help")

    def fire(self, context: Dict[str, Any]) -> None:
        pattern: str = self.sanitise(context['user_input'])
        if not pattern:
            log.debug('displaying all help')
            print(HelpCmd.HELP_MSG)
        else:
            log.info(f'displaying help for {pattern}')
            for line in HelpCmd.HELP_MSG.splitlines():
                if pattern.lower() in line.lower():
                    print(line)


class TablesCmd(MetaCmd):
    def __init__(self):
        super().__init__(".tables")

    def fire(self, context: Dict[str, Any]) -> None:
        pattern: str = self.sanitise(context['user_input'])
        with context['con'] as c:
            cursor: Cursor = c.cursor()
            if not pattern:
                log.debug('showing all tables')
                cursor.execute("SELECT * FROM sqlite_master where type='table'")
            else:
                log.debug(f'showing tables matching {pattern}')
                cursor.execute(f"SELECT * FROM sqlite_master WHERE type='table' AND tbl_name LIKE '%{pattern}%'")

            print(tabulate(cursor.fetchall()))
            cursor.close()


class ShowCmd(MetaCmd):
    def __init__(self):
        super().__init__(".show")

    @staticmethod
    def _docstring(context: Dict[str, Any]) -> str:
        return f'''
SQLite
--------
sqlite                  {sqlite3.sqlite_version}
database                {context['database']}
verbose                 {context['verbose']}

Environment
-----------
CWD                     {context['cwd']}
EDITOR                  {getenv('EDITOR', '?')}
HOME                    {getenv('HOME', '?')}
USER                    {getenv('USER', '?')}
LC_ALL                  {getenv('LC_ALL', '?')}

Styling
-----------
prompt                  {context['prompt_session'].message}
style                   {context['prompt_session'].style}
table style             {context['table_style']}

Prompt Toolkit Main
-------------------
multi-line              {context['prompt_session'].multiline}
editing mode            {context['prompt_session'].editing_mode}

Prompt Toolkit Specifics
------------------------
bottom toolbar          {context["prompt_session"].bottom_toolbar}
wrap lines              {context["prompt_session"].wrap_lines}
right prompt            {context["prompt_session"].rprompt}
mouse support           {context["prompt_session"].mouse_support}
color depth             {context['prompt_session'].color_depth}
history search          {context['prompt_session'].enable_history_search}
search case sensitivity {context['prompt_session'].search_ignore_case}
complete while typing   {context['prompt_session'].complete_while_typing}
complete style          {context['prompt_session'].complete_style}
open in editor          {context['prompt_session'].enable_open_in_editor}

    '''.strip()

    def fire(self, context: Dict[str, Any]) -> None:
        pattern: str = self.sanitise(context['user_input'])
        if not pattern:
            log.debug('showing info')
            print(ShowCmd._docstring(context))
        else:
            log.debug(f'showing info about {pattern}*')
            for line in ShowCmd._docstring(context):
                if line.startswith(pattern):
                    print(line)


class DumpCmd(MetaCmd):
    def __init__(self):
        super().__init__(".dump")

    def fire(self, context: Dict[str, Any]) -> None:
        maybe_file: Optional[str] = expanduser(self.sanitise(context['user_input']))
        if maybe_file:
            log.info(f'performing a database dump to {maybe_file}')
            n = 0
            with open(maybe_file, mode='a', encoding='utf-8') as f:
                for line in context['con'].iterdump():
                    f.write(line + '\n')
                    n += 1
            print(f'wrote database dump to {maybe_file} ({n} lines of SQL)')
        else:
            log.info('performing a database dump to STDOUT')
            for line in context['con'].iterdump():
                print(line)


class OpenCmd(MetaCmd):
    def __init__(self):
        super().__init__(".open")

    def fire(self, context: Dict[str, Any]) -> None:
        file_name: str = expanduser(self.sanitise(context['user_input']))
        if file_name:
            log.info(f'new database path is {file_name}')
            context['con'].commit()
            context['con'].close()
            log.debug(f'closed old connection to {context["database"]}')
            prompt = f'Would you like to create a new database in {abspath(file_name)}? [y/n]\n => '
            if isfile(file_name) or input(prompt).lower().startswith('y'):
                context['con'] = sqlite3.connect(file_name)
                context['database'] = file_name
                log.debug(f'opened new connection to {file_name}')
                log.debug(f'updating prompt_session from modified context')
                context['prompt_session'] = custom_prompt_sess(context)
        else:
            print("please provide file name")


class PrintCmd(MetaCmd):
    def __init__(self):
        super().__init__(".print")

    def fire(self, context: Dict[str, Any]) -> None:
        s: str = self.sanitise(context['user_input'])
        if s:
            print(s)


class ShellCmd(MetaCmd):
    def __init__(self):
        super().__init__(".shell", ".system")

    def fire(self, context: Dict[str, Any]) -> None:
        args: List[str] = [expanduser(arg) if arg.startswith('~') else arg for arg in
                           split(self.sanitise(context['user_input']))]
        log.debug(f'running shell cmd "{" ".join(args)}"')
        print(run(args, stdout=PIPE, encoding='utf-8').stdout, end='')


class LogCmd(MetaCmd):
    def __init__(self):
        super().__init__(".log")

    def fire(self, context: Dict[str, Any]) -> None:
        from logging import DEBUG, WARN
        import logging
        is_verbose: bool = context['verbose']
        maybe_file: Optional[str] = expanduser(self.sanitise(context['user_input']))
        log.setLevel(WARN if is_verbose else DEBUG)

        if (maybe_file.lower() == 'stdout') or (maybe_file == ''):
            log.info(f'redirecting logging to STDOUT')
            logging.basicConfig(stream=sys.__stdout__)

        elif maybe_file:
            log.info(f'redirecting logging to {maybe_file}')
            logging.basicConfig(filename=maybe_file)

        context['verbose'] = not is_verbose

        log.info(f'verbose logging {"on" if context["verbose"] else "off"}')


class PromptCmd(MetaCmd):
    def __init__(self):
        super().__init__(".prompt")

    def fire(self, context: Dict[str, Any]) -> None:
        new_prompt = self.sanitise(context['user_input']) + " "
        log.info(f'changing prompt from {context["prompt"]} to {new_prompt}')
        context['prompt_session'].message = new_prompt


class ModeCmd(MetaCmd):
    def __init__(self):
        super().__init__(".mode")

    def fire(self, context: Dict[str, Any]) -> None:
        new_style = self.sanitise(context['user_input'])
        log.info(f'changing table style from {context["table_style"]} to {new_style}')
        context['table_style'] = new_style


class ReadCmd(MetaCmd):
    def __init__(self):
        super().__init__(".read")

    @staticmethod
    def _docstring(file_name: str) -> str:
        return f'''
-- vim:ft=sql:

-- Copy of {file_name}

-- Verify this script before running it
-- Feel free to modify it or just save & exit to evaluate it as is

'''.lstrip()

    def fire(self, context: Dict[str, Any]) -> None:
        file_name: str = expanduser(self.sanitise(context['user_input']))
        if file_name and isfile(file_name):

            log.info(f'reading SQL script from {file_name}')

            editor: Optional[str] = getenv('EDITOR')

            # $EDITOR env variable is set so open the script with it
            if (editor is not None) or (editor == ''):
                log.debug('editor was set, trying to edit script before running')
                tmp_file = NamedTemporaryFile(mode='a+', encoding='utf-8', delete=False)
                tmp_file.write(ReadCmd._docstring(file_name))
                with open(file_name, encoding='utf-8') as sql_script:
                    tmp_file.write(sql_script.read())
                tmp_file.close()
                run([editor, tmp_file.name])
                with open(tmp_file.name, encoding='utf-8') as tmp_file:
                    query = tmp_file.read()
                remove(tmp_file.name)

            # $EDITOR not set, ask if eval?
            elif input(f'Would you like to eval SQL from {file_name}? [y/n]\n => ').lower().startswith('y'):
                with open(file_name, encoding='utf-8') as sql_script:
                    query = sql_script.read()

            # disagreed to eval
            else:
                return

            try:
                # run the script
                with context['con'] as c:
                    cursor: Cursor = c.cursor()
                    cursor.executescript(query)
                    print(tabulate(cursor.fetchall()))
                    cursor.close()
            except sqlite3.OperationalError as e:
                print(str(e))
        else:
            print("please provide file name")


class OutputCmd(MetaCmd):
    def __init__(self):
        super().__init__(".output")

    def fire(self, context: Dict[str, Any]) -> None:

        file_name: str = expanduser(self.sanitise(context['user_input']))

        if file_name == '' or file_name.lower() == 'stdout':
            log.info("redirecting output to STDOUT")
            sys.stdout = sys.__stdout__

        elif file_name:
            log.info(f'redirecting output to {file_name}')
            sys.stdout = open(file_name, encoding='utf-8', mode='a')


class CdCmd(MetaCmd):
    def __init__(self):
        super().__init__(".cd")

    def fire(self, context: Dict[str, Any]) -> None:
        from os import chdir
        path: str = expanduser(self.sanitise(context['user_input']))
        try:
            chdir(path if path else expanduser('~/'))
            # update cwd (necessary) to keep data in context valid
            context['cwd'] = getcwd()
            log.info(f'changed dir to {context["cwd"]}')
            return
        except FileNotFoundError:
            pass


class BackupCmd(MetaCmd):
    def __init__(self):
        super().__init__(".backup")

    def fire(self, context: Dict[str, Any]) -> None:
        target_file = self.sanitise(context['user_input'])
        if target_file:
            log.info(f'backing up the database to {target_file}')
            with sqlite3.connect(target_file) as backup:
                context['con'].backup(
                    target=backup,
                    progress=(
                        lambda status, remaining, total: print(f'Copied {total - remaining} of {total} pages...')))
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
    ShowCmd(),
    TablesCmd(),
    OpenCmd(),
    ModeCmd(),
    LogCmd(),
    PrintCmd(),
]
