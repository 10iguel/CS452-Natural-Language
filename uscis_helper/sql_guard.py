"""Rejects model-generated SQL that is not a read-only query."""
import re

_READ_ONLY_START = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)


class UnsafeSqlError(ValueError):
    """Raised when SQL is not a SELECT query."""


def ensure_read_only_select(sql: str) -> None:
    """First line of defence; the database connection itself is also read-only."""
    if not _READ_ONLY_START.match(sql):
        raise UnsafeSqlError(f"Only SELECT queries are allowed, got: {sql[:60]!r}")
