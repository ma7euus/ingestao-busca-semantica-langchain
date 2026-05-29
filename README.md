# Ingestao e Busca Semantica com LangChain e Postgres

Projeto em Python para ingestao de um PDF em PostgreSQL com pgVector e busca semantica via CLI usando LangChain.

## Tecnologias

- Python
- LangChain
- PostgreSQL + pgVector
- Docker Compose
- OpenAI por padrao, com suporte opcional a Gemini

## Estrutura

```text
.
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py
│   ├── search.py
│   └── chat.py
├── document.pdf
└── README.md
```

## Configuracao

Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Se o comando de `venv` falhar em Debian/Ubuntu por falta de `ensurepip`, instale o pacote do sistema correspondente, por exemplo `sudo apt install python3-venv` ou `sudo apt install python3.14-venv`.

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env`:

```bash
cp .env.example .env
```

Preencha `OPENAI_API_KEY` no `.env`.

Por padrao o projeto usa:

- Embeddings OpenAI: `text-embedding-3-small`
- LLM OpenAI: `gpt-5-nano`
- Banco: `postgresql+psycopg://postgres:postgres@localhost:5432/langchain`

Para usar Gemini, configure:

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=sua-chave
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

Use o mesmo provedor na ingestao e na busca. Se trocar de OpenAI para Gemini, rode `python src/ingest.py` novamente para recriar os vetores.

## Execucao

Suba o banco:

```bash
docker compose up -d
```

Execute a ingestao do PDF:

```bash
python src/ingest.py
```

Rode o chat:

```bash
python src/chat.py
```

Exemplo:

```text
Faça sua pergunta. Digite 'sair' para encerrar.

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

Perguntas sem resposta explicita no PDF devem retornar:

```text
Não tenho informações necessárias para responder sua pergunta.
```

## Observacoes

- O PDF padrao deve estar na raiz do projeto com o nome `document.pdf`.
- Para usar outro arquivo, altere `PDF_PATH` no `.env`.
- A ingestao divide o PDF em chunks de 1000 caracteres com overlap de 150.
- A busca recupera os 10 trechos mais relevantes com `similarity_search_with_score`.
- `RECREATE_COLLECTION=true` recria a colecao a cada ingestao, evitando dados duplicados durante testes.

## Solucao de problemas

### OpenAI `insufficient_quota`

O erro abaixo significa que a conta/chave da OpenAI nao tem quota ou billing disponivel para chamar o modelo de embeddings:

```text
openai.RateLimitError: Error code: 429 ... code: 'insufficient_quota'
```

Opcoes:

1. Verifique billing/quota da conta OpenAI e execute `python src/ingest.py` novamente.
2. Use Gemini no lugar da OpenAI:

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=sua-chave-google
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

Depois rode novamente:

```bash
python src/ingest.py
python src/chat.py
```

### Aviso de `langchain-community`

O aviso de deprecacao do `langchain-community` nao impede a execucao. Ele aparece porque o `PyPDFLoader` recomendado no enunciado ainda vem desse pacote na documentacao atual do LangChain.

### Gemini `models/embedding-001` nao encontrado

Se a ingestao retornar erro `404 NOT_FOUND` para `models/embedding-001`, altere o `.env`:

```env
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

O modelo `gemini-embedding-001` e compativel com busca textual. O modelo mais recente da API Gemini e `gemini-embedding-2`, mas ele tem diferencas de uso e de espaco vetorial; ao trocar qualquer modelo de embeddings, rode a ingestao novamente.
