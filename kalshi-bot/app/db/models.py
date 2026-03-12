from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

DECIMAL_18_8 = Numeric(18, 8, asdecimal=True)
DECIMAL_24_8 = Numeric(24, 8, asdecimal=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Markets(Base, TimestampMixin):
    __tablename__ = "markets"

    ticker: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    close_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_price_str: Mapped[str | None] = mapped_column(String(64))
    last_price: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    volume_count_str: Mapped[str | None] = mapped_column(String(64))
    volume_count: Mapped[Decimal | None] = mapped_column(DECIMAL_24_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class MarketSnapshots(Base, TimestampMixin):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    yes_bid_str: Mapped[str | None] = mapped_column(String(64))
    yes_bid: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    yes_ask_str: Mapped[str | None] = mapped_column(String(64))
    yes_ask: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    volume_count_str: Mapped[str | None] = mapped_column(String(64))
    volume_count: Mapped[Decimal | None] = mapped_column(DECIMAL_24_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class OrderbookSnapshots(Base, TimestampMixin):
    __tablename__ = "orderbook_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    best_bid_str: Mapped[str | None] = mapped_column(String(64))
    best_bid: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    best_ask_str: Mapped[str | None] = mapped_column(String(64))
    best_ask: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class ResearchBriefs(Base, TimestampMixin):
    __tablename__ = "research_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    thesis: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_str: Mapped[str | None] = mapped_column(String(64))
    confidence: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class ForecastRuns(Base, TimestampMixin):
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    probability_str: Mapped[str] = mapped_column(String(64), nullable=False)
    probability: Mapped[Decimal] = mapped_column(DECIMAL_18_8, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class RiskDecisions(Base, TimestampMixin):
    __tablename__ = "risk_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    approved: Mapped[str] = mapped_column(String(8), nullable=False)
    max_size_str: Mapped[str | None] = mapped_column(String(64))
    max_size: Mapped[Decimal | None] = mapped_column(DECIMAL_24_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class Orders(Base, TimestampMixin):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_order_id: Mapped[str | None] = mapped_column(String(64), index=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    count_str: Mapped[str] = mapped_column(String(64), nullable=False)
    count: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    price_str: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL_18_8, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class Fills(Base, TimestampMixin):
    __tablename__ = "fills"

    fill_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    count_str: Mapped[str] = mapped_column(String(64), nullable=False)
    count: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    price_str: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL_18_8, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class Positions(Base, TimestampMixin):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    yes_count_str: Mapped[str] = mapped_column(String(64), nullable=False)
    yes_count: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    avg_price_str: Mapped[str | None] = mapped_column(String(64))
    avg_price: Mapped[Decimal | None] = mapped_column(DECIMAL_18_8)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class Settlements(Base, TimestampMixin):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_ticker: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    settled_price_str: Mapped[str] = mapped_column(String(64), nullable=False)
    settled_price: Mapped[Decimal] = mapped_column(DECIMAL_18_8, nullable=False)
    pnl_str: Mapped[str] = mapped_column(String(64), nullable=False)
    pnl: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    metric_date: Mapped[date] = mapped_column(Date, primary_key=True)
    gross_pnl_str: Mapped[str] = mapped_column(String(64), nullable=False)
    gross_pnl: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    net_pnl_str: Mapped[str] = mapped_column(String(64), nullable=False)
    net_pnl: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    volume_count_str: Mapped[str] = mapped_column(String(64), nullable=False)
    volume_count: Mapped[Decimal] = mapped_column(DECIMAL_24_8, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class FailureLog(Base, TimestampMixin):
    __tablename__ = "failure_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component: Mapped[str] = mapped_column(String(64), nullable=False)
    error_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class ConfigSnapshots(Base, TimestampMixin):
    __tablename__ = "config_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_version: Mapped[str] = mapped_column(String(64), nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
