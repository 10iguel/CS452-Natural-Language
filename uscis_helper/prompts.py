"""Prompt construction for the text-to-SQL and answer-writing steps.

The three SQL strategies follow https://arxiv.org/abs/2305.11853:
  * zero-shot:     schema only
  * single-domain: schema + worked examples written for this same database
  * cross-domain:  schema + worked examples written for an unrelated database
"""
import json
from enum import Enum

from uscis_helper.database import QueryResult
from uscis_helper.language_model import Message


# The model writes this placeholder; the database layer binds the real id, so the
# model never has to copy a 36-character UUID (it sometimes got it wrong).
USER_ID_PARAMETER = "user_id"
_USER_ID_PLACEHOLDER = f":{USER_ID_PARAMETER}"


class PromptingStrategy(Enum):
    ZERO_SHOT = "zero-shot"
    SINGLE_DOMAIN = "single-domain"
    CROSS_DOMAIN = "cross-domain"


_SQL_RULES = """\
You translate a question into ONE SQLite SELECT query for the database below.

Rules:
- Reply with the SQL only: no explanation and no markdown.
- Use only the tables and columns in the schema.
- Boolean columns hold 1 (true) or 0 (false).
- Form codes look like 'I-485' or 'N-400'; checklist status is 'IN_PROGRESS' or 'COMPLETED'.
- Match free text with LIKE and wildcards, not equality. Check title and description together,
  e.g. (r.title LIKE '%x%' OR r.description LIKE '%x%').
- Select readable columns (form_code, title, name), never raw id columns.
- uscis_forms and form_requirements describe forms for everyone. Join checklists or
  checklist_items only when the question is about the asking user's own progress, status or notes.
- The person asking is the named parameter {parameter}. Questions that say "my" or "I" are about
  this user, so filter with c.user_id = {parameter}. Never write the id itself.

Schema:
{schema}"""

_SINGLE_DOMAIN_EXAMPLES = """\
Examples for this database:

Question: What documents do I need for Form N-400?
SQL: SELECT r.title, r.is_required FROM form_requirements r JOIN uscis_forms f ON f.id = r.form_id WHERE f.form_code = 'N-400' ORDER BY r.sort_order;

Question: Which items have I not finished on my I-765 checklist?
SQL: SELECT r.title FROM checklist_items ci JOIN checklists c ON c.id = ci.checklist_id JOIN uscis_forms f ON f.id = c.form_id JOIN form_requirements r ON r.id = ci.requirement_id WHERE c.user_id = {parameter} AND f.form_code = 'I-765' AND ci.is_completed = 0 ORDER BY r.sort_order;

Question: How many forms can I get a checklist for?
SQL: SELECT COUNT(*) FROM uscis_forms;"""

_CROSS_DOMAIN_EXAMPLES = """\
Examples for a different database (a university):

Schema:
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, major TEXT);
CREATE TABLE enrollments (student_id INTEGER, course_id INTEGER, grade TEXT);
CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, credits INTEGER);

Question: How many students are majoring in Biology?
SQL: SELECT COUNT(*) FROM students WHERE major = 'Biology';

Question: Which courses has Ana Silva completed with an A?
SQL: SELECT c.title FROM courses c JOIN enrollments e ON e.course_id = c.id JOIN students s ON s.id = e.student_id WHERE s.name = 'Ana Silva' AND e.grade = 'A';"""

_ANSWER_RULES = """\
You answer a user's question about USCIS forms and their document checklists.
Use ONLY the query result you are given. Never guess.
If the result is empty, say no matching records were found.
If it has rows but they do not contain what was asked, say the database does not have that information.
Be brief and plain-spoken. Do not give legal advice."""


def build_sql_messages(
    question: str, schema: str, strategy: PromptingStrategy
) -> list[Message]:
    system = _SQL_RULES.format(schema=schema, parameter=_USER_ID_PLACEHOLDER)
    if strategy is PromptingStrategy.SINGLE_DOMAIN:
        system += "\n\n" + _SINGLE_DOMAIN_EXAMPLES.format(parameter=_USER_ID_PLACEHOLDER)
    elif strategy is PromptingStrategy.CROSS_DOMAIN:
        system += "\n\n" + _CROSS_DOMAIN_EXAMPLES
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]


def build_answer_messages(question: str, sql: str, result: QueryResult) -> list[Message]:
    data = json.dumps(
        {
            "columns": result.columns,
            "rows": [list(row) for row in result.rows],
            "truncated": result.truncated,
        },
        default=str,
    )
    return [
        {"role": "system", "content": _ANSWER_RULES},
        {
            "role": "user",
            "content": f"Question: {question}\nSQL used: {sql}\nQuery result: {data}",
        },
    ]
