# Kalshi-only Prediction Market Trading Bot

Kalshi-only, demo-first trading bot scaffold focused on deterministic risk controls, fixed-point data handling, and limit-order execution.

## Safety Defaults
- `ENABLE_LIVE_TRADING=false`
- `PLACE_REAL_ORDERS=false`
- `KALSHI_ENV=demo`
- fail-closed behavior on ambiguous config and risk blockers

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Scope
This repository intentionally excludes Polymarket, Polygon, wallets, and cross-exchange abstractions.
