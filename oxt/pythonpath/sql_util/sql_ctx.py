from __future__ import annotations
import sqlite3 as sql
from typing import Union, TYPE_CHECKING
from os import PathLike

if TYPE_CHECKING:
    StrPath = Union[str, PathLike[str]]  # stable
    StrOrBytesPath = Union[StrPath, bytes, PathLike[bytes]]  # stable
else:
    StrPath = object
    StrOrBytesPath = object


class SqlCtx:
    """A context manager for sqlite3 connections."""

    # Using a context manager: https://tinyurl.com/y8dplak5
    def __init__(self, connect_str: StrOrBytesPath) -> None:
        """Constructor for SqlCtx

        Args:
            connect_str (str): The connection string for sqlite3.
        """
        self._cstr = connect_str

    def __enter__(self):
        # DateTime for sqlite:
        #   See: https://stackoverflow.com/a/37222799/1171746
        #   See: https://stackoverflow.com/a/1830499/1171746
        self.connection = sql.connect(self._cstr, detect_types=sql.PARSE_DECLTYPES)
        self.connection.row_factory = sql.Row
        self.cursor: sql.Cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def get_connection(self) -> sql.Connection:
        return self.connection
