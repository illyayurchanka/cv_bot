# CV Bot — AI-Powered CV Tailoring via Telegram

A Telegram bot that automatically tailors your CV to a specific job description using an LLM agent. Send a job posting link, and the agent will analyze it, rewrite your LaTeX CV to highlight relevant skills, compile it to PDF, and send it back.

## How It Works

```
User sends .tex CV → stored per-user in database
User sends job link → agent reads job description
                   → agent reads existing CV
                   → rewrites CV to match job keywords
                   → compiles LaTeX to PDF
                   → sends PDF back via Telegram
```

## Architecture

```
Telegram  →  FastAPI webhook server  →  pyTelegramBotAPI (bot.py)
                                            │
                                            ▼
                                      Agent Loop (agent.py)
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                         File Tools    Web Tools     LaTeX Tools
                         (read/write)  (fetch/search) (compile)
                              │             │             │
                              └─────────────┼─────────────┘
                                            ▼
                                     SQLite Database
                                   (users, cv history)
```

### Key Components

| File | Purpose |
|------|---------|
| `main.py` | FastAPI entry point, webhook setup via ngrok |
| `src/bot.py` | Telegram bot handlers (start, document, link, callback) |
| `src/agent.py` | LLM agent loop — tool calling, iteration, validation |
| `src/context.py` | `ContextVar` for per-request `chat_id` propagation |
| `src/database.py` | SQLite database — users, CV storage, history, path resolution |
| `src/config.py` | Environment config (tokens, paths) |
| `src/tools/` | Agent tools: `files.py`, `web.py`, `latex.py`, `send_pdf.py` |
| `AGENTS.md` | System prompt defining agent behavior and pipeline |

### Per-User Context

Each user's `chat_id` is stored in a `ContextVar` before the agent loop starts. This allows tools to resolve user-specific file paths from the database without the LLM needing to handle `chat_id` explicitly. Safe for concurrent users.

```
bot.py:  chat_id_var.set(chat_id)  →  run_agent()  →  tools call get_chat_id()
```

## Setup

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) running locally
- A Telegram bot token ([@BotFather](https://t.me/BotFather))
- ngrok account + auth token (for webhook tunneling)
- TeX Live or MiKTeX (for LaTeX compilation)

### 1. Clone and install

```bash
git clone <repo-url>
cd cv_bot
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
NGROK_TOKEN=your_ngrok_auth_token
```

### 3. Run

```bash
python main.py
```

On startup, the app will:
1. Expose the local server via ngrok
2. Set the Telegram webhook
3. Initialize the SQLite database

## Usage

1. **Start the bot** — send `/start`
2. **Upload your CV** — send your `.tex` file (once; it's stored for future use)
3. **Send a job link** — paste a URL to a job posting
3. **Choose an action:**
   - **Summary** — get an analysis of how well you match the role
   - **New CV** — get a tailored CV rewritten for the job + compiled PDF


## Database Schema

```sql
users (
    id          INTEGER PRIMARY KEY,
    chat_id     TEXT UNIQUE NOT NULL,
    username    TEXT,
    joined_at   TIMESTAMP,
    cv_exist    INTEGER DEFAULT 0
)

cv_history (
    id          INTEGER PRIMARY KEY,
    chat_id     TEXT NOT NULL,
    job_url     TEXT NOT NULL,
    created_at  TIMESTAMP
)
```

User files are stored at `cv/<chat_id>/cv.tex` with compiled PDFs at `cv/<chat_id>/output/`.

## Agent Tools

| Tool | Description |
|------|-------------|
| `read_cv` | Read a local cv file by path |
| `write_cv` | Write content to a local cv file |
| `web_fetch` | Fetch and extract text from a URL (via Jina AI) |
| `web_search` | Search the web (via DuckDuckGo HTML) |
| `compile_latex` | Compile a `.tex` file to PDF via `pdflatex` |

## Project Structure

```
cv_bot/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment & path config
├── AGENTS.md                  # Agent system prompt
├── pyproject.toml
├── .env                       # Secrets (not in git)
├── .python-version
├── src/
│   ├── bot.py                 # Telegram handlers
│   ├── agent.py               # LLM agent loop
│   ├── context.py             # ContextVar for chat_id
│   ├── database.py            # SQLite operations
│   ├── tools/
│   │   ├── __init__.py        # Tool exports
│   │   ├── registry.py        # Tool registration & execution
│   │   ├── schemas.py         # Pydantic models for tool args
│   │   ├── files.py           # read_file, write_file
│   │   ├── web.py             # web_fetch, web_search
│   │   ├── latex.py           # compile_latex
│   └── logging/
│       └── agent_log.py       # Agent trace logging
├── cv/                        # Per-user CV storage
│   └── <chat_id>/
│       ├── cv.tex
│       └── output/
│           └── cv.pdf
├── tests/
│   └── test_tools/
│       ├── test_files.py
│       └── test_web.py
└── pdf/                       # Default compilation output
```
