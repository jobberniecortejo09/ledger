"""Data models for trade statistics and performance metrics."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Core performance metrics for a set of trades."""

    total_trades: int = Field(..., description="Total number of trades analyzed")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    win_rate: float = Field(..., description="Percentage of winning trades (0-100)")
    gross_profit: float = Field(..., description="Sum of all profits")
    gross_loss: float = Field(..., description="Sum of all losses (absolute value)")
    net_profit: float = Field(..., description="Total P&L after fees")
    profit_factor: float = Field(
        ..., description="Gross profit / Gross loss (1.0 = break even)"
    )
    average_win: float = Field(..., description="Average winning trade size")
    average_loss: float = Field(..., description="Average losing trade size")
    largest_win: float = Field(..., description="Largest winning trade")
    largest_loss: float = Field(..., description="Largest losing trade (absolute)")
    expectancy: float = Field(
        ..., description="Average profit per trade (expectation)"
    )
    consecutive_wins: int = Field(..., description="Longest winning streak")
    consecutive_losses: int = Field(..., description="Longest losing streak")
    max_drawdown: float = Field(..., description="Largest peak-to-trough decline")
    max_consecutive_loss: float = Field(..., description="Largest consecutive loss sum")
    sharpe_ratio: Optional[float] = Field(
        None, description="Risk-adjusted return metric"
    )
    recovery_factor: float = Field(
        ..., description="Net profit / Max drawdown (higher is better)"
    )
    avg_risk_reward: Optional[float] = Field(
        None, description="Average risk/reward ratio across trades"
    )

    class Config:
        """Pydantic config."""
        extra = "allow"


class TimeSeriesMetrics(BaseModel):
    """Cumulative metrics over time (daily, weekly, monthly)."""

    period: str = Field(..., description="Time period identifier (YYYY-MM, YYYY-W##, etc.)")
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    trades_count: int = Field(default=0)
    period_profit: float = Field(default=0.0)
    period_win_rate: float = Field(default=0.0)
    cumulative_profit: float = Field(..., description="Running total from start")


class TradeStatistics(BaseModel):
    """Complete statistics report for a set of trades."""

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period_start: Optional[datetime] = Field(None, description="Analysis start date")
    period_end: Optional[datetime] = Field(None, description="Analysis end date")
    symbol_filter: Optional[str] = Field(None, description="Symbol filter applied (if any)")
    
    # Core metrics
    metrics: PerformanceMetrics = Field(...)
    
    # Breakdown by symbol
    by_symbol: dict[str, PerformanceMetrics] = Field(
        default_factory=dict, description="Metrics grouped by trading symbol"
    )
    
    # Time series metrics
    daily_metrics: List[TimeSeriesMetrics] = Field(
        default_factory=list, description="Daily performance breakdown"
    )
    
    # Trade history
    trades_analyzed: int = Field(..., description="Total trades in this analysis")
    trade_tickets: List[int] = Field(
        default_factory=list, description="Ticket numbers of trades analyzed"
    )
    
    class Config:
        """Pydantic config."""
        extra = "allow"
