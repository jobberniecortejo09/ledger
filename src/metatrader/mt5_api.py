"""MetaTrader 5 API wrapper using pymetatrader or mt5 library."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

logger = logging.getLogger(__name__)


class MT5ConnectionError(Exception):
    """Raised when MT5 connection fails."""
    pass


class MT5APIWrapper:
    """Wrapper around MetaTrader 5 Python API.
    
    Requires MetaTrader 5 terminal running on Windows and the MetaTrader5 Python package.
    Install with: pip install MetaTrader5
    """

    def __init__(self, timeout: int = 5000):
        """Initialize MT5 API wrapper.
        
        Args:
            timeout: Connection timeout in milliseconds
            
        Raises:
            ImportError: If MetaTrader5 package is not installed
        """
        if not MT5_AVAILABLE:
            raise ImportError(
                "MetaTrader5 library not installed. Install with: pip install MetaTrader5"
            )
        self.timeout = timeout
        self.connected = False

    def connect(
        self,
        account: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
    ) -> bool:
        """Connect to MetaTrader 5 terminal.
        
        Args:
            account: Account number (optional)
            password: Account password (optional)
            server: Server name (optional)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not mt5.initialize():
                logger.error(f"Failed to initialize MT5: {mt5.last_error()}")
                return False

            if account and password and server:
                if not mt5.login(login=account, password=password, server=server):
                    logger.error(f"Failed to login to MT5: {mt5.last_error()}")
                    return False

            self.connected = True
            logger.info("Successfully connected to MetaTrader 5")
            return True
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from MetaTrader 5."""
        try:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MetaTrader 5")
        except Exception as e:
            logger.error(f"Error disconnecting from MT5: {e}")

    def get_account_info(self) -> Optional[dict]:
        """Get current account information.
        
        Returns:
            Dictionary with account details or None on error
        """
        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        try:
            account_info = mt5.account_info()
            if account_info is None:
                logger.error(f"Failed to get account info: {mt5.last_error()}")
                return None

            return {
                "login": account_info.login,
                "name": account_info.name,
                "server": account_info.server,
                "currency": account_info.currency,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "credit": account_info.credit,
                "profit": account_info.profit,
                "margin": account_info.margin,
                "margin_free": account_info.margin_free,
                "margin_level": account_info.margin_level,
                "margin_so_call": account_info.margin_so_call,
                "margin_so_so": account_info.margin_so_so,
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def get_closed_positions(
        self,
        symbol: Optional[str] = None,
        group: Optional[str] = None,
        days_back: int = 30,
    ) -> List[dict]:
        """Get closed positions from account history.
        
        Args:
            symbol: Filter by symbol (e.g., 'EURUSD')
            group: Filter by symbol group (e.g., 'Forex')
            days_back: Number of days back to retrieve
            
        Returns:
            List of closed position dictionaries
        """
        if not self.connected:
            logger.warning("Not connected to MT5")
            return []

        try:
            # Get positions from account history
            start_date = datetime.now() - timedelta(days=days_back)
            
            deals = mt5.history_deals_get(start_date, datetime.now())
            if deals is None:
                logger.error(f"Failed to get history deals: {mt5.last_error()}")
                return []

            closed_positions = []
            processed_tickets = set()

            for deal in deals:
                if deal.ticket in processed_tickets:
                    continue

                # Filter by symbol if specified
                if symbol and deal.symbol != symbol:
                    continue

                # Convert DEAL_ENTRY to readable format
                deal_entry = "ENTRY" if deal.entry == 0 else "EXIT" if deal.entry == 1 else "UNKNOWN"

                position_data = {
                    "ticket": deal.ticket,
                    "symbol": deal.symbol,
                    "type": "BUY" if deal.type == 0 else "SELL" if deal.type == 1 else "UNKNOWN",
                    "volume": deal.volume,
                    "price": deal.price,
                    "time": datetime.fromtimestamp(deal.time),
                    "profit": deal.profit,
                    "commission": deal.commission,
                    "swap": deal.swap,
                    "comment": deal.comment,
                    "magic": deal.magic,
                }
                closed_positions.append(position_data)
                processed_tickets.add(deal.ticket)

            logger.info(f"Retrieved {len(closed_positions)} closed positions")
            return closed_positions
        except Exception as e:
            logger.error(f"Error retrieving closed positions: {e}")
            return []

    def get_open_positions(self, symbol: Optional[str] = None) -> List[dict]:
        """Get currently open positions.
        
        Args:
            symbol: Filter by symbol (e.g., 'EURUSD')
            
        Returns:
            List of open position dictionaries
        """
        if not self.connected:
            logger.warning("Not connected to MT5")
            return []

        try:
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                logger.error(f"Failed to get open positions: {mt5.last_error()}")
                return []

            open_positions = []
            for pos in positions:
                position_data = {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == 0 else "SELL",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "time_open": datetime.fromtimestamp(pos.time),
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "comment": pos.comment,
                    "magic": pos.magic,
                }
                open_positions.append(position_data)

            logger.info(f"Retrieved {len(open_positions)} open positions")
            return open_positions
        except Exception as e:
            logger.error(f"Error retrieving open positions: {e}")
            return []

    def get_symbol_info(self, symbol: str) -> Optional[dict]:
        """Get detailed information about a symbol.
        
        Args:
            symbol: Symbol name (e.g., 'EURUSD')
            
        Returns:
            Dictionary with symbol details or None on error
        """
        if not self.connected:
            logger.warning("Not connected to MT5")
            return None

        try:
            sym_info = mt5.symbol_info(symbol)
            if sym_info is None:
                logger.error(f"Symbol {symbol} not found: {mt5.last_error()}")
                return None

            return {
                "name": sym_info.name,
                "description": sym_info.description,
                "bid": sym_info.bid,
                "ask": sym_info.ask,
                "point": sym_info.point,
                "digits": sym_info.digits,
                "volume": sym_info.volume,
                "volume_high": sym_info.volume_high,
                "volume_low": sym_info.volume_low,
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
