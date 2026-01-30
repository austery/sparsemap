# SparseMap

High-signal knowledge graph extractor. Mapping the critical path through the noise.

## Quick Start

```bash
uv sync
uv run sparsemap
```

Open http://localhost:8003 in your browser.

## Environment

Create a `.env` file in the project root:

```bash
LLM_API_KEY=your_api_key
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sparsemap
```

You can override any settings via environment variables defined in `src/sparsemap/core/config.py`.
