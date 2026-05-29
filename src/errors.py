from __future__ import annotations


def friendly_error_message(exc: Exception) -> str:
    message = str(exc)
    lower_message = message.lower()
    class_name = exc.__class__.__name__.lower()
    module_name = exc.__class__.__module__.lower()

    if "insufficient_quota" in lower_message or (
        "openai" in module_name and "ratelimit" in class_name
    ):
        return (
            "A OpenAI recusou a requisicao por quota/billing insuficiente. "
            "Verifique a chave e o plano da conta OpenAI ou use Gemini configurando "
            "AI_PROVIDER=gemini e GOOGLE_API_KEY no .env. Depois execute a ingestao novamente."
        )

    if (
        "embedcontent" in lower_message
        and "not_found" in lower_message
        and "embedding-001" in lower_message
    ):
        return (
            "O modelo Gemini de embeddings configurado nao foi encontrado. "
            "Use GEMINI_EMBEDDING_MODEL=gemini-embedding-001 no .env e execute a ingestao novamente."
        )

    if "rate limit" in lower_message or "ratelimit" in class_name:
        return (
            "O provedor de IA recusou a requisicao por limite de uso. "
            "Aguarde alguns instantes ou troque a chave/provedor no .env."
        )

    return message
