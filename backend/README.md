
# SWE40006 Backend Program
## Prerequisites
- **Python**: Version 3.13 or newer
- **uv**: Project and dependency manager (Fast Python package installer)
- **SQLite**: Default database (no separate installation required)
---
## Setup & Installation
1. **Initialize the Virtual Environment**:
	```shell
    uv venv
    ```
2. **Install All Dependencies**: Installs FastAPI, SQLAlchemy, and dev tools (`pytest`, `ruff`, `mypy`, `httpx2`):
    ```shell
    uv sync --all-groups
    ```
3. **Database Configuration**: The application uses **SQLite** by default for development. **ADD LATER**