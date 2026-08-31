# Ledger

**ICT Trade Journal for Windows** — A comprehensive trading journal system for MetaTrader 5.

Ledger automatically reads closed positions from MetaTrader 5, records your trading reasoning, syncs all data with Notion, and generates detailed statistics with rigorous corrections.

## Features

### MetaTrader 5 Integration
- Automatically retrieve closed positions from MT5
- Extract all trade metadata: entry/exit prices, times, volume, P&L
- Filter trades by symbol and date range
- Support for all order types (BUY, SELL, LIMIT, STOP)

### Notion Syncing
- Create and update trade records in your Notion database
- Rich formatting with all trade details
- Track trading reasoning, setup notes, and ICT concepts
- Easy filtering and analysis within Notion

### Statistics & Reporting
- **Core Metrics**: Win rate, profit factor, expectancy, Sharpe ratio
- **Risk Analysis**: Maximum drawdown, consecutive losses, recovery factor
- **Performance Breakdown**: By-symbol analysis and time-series tracking
- **Rigorous Corrections**: Account for commissions, swaps, and fees
- **Risk/Reward Analysis**: Track RR ratios and average performance

## Project Structure

```
ledger/
├── src/
│   ├── metatrader/        # MT5 integration
│   │   ├── client.py      # MT5 connection and position retrieval
│   │   └── models.py      # Trade and position data models
│   ├── notion/            # Notion database syncing
│   │   ├── client.py      # Notion API client
│   │   └── models.py      # Notion record models
│   ├── statistics/        # Analytics and reporting
│   │   ├── analyzer.py    # Performance calculation engine
│   │   └── models.py      # Metrics and report models
│   ├── config.py          # Application configuration
│   └── main.py            # Main entry point
├── tests/                 # Unit tests
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Dependencies
└── .env.example           # Environment variables template
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ledger
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# MetaTrader 5 Configuration
MT5_ACCOUNT_NUMBER=123456
MT5_SERVER=ICMarkets-Demo

# Notion Configuration
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxx

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### 3. Run

```bash
python -m src.main
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MT5_ACCOUNT_NUMBER` | Your MetaTrader 5 account number | ✓ |
| `MT5_SERVER` | MT5 server name (e.g., ICMarkets-Demo) | ✓ |
| `NOTION_API_KEY` | Notion API integration key | ✓ |
| `NOTION_DATABASE_ID` | ID of your trades database in Notion | ✓ |
| `DEBUG` | Enable debug logging | ✗ |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ✗ |

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
pytest --cov=src tests/  # With coverage report
```

### Code Quality

```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

## API Overview

### MetaTrader 5 Client

```python
from src.metatrader import MetaTrader5Client

client = MetaTrader5Client()
client.connect()

# Get closed positions from last 30 days
positions = client.get_closed_positions(days_back=30)

# Filter by symbol
eurusd_positions = client.get_closed_positions(symbol="EURUSD")
```

### Notion Client

```python
from src.notion import NotionClient
from src.notion.models import NotionTradeRecord

notion = NotionClient()
notion.connect()

# Create trade record
record = NotionTradeRecord(...)
page_id = notion.create_trade_record(record)

# Query trades
trades = notion.query_trades(symbol="EURUSD", status="Closed")
```

### Statistics Analyzer

```python
from src.statistics import StatisticsAnalyzer

analyzer = StatisticsAnalyzer()
analyzer.add_trades(trades)

# Calculate performance metrics
metrics = analyzer.calculate_metrics()
print(f"Win Rate: {metrics.win_rate}%")
print(f"Profit Factor: {metrics.profit_factor}")
print(f"Max Drawdown: ${metrics.max_drawdown}")

# Generate full report
report = analyzer.generate_report()
```

## TODO

- [ ] Implement actual MetaTrader 5 API connection (requires `mt5` Python library)
- [ ] Implement Notion API integration (setup `notion-client` calls)
- [ ] Add Windows-specific MT5 terminal communication
- [ ] Build CLI interface with Click
- [ ] Add periodic sync scheduling
- [ ] Implement detailed performance reports (PDF export)
- [ ] Add trade journal UI (optional)
- [ ] Add more advanced statistics (Monte Carlo, VAR)

## License

MIT License - See LICENSE file for details

## Author

Jobberniecortejo09
