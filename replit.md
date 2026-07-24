# Ghop Baka Bot

A Python Telegram bot with economy, games, AI chat (Groq/Llama), and admin features.

## Stack
- **Language**: Python 3.12
- **Bot framework**: python-telegram-bot ≥ 21 (polling mode)
- **Database**: SQLite via aiosqlite (`baka.db`)
- **AI**: Groq (`llama-3.1-8b-instant`)

## Running on Replit
The bot runs as a background console worker (no web server needed).

**Workflow**: `Start Bot` — runs `python main.py`

**Required secrets** (set in Replit Secrets):
- `BOT_TOKEN` — Telegram bot token from @BotFather
- `GROQ_API_KEY` — Groq API key from console.groq.com

## Running on Render
Deploy as a **Background Worker** service.

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `python main.py`
- **Environment variables**: `BOT_TOKEN`, `GROQ_API_KEY`

A `Procfile` is included for convenience.

## Project structure
- `main.py` — entry point, registers all handlers
- `config.py` — configuration (reads secrets from env vars)
- `database.py` — SQLite schema and queries
- `handlers/` — one file per command/feature
- `ai/` — Groq AI chat integration
- `utils/` — shared helpers (permissions, time, rate limiting)

## User preferences
- Keep existing project structure and stack
- requirements.txt should be minimal and accurate
