"""Tests for MetaTrader 5 API wrapper."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.metatrader.mt5_api import MT5APIWrapper, MT5ConnectionError


class TestMT5APIWrapper:
    """Test MetaTrader5 API wrapper."""

    def test_mt5_not_available(self):
        """Test handling when MT5 library is not available."""
        with patch('src.metatrader.mt5_api.MT5_AVAILABLE', False):
            with pytest.raises(ImportError):
                MT5APIWrapper()

    @patch('src.metatrader.mt5_api.MT5_AVAILABLE', True)
    @patch('src.metatrader.mt5_api.mt5')
    def test_connect_success(self, mock_mt5):
        """Test successful connection to MT5."""
        mock_mt5.initialize.return_value = True
        
        wrapper = MT5APIWrapper()
        result = wrapper.connect()
        
        assert result is True
        assert wrapper.connected is True
        mock_mt5.initialize.assert_called_once()

    @patch('src.metatrader.mt5_api.MT5_AVAILABLE', True)
    @patch('src.metatrader.mt5_api.mt5')
    def test_connect_failure(self, mock_mt5):
        """Test failed connection to MT5."""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = "Connection error"
        
        wrapper = MT5APIWrapper()
        result = wrapper.connect()
        
        assert result is False
        assert wrapper.connected is False

    @patch('src.metatrader.mt5_api.MT5_AVAILABLE', True)
    @patch('src.metatrader.mt5_api.mt5')
    def test_disconnect(self, mock_mt5):
        """Test disconnect from MT5."""
        mock_mt5.initialize.return_value = True
        
        wrapper = MT5APIWrapper()
        wrapper.connect()
        wrapper.disconnect()
        
        assert wrapper.connected is False
        mock_mt5.shutdown.assert_called_once()


class TestStatisticsAnalyzer:
    """Test statistics analyzer."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        from src.statistics import StatisticsAnalyzer
        
        analyzer = StatisticsAnalyzer()
        assert analyzer.trades == []

    def test_empty_metrics(self):
        """Test metrics calculation with no trades."""
        from src.statistics import StatisticsAnalyzer
        
        analyzer = StatisticsAnalyzer()
        metrics = analyzer.calculate_metrics()
        
        assert metrics.total_trades == 0
        assert metrics.win_rate == 0.0
        assert metrics.net_profit == 0.0
