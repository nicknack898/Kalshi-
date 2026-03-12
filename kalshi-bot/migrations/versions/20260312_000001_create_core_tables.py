"""create core tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260312_000001"
down_revision = None
branch_labels = None
depends_on = None


DECIMAL_18_8 = sa.Numeric(18, 8, asdecimal=True)
DECIMAL_24_8 = sa.Numeric(24, 8, asdecimal=True)


def upgrade() -> None:
    op.create_table(
        "markets",
        sa.Column("ticker", sa.String(length=64), primary_key=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("close_time", sa.DateTime(timezone=True)),
        sa.Column("last_price_str", sa.String(length=64)),
        sa.Column("last_price", DECIMAL_18_8),
        sa.Column("volume_count_str", sa.String(length=64)),
        sa.Column("volume_count", DECIMAL_24_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("yes_bid_str", sa.String(length=64)),
        sa.Column("yes_bid", DECIMAL_18_8),
        sa.Column("yes_ask_str", sa.String(length=64)),
        sa.Column("yes_ask", DECIMAL_18_8),
        sa.Column("volume_count_str", sa.String(length=64)),
        sa.Column("volume_count", DECIMAL_24_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_market_snapshots_market_ticker", "market_snapshots", ["market_ticker"])

    op.create_table(
        "orderbook_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("best_bid_str", sa.String(length=64)),
        sa.Column("best_bid", DECIMAL_18_8),
        sa.Column("best_ask_str", sa.String(length=64)),
        sa.Column("best_ask", DECIMAL_18_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_orderbook_snapshots_market_ticker", "orderbook_snapshots", ["market_ticker"])

    op.create_table(
        "research_briefs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=False),
        sa.Column("confidence_str", sa.String(length=64)),
        sa.Column("confidence", DECIMAL_18_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_research_briefs_market_ticker", "research_briefs", ["market_ticker"])

    op.create_table(
        "forecast_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("probability_str", sa.String(length=64), nullable=False),
        sa.Column("probability", DECIMAL_18_8, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_forecast_runs_market_ticker", "forecast_runs", ["market_ticker"])

    op.create_table(
        "risk_decisions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("approved", sa.String(length=8), nullable=False),
        sa.Column("max_size_str", sa.String(length=64)),
        sa.Column("max_size", DECIMAL_24_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_risk_decisions_market_ticker", "risk_decisions", ["market_ticker"])

    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(length=64), primary_key=True),
        sa.Column("client_order_id", sa.String(length=64)),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("count_str", sa.String(length=64), nullable=False),
        sa.Column("count", DECIMAL_24_8, nullable=False),
        sa.Column("price_str", sa.String(length=64), nullable=False),
        sa.Column("price", DECIMAL_18_8, nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_orders_client_order_id", "orders", ["client_order_id"])
    op.create_index("ix_orders_market_ticker", "orders", ["market_ticker"])

    op.create_table(
        "fills",
        sa.Column("fill_id", sa.String(length=64), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("count_str", sa.String(length=64), nullable=False),
        sa.Column("count", DECIMAL_24_8, nullable=False),
        sa.Column("price_str", sa.String(length=64), nullable=False),
        sa.Column("price", DECIMAL_18_8, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_fills_order_id", "fills", ["order_id"])
    op.create_index("ix_fills_market_ticker", "fills", ["market_ticker"])

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False, unique=True),
        sa.Column("yes_count_str", sa.String(length=64), nullable=False),
        sa.Column("yes_count", DECIMAL_24_8, nullable=False),
        sa.Column("avg_price_str", sa.String(length=64)),
        sa.Column("avg_price", DECIMAL_18_8),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "settlements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("market_ticker", sa.String(length=64), nullable=False),
        sa.Column("settled_price_str", sa.String(length=64), nullable=False),
        sa.Column("settled_price", DECIMAL_18_8, nullable=False),
        sa.Column("pnl_str", sa.String(length=64), nullable=False),
        sa.Column("pnl", DECIMAL_24_8, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_settlements_market_ticker", "settlements", ["market_ticker"])

    op.create_table(
        "daily_metrics",
        sa.Column("metric_date", sa.Date(), primary_key=True),
        sa.Column("gross_pnl_str", sa.String(length=64), nullable=False),
        sa.Column("gross_pnl", DECIMAL_24_8, nullable=False),
        sa.Column("net_pnl_str", sa.String(length=64), nullable=False),
        sa.Column("net_pnl", DECIMAL_24_8, nullable=False),
        sa.Column("volume_count_str", sa.String(length=64), nullable=False),
        sa.Column("volume_count", DECIMAL_24_8, nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "failure_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "config_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("config_version", sa.String(length=64), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("config_snapshots")
    op.drop_table("failure_log")
    op.drop_table("daily_metrics")
    op.drop_index("ix_settlements_market_ticker", table_name="settlements")
    op.drop_table("settlements")
    op.drop_table("positions")
    op.drop_index("ix_fills_market_ticker", table_name="fills")
    op.drop_index("ix_fills_order_id", table_name="fills")
    op.drop_table("fills")
    op.drop_index("ix_orders_market_ticker", table_name="orders")
    op.drop_index("ix_orders_client_order_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_risk_decisions_market_ticker", table_name="risk_decisions")
    op.drop_table("risk_decisions")
    op.drop_index("ix_forecast_runs_market_ticker", table_name="forecast_runs")
    op.drop_table("forecast_runs")
    op.drop_index("ix_research_briefs_market_ticker", table_name="research_briefs")
    op.drop_table("research_briefs")
    op.drop_index("ix_orderbook_snapshots_market_ticker", table_name="orderbook_snapshots")
    op.drop_table("orderbook_snapshots")
    op.drop_index("ix_market_snapshots_market_ticker", table_name="market_snapshots")
    op.drop_table("market_snapshots")
    op.drop_table("markets")
