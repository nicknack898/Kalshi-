from sqlalchemy import JSON, Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Market(Base):
    __tablename__ = "markets"
    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    yes_price_str: Mapped[str] = mapped_column(String)
    yes_price: Mapped[float] = mapped_column(Numeric(18, 8))


class OrderbookSnapshot(Base):
    __tablename__ = "orderbook_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class ResearchBrief(Base):
    __tablename__ = "research_briefs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    narrative_summary: Mapped[str] = mapped_column(String)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    p_model: Mapped[float] = mapped_column(Numeric(18, 8))
    confidence: Mapped[float] = mapped_column(Numeric(18, 8))


class RiskDecisionLog(Base):
    __tablename__ = "risk_decisions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    approved: Mapped[bool] = mapped_column(Boolean)
    reasons: Mapped[dict] = mapped_column(JSON)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class Fill(Base):
    __tablename__ = "fills"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(String, index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class Position(Base):
    __tablename__ = "positions"
    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    size_str: Mapped[str] = mapped_column(String)
    size: Mapped[float] = mapped_column(Numeric(18, 8))


class Settlement(Base):
    __tablename__ = "settlements"
    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    outcome: Mapped[str] = mapped_column(String)


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    day: Mapped[str] = mapped_column(String, primary_key=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class FailureLog(Base):
    __tablename__ = "failure_log"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class ConfigSnapshot(Base):
    __tablename__ = "config_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(DateTime)
    raw_payload: Mapped[dict] = mapped_column(JSON)
