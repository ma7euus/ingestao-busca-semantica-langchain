from __future__ import annotations

from typing import Iterable

from langchain_core.documents import Document
from langchain_postgres import PGVector

try:
    from .config import COLLECTION_NAME, DATABASE_URL, SEARCH_K, get_embeddings, get_llm
except ImportError:
    from config import (  # type: ignore
        COLLECTION_NAME,
        DATABASE_URL,
        SEARCH_K,
        get_embeddings,
        get_llm,
    )


FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

PROMPT_TEMPLATE = """CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


SearchResult = tuple[Document, float]


def get_vector_store() -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )


def search_documents(question: str, k: int = SEARCH_K) -> list[SearchResult]:
    vector_store = get_vector_store()
    return vector_store.similarity_search_with_score(question, k=k)


def format_context(results: Iterable[SearchResult]) -> str:
    parts: list[str] = []
    for index, (document, score) in enumerate(results, start=1):
        metadata = document.metadata or {}
        source = metadata.get("source", "document.pdf")
        page = metadata.get("page")
        page_info = f", pagina {page + 1}" if isinstance(page, int) else ""
        parts.append(
            f"[Trecho {index} | fonte: {source}{page_info} | score: {score:.4f}]\n"
            f"{document.page_content}"
        )
    return "\n\n".join(parts)


def build_prompt(question: str, context: str) -> str:
    return PROMPT_TEMPLATE.format(context=context, question=question)


def _message_content_to_text(message: object) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    text_parts.append(str(text))
            else:
                text_parts.append(str(item))
        return "\n".join(text_parts).strip()
    return str(content).strip()


def answer_question(question: str, k: int = SEARCH_K) -> str:
    results = search_documents(question, k=k)
    context = format_context(results)
    if not context:
        return FALLBACK_ANSWER

    response = get_llm().invoke(build_prompt(question, context))
    answer = _message_content_to_text(response)
    return answer or FALLBACK_ANSWER


if __name__ == "__main__":
    question = input("PERGUNTA: ").strip()
    if question:
        print(f"RESPOSTA: {answer_question(question)}")
