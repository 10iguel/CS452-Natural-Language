"""Command-line interface: ask plain-English questions about USCIS form checklists."""
import argparse
import os
import sys

from dotenv import load_dotenv

from uscis_helper.config import DATABASE_PATH, DEFAULT_MODEL, DEFAULT_USER_EMAIL
from uscis_helper.database import ChecklistDatabase, UnknownUserError
from uscis_helper.interface import Answer, GeneratedSqlError, NaturalLanguageInterface
from uscis_helper.language_model import OpenAIChatModel
from uscis_helper.prompts import PromptingStrategy
from uscis_helper.seed import build_database

_EXIT_WORDS = {"exit", "quit", "q"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="ask one question and exit")
    parser.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in PromptingStrategy],
        default=PromptingStrategy.SINGLE_DOMAIN.value,
    )
    parser.add_argument("--user", default=DEFAULT_USER_EMAIL, help="email of the asking user")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--rebuild", action="store_true", help="recreate the demo database")
    return parser.parse_args(argv)


def format_answer(answer: Answer) -> str:
    return f"SQL:    {answer.sql}\nAnswer: {answer.text}"


def ask_and_print(interface: NaturalLanguageInterface, question: str) -> None:
    try:
        print(format_answer(interface.ask(question)))
    except GeneratedSqlError as error:
        print(f"The generated SQL could not be used ({error}).\nSQL:    {error.sql}")


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = parse_args(argv)
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set (export it or put it in a .env file).", file=sys.stderr)
        return 1
    if args.rebuild or not DATABASE_PATH.exists():
        build_database(DATABASE_PATH)

    database = ChecklistDatabase(DATABASE_PATH)
    try:
        user_id = database.find_user_id(args.user)
    except UnknownUserError as error:
        print(error, file=sys.stderr)
        return 1
    interface = NaturalLanguageInterface(
        database, OpenAIChatModel(args.model), PromptingStrategy(args.strategy), user_id
    )

    if args.question:
        ask_and_print(interface, args.question)
        return 0

    print(f"USCIS checklist helper ({args.strategy}, {args.model}) - type 'exit' to quit.")
    print("Information only, not legal advice.")
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if question.lower() in _EXIT_WORDS:
            return 0
        if question:
            ask_and_print(interface, question)


if __name__ == "__main__":
    sys.exit(main())
