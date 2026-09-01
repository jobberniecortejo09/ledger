"""Trade statistics and performance analysis engine."""

import logging
from datetime import datetime
from typing import List, Optional

from src.metatrader.models import Trade, OrderType
from .models import PerformanceMetrics, TradeStatistics

logger = logging.getLogger(__name__)


class StatisticsAnalyzer:
    """Analyzes trade performance with rigorous corrections and metrics."""

    def __init__(self):
        """Initialize the statistics analyzer."""
        self.trades: List[Trade] = []

    def add_trades(self, trades: List[Trade]) -> None:
        """Add trades for analysis.
        
        Args:
            trades: List of Trade objects to analyze
        """
        self.trades.extend(trades)
        logger.info(f"Added {len(trades)} trades for analysis. Total: {len(self.trades)}")

    def clear_trades(self) -> None:
        """Clear all loaded trades."""
        self.trades.clear()
        logger.info("Cleared all trades")

    def calculate_metrics(
        self,
        trades: Optional[List[Trade]] = None,
        symbol_filter: Optional[str] = None,
    ) -> PerformanceMetrics:
        """Calculate performance metrics for trades.
        
        Args:
            trades: List of trades to analyze (uses self.trades if None)
            symbol_filter: Only analyze trades for this symbol
            
        Returns:
            PerformanceMetrics object with calculated statistics
        """
        trades = trades or self.trades
        
        # Filter by symbol if specified
        if symbol_filter:
            trades = [t for t in trades if t.position.symbol == symbol_filter]
        
        if not trades:
            logger.warning("No trades to analyze")
            return self._empty_metrics()
        
        # Separate winning and losing trades
        winning_trades = [t for t in trades if t.position.profit > 0]
        losing_trades = [t for t in trades if t.position.profit < 0]
        
        total_trades = len(trades)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        
        # Calculate basic metrics
        gross_profit = sum(t.position.profit for t in winning_trades)
        gross_loss = abs(sum(t.position.profit for t in losing_trades))
        net_profit = sum(t.position.profit for t in trades)
        
        # Commission and swap adjustments
        total_commission = sum(t.position.commission for t in trades)
        total_swap = sum(t.position.swap for t in trades)
        net_profit_after_fees = net_profit - total_commission + total_swap
        
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        avg_win = gross_profit / winning_count if winning_count > 0 else 0.0
        avg_loss = gross_loss / losing_count if losing_count > 0 else 0.0
        
        largest_win = max(
            (t.position.profit for t in winning_trades), default=0.0
        )
        largest_loss = abs(min(
            (t.position.profit for t in losing_trades), default=0.0
        ))
        
        expectancy = net_profit / total_trades if total_trades > 0 else 0.0
        
        # Consecutive win/loss streaks
        consecutive_wins, consecutive_losses = self._calculate_streaks(trades)
        
        # Drawdown analysis
        max_drawdown, max_consecutive_loss = self._calculate_drawdown(trades)
        
        # Recovery factor
        recovery_factor = net_profit / max_drawdown if max_drawdown > 0 else 0.0
        
        # Average risk/reward ratio
        avg_rr = self._calculate_avg_risk_reward(trades)
        
        # Sharpe ratio (simple calculation)
        sharpe_ratio = self._calculate_sharpe_ratio(trades)
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_count,
            losing_trades=losing_count,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit_after_fees,
            profit_factor=profit_factor,
            average_win=avg_win,
            average_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            expectancy=expectancy,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            max_drawdown=max_drawdown,
            max_consecutive_loss=max_consecutive_loss,
            sharpe_ratio=sharpe_ratio,
            recovery_factor=recovery_factor,
            avg_risk_reward=avg_rr,
        )

    def generate_report(
        self,
        trades: Optional[List[Trade]] = None,
        symbol_filter: Optional[str] = None,
    ) -> TradeStatistics:
        """Generate a complete trade statistics report.
        
        Args:
            trades: List of trades to analyze (uses self.trades if None)
            symbol_filter: Only analyze trades for this symbol
            
        Returns:
            TradeStatistics report object
        """
        trades = trades or self.trades
        metrics = self.calculate_metrics(trades, symbol_filter)
        
        # TODO: Calculate by-symbol metrics
        by_symbol = {}
        symbols = set(t.position.symbol for t in trades)
        for symbol in symbols:
            symbol_trades = [t for t in trades if t.position.symbol == symbol]
            by_symbol[symbol] = self.calculate_metrics(symbol_trades)
        
        # TODO: Calculate daily metrics for time series analysis
        daily_metrics = []
        
        report = TradeStatistics(
            period_start=min(
                (t.position.open_time for t in trades), default=None
            ),
            period_end=max(
                (t.position.close_time for t in trades if t.position.close_time), default=None
            ),
            symbol_filter=symbol_filter,
            metrics=metrics,
            by_symbol=by_symbol,
            daily_metrics=daily_metrics,
            trades_analyzed=len(trades),
            trade_tickets=[t.position.ticket for t in trades],
        )
        
        return report

    def _empty_metrics(self) -> PerformanceMetrics:
        """Return metrics with all zeros for empty trade set."""
        return PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            gross_profit=0.0,
            gross_loss=0.0,
            net_profit=0.0,
            profit_factor=0.0,
            average_win=0.0,
            average_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            expectancy=0.0,
            consecutive_wins=0,
            consecutive_losses=0,
            max_drawdown=0.0,
            max_consecutive_loss=0.0,
            recovery_factor=0.0,
        )

    def _calculate_streaks(self, trades: List[Trade]) -> tuple[int, int]:
        """Calculate longest consecutive wins and losses.
        
        Args:
            trades: Trades sorted by close time
            
        Returns:
            Tuple of (max_consecutive_wins, max_consecutive_losses)
        """
        if not trades:
            return 0, 0
        
        sorted_trades = sorted(trades, key=lambda t: t.position.close_time or datetime.min)
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in sorted_trades:
            if trade.position.profit > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses

    def _calculate_drawdown(self, trades: List[Trade]) -> tuple[float, float]:
        """Calculate maximum drawdown and consecutive loss.
        
        Args:
            trades: Trades to analyze
            
        Returns:
            Tuple of (max_drawdown, max_consecutive_loss)
        """
        if not trades:
            return 0.0, 0.0
        
        sorted_trades = sorted(trades, key=lambda t: t.position.close_time or datetime.min)
        
        cumulative = 0.0
        peak = 0.0
        max_drawdown = 0.0
        consecutive_loss = 0.0
        max_consecutive_loss = 0.0
        
        for trade in sorted_trades:
            cumulative += trade.position.profit
            
            if cumulative > peak:
                peak = cumulative
            
            drawdown = peak - cumulative
            max_drawdown = max(max_drawdown, drawdown)
            
            if trade.position.profit < 0:
                consecutive_loss += abs(trade.position.profit)
                max_consecutive_loss = max(max_consecutive_loss, consecutive_loss)
            else:
                consecutive_loss = 0.0
        
        return max_drawdown, max_consecutive_loss

    def _calculate_avg_risk_reward(self, trades: List[Trade]) -> Optional[float]:
        """Calculate average risk/reward ratio.
        
        Args:
            trades: Trades with risk_reward_ratio set
            
        Returns:
            Average risk/reward ratio or None if not available
        """
        rr_ratios = [t.risk_reward_ratio for t in trades if t.risk_reward_ratio]
        if not rr_ratios:
            return None
        return sum(rr_ratios) / len(rr_ratios)

    def _calculate_sharpe_ratio(
        self,
        trades: List[Trade],
        risk_free_rate: float = 0.02,
    ) -> Optional[float]:
        """Calculate Sharpe ratio for the trade set.
        
        Args:
            trades: Trades to analyze
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio or None if insufficient data
        """
        if len(trades) < 2:
            return None
        
        profits = [t.position.profit for t in trades]
        mean_profit = sum(profits) / len(profits)
        
        # Calculate standard deviation
        variance = sum((p - mean_profit) ** 2 for p in profits) / (len(profits) - 1)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return None
        
        # Simplified Sharpe ratio (daily returns assumed)
        sharpe = (mean_profit - (risk_free_rate / 252)) / std_dev if std_dev > 0 else 0
        return sharpe
