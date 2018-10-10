# Standard Library
from typing import List, Set, Iterable
from itertools import chain

# 3rd Party
from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document

Completions = Iterable[Completion]

sql_keywords: Set[str] = {
    'ABORT',
    'ACTION',
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
    'BEGIN TRANSACTION',
    'BEGIN',
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
    'DETACH',
    'DISTINCT',
    'DROP INDEX',
    'DROP TABLE',
    'DROP TRIGGER',
    'DROP VIEW',
    'EACH',
    'ELSE',
    'END',
    'ESCAPE',
    'EXCEPT',
    'EXCLUSIVE',
    'EXISTS',
    'EXPLAIN',
    'FAIL',
    'FOR',
    'FOREIGN',
    'FROM',
    'FULL',
    'GROUP BY',
    'HAVING',
    'IF',
    'IGNORE',
    'IMMEDIATE',
    'IN',
    'INDEX',
    'INDEXED BY',
    'INITIALLY',
    'INNER',
    'INSERT INTO',
    'INSTEAD',
    'INTERSECT',
    'INTO',
    'IS',
    'ISNULL',
    'JOIN',
    'KEY',
    'LEFT',
    'LIKE',
    'LIMIT',
    'MATCH',
    'NATURAL',
    'NO',
    'NOT',
    'NOT NULL',
    'OF',
    'OFFSET',
    'ON CONFLICT',
    'ON',
    'OR',
    'ORDER BY',
    'OUTER',
    'PLAN',
    'PRAGMA',
    'PRIMARY KEY',
    'QUERY',
    'RAISE',
    'RECURSIVE',
    'REFERENCES',
    'REGEXP',
    'REINDEX',
    'RELEASE SAVEPOINT',
    'RENAME',
    'RESTRICT',
    'RIGHT',
    'ROLLBACK',
    'ROW',
    'SAVEPOINT',
    'SELECT',
    'SELECT * FROM',
    'SET',
    'TABLE',
    'TEMP',
    'TEMPORARY',
    'THEN',
    'TO',
    'TRANSACTION',
    'TRIGGER',
    'UNION',
    'UNIQUE',
    'UPDATE',
    'USING',
    'VACUUM',
    'VALUES',
    'VIEW',
    'VIRTUAL',
    'WHEN',
    'WHERE',
    'WITH',
    'WITHOUT'}

sql_tables: Set[str] = {'sqlite_master', 'table_info'}

sql_dtypes: Set[str] = {
    'TEXT',
    'INTEGER',
    'NULL',
    'BLOB',
    'REAL'
}

sql_numeric: Set[str] = {
    'NUMERIC'
    'DECIMAL(10,5)',
    'BOOLEAN',
    'DATE',
    'DATETIME'
}

sql_integer: Set[str] = {
    'INT',
    'MEDIUMINT',
    'SMALLINT',
    'BIGINT',
    'INT2',
    'INT8',
    'TINYINT',
    'UNSIGNED BIG INT'
}

sql_real: Set[str] = {
    'DOUBLE',
    'FLOAT',
    'DOUBLE PRECISION'
}

sql_text: Set[str] = {
    'CHARACTER(20)',
    'CLOB',
    'NATIVE CHARACTER(70)',
    'NCHAR(255)',
    'NVARCHAR(100)'
    'VARCHAR(255)',
    'VARYING CHARACTER(255)',
}

sql_functions: Set[str] = {
    'ABS(',
    'CHANGES(',
    'CHAR(',
    'COALESCE(',
    'DATE(',
    'GLOB(',
    'HEX(',
    'IFNULL(',
    'INSTR(',
    'COUNT(',
    'GROUP_CONCAT(',
    'LAST_INSERT_ROWID(',
    'LAST_INSERT_ROWID()',
    'LENGTH(',
    'LIKE(',
    'LIKELIHOOD(',
    'LIKELY(',
    'LOAD_EXTENSION(',
    'LOWER(',
    'LTRIM(',
    'MAX(',
    'MIN(',
    'NULLIF(',
    'PRINTF(',
    'QUOTE(',
    'QUOTE(',
    'RANDOM(',
    'JULIANDAY(',
    'DATETIME(',
    'RANDOMBLOB(',
    'REPLACE(',
    'ROUND(',
    'RTRIM(',
    'SOUNDEX(',
    'SQLITE_COMPILEOPTION_GET(',
    'SQLITE_COMPILEOPTION_USED(',
    'SQLITE_SOURCE_ID()',
    'SQLITE_VERSION()',
    'SUBSTR(',
    'STRFTIME(',
    'TOTAL_CHANGES()',
    'total('
    'TRIM(',
    'TYPEOF(',
    'UNICODE(',
    'UNLIKELY(',
    'UPPER(',
    'ZEROBLOB('}

sql_meta: Set[str] = {
    'exit',
    '.tables',
    '.quit', }


def sql_completions(doc: Document) -> Completions:
    meta: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="META Command") for i in sql_meta)
    keywords: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="keyword") for i in sql_keywords)
    tables: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="table") for i in sql_tables)
    functions: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="function") for i in sql_functions)
    dtypes: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="data type") for i in sql_dtypes)
    numeric: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="numeric (alias)") for i in sql_numeric)
    text: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="text (alias)") for i in sql_text)
    real: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="real (alias)") for i in sql_real)
    integer: Completions = (Completion(i, start_position=doc.find_boundaries_of_current_word(
        WORD=True)[0], display_meta="integer (alias)") for i in sql_integer)
    return chain(meta, keywords, tables, functions, integer, numeric, real, text, dtypes)
