# Bitcoin-Facebook (API with uv)

This project provides an API server that works with GIS data and embeddings.  
We use [uv](https://github.com/astral-sh/uv), a fast Python package manager and runner, instead of pip and venv.

---

## Installation

### 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

Verify:
uv --version

---

## Running the API Server

Run the server with:
uv run server.py

Or specify a module:
uv run python -m server

By default, the server starts on http://127.0.0.1:8000  
(you can adjust host/port in server.py).

---

## Managing Dependencies

### Add a new requirement
uv add requests

### Add multiple requirements
uv add fastapi uvicorn

This updates pyproject.toml and uv.lock.

### Remove a requirement
uv remove requests

### Sync environment (install all dependencies)
uv sync

---

## Development

### Run Jupyter Notebook
uv run jupyter notebook emdedding_vector.ipynb

### Format & Lint
uv run ruff check .
uv run black .

---

## Docker

docker-compose up --build

---

## Project Structure
.
├── db/pgvector            # Database / vector storage
├── gis_data/              # GIS CSV input data
├── main.py                # Entry point / app logic
├── server.py              # API server
├── emdedding_vector.ipynb # Notebook for embeddings
├── pyproject.toml         # Project config (uv/poetry compatible)
├── uv.lock                # Dependency lockfile
└── docker-compose.yaml    # Docker setup

---

## Notes
- Use `uv run` instead of `python` to ensure correct deps are loaded.  
- Dependencies are fully reproducible thanks to uv.lock.  
- For more commands: uv --help.