"""Tests for data models."""

import pytest
from datetime import datetime
from src.metatrader.models import TradePosition, OrderType, Trade
from src.notion.models import NotionTradeRecord
from src.statistics.models import PerformanceMetrics


class TestTradePosition:
    """Test TradePosition model."""

    def test_trade_position_creation(self):
        """Test creating a TradePosition."""
        position = TradePosition(
            ticket=123456,
            symbol="EURUSD",
            order_type=OrderType.BUY,
            volume=1.0,
            open_price=1.0850,
            open_time=datetime.utcnow(),
            close_price=1.0900,
            close_time=datetime.utcnow(),
            profit=50.00,
            commission=-10.00,
        )
        assert position.ticket == 123456
        assert position.symbol == "EURUSD"
        assert position.profit == 50.00


class TestNotionTradeRecord:
    """Test NotionTradeRecord model."""

    def test_notion_record_from_trade(self):
        """Test converting Trade to NotionTradeRecord."""
        position = TradePosition(
            ticket=123456,
            symbol="EURUSD",
            order_type=OrderType.BUY,
            volume=1.0,
            open_price=1.0850,
            open_time=datetime.utcnow(),
            close_price=1.0900,
            close_time=datetime.utcnow(),
            profit=50.00,
            commission=-10.00,
            swap=2.00,
        )
        trade = Trade(position=position, reasoning="Test trade")
        notion_record = NotionTradeRecord.from_trade(trade)
        
        assert notion_record.symbol == "EURUSD"
        assert notion_record.net_profit == 42.00  # 50 - (-10) + 2
        assert notion_record.reasoning == "Test trade"


class TestPerformanceMetrics:
    """Test PerformanceMetrics model."""

    def test_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            win_rate=60.0,
            gross_profit=1000.0,
            gross_loss=500.0,
            net_profit=500.0,
            profit_factor=2.0,
            average_win=166.67,
            average_loss=125.0,
            largest_win=300.0,
            largest_loss=200.0,
            expectancy=50.0,
            consecutive_wins=3,
            consecutive_losses=2,
            max_drawdown=250.0,
            max_consecutive_loss=250.0,
            recovery_factor=2.0,
        )
        assert metrics.total_trades == 10
        assert metrics.win_rate == 60.0
        assert metrics.profit_factor == 2.0
