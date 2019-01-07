# Standard Library
from functools import reduce
from glob import iglob
from operator import concat
from os import listdir, getenv
from os.path import expanduser, isdir, isfile
from typing import Dict, Generator, Iterable, List, Set

# 3rd Party
from prompt_toolkit.completion import CompleteEvent, Completer, Completion, ThreadedCompleter, merge_completers
from prompt_toolkit.document import Document
from pygments.styles import STYLE_MAP


class _MetaCmdCompleter(Completer):
    META: Dict[str, str] = {f'.{k}': (v[0], v[1] + '.') for k, v in {
        'cd': ("[DIR]", 'Change directory to DIR or $HOME if DIR is not provided'),
        'dump': ("[FILE]", 'Stringify database into SQL commands or STDOUT if FILE is not provided'),
        'exit': ("", 'Exit the REPL'),
        'help': ("[PATTERN]", 'Display meta commands matching PATTERN or ALL if PATTERN is not provided'),
        'mode': ("[STYLE]", 'Change table style to STYLE or display current style if STYLE is not provided'),
        'log': ("[FILE|off]",
                'Redirect (implicitly enable) logging into FILE or disable logging with "off", shows current setting with no arg'),
        'open': (
            "[DATABASE]", 'Close this database and open DATABASE or show current database if DATABASE is not provided'),
        'output': ("[FILE]", 'Redirect output of commands to FILE (or to STDOUT if FILE == "stdout"), shows current '
                             'output stream if FILE is not provided'),
        'print': ("[STRING, ...]", 'Display given STRING in the terminal'),
        'prompt': ("[STRING]", 'Change prompt to STRING'),
        'quit': ("", 'Exit the REPL'),
        'read': ("[FILE]", 'Eval SQL from FILE'),
        'save': ("<FILE>", 'Save in-memory database to FILE'),
        'schema': ("[PATTERN]", 'Show schemas for tables in the database matching PATTERN'),
        'shell': ("<CMD> [ARG, ...]", 'Run an OS command CMD'),
        'show': (
            "[PATTERN]", 'Display info about the REPL starting with PATTERN or all info if PATTERN is not provided'),
        'style': ("[STYLE]", 'Change style to STYLE or show current style if STYLE is not provided'),
        'system': ("<CMD> [ARG, ...]", 'Run an OS command CMD with ARGS'),
        'tables': (
            "[PATTERN]", 'Show tables in the database matching PATTERN or show all tables if PATTERN is not provided'),
    }.items()}

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0 or (not doc.text.strip().startswith('.')):
            return

        curr_word = doc.get_word_before_cursor(WORD=True)
        curr_word_upper = curr_word.upper()
        curr_word_lower = curr_word.lower()
        start_position, _ = doc.find_boundaries_of_current_word(WORD=True)

        # only complete on the *first* word starting with a dot ('.')
        if curr_word.strip() == '' or (len(doc.text.strip().split(' ')) > 1 and curr_word.strip().startswith('.')):
            return

        for completion, pair in _MetaCmdCompleter.META.items():
            syntax, descr = pair
            if completion.startswith(curr_word_lower) or completion.startswith(curr_word_upper):
                yield Completion(completion, start_position=start_position, display_meta=descr)
        return


class _StyleCompleter(Completer):
    STYLES: Set[str] = set(STYLE_MAP.keys())

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if (len(doc.text.strip()) == 0) or (not doc.text.strip().startswith('.style')): return

        curr_word = doc.get_word_before_cursor(WORD=True)
        curr_word_upper = curr_word.upper()
        curr_word_lower = curr_word.lower()
        start_position, _ = doc.find_boundaries_of_current_word(WORD=True)

        for style in _StyleCompleter.STYLES:
            if style.startswith(curr_word_lower) or style.startswith(curr_word_upper):
                yield Completion(style, start_position=start_position, display_meta='style')


class _TableStyleCompleter(Completer):
    STYLES: Set[str] = {
        'orgtbl',
        'simple',
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
    }

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if (len(doc.text.strip()) == 0) or (not doc.text.strip().startswith('.mode')): return

        curr_word = doc.get_word_before_cursor(WORD=True)
        curr_word_upper = curr_word.upper()
        curr_word_lower = curr_word.lower()
        start_position, _ = doc.find_boundaries_of_current_word(WORD=True)

        for style in _TableStyleCompleter.STYLES:
            if style.startswith(curr_word_lower) or style.startswith(curr_word_upper):
                yield Completion(style, start_position=start_position, display_meta='table style')


class _ExecutablesCompleter(Completer):
    from sys import platform
    CACHE: Set[str] = None
    if platform.startswith('win'):
        CACHE = set(
            filter(lambda x: not ('.' in x), reduce(concat, [listdir(d) for d in filter(isdir, filter(bool,
                                                                                                      getenv(
                                                                                                          "PATH").split(
                                                                                                          ';')))])))
    else:
        CACHE = set(
            filter(lambda x: not ('.' in x), reduce(concat, [listdir(d) for d in filter(isdir, filter(bool,
                                                                                                      getenv(
                                                                                                          "PATH").split(
                                                                                                          ':')))])))

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0: return

        curr_word = doc.get_word_before_cursor(WORD=True)
        pos, _ = doc.find_boundaries_of_current_word()

        if (doc.text.startswith('.shell') or doc.text.startswith('.system')) and len(doc.current_line.split(' ')) < 3:
            for binary in _ExecutablesCompleter.CACHE:
                if binary.startswith(curr_word):
                    yield Completion(binary, start_position=pos, display_meta='executable')


class _FileCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:
        if (len(doc.current_line.strip()) == 0) or \
                ((not (doc.text.strip().startswith('.dump'))) and
                 (not doc.text.strip().startswith('.read')) and
                 (not doc.text.strip().startswith('.open')) and
                 (not doc.text.strip().startswith('.log')) and
                 (not doc.text.strip().startswith('.output'))):
            return

        pos, _ = doc.find_boundaries_of_current_word(WORD=True)
        word_ = doc.get_word_under_cursor(WORD=True)
        word = expanduser(word_)

        for node in iglob(expanduser(word_) + '*'):
            if node.startswith(word) and isfile(node):
                yield Completion(node, start_position=pos, display_meta='file')


class _CdCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if (len(doc.current_line.strip()) == 0) or (not doc.text.strip().startswith('.cd')): return

        pos, _ = doc.find_boundaries_of_current_word(WORD=True)
        word_ = doc.get_word_under_cursor(WORD=True)
        word = expanduser(word_)

        for node in iglob(expanduser(word_) + '*'):
            if node.startswith(word) and isdir(node):
                yield Completion(node, start_position=pos, display_meta='dir')
        yield Completion('..', start_position=pos, display_meta='dir (parent dir)')


class _FileSystemCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        # .cd handled by the CdCompleter
        if (len(doc.current_line.strip()) == 0) or doc.text.strip().startswith('.cd'): return

        patterns: List[str] = ['./', '/', '~/']

        pos, _ = doc.find_boundaries_of_current_word(WORD=True)
        word_ = doc.get_word_under_cursor(WORD=True)
        word = expanduser(word_)

        for pattern in patterns:
            if word_.startswith(pattern):
                for node in iglob(expanduser(word_) + '*'):
                    if node.startswith(word):
                        yield Completion(node, start_position=pos, display_meta=('file' if isfile(node) else 'dir'))
                return


class _SQLCompleter(Completer):
    KEYWORDS: Iterable[str] = [
        'ABORT',
        'ACTION',
        'ADD COLUMN',
        'ADD',
        'ADD',
        'AFTER',
        'ALL',
        'ALTER DATABASE',
        'ALTER TABLE',
        'ANALYZE',
        'AND',
        'ASC',
        'ATTACH DATABASE',
        'AUTOINCREMENT',
        'BEFORE',
        'BEGIN DEFERRED TRANSACTION',
        'BEGIN EXCLUSIVE TRANSACTION',
        'BEGIN IMMEDIATE TRANSACTION',
        'BEGIN TRANSACTION',
        'BETWEEN',
        'BY',
        'CASCADE',
        'CASE',
        'CAST',
        'CHECK',
        'COLLATE',
        'COLUMN',
        'COMMIT TRANSACTION',
        'CONFLICT',
        'CONSTRAINT',
        'CREATE INDEX',
        'CREATE TABLE',
        'CREATE TRIGGER',
        'CREATE VIEW',
        'CREATE VIRTUAL TABLE',
        'CREATE TEMPORARY VIEW',
        'CREATE TEMPORARY TABLE',
        'CREATE TEMPORARY TRIGGER',
        'CREATE TEMPORARY INDEX',
        'CREATE TEMPORARY VIRTUAL TABLE',
        'CREATE TEMPORARY VIEW IF NOT EXISTS',
        'CREATE TEMPORARY TABLE IF NOT EXISTS',
        'CREATE TEMPORARY TRIGGER IF NOT EXISTS',
        'CREATE TEMPORARY INDEX IF NOT EXISTS',
        'CREATE TEMPORARY VIRTUAL TABLE IF NOT EXISTS',
        'CROSS',
        'CURRENT_DATE',
        'CURRENT_TIME',
        'CURRENT_TIMESTAMP',
        'DATABASE',
        'DEFAULT',
        'DEFAULT VALUES',
        'DEFERRABLE',
        'DEFERRED',
        'DELETE',
        'DESC',
        'DETACH DATABASE',
        'DISTINCT',
        'DROP INDEX',
        'DROP TABLE',
        'DROP TRIGGER',
        'DROP VIEW',
        'ELSE',
        'END TRANSACTION',
        'ESCAPE',
        'EXCEPT',
        'EXCLUSIVE',
        'EXISTS',
        'EXPLAIN',
        'FAIL',
        'FOR EACH ROW',
        'FOR',
        'FOREIGN',
        'FROM',
        'FULL',
        'GROUP BY',
        'HAVING',
        'IF EXISTS',
        'IF NOT EXISTS',
        'IF',
        'IGNORE',
        'IMMEDIATE',
        'IN',
        'INDEX',
        'INDEXED BY',
        'INITIALLY',
        'INNER',
        'INSERT INTO',
        'INSERT OR ABORT INTO',
        'INSERT OR FAIL INTO',
        'INSERT OR IGNORE INTO',
        'INSERT OR REPLACE INTO',
        'INSERT OR ROLLBACK INTO',
        'INSTEAD OF',
        'INTERSECT',
        'INTO',
        'IS NOT',
        'IS',
        'ISNULL',
        'JOIN',
        'KEY',
        'LEFT',
        'LIKE',
        'LIMIT',
        'MATCH',
        'NATURAL',
        'NOT BETWEEN',
        'NOT EXISTS',
        'NOT GLOB',
        'NOT IN',
        'NOT INDEXED',
        'NOT LIKE',
        'NOT MATCH',
        'NOT NULL',
        'NOT REGEXP',
        'NOT',
        'NOTNULL',
        'OF',
        'OFFSET',
        'ON CONFLICT ABORT',
        'ON CONFLICT FAIL',
        'ON CONFLICT IGNORE',
        'ON CONFLICT REPLACE',
        'ON CONFLICT ROLLBACK',
        'ON CONFLICT',
        'ON',
        'OR',
        'ORDER BY',
        'OUTER',
        'OVER',
        'PLAN',
        'PRAGMA',
        'PRIMARY KEY',
        'QUERY PLAN',
        'QUERY',
        'RAISE',
        'RECURSIVE',
        'REFERENCES',
        'REGEXP',
        'REINDEX',
        'RELEASE SAVEPOINT',
        'RENAME COLUMN',
        'RENAME TO',
        'RENAME',
        'REPLACE',
        'RESTRICT',
        'RIGHT',
        'ROLLBACK TO SAVEPOINT',
        'ROLLBACK TRANSACTION TO SAVEPOINT',
        'ROLLBACK TRANSACTION',
        'ROW',
        'SAVEPOINT',
        'SELECT * FROM',
        'SELECT',
        'SET',
        'TABLE',
        'TEMPORARY',
        'THEN',
        'TO',
        'TRANSACTION',
        'TRIGGER',
        'UNION',
        'UNIQUE',
        'UPDATE OR ABORT',
        'UPDATE OR FAIL',
        'UPDATE OR IGNORE',
        'UPDATE OR REPLACE',
        'UPDATE OR ROLLBACK',
        'UPDATE',
        'USING',
        'VACUUM',
        'VALUES',
        'VIEW',
        'VIRTUAL',
        'WHEN',
        'WHERE',
        'WITH',
        'WITHOUT',
    ]
    PRAGMAS: Iterable[str] = [
        'application_id',
        'auto_vacuum',
        'automatic_index',
        'busy_timeout',
        'cache_size',
        'cache_spill',
        'case_sensitive_like',
        'cell_size_check',
        'checkpoint_fullfsync',
        'collation_list',
        'compile_options',
        'data_version',
        'database_list',
        'encoding',
        'foreign_key_check',
        'foreign_key_list',
        'foreign_keys',
        'freelist_count',
        'fullfsync',
        'function_list',
        'ignore_check_constraints',
        'incremental_vacuum',
        'index_info',
        'index_list',
        'index_xinfo',
        'integrity_check',
        'journal_mode',
        'journal_size_limit',
        'legacy_alter_table',
        'legacy_file_format',
        'locking_mode',
        'max_page_count',
        'mmap_size',
        'module_list',
        'optimize',
        'page_count',
        'page_size',
        'parser_trace',
        'pragma_list',
        'query_only',
        'quick_check',
        'read_uncommitted',
        'recursive_triggers',
        'reverse_unordered_selects',
        'shrink_memory',
        'soft_heap_limit',
        'stats',
        'synchronous',
        'table_info',
        'temp_store',
        'threads',
        'user_version',
        'vdbe_addoptrace',
        'vdbe_debug',
        'vdbe_listing',
        'vdbe_trace',
        'wal_autocheckpoint',
        'wal_checkpoint',
        'writable_schema',
    ]
    AGGR_FUNCTS: Iterable[str] = [i + '(' for i in [
        'avg',
        'count',
        'count',
        'group_concat',
        'group_concat',
        'max',
        'min',
        'sum',
    ]]
    TABLES: Iterable[str] = [
        'sqlite_master',
        'sqlite_sequence',
    ]
    FUNCTS: Iterable[str] = [i + '(' for i in [
        'abs',
        'changes',
        'char',
        'coalesce',
        'date',
        'glob',
        'hex',
        'ifnull',
        'instr',
        'count',
        'group_concat',
        'last_insert_rowid',
        'length',
        'like',
        'likelihood',
        'likely',
        'load_extension',
        'lower',
        'ltrim',
        'max',
        'min',
        'nullif',
        'printf',
        'quote',
        'quote',
        'random',
        'julianday',
        'datetime',
        'randomblob',
        'replace',
        'round',
        'rtrim',
        'soundex',
        'sqlite_compileoption_get',
        'sqlite_compileoption_used',
        'sqlite_source_id',
        'sqlite_version',
        'substr',
        'strftime',
        'total_changes',
        'total',
        'trim',
        'typeof',
        'unicode',
        'unlikely',
        'upper',
        'zeroblob',
    ]]
    DTYPES: Iterable[str] = [
        'BLOB',
        'INTEGER',
        'NULL',
        'REAL',
        'TEXT',
    ]
    NUMERIC: Iterable[str] = [
        'BOOLEAN',
        'DATE',
        'DATETIME',
        'DECIMAL(10,5)',
        'NUMERIC',
    ]
    TEXT: Iterable[str] = [
        'CHARACTER(20)',
        'CLOB',
        'NATIVE CHARACTER(70)',
        'NCHAR(255)',
        'NVARCHAR(100)',
        'VARCHAR(255)',
        'VARYING CHARACTER(255)',
    ]
    REAL: Iterable[str] = [
        'DOUBLE PRECISION',
        'DOUBLE',
        'FLOAT',
    ]
    INTEGER: Iterable[str] = [
        'BIGINT',
        'INT',
        'INT2',
        'INT8',
        'MEDIUMINT',
        'SMALLINT',
        'TINYINT',
        'UNSIGNED BIG INT',
    ]

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0 or doc.text.strip().startswith('.'):
            return

        word = doc.get_word_before_cursor(WORD=True)
        word_upper = word.upper()
        word_lower = word.lower()
        pos = doc.find_boundaries_of_current_word(WORD=True)[0]

        def matches(completion: str) -> bool:
            return completion.startswith(word_lower) or completion.startswith(word_upper)

        def from_iter(words: Iterable[str], meta_info: str) -> Generator[Completion, None, None]:
            for w in filter(matches, words):
                yield Completion(w, start_position=pos, display_meta=meta_info)

        yield from from_iter(_SQLCompleter.PRAGMAS, "pragma")
        yield from from_iter([f'pragma_{i}(' for i in _SQLCompleter.PRAGMAS], "pragma function")
        yield from from_iter(_SQLCompleter.AGGR_FUNCTS, "aggregate function")
        yield from from_iter(_SQLCompleter.KEYWORDS, "keyword")
        yield from from_iter(_SQLCompleter.TABLES, "table")
        yield from from_iter(_SQLCompleter.FUNCTS, "function")
        yield from from_iter(_SQLCompleter.DTYPES, "data type")
        yield from from_iter(_SQLCompleter.NUMERIC, "NUMERIC (alias)")
        yield from from_iter(_SQLCompleter.TEXT, "TEXT (alias)")
        yield from from_iter(_SQLCompleter.REAL, "REAL (alias)")
        yield from from_iter(_SQLCompleter.INTEGER, "INTEGER (alias)")


def SQLiteCompleter() -> Completer:
    return ThreadedCompleter(
        merge_completers([
            _MetaCmdCompleter(),
            _ExecutablesCompleter(),
            _FileSystemCompleter(),
            _TableStyleCompleter(),
            _FileCompleter(),
            _StyleCompleter(),
            _CdCompleter(),
            _SQLCompleter(),
        ]))
