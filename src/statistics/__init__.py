"""Statistics and reporting module.

Generates trade statistics and rigorous performance analysis.
"""

from .analyzer import StatisticsAnalyzer
from .models import TradeStatistics, PerformanceMetrics

__all__ = ["StatisticsAnalyzer", "TradeStatistics", "PerformanceMetrics"]
