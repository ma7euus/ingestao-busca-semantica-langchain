from __future__ import annotations

from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from .config import (
        COLLECTION_NAME,
        DATABASE_URL,
        PDF_PATH,
        RECREATE_COLLECTION,
        get_embeddings,
    )
except ImportError:
    from config import (  # type: ignore
        COLLECTION_NAME,
        DATABASE_URL,
        PDF_PATH,
        RECREATE_COLLECTION,
        get_embeddings,
    )


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def ingest_pdf() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF nao encontrado em {PDF_PATH}. Configure PDF_PATH no .env ou coloque document.pdf na raiz."
        )

    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()
    if not pages:
        raise RuntimeError(f"Nenhum texto foi carregado do PDF {PDF_PATH}.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk"] = index

    PGVector.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        pre_delete_collection=RECREATE_COLLECTION,
        use_jsonb=True,
    )

    print(f"Ingestao concluida: {len(chunks)} chunks salvos na colecao '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest_pdf()
