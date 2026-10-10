"""The natural-language pipeline: question -> SQL -> rows -> plain-language answer."""
import re
from dataclasses import dataclass

from uscis_helper.database import ChecklistDatabase, QueryExecutionError, QueryResult
from uscis_helper.language_model import LanguageModel
from uscis_helper.prompts import (
    USER_ID_PARAMETER,
    PromptingStrategy,
    build_answer_messages,
    build_sql_messages,
)
from uscis_helper.sql_guard import UnsafeSqlError

_CODE_FENCE = re.compile(r"^```(?:sql)?\s*|\s*```$", re.IGNORECASE)


class GeneratedSqlError(Exception):
    """The model produced SQL that was rejected or failed; keeps it for inspection."""

    def __init__(self, sql: str, reason: str):
        super().__init__(reason)
        self.sql = sql


@dataclass(frozen=True)
class Answer:
    question: str
    sql: str
    result: QueryResult
    text: str


class NaturalLanguageInterface:
    def __init__(
        self,
        database: ChecklistDatabase,
        model: LanguageModel,
        strategy: PromptingStrategy,
        user_id: str,
    ):
        self._database = database
        self._model = model
        self._strategy = strategy
        self._user_id = user_id
        self._schema = database.describe_schema()

    def ask(self, question: str) -> Answer:
        sql = self._generate_sql(question)
        try:
            result = self._database.run_query(sql, {USER_ID_PARAMETER: self._user_id})
        except (UnsafeSqlError, QueryExecutionError) as error:
            raise GeneratedSqlError(sql, str(error)) from error
        text = self._model.complete(build_answer_messages(question, sql, result))
        return Answer(question=question, sql=sql, result=result, text=text.strip())

    def _generate_sql(self, question: str) -> str:
        messages = build_sql_messages(question, self._schema, self._strategy)
        return _CODE_FENCE.sub("", self._model.complete(messages).strip()).strip()
