"""Project-wide paths and defaults."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
DATABASE_PATH = PROJECT_ROOT / "uscis_checklist.db"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_USER_EMAIL = "maria@example.com"
