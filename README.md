# SparseMap

> **Mapping the critical path through the noise.**

SparseMap is a high-signal knowledge graph extractor powered by Large Language Models (LLMs). It transforms unstructured text or web content into structured, interactive directed graphs, helping users visualize complex concepts, dependencies, and "best practices" without getting lost in the details.

## ✨ Key Features

- **🌐 Multi-Source Extraction**: Analyze content directly from URLs or raw text input.
- **🧠 AI-Powered Analysis**: Uses advanced LLMs (OpenAI, DeepSeek, Gemini) to extract semantic nodes and edges.
- **🕸️ Interactive Visualization**: Explore connections using a force-directed graph (Cytoscape.js).
- **🔍 Deep Dive Mode**: Click on any node to get an AI-generated comprehensive explanation, analogies, and actionable steps.
- **💾 History & Persistence**: Automatically saves analysis results to a PostgreSQL database for future reference.
- **🛡️ Robust Architecture**: Built with strict data contracts (Pydantic), auto-healing JSON parsers, and a type-safe backend.

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLModel (SQLAlchemy + Pydantic).
- **Database**: PostgreSQL (with async support).
- **Frontend**: Vanilla JavaScript (ES Modules), Cytoscape.js, CSS3.
- **Package Management**: `uv` (Python), `bun` (JavaScript tooling).
- **CI/CD**: GitHub Actions, Ruff, Biome, Pre-commit hooks.

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (Installed via [uv](https://github.com/astral-sh/uv) recommended)
- **Bun** (For frontend testing/linting)
- **Docker** (For local database)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/sparsemap.git
    cd sparsemap
    ```

2.  **Environment Setup**
    Create a `.env` file in the project root:
    ```bash
    cp .env.sample .env
    ```
    Update `.env` with your API keys (OpenAI/DeepSeek/Gemini) and database credentials.

3.  **Start the Database**
    ```bash
    docker-compose up -d
    ```

4.  **Install Dependencies**
    ```bash
    uv sync
    ```

5.  **Run Migrations**
    Initialize the database schema:
    ```bash
    uv run alembic upgrade head
    ```

### Running the Application

Start the development server:

```bash
uv run sparsemap
```

- **Web Interface**: [http://localhost:8003](http://localhost:8003)
- **API Documentation**: [http://localhost:8003/docs](http://localhost:8003/docs)

## 🧪 Development & Testing

We enforce high code quality using strict linting and automated tests.

### Run Tests
```bash
# Backend (Python)
uv run pytest

# Frontend (JavaScript)
bun test
```

### Linting & Formatting
```bash
# Backend (Auto-fix)
uv run ruff check --fix .
uv run ruff format .

# Frontend (Auto-fix)
bun check --write --unsafe ./static/js
```

### Database Migrations
When you modify `src/sparsemap/domain/models.py`, generate a new migration:
```bash
uv run alembic revision --autogenerate -m "describe_your_changes"
uv run alembic upgrade head
```

## 📂 Project Structure

```text
/
├── src/sparsemap/       # FastAPI Application
│   ├── api/             # Routes & Controllers
│   ├── domain/          # Database Models & Schemas
│   ├── services/        # Business Logic (LLM, ETL)
│   └── infra/           # Database Connection
├── static/              # Frontend Assets (No build step required)
├── migrations/          # Alembic versions
└── tests/               # Unit & Integration Tests
```

## 📝 License

[MIT](LICENSE)