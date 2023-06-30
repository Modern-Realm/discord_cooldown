from discord_cooldown.modules import *

from typing import Tuple, Any, Union, List, TypeVar

__all__ = [
    "Database"
]

_RowSet = Tuple[Any, ...]
_MultiRowSet = List[_RowSet]
_Configs = Union[SQlite, MySQL, PostgreSQL]

RowSet = TypeVar("RowSet", _RowSet, None)
MultiRowSet = TypeVar("MultiRowSet", bound=_MultiRowSet)
ResultSet = Union[RowSet, MultiRowSet]


class Database:
    def __init__(self, config: _Configs):
        self.config: _Configs = config
        self.conn = None

        self.fmtr: str = self.config.fmtr
        self.table_prefix = self.config.table_prefix

    def connect(self) -> None:
        if isinstance(self.config, PostgreSQL):
            import psycopg2

            self.conn = psycopg2.connect(**self.config.kwargs)
        elif isinstance(self.config, MySQL):
            import mysql.connector as mysql

            self.conn = mysql.connect(**self.config.kwargs)
        else:
            import sqlite3

            self.conn = sqlite3.connect(**self.config.kwargs)

    @property
    def is_connected(self) -> bool:
        return self.conn is not None

    @staticmethod
    def _fetch(cursor, mode: str) -> ResultSet:
        if mode == "one":
            return cursor.fetchone()
        if mode == "many":
            return cursor.fetchmany()
        if mode == "all":
            return cursor.fetchall()

        return None

    def execute(
        self, query: str, values: Tuple[Any, ...] = (),
        *, fetch: str = "one",
    ) -> ResultSet:
        cursor = self.conn.cursor()

        cursor.execute(query, values)
        data = self._fetch(cursor, fetch)

        cursor.close()
        return data

    def run(self, query: str, values: Tuple[Any, ...] = ()) -> None:
        cursor = self.conn.cursor()

        cursor.execute(query, values)
        self.conn.commit()

        cursor.close()
