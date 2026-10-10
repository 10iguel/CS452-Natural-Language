"""The language-model boundary: everything OpenAI-specific lives here."""
from typing import Protocol

from openai import OpenAI

Message = dict[str, str]


class LanguageModel(Protocol):
    def complete(self, messages: list[Message]) -> str: ...


class OpenAIChatModel:
    def __init__(self, model: str, client: OpenAI | None = None):
        self._model = model
        self._client = client or OpenAI()
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def complete(self, messages: list[Message]) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0,
        )
        if response.usage is not None:
            self.prompt_tokens += response.usage.prompt_tokens
            self.completion_tokens += response.usage.completion_tokens
        return response.choices[0].message.content or ""
