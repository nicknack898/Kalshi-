from decimal import Decimal
from enum import Enum

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeMode(str, Enum):
    DEMO = "demo"
    PAPER = "paper"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kalshi_env: RuntimeMode = Field(default=RuntimeMode.DEMO, alias="KALSHI_ENV")
    kalshi_api_key_id: str = Field(default="", alias="KALSHI_API_KEY_ID")
    kalshi_private_key_path: str = Field(default="", alias="KALSHI_PRIVATE_KEY_PATH")
    database_url: str = Field(default="sqlite:///./kalshi_bot.db", alias="DATABASE_URL")

    enable_live_trading: bool = Field(default=False, alias="ENABLE_LIVE_TRADING")
    place_real_orders: bool = Field(default=False, alias="PLACE_REAL_ORDERS")
    stop_file_path: str = Field(default="./STOP", alias="STOP_FILE_PATH")

    scan_interval_seconds: int = Field(default=60, alias="SCAN_INTERVAL_SECONDS")
    max_single_position_pct: Decimal = Field(default=Decimal("0.05"), alias="MAX_SINGLE_POSITION_PCT")
    max_total_open_exposure_pct: Decimal = Field(default=Decimal("0.30"), alias="MAX_TOTAL_OPEN_EXPOSURE_PCT")
    max_daily_loss_pct: Decimal = Field(default=Decimal("0.15"), alias="MAX_DAILY_LOSS_PCT")
    max_drawdown_pct: Decimal = Field(default=Decimal("0.08"), alias="MAX_DRAWDOWN_PCT")
    fractional_kelly: Decimal = Field(default=Decimal("0.25"), alias="FRACTIONAL_KELLY")
    edge_threshold: Decimal = Field(default=Decimal("0.04"), alias="EDGE_THRESHOLD")
    max_slippage_dollars: Decimal = Field(default=Decimal("0.02"), alias="MAX_SLIPPAGE_DOLLARS")
    min_expected_profit_dollars: Decimal = Field(default=Decimal("5.00"), alias="MIN_EXPECTED_PROFIT_DOLLARS")

    @model_validator(mode="after")
    def validate_safety(self) -> "Settings":
        if self.kalshi_env == RuntimeMode.PROD and not self.enable_live_trading:
            raise ValueError("Fail closed: prod mode requires ENABLE_LIVE_TRADING=true")
        if self.place_real_orders and not self.enable_live_trading:
            raise ValueError("Fail closed: PLACE_REAL_ORDERS requires ENABLE_LIVE_TRADING=true")
        return self
