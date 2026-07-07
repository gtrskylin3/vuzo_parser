# Project Overview

This project is a Telegram bot named "VUZOPARSER" developed in Python. Its main purpose is to help university applicants track their position in the competitive admission lists for various academic programs.

The bot is built using the following core technologies:
- **`aiogram`**: A modern and fully asynchronous framework for the Telegram Bot API.
- **`SQLAlchemy`**: A SQL toolkit and Object-Relational Mapper (ORM) for database interaction. The project uses an asynchronous engine with `aiosqlite`.
- **`BeautifulSoup`**: A library for pulling data out of HTML and XML files, used here for parsing university admission websites.
- **`Alembic`**: A lightweight database migration tool for SQLAlchemy.
- **`loguru`**: A library for pleasant and powerful logging in Python.
- **`uv`**: A fast Python package installer and resolver, used for dependency management.

The bot supports several universities (NSU, NSTU NETI, TSU) and can send notifications to users when their ranking changes.

## Building and Running

### 1. Installation

The project uses `uv` for package management. To install the dependencies listed in `pyproject.toml`, run the following command in your terminal:

```bash
uv pip install aiogram aiohttp-socks aiosqlite alembic apscheduler beautifulsoup4 loguru pydantic-settings requests sqlalchemy
```

### 2. Configuration

The project requires a `.env` file in the root directory for configuration. You can create one by copying the example file:

```bash
cp .env.example .env
```

Then, edit the `.env` file to include the following required variables:

- `BOT_TOKEN`: Your Telegram bot token.
- `USER_AGENT`: A user-agent string for making HTTP requests.

The `PROXY_TG` variable is optional and can be used to configure a proxy for accessing the Telegram API.

### 3. Database Setup

The project uses SQLite as its database and `Alembic` for migrations. The database file `vuzoparser.db` will be created automatically in the root directory when you first run the bot.

To apply the initial database schema, you can use Alembic:

```bash
alembic upgrade head
```

### 4. Running the Bot

To start the bot, simply run the `main.py` script:

```bash
python main.py
```

## Development Conventions

- **Code Style**: The project follows standard Python conventions. While no specific linter or formatter is enforced in the configuration, the code is well-structured and readable. The `alembic.ini` file contains commented-out sections for `black` and `ruff`, suggesting they are the preferred tools for formatting and linting.
- **Logging**: The project uses `loguru` for structured logging. The configuration is defined in `logging_config.py`. Logs are output to both the console (INFO level and above) and a file (`logs/bot.log`, DEBUG level and above) with rotation and compression.
- **Project Structure**: The codebase is organized into distinct modules:
    - `handlers/`: Contains `aiogram` handlers for processing user commands and messages.
    - `models/`: Defines the SQLAlchemy ORM models.
    - `repository/`: Implements the repository pattern for database access.
    - `middleware/`: Contains custom `aiogram` middleware for tasks like database session management and logging.
    - `keyboards/`: Defines inline keyboards for the bot's interface.
    - `utils/`: Includes utility functions and helper scripts.
- **State Management**: The bot uses an in-memory storage (`MemoryStorage`) for Finite State Machine (FSM) contexts. This means that user states will be lost if the bot is restarted.
