# SQLite REPL written in Python3

## Good completion

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/6.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/1.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/2.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/3.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/7.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/8.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/9.png)

![](https://raw.githubusercontent.com/nl253/SQLiteREPL/master/screens/10.png)

```
usage: SQLiteREPL [-h] [-H [PATH]] [-e [FILE]] [-m] [-v] [-M]
                  [--no-history-search] [--no-complete-while-typing]
                  [--no-infobar] [--no-editor] [-t STYLE] [-s STYLE]
                  [-p STRING]
                  [database]

A dead simple REPL for SQLite

positional arguments:
  database              path to database

optional arguments:
  -h, --help            show this help message and exit
  -H [PATH], --history [PATH]
                        path to history file
  -e [FILE], --eval [FILE]
                        eval SQL script before running the REPL
  -m, --multiline       enable multiline mode (useful for creating tables)
  -v, --verbose         enable verbose logging
  -M, --memory          in memory database
  --no-history-search   disable history search
  --no-complete-while-typing
                        disable completion while typing
  --no-infobar          disable info bar at the bottom of the screen
  --no-editor           disable opening in $EDITOR
  -t STYLE, --table_style STYLE
                        set table style to <STYLE>, (see
                        https://pypi.org/project/tabulate/) (hint: try
                        "simple", "orgtbl", "pipe", "html" or "latex")
  -s STYLE, --style STYLE
                        pygments style (see
                        http://pygments.org/docs/styles/#builtin-styles)
  -p STRING, --prompt STRING
                        prompt string
```

## Modify REPL whilst it's running  

The following `.meta` commands are supported:

```
   .dump [FILE]            Stringify database into SQL commands or STDOUT if FILE is not provided.
  .exit                   Exit the REPL.
  .help [PATTERN]         Display meta commands matching PATTERN or ALL if PATTERN is not provided.
  .mode [STYLE]           Change table style to STYLE or display current style if STYLE is not provided.
  .open [DATABASE]        Close this database and open DATABASE or show current database if DATABASE is not provided.
.output [FILE]            Redirect output of commands to FILE (or to STDOUT if FILE == "stdout"), shows current output stream if FILE is not provided.
 .print [STRING, ...]     Display given STRING in the terminal.
.prompt [STRING]          Change prompt to STRING.
  .quit                   Exit the REPL.
  .read [FILE]            Eval SQL from FILE.
  .save <FILE>            Save in-memory database to FILE.
.schema [PATTERN]         Show schemas for tables in the database matching PATTERN.
 .shell <CMD> [ARG, ...]  Run an OS command CMD.
  .show [PATTERN]         Display info about the REPL starting with PATTERN or all info if PATTERN is not provided.
 .style [STYLE]           Change style to STYLE or show current style if STYLE is not provided.
.system <CMD> [ARG, ...]  Run an OS command CMD with ARGS.
.tables [PATTERN]         Show tables in the database matching PATTERN or show all tables if PATTERN is not provided.
```

**NOTE**:

These are actually a subset of what the official sqlite3 REPL supports. The syntax is kept similar.

**NOTE**:

unless you specify the database location with database, it will be
loaded in memory.

## Customisation

- check out pygments for all the possible styles
- check out tabulate for all the table types
- use aliases for "semi-permanent" config e.g.: `alias sqlite='sqliterepl --multiline'`

## Compatibility

It should work on Win10 and Linux.

## Installation

```sh
$ pip install --user sqliterepl
```

**NOTE** <br>
make sure your `~/.local/bin` (GNU/Linux) or `~\AppData\Roaming\Python\Python<VERSION>\Scripts` (Win10) dir is in `$PATH`.

## Running

```sh
$ sqliterepl
```

## Limitations

-   not context sensitive
-   doesn't complete table names
-   no table headings

## Dependencies

- [prompt-toolkit](https://github.com/jonathanslenders/python-prompt-toolkit)
- [tabulate](https://pypi.org/project/tabulate/)
- Python >= 3.7

**Note**:

SQLiteREPL has been updated to use `prompt_toolkit 2`.

## Related

-   <https://github.com/dbcli/mycli>

