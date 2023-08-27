from datasette import hookimpl
import sqlite_robotstxt

from datasette_sqlite_robotstxt.version import __version_info__, __version__

@hookimpl
def prepare_connection(conn):
    conn.enable_load_extension(True)
    sqlite_robotstxt.load(conn)
    conn.enable_load_extension(False)
