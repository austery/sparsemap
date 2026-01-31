# AGENTS.md

> **Context for AI Agents**
> This file contains instructions, conventions, and context for AI agents working on this repository. Read this before proposing changes.

## 1. Project Overview
**SparseMap** is a high-signal knowledge graph extractor. It processes URL/text inputs using LLMs to generate directed graphs (`Node` + `Edge`) representing critical concepts and dependencies.
- **Backend**: Python (FastAPI, SQLModel, PostgreSQL).
- **Frontend**: Vanilla JS (ES Modules, Cytoscape.js), served statically.
- **Goal**: "Steel thread" implementation—minimal dependencies, high stability, strict data contracts.

## 2. Environment & Tooling
*   **OS**: macOS (Darwin) / Linux
*   **Python Manager**: `uv` (Required). Do not use `pip` or `poetry` directly.
*   **JS Manager**: `bun` (Required). Do not use `npm` or `yarn`.
*   **Database**: PostgreSQL.
*   **Linting**: `Ruff` (Python), `Biome` (JS).

## 3. Directory Structure
```text
/
├── src/sparsemap/       # Backend Application Package
│   ├── api/             # FastAPI routes & app entry
│   ├── core/            # Config & Logging
│   ├── domain/          # Pydantic/SQLModel entities (Data Contract)
│   ├── infra/           # DB Session & Engines
│   └── services/        # Business Logic (ETL, LLM extraction)
├── static/              # Frontend (No build step, raw ES modules)
│   ├── js/              # State, UI, Graph Logic
│   └── style.css        # CSS
├── tests/               # Test Suite
│   ├── unit/            # Python Unit Tests
│   └── frontend/        # JS Unit Tests
├── migrations/          # Alembic Migrations
├── pyproject.toml       # Python Dependencies & Config
├── biome.json           # JS Linter Config
└── .pre-commit-config.yaml # Git Hooks
```

## 4. Operational Commands (The Source of Truth)
Agents MUST use these exact commands to ensure consistency.

### 📦 Installation
```bash
# Python
uv sync

# Git Hooks (Crucial for CI)
uv run pre-commit install --install-hooks
```

### 🚀 Running the App
```bash
# Start Backend (Auto-reloads)
uv run sparsemap
# App will serve at http://localhost:8003
```

### 🧪 Testing
**Run all tests before submitting changes.**
```bash
# Backend (pytest)
uv run pytest

# Frontend (bun test)
bun test
```

### 🧹 Linting & Formatting
**Fix style issues automatically.**
```bash
# Python (Ruff)
uv run ruff check --fix .
uv run ruff format .

# JavaScript (Biome)
bun check --write --unsafe ./static/js
```

### 🗄️ Database Migrations
```bash
# Create a new migration (after modifying models.py)
uv run alembic revision --autogenerate -m "description_of_change"

# Apply migrations
uv run alembic upgrade head
```

## 5. Coding Conventions
1.  **Strict Typing**: All Python code must have type hints. Pydantic models are the source of truth for data structures.
2.  **No Frontend Build**: The frontend is "Vanilla JS". Do not introduce Webpack/Vite/React. Keep it simple, using native ES Modules.
3.  **Testing**:
    *   Python: `tests/unit` must mirror `src/` structure.
    *   JS: Use `bun test`. Logic must be testable (separate logic from DOM where possible).
4.  **Security**: Never commit secrets. Use `.env` (managed by `python-dotenv`).

## 6. Known Constraints
- **Graph Logic**: Layout is handled by Cytoscape (`dagre` or `grid`).
- **LLM**: Currently supports OpenAI, DeepSeek, and Google Gemini via `services/llm_provider.py`.
