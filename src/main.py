"""Main entry point for the Ledger application."""

import logging
from datetime import datetime

from src.config import settings
from src.metatrader import MetaTrader5Client
from src.notion import NotionClient
from src.statistics import StatisticsAnalyzer

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main application flow."""
    logger.info("=" * 60)
    logger.info("Ledger - ICT Trade Journal for MetaTrader 5")
    logger.info(f"Started at {datetime.utcnow().isoformat()}")
    logger.info("=" * 60)
    
    # Initialize clients
    mt5_client = MetaTrader5Client()
    notion_client = NotionClient()
    analyzer = StatisticsAnalyzer()
    
    try:
        # Connect to MetaTrader 5
        logger.info("Connecting to MetaTrader 5...")
        if not mt5_client.connect():
            logger.error("Failed to connect to MetaTrader 5")
            return
        
        # Connect to Notion
        logger.info("Connecting to Notion...")
        if not notion_client.connect():
            logger.warning("Could not connect to Notion (optional)")
        
        # Retrieve closed positions from MT5
        logger.info("Retrieving closed positions...")
        positions = mt5_client.get_closed_positions(days_back=30)
        logger.info(f"Retrieved {len(positions)} closed positions")
        
        # TODO: Process trades and sync to Notion
        # TODO: Generate statistics and reports
        
        logger.info("Ledger sync completed successfully")
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        mt5_client.disconnect()
        notion_client.disconnect()
        logger.info("Disconnected from all services")


if __name__ == "__main__":
    main()
