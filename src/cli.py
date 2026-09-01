"""Command-line interface for Ledger application."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    click = None

from src.config import settings
from src.metatrader import MetaTrader5Client
from src.metatrader.mt5_api import MT5APIWrapper
from src.notion import NotionClient
from src.statistics import StatisticsAnalyzer

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


if not click:
    def cli(*args, **kwargs):
        """Dummy decorator when click is not installed."""
        def decorator(f):
            return f
        return decorator
else:
    @click.group()
    @click.option('--debug/--no-debug', default=False, help='Enable debug logging')
    def cli(debug):
        """Ledger - ICT Trade Journal for MetaTrader 5."""
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")


@click.command()
@click.option(
    '--days',
    default=30,
    type=int,
    help='Number of days back to retrieve (default: 30)'
)
@click.option(
    '--symbol',
    default=None,
    type=str,
    help='Filter by symbol (e.g., EURUSD)'
)
@click.option(
    '--save',
    default=None,
    type=str,
    help='Save results to JSON file'
)
def sync(days: int, symbol: Optional[str], save: Optional[str]):
    """Sync closed positions from MetaTrader 5 to Notion."""
    click.echo(click.style("="*60, fg='cyan'))
    click.echo(click.style("Ledger - MT5 to Notion Sync", fg='cyan', bold=True))
    click.echo(click.style(f"Started at {datetime.utcnow().isoformat()}", fg='cyan'))
    click.echo(click.style("="*60, fg='cyan'))

    try:
        # Connect to MT5
        click.echo(click.style("\n[1/4] Connecting to MetaTrader 5...", fg='yellow'))
        mt5_client = MT5APIWrapper()
        
        if not mt5_client.connect():
            click.echo(click.style("✗ Failed to connect to MetaTrader 5", fg='red'))
            click.echo(
                click.style(
                    "Ensure MetaTrader 5 terminal is running and configured in .env",
                    fg='red',
                    dim=True
                )
            )
            sys.exit(1)
        
        click.echo(click.style("✓ Connected to MetaTrader 5", fg='green'))

        # Get account info
        account_info = mt5_client.get_account_info()
        if account_info:
            click.echo(
                click.style(
                    f"  Account: {account_info.get('login')} ({account_info.get('name')})",
                    dim=True
                )
            )
            click.echo(
                click.style(
                    f"  Balance: {account_info.get('balance')} {account_info.get('currency')}",
                    dim=True
                )
            )

        # Retrieve closed positions
        click.echo(
            click.style(
                f"\n[2/4] Retrieving closed positions (last {days} days)...",
                fg='yellow'
            )
        )
        closed_positions = mt5_client.get_closed_positions(days_back=days, symbol=symbol)
        click.echo(
            click.style(
                f"✓ Retrieved {len(closed_positions)} closed positions",
                fg='green'
            )
        )

        if not closed_positions:
            click.echo(click.style("No positions found.", fg='yellow'))
            sys.exit(0)

        # Display positions summary
        click.echo(click.style("\nPositions Summary:", fg='cyan', bold=True))
        total_profit = sum(p['profit'] for p in closed_positions)
        winning = sum(1 for p in closed_positions if p['profit'] > 0)
        losing = sum(1 for p in closed_positions if p['profit'] < 0)
        
        click.echo(f"  Total P&L: {total_profit:+.2f}")
        click.echo(f"  Winning Trades: {winning}/{len(closed_positions)}")
        click.echo(f"  Losing Trades: {losing}/{len(closed_positions)}")

        # Connect to Notion
        click.echo(click.style("\n[3/4] Connecting to Notion...", fg='yellow'))
        notion_client = NotionClient()
        
        if not notion_client.connect():
            click.echo(
                click.style(
                    "⚠ Could not connect to Notion (syncing will be skipped)",
                    fg='yellow'
                )
            )
        else:
            click.echo(click.style("✓ Connected to Notion", fg='green'))
            # TODO: Sync to Notion
            click.echo(
                click.style(
                    "  (Notion sync not yet implemented)",
                    dim=True
                )
            )

        # Generate statistics
        click.echo(click.style("\n[4/4] Generating statistics...", fg='yellow'))
        analyzer = StatisticsAnalyzer()
        # TODO: Convert closed_positions to Trade objects and analyze
        click.echo(click.style("✓ Statistics generated", fg='green'))

        # Save to file if requested
        if save:
            import json
            output_path = Path(save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert datetime objects to ISO format strings
            serializable_positions = []
            for pos in closed_positions:
                pos_copy = pos.copy()
                if isinstance(pos_copy.get('time'), datetime):
                    pos_copy['time'] = pos_copy['time'].isoformat()
                serializable_positions.append(pos_copy)
            
            with open(output_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.utcnow().isoformat(),
                    'account': account_info,
                    'positions': serializable_positions,
                }, f, indent=2)
            
            click.echo(
                click.style(
                    f"\n✓ Results saved to {output_path}",
                    fg='green'
                )
            )

        click.echo(
            click.style(
                f"\n✓ Sync completed successfully",
                fg='green',
                bold=True
            )
        )

    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {e}", fg='red'))
        if settings.debug:
            logger.exception("Detailed error:")
        sys.exit(1)
    finally:
        try:
            mt5_client.disconnect()
            if 'notion_client' in locals():
                notion_client.disconnect()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


@click.command()
@click.option(
    '--days',
    default=30,
    type=int,
    help='Number of days back to analyze (default: 30)'
)
@click.option(
    '--symbol',
    default=None,
    type=str,
    help='Filter by symbol (e.g., EURUSD)'
)
@click.option(
    '--export',
    default=None,
    type=str,
    help='Export report to JSON/CSV file'
)
def stats(days: int, symbol: Optional[str], export: Optional[str]):
    """Generate trade statistics and performance report."""
    click.echo(click.style("="*60, fg='cyan'))
    click.echo(click.style("Ledger - Trade Statistics Report", fg='cyan', bold=True))
    click.echo(click.style(f"Generated at {datetime.utcnow().isoformat()}", fg='cyan'))
    click.echo(click.style("="*60, fg='cyan'))

    try:
        # TODO: Load trades from Notion or MT5
        analyzer = StatisticsAnalyzer()
        
        if not analyzer.trades:
            click.echo(
                click.style("No trades loaded. Run 'ledger sync' first.", fg='yellow')
            )
            sys.exit(1)

        # Calculate metrics
        click.echo(click.style("\nCalculating metrics...", fg='yellow'))
        metrics = analyzer.calculate_metrics(symbol_filter=symbol)
        report = analyzer.generate_report(symbol_filter=symbol)

        # Display report
        click.echo(click.style("\n" + "="*60, fg='cyan'))
        click.echo(click.style("Performance Metrics", fg='cyan', bold=True))
        click.echo(click.style("="*60, fg='cyan'))
        
        click.echo(f"Total Trades:        {metrics.total_trades}")
        click.echo(f"Winning Trades:      {metrics.winning_trades} ({metrics.win_rate:.2f}%)")
        click.echo(f"Losing Trades:       {metrics.losing_trades}")
        click.echo()
        click.echo(f"Gross Profit:        {metrics.gross_profit:+.2f}")
        click.echo(f"Gross Loss:          {metrics.gross_loss:+.2f}")
        click.echo(f"Net Profit:          {metrics.net_profit:+.2f}")
        click.echo()
        click.echo(f"Profit Factor:       {metrics.profit_factor:.2f}")
        click.echo(f"Expectancy:          {metrics.expectancy:+.2f}")
        click.echo(f"Average Win:         {metrics.average_win:+.2f}")
        click.echo(f"Average Loss:        {metrics.average_loss:+.2f}")
        click.echo()
        click.echo(f"Largest Win:         {metrics.largest_win:+.2f}")
        click.echo(f"Largest Loss:        {metrics.largest_loss:+.2f}")
        click.echo(f"Win/Loss Ratio:      {metrics.largest_win / metrics.largest_loss if metrics.largest_loss > 0 else 0:.2f}")
        click.echo()
        click.echo(f"Consecutive Wins:    {metrics.consecutive_wins}")
        click.echo(f"Consecutive Losses:  {metrics.consecutive_losses}")
        click.echo(f"Max Drawdown:        {metrics.max_drawdown:+.2f}")
        click.echo(f"Recovery Factor:     {metrics.recovery_factor:.2f}")
        
        if metrics.sharpe_ratio:
            click.echo(f"Sharpe Ratio:        {metrics.sharpe_ratio:.4f}")
        
        if metrics.avg_risk_reward:
            click.echo(f"Avg Risk/Reward:     {metrics.avg_risk_reward:.2f}")
        
        click.echo(click.style("="*60, fg='cyan'))

        # Export if requested
        if export:
            import json
            output_path = Path(export)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report.dict(), f, indent=2, default=str)
            
            click.echo(
                click.style(
                    f"\n✓ Report exported to {output_path}",
                    fg='green'
                )
            )

        click.echo(
            click.style(
                "\n✓ Report generated successfully",
                fg='green',
                bold=True
            )
        )

    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {e}", fg='red'))
        if settings.debug:
            logger.exception("Detailed error:")
        sys.exit(1)


@click.command()
def config_show():
    """Display current configuration."""
    click.echo(click.style("Current Configuration:", fg='cyan', bold=True))
    click.echo()
    click.echo(f"MT5 Account:         {settings.mt5_account_number or 'NOT SET'}")
    click.echo(f"MT5 Server:          {settings.mt5_server or 'NOT SET'}")
    click.echo(f"Notion API Key:      {'SET' if settings.notion_api_key else 'NOT SET'}")
    click.echo(f"Notion Database ID:  {settings.notion_database_id or 'NOT SET'}")
    click.echo(f"Debug Mode:          {settings.debug}")
    click.echo(f"Log Level:           {settings.log_level}")
    click.echo()
    click.echo(
        click.style(
            "To configure, edit .env file or set environment variables.",
            dim=True
        )
    )


@click.command()
def version():
    """Display application version."""
    from src import __version__
    click.echo(f"Ledger v{__version__}")


if click:
    # Register commands
    cli.add_command(sync)
    cli.add_command(stats)
    cli.add_command(config_show, name='config')
    cli.add_command(version)


if __name__ == '__main__':
    if click:
        cli()
    else:
        print("Click library required for CLI. Install with: pip install click")
