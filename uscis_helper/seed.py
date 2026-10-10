"""Builds the SQLite database from schema.sql and the static seed data."""
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from uscis_helper.config import SCHEMA_PATH
from uscis_helper.seed_data import CHECKLISTS, FORMS, USERS

_ID_NAMESPACE = uuid.UUID("5f0c1a52-8d4e-4d6a-9a53-2f1f3c1b7a10")
_COMPLETED_AT = "2026-09-15 10:00:00"


def _stable_id(*parts: str) -> str:
    """Deterministic ids keep the demo database (and documented examples) reproducible."""
    return str(uuid.uuid5(_ID_NAMESPACE, "/".join(parts)))


def build_database(path: Path) -> None:
    path.unlink(missing_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _insert_users(connection)
        _insert_forms(connection)
        _insert_checklists(connection)
        connection.commit()


def _insert_users(connection: sqlite3.Connection) -> None:
    connection.executemany(
        "INSERT INTO users (id, email, name) VALUES (?, ?, ?)",
        [(_stable_id("user", user.email), user.email, user.name) for user in USERS],
    )


def _insert_forms(connection: sqlite3.Connection) -> None:
    for form in FORMS:
        form_id = _stable_id("form", form.form_code)
        connection.execute(
            "INSERT INTO uscis_forms (id, form_code, title, description, official_url) "
            "VALUES (?, ?, ?, ?, ?)",
            (form_id, form.form_code, form.title, form.description, form.official_url),
        )
        connection.executemany(
            "INSERT INTO form_requirements "
            "(id, form_id, title, description, is_required, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    _stable_id("requirement", form.form_code, str(position)),
                    form_id,
                    requirement.title,
                    requirement.description,
                    requirement.is_required,
                    position,
                )
                for position, requirement in enumerate(form.requirements)
            ],
        )


def _insert_checklists(connection: sqlite3.Connection) -> None:
    requirement_counts = {form.form_code: len(form.requirements) for form in FORMS}
    for checklist in CHECKLISTS:
        checklist_id = _stable_id("checklist", checklist.user_email, checklist.form_code)
        connection.execute(
            "INSERT INTO checklists (id, user_id, form_id, status) VALUES (?, ?, ?, ?)",
            (
                checklist_id,
                _stable_id("user", checklist.user_email),
                _stable_id("form", checklist.form_code),
                checklist.status,
            ),
        )
        connection.executemany(
            "INSERT INTO checklist_items "
            "(id, checklist_id, requirement_id, is_completed, user_notes, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    _stable_id("item", checklist_id, str(position)),
                    checklist_id,
                    _stable_id("requirement", checklist.form_code, str(position)),
                    position in checklist.completed,
                    checklist.notes.get(position),
                    _COMPLETED_AT if position in checklist.completed else None,
                )
                for position in range(requirement_counts[checklist.form_code])
            ],
        )
