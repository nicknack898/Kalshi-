# Kalshi Bot

Kalshi-only trading bot project scaffold.

## Structure

- `app/` — Python application package.
  - `clients/`
  - `schemas/`
  - `scanner/`
  - `research/`
  - `forecast/`
  - `risk/`
  - `execution/`
  - `portfolio/`
  - `backtest/`
  - `learning/`
  - `ops/`
  - `db/`
- `tests/` — Test suite package.
- `docs/` — Project documentation.
- `migrations/` — Alembic migrations.
- `.env.example` — Environment variable template.
- `pyproject.toml` — Python project metadata.
- `alembic.ini` — Alembic configuration.

This scaffold intentionally keeps architecture Kalshi-only and does not introduce multi-exchange abstractions.
