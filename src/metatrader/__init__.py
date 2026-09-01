"""MetaTrader 5 integration module.

Handles reading closed positions and trade data from MetaTrader 5 terminal.
"""

from .client import MetaTrader5Client
from .models import Trade, TradePosition

__all__ = ["MetaTrader5Client", "Trade", "TradePosition"]
