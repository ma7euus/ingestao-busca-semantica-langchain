from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/langchain"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "document_pdf")
PDF_PATH = Path(os.getenv("PDF_PATH", "document.pdf"))
if not PDF_PATH.is_absolute():
    PDF_PATH = ROOT_DIR / PDF_PATH

SEARCH_K = int(os.getenv("SEARCH_K", "10"))
RECREATE_COLLECTION = os.getenv("RECREATE_COLLECTION", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
}


def _provider(kind: str) -> str:
    provider = os.getenv(f"{kind.upper()}_PROVIDER") or os.getenv("AI_PROVIDER", "openai")
    provider = provider.strip().lower()
    if provider in {"google", "google-genai"}:
        return "gemini"
    return provider


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variavel {name} nao configurada. Copie .env.example para .env e preencha o valor."
        )
    return value


def get_embeddings():
    provider = _provider("embedding")

    if provider == "openai":
        _require_env("OPENAI_API_KEY")
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )

    if provider == "gemini":
        _require_env("GOOGLE_API_KEY")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        )

    raise RuntimeError(f"Provedor de embeddings nao suportado: {provider}")


def get_llm():
    provider = _provider("llm")

    if provider == "openai":
        _require_env("OPENAI_API_KEY")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano"))

    if provider == "gemini":
        _require_env("GOOGLE_API_KEY")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash-lite")
        )

    raise RuntimeError(f"Provedor de LLM nao suportado: {provider}")
