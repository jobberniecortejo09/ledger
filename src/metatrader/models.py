"""Data models for MetaTrader 5 trades and positions."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """MetaTrader 5 order types."""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class TradePosition(BaseModel):
    """Represents an open or closed position in MetaTrader 5."""

    ticket: int = Field(..., description="Unique position ticket identifier")
    symbol: str = Field(..., description="Trading instrument (e.g., EURUSD)")
    order_type: OrderType = Field(..., description="Type of order (BUY/SELL)")
    volume: float = Field(..., description="Position volume in lots")
    open_price: float = Field(..., description="Opening price")
    open_time: datetime = Field(..., description="Time position opened")
    close_price: Optional[float] = Field(None, description="Closing price (if closed)")
    close_time: Optional[datetime] = Field(None, description="Time position closed (if closed)")
    profit: float = Field(..., description="Profit/loss in account currency")
    commission: float = Field(default=0.0, description="Commission paid")
    swap: float = Field(default=0.0, description="Swap/interest")
    comment: Optional[str] = Field(None, description="Position comment/label")
    magic: int = Field(default=0, description="Magic number/EA identifier")

    class Config:
        """Pydantic config."""
        use_enum_values = True


class Trade(BaseModel):
    """Extended trade model with reasoning and analysis."""

    position: TradePosition = Field(..., description="Base position data")
    reasoning: Optional[str] = Field(None, description="Trading reasoning and analysis")
    setup_notes: Optional[str] = Field(None, description="Trade setup description")
    entry_condition: Optional[str] = Field(None, description="Entry signal/condition")
    exit_condition: Optional[str] = Field(None, description="Exit signal/reason")
    risk_reward_ratio: Optional[float] = Field(None, description="Risk/reward ratio")
    ict_concepts: Optional[str] = Field(None, description="Relevant ICT concepts applied")
    datetime_recorded: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        use_enum_values = True
