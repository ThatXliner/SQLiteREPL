# Standard Library
from functools import reduce
from glob import iglob
from os import listdir
from os.path import isfile, expanduser, isdir
from typing import Dict, Generator, Iterable, List, Set

# 3rd Party
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    merge_completers,
    ThreadedCompleter,
)
from prompt_toolkit.document import Document

Completions = Iterable[Completion]

sql_keywords: Iterable[str] = [
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
    'CREATE TEMPORARY VIEW',
    'CREATE TRIGGER',
    'CREATE VIEW',
    'CREATE VIRTUAL TABLE',
    'CROSS',
    'CURRENT_DATE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'DATABASE',
    'DEFAULT',
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

sql_pragmas: Iterable[str] = [
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

sql_agg_functs: Iterable[str] = [i + '(' for i in [
    'avg',
    'count',
    'count',
    'group_concat',
    'group_concat',
    'max',
    'min',
    'sum',
]]

sql_tables: Iterable[str] = [
    'sqlite_master',
    'sqlite_sequence',
]

sql_dtypes: Iterable[str] = [
    'BLOB',
    'INTEGER',
    'NULL',
    'REAL',
    'TEXT',
]

sql_numeric: Iterable[str] = [
    'BOOLEAN',
    'DATE',
    'DATETIME',
    'DECIMAL(10,5)',
    'NUMERIC',
]

sql_integer: Iterable[str] = [
    'BIGINT',
    'INT',
    'INT2',
    'INT8',
    'MEDIUMINT',
    'SMALLINT',
    'TINYINT',
    'UNSIGNED BIG INT',
]

sql_real: Iterable[str] = [
    'DOUBLE PRECISION',
    'DOUBLE',
    'FLOAT',
]

sql_text: Iterable[str] = [
    'CHARACTER(20)',
    'CLOB',
    'NATIVE CHARACTER(70)',
    'NCHAR(255)',
    'NVARCHAR(100)',
    'VARCHAR(255)',
    'VARYING CHARACTER(255)',
]

sql_functions: Iterable[str] = [i + '(' for i in [
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

sql_meta: Dict[str, str] = {f'.{k}': v for k, v in {
    'exit': 'exit the REPL',
    'open': 'close this database and open <database>',
    'help': 'display all available commands',
    'output': 'redirect ouput of commands to <path>',
    'quit': 'exit the REPL',
    'cd': 'change directory to <dir>',
    'read': 'read SQL from <file>',
    'show': 'display info about the REPL',
    'dump': 'stringify database into SQL commands',
    'print': 'display given <string> in the terminal',
    'shell': 'run an OS command <cmd>',
    'system': 'run an OS command <cmd>',
    'prompt': 'change prompt to <str>',
    'tables': 'show all tables in the database',
}.items()}


class MetaCmdSQLiteCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0: return None

        curr_word = doc.get_word_before_cursor(WORD=True)
        curr_word_upper = curr_word.upper()
        curr_word_lower = curr_word.lower()
        start_position, _ = doc.find_boundaries_of_current_word(WORD=True)

        if curr_word.startswith('.'):
            for completion, descr in sql_meta.items():
                if completion.startswith(curr_word_lower) or completion.startswith(curr_word_upper):
                    yield Completion(completion, start_position=start_position, display_meta=descr)
            return


class CustomBinariesCompleter(Completer):
    CACHE: Set[str] = set(reduce(lambda x, y: x + y, [
        [binary for binary in listdir(d) if 2 <= len(binary) <= 12 and binary.find('.') == -1] if isdir(
            d) else [] for d in map(expanduser, ['/usr/bin', '/usr/local/bin', '~/.local/bin'])]))

    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0: return None

        pos, _ = doc.find_boundaries_of_current_word()

        if (doc.text.startswith('.shell') or doc.text.startswith('.system')) and len(doc.current_line.split(' ')) < 3:
            for binary in CustomBinariesCompleter.CACHE:
                if doc.text[doc.cursor_position:].startswith(binary) or binary.startswith(
                        doc.text[doc.cursor_position:]):
                    yield Completion(binary, start_position=pos, display_meta='executable')


class CustomFileSystemCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0:
            return

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


class BaseSQLiteCompleter(Completer):
    def get_completions(self, doc: Document, event: CompleteEvent) -> Generator[Completion, None, None]:

        if len(doc.current_line.strip()) == 0:
            return None

        word = doc.get_word_before_cursor(WORD=True)
        word_upper = word.upper()
        word_lower = word.lower()
        pos = doc.find_boundaries_of_current_word(WORD=True)[0]

        def matches(completion: str) -> bool:
            return completion.startswith(word_lower) or completion.startswith(word_upper)

        def from_iter(words: Iterable[str], meta_info: str) -> Generator[Completion, None, None]:
            for w in filter(matches, words):
                yield Completion(w, start_position=pos, display_meta=meta_info)

        yield from from_iter(sql_pragmas, "pragma")
        yield from from_iter([f'pragma_{i}(' for i in sql_pragmas], "pragma function")
        yield from from_iter(sql_agg_functs, "aggregate function")
        yield from from_iter(sql_keywords, "keyword")
        yield from from_iter(sql_tables, "table")
        yield from from_iter(sql_functions, "function")
        yield from from_iter(sql_dtypes, "data type")
        yield from from_iter(sql_numeric, "NUMERIC (alias)")
        yield from from_iter(sql_text, "TEXT (alias)")
        yield from from_iter(sql_real, "REAL (alias)")
        yield from from_iter(sql_integer, "INTEGER (alias)")


def SQLiteCompleter() -> Completer:
    return ThreadedCompleter(
        merge_completers([
            MetaCmdSQLiteCompleter(),
            CustomBinariesCompleter(),
            CustomFileSystemCompleter(),
            BaseSQLiteCompleter(),
        ]))
