from __future__ import annotations

try:
    from .errors import friendly_error_message
    from .search import answer_question
except ImportError:
    from errors import friendly_error_message  # type: ignore
    from search import answer_question  # type: ignore


EXIT_COMMANDS = {"sair", "exit", "quit", "q"}


def main() -> None:
    print("Faça sua pergunta. Digite 'sair' para encerrar.\n")

    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue

        if question.lower() in EXIT_COMMANDS:
            break

        try:
            answer = answer_question(question)
        except Exception as exc:
            print(f"ERRO: {friendly_error_message(exc)}\n")
            continue

        print(f"RESPOSTA: {answer}\n")


if __name__ == "__main__":
    main()
