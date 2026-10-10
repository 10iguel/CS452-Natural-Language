"""Read-only access to the USCIS checklist SQLite database."""
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from uscis_helper.sql_guard import ensure_read_only_select

MAX_RESULT_ROWS = 50


class QueryExecutionError(Exception):
    """Raised when SQLite rejects or fails to run a query."""


class UnknownUserError(LookupError):
    """Raised when no user has the given email."""


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]
    truncated: bool


class ChecklistDatabase:
    def __init__(self, path: Path):
        self._path = path

    def describe_schema(self) -> str:
        """The CREATE TABLE statements, straight from the database."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        return "\n\n".join(sql for (sql,) in rows)

    def find_user_id(self, email: str) -> str:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
        if row is None:
            raise UnknownUserError(f"No user with email {email!r}")
        return row[0]

    def run_query(self, sql: str, parameters: Mapping[str, str] | None = None) -> QueryResult:
        ensure_read_only_select(sql)
        try:
            with closing(self._connect()) as connection:
                cursor = connection.execute(sql, parameters or {})
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)
        except sqlite3.Error as error:
            raise QueryExecutionError(str(error)) from error
        return QueryResult(
            columns=columns,
            rows=rows[:MAX_RESULT_ROWS],
            truncated=len(rows) > MAX_RESULT_ROWS,
        )

    def _connect(self) -> sqlite3.Connection:
        # mode=ro makes SQLite itself refuse writes, whatever the model generates.
        return sqlite3.connect(f"{self._path.resolve().as_uri()}?mode=ro", uri=True)
