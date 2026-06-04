# Odia AI Educational Platform

An Odia-first educational AI assistant for curriculum-based question answering. The project combines document ingestion, chunking, dense embeddings, Qdrant retrieval, and OpenAI generation in a Streamlit chat interface.

The current implementation is focused on educational retrieval-augmented generation (RAG): a learner asks a question, the application retrieves relevant curriculum chunks from a local Qdrant vector database, builds context, and asks OpenAI GPT to produce a beginner-friendly answer.

## Project Objective

This project exists to support learners who need educational explanations in Odia, with English support where useful. It is designed around curriculum-grounded answers rather than open-ended web search.

Current objectives:

- Provide an Odia-first educational assistant.
- Answer academic questions using retrieved curriculum content.
- Support conversational follow-up questions within the current Streamlit session.
- Keep the runtime architecture simple enough for solo development and future extension.
- Provide a foundation for multilingual educational workflows.

Current scope:

- Streamlit chat UI.
- LLM-based intent routing.
- Educational RAG over local Qdrant.
- BGE-M3 embeddings.
- OpenAI GPT-4o-mini integration.
- Session-based conversation history.

Current limitations:

- Conversation history is stored only in Streamlit session state.
- No persistent chat database is implemented.
- No source citation UI is implemented.
- Retrieval depends on the curriculum already ingested into Qdrant.
- Multilingual behavior is supported through prompts and model capability, not a separate translation pipeline.

## Current Runtime Architecture

```text
User Query
    |
    v
Streamlit UI
    |
    v
Query Orchestrator
    |
    v
Intent Router
    |
    +--> greeting ---------> Greeting Handler ---------> Response
    |
    +--> conversational ---> Conversational Handler ---> OpenAI ---> Response
    |
    +--> educational ------> Educational Handler
                              |
                              v
                            Qdrant Retriever
                              |
                              v
                            Retrieved Chunks
                              |
                              v
                            Context Builder
                              |
                              v
                            OpenAI
                              |
                              v
                            Response
    |
    +--> out_of_scope -----> Safe Response
```

The orchestrator is the single runtime entry point. It classifies the query, selects the appropriate handler, and returns a structured result to the UI.

## Core Runtime Components

| Component | Purpose | Responsibilities | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| `app/orchestrator/query_orchestrator.py` | Single runtime entry point | Receives queries, calls intent router, dispatches to handlers, returns a `QueryResult` dictionary | User query, session ID, conversation history, `top_k` | Answer, intent, retrieved chunks, context, debug metadata |
| `app/intent/intent_router.py` | LLM-based intent classification | Classifies input into `greeting`, `educational`, `conversational`, or `out_of_scope` | User query | Intent label |
| `app/retrieval/qdrant_retriever.py` | Curriculum retrieval | Embeds the query with BGE-M3, searches Qdrant, filters and deduplicates chunks | User query, `top_k` | Retrieved chunk list and retrieval debug metadata |
| `app/handlers/educational_handler.py` | Educational RAG handling | Retrieves chunks, builds context, calls OpenAI with current query, context, and conversation history | Query, conversation history, `top_k` | Educational answer |
| `app/handlers/conversational_handler.py` | Non-RAG conversation handling | Sends current query and recent conversation history directly to OpenAI | Query, conversation history | Conversational answer |
| `app/handlers/greeting_handler.py` | Greeting response handling | Returns lightweight greeting responses without retrieval or OpenAI | Query | Greeting response |
| `app/llm/openai_service.py` | OpenAI integration | Builds OpenAI chat messages, includes history/context, calls chat completions | System prompt, query, context, history, metadata | LLM response text |
| `app/prompts/prompts.py` | Runtime prompt definitions | Stores intent, educational, conversational, and fallback prompt text | Imported prompt constants | Prompt strings |
| `streamlit_app.py` | User interface | Manages UI, session state, sidebar settings, chat display, and debug panel | User input | Rendered chat response |

## RAG Pipeline

```text
Curriculum Documents
    |
    v
OCR / Text Extraction
    |
    v
Cleaning
    |
    v
Chunking
    |
    v
BGE-M3 Embeddings
    |
    v
Qdrant Vector Database
    |
    v
Query Retrieval
    |
    v
Context Building
    |
    v
OpenAI GPT-4o-mini
    |
    v
Educational Answer
```

Implemented data and retrieval components:

- Document ingestion scripts under `scripts/`.
- Text cleaning and chunking under `scripts/preprocessing/`.
- Embedding pipeline under `rag/embeddings/embedding_pipeline.py`.
- BGE-M3 embedding model via `rag/embeddings/embedder.py`.
- Local Qdrant storage via `rag/vectordb/qdrant_store.py`.
- Runtime retrieval via `app/retrieval/qdrant_retriever.py`.

## Current Project Status

### Completed

- Document ingestion workflow.
- OCR/text extraction support.
- Text cleaning.
- Chunking.
- Embedding generation.
- Qdrant vector database integration.
- Query retrieval.
- Educational RAG flow.
- OpenAI GPT integration.
- Streamlit chat UI.
- LLM intent routing.
- Greeting, conversational, educational, and out-of-scope routing.
- Session-based conversation history.
- Retrieval debug panel in the UI.
- Unit-style tests for intent routing and orchestrator dispatch.

### In Progress

- Additional curriculum ingestion.
- Better retrieval evaluation.
- Source citation display.
- More robust conversational follow-up behavior.

### Future

- Translation workflows.
- Multi-subject curriculum expansion.
- Persistent memory.
- MySQL or other durable storage.
- Source-aware answer citations.
- Agent-style educational tools.
- Quiz generation and lesson planning.

## Conversation Memory

Conversation memory is currently session-based and managed by Streamlit.

Storage:

- `streamlit_app.py` initializes `st.session_state.messages`.
- Each user message is appended to this list.
- Each assistant response is appended after generation.
- Resetting the conversation clears the list and creates a new `session_id`.

Runtime flow:

```text
st.session_state.messages
    |
    v
conversation_history argument
    |
    v
QueryOrchestrator.ask(...)
    |
    v
EducationalHandler or ConversationalHandler
    |
    v
OpenAIService.generate(...)
    |
    v
OpenAI chat messages
```

`OpenAIService` builds chat messages by adding:

1. The system prompt.
2. Recent conversation history.
3. Retrieved context, for educational RAG requests.
4. The current user query.

The implementation currently uses recent session history only. It is not persisted to Redis, MySQL, Qdrant, or any external memory store.

## Project Structure

```text
.
├── app/
│   ├── api/
│   ├── config/
│   ├── handlers/
│   │   ├── conversational_handler.py
│   │   ├── educational_handler.py
│   │   └── greeting_handler.py
│   ├── intent/
│   │   └── intent_router.py
│   ├── llm/
│   │   └── openai_service.py
│   ├── models/
│   │   └── query_result.py
│   ├── orchestrator/
│   │   └── query_orchestrator.py
│   ├── prompts/
│   │   └── prompts.py
│   ├── retrieval/
│   │   └── qdrant_retriever.py
│   └── ui/
├── configs/
│   └── settings.py
├── rag/
│   ├── chunking/
│   ├── embeddings/
│   │   ├── embedder.py
│   │   └── embedding_pipeline.py
│   ├── vectordb/
│   │   └── qdrant_store.py
│   └── logging_config.py
├── scripts/
│   ├── ingestion/
│   ├── orchestration/
│   ├── preprocessing/
│   └── utils/
├── tests/
│   ├── test_intent_router.py
│   └── test_query_orchestrator.py
├── main.py
├── streamlit_app.py
├── pyproject.toml
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Odia-AI-Educational-Platform
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

This project uses `pyproject.toml` for dependency metadata.

```bash
pip install -e .
```

If you use `uv`:

```bash
uv sync
```

### 4. Create environment file

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 5. Configure OpenAI

Edit `.env` and set:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
```

### 6. Configure Qdrant path

The default local Qdrant path is configured in `configs/settings.py`:

```text
data/qdrant_db
```

The default collection name is:

```text
odia_education_chunks
```

These values are used by `EmbeddingSettings`, `RetrievalSettings`, and `QdrantStore`.

### 7. Run Streamlit

```bash
streamlit run streamlit_app.py
```

## Environment Variables

| Variable | Required | Used By | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes | `LLMSettings`, `OpenAIService` | API key for OpenAI chat completions |
| `OPENAI_MODEL` | No | `LLMSettings` | Model name. Defaults to `gpt-4o-mini` |
| `LLM_TIMEOUT_SECONDS` | No | `LLMSettings`, `OpenAIService` | OpenAI request timeout. Defaults to `30.0` |
| `LLM_MAX_RETRIES` | No | `LLMSettings`, `OpenAIService` | OpenAI client retry count. Defaults to `2` |

Note: `.env.example` may include older variables. The runtime code currently reads the variables listed above.

## How To Run

Start the application:

```bash
streamlit run streamlit_app.py
```

Expected behavior:

- The Streamlit app opens a chat interface.
- The sidebar displays model, retrieval, vector DB, collection, embedding, and session information.
- User queries are routed by intent.
- Educational queries retrieve context from Qdrant before calling OpenAI.
- Conversational queries call OpenAI without retrieval.
- Greeting queries return a lightweight greeting response.
- The debug expander shows retrieval details for the latest response.

To verify retrieval:

1. Ask an educational question related to ingested curriculum.
2. Open the "Retrieval debug" expander.
3. Confirm retrieved chunks, similarity scores, and generated context are shown.

## Testing

Existing tests:

- `tests/test_intent_router.py`
  - Validates strict intent labels.
  - Validates markdown/noisy label normalization.
  - Validates fallback to `out_of_scope`.
  - Validates empty-query behavior.

- `tests/test_query_orchestrator.py`
  - Validates educational route dispatch.
  - Validates conversational route dispatch.
  - Validates greeting route dispatch.

Run tests:

```bash
python -m pytest -q
```

If `pytest` is not installed in the active environment:

```bash
pip install pytest
python -m pytest -q
```

Smoke checks:

```bash
python -m compileall -q app streamlit_app.py configs rag scripts main.py
```

## Known Limitations

- Conversation memory is session-only and not stored in a database.
- Source citations are not displayed as formal citations in the UI.
- Retrieval quality depends on the size and quality of ingested curriculum chunks.
- No persistent user profiles or learner state are implemented.
- No separate translation, quiz generation, or lesson planning workflows are implemented yet.
- The app uses local Qdrant storage through `qdrant-client`; deployment-specific Qdrant hosting is not configured in the runtime.
- The UI is a Streamlit prototype, not a production web application.

## Roadmap

### Short Term

- Improve README and developer documentation.
- Add more end-to-end smoke tests.
- Add source metadata display for generated answers.
- Improve retrieval evaluation with known question-answer examples.

### Medium Term

- Add citation-aware responses.
- Add persistent conversation storage.
- Add translation and explanation mode controls.
- Add support for more subjects and grade levels.
- Add FastAPI endpoints under `app/api/`.

### Long Term

- Add durable learner profiles.
- Add quiz generation and lesson planning workflows.
- Add teacher/admin curriculum upload tools.
- Add production deployment configuration.
- Add evaluation dashboards for retrieval and answer quality.

## Tech Stack

| Area | Technology |
| --- | --- |
| Language | Python 3.10 |
| UI | Streamlit |
| LLM | OpenAI chat completions |
| Default model | GPT-4o-mini |
| Embeddings | BGE-M3 via `sentence-transformers` |
| Vector database | Qdrant |
| OCR / ingestion support | Tesseract, PaddleOCR, PyMuPDF |
| Configuration | `python-dotenv`, dataclass settings |
| Data utilities | pandas, NumPy |
| ML runtime dependencies | torch, torchvision |

## Development Notes

- Runtime code lives under `app/`.
- Data ingestion and preprocessing scripts live under `scripts/`.
- Embedding and vector database support live under `rag/`.
- The current Streamlit UI is the main application entry point.
- The orchestrator should remain the single runtime entry point for query handling.

## License

No license file is currently included in this repository.
