# Ledger

**ICT Trade Journal for Windows** — A comprehensive trading journal system for MetaTrader 5.

Ledger automatically reads closed positions from MetaTrader 5, records your trading reasoning, syncs all data with Notion, and generates detailed statistics with rigorous corrections.

## Features

### MetaTrader 5 Integration
- Automatically retrieve closed positions from MT5 using official Python API
- Extract all trade metadata: entry/exit prices, times, volume, P&L, commissions, swaps
- Filter trades by symbol and date range
- Support for all order types (BUY, SELL, LIMIT, STOP)
- Account information tracking (balance, equity, margin)

### Notion Syncing
- Create and update trade records in your Notion database
- Rich formatting with all trade details
- Track trading reasoning, setup notes, and ICT concepts
- Easy filtering and analysis within Notion
- Bi-directional sync support

### Statistics & Reporting
- **Core Metrics**: Win rate, profit factor, expectancy, Sharpe ratio
- **Risk Analysis**: Maximum drawdown, consecutive losses, recovery factor
- **Performance Breakdown**: By-symbol analysis and time-series tracking
- **Rigorous Corrections**: Account for commissions, swaps, and fees
- **Risk/Reward Analysis**: Track RR ratios and average performance

### Command-Line Interface (CLI)
- `ledger sync` — Sync trades from MT5 to Notion
- `ledger stats` — Generate performance reports
- `ledger config` — View/manage configuration
- Easy export to JSON/CSV

## Quick Start

### 1. Prerequisites

- **Windows** (required for MetaTrader 5)
- Python 3.9+
- MetaTrader 5 terminal installed and running
- Notion API key and database ID

### 2. Clone and Install

```bash
git clone <repository-url>
cd ledger
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -e ".[dev,mt5]"
```

### 3. Configure

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

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

### 4. Run

**Sync trades from MT5 to Notion:**
```bash
ledger sync --days 30
```

**Generate statistics report:**
```bash
ledger stats --symbol EURUSD
```

**View current configuration:**
```bash
ledger config
```

## Project Structure

```
ledger/
├── src/
│   ├── metatrader/
│   │   ├── __init__.py
│   │   ├── client.py          # MetaTrader5Client (legacy)
│   │   ├── mt5_api.py         # MT5APIWrapper (actual implementation)
│   │   └── models.py          # Trade and position models
│   ├── notion/
│   │   ├── __init__.py
│   │   ├── client.py          # Notion API client
│   │   └── models.py          # Notion record models
│   ├── statistics/
│   │   ├── __init__.py
│   │   ├── analyzer.py        # Performance calculator
│   │   └── models.py          # Metrics and report models
│   ├── config.py              # Configuration management
│   ├── cli.py                 # Command-line interface
│   ├── main.py                # Application entry point
│   └── __init__.py
├── tests/
│   ��── __init__.py
│   ├── test_models.py         # Data model tests
│   ├── test_mt5_api.py        # MT5 API tests
│   └── test_cli.py            # CLI tests
├── .github/
│   └── workflows/
│       ├── tests.yml          # Test automation
│       ├── lint.yml           # Code quality checks
│       ├── security.yml       # Security scanning
│       └── build.yml          # Package building
├── .env.example               # Configuration template
├── .gitignore
├── Makefile                   # Development commands
├── pyproject.toml             # Project metadata & build config
├── requirements.txt           # Core dependencies
├── requirements-dev.txt       # Dev & test dependencies
├── requirements-mt5.txt       # MetaTrader5 library
├── README.md
└── LICENSE
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MT5_ACCOUNT_NUMBER` | MetaTrader 5 account number | ✓ |
| `MT5_SERVER` | MT5 server name (e.g., ICMarkets-Demo) | ✓ |
| `NOTION_API_KEY` | Notion API integration token | ✓ |
| `NOTION_DATABASE_ID` | Notion trades database ID | ✓ |
| `DEBUG` | Enable debug logging | ✗ |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ✗ |

### Setup Notion Database

1. Create a new database in Notion
2. Add properties:
   - `Symbol` (Text)
   - `Type` (Select: BUY, SELL)
   - `Volume` (Number)
   - `OpenPrice` (Number)
   - `OpenTime` (Date)
   - `ClosePrice` (Number)
   - `CloseTime` (Date)
   - `Profit` (Number)
   - `Commission` (Number)
   - `Swap` (Number)
   - `NetProfit` (Number)
   - `Reasoning` (Rich Text)
   - `EntryCondition` (Text)
   - `ExitCondition` (Text)
   - `RiskReward` (Number)
   - `ICTConcepts` (Text)
   - `Status` (Select: Closed, Open)
   - `DateRecorded` (Date)

## Development

### Setup Development Environment

```bash
make install-dev
```

### Run Tests

```bash
make test                    # Full test suite with coverage
make test-fast              # Quick tests
```

### Code Quality

```bash
make lint                   # Check code style
make format                 # Auto-format code
make format-check          # Check if formatting needed
```

### Available Make Commands

```bash
make help                   # Show all commands
make install               # Install dependencies
make install-dev           # Install dev dependencies
make install-mt5           # Install MetaTrader5 library
make test                  # Run full test suite
make lint                  # Check code quality
make format                # Format code
make clean                 # Clean build artifacts
make run                   # Run application
```

## CLI Reference

### Sync Command

```bash
ledger sync [OPTIONS]
  --days INTEGER           Days back to retrieve (default: 30)
  --symbol TEXT           Filter by symbol (e.g., EURUSD)
  --save TEXT             Save results to JSON file
```

Example:
```bash
ledger sync --days 60 --symbol EURUSD --save trades.json
```

### Stats Command

```bash
ledger stats [OPTIONS]
  --days INTEGER          Days back to analyze (default: 30)
  --symbol TEXT          Filter by symbol
  --export TEXT          Export report to JSON/CSV
```

Example:
```bash
ledger stats --symbol EURUSD --export report.json
```

### Config Command

```bash
ledger config
```

Displays current configuration settings.

## API Overview

### MetaTrader 5 API

```python
from src.metatrader.mt5_api import MT5APIWrapper

# Initialize and connect
mt5 = MT5APIWrapper()
if mt5.connect(account=123456, password="pass", server="Server"):
    # Get account info
    account = mt5.get_account_info()
    print(f"Balance: {account['balance']}")
    
    # Get closed positions
    positions = mt5.get_closed_positions(days_back=30)
    print(f"Found {len(positions)} closed positions")
    
    # Get symbol info
    symbol_info = mt5.get_symbol_info("EURUSD")
    print(f"Ask: {symbol_info['ask']}, Bid: {symbol_info['bid']}")
    
    mt5.disconnect()
```

### Statistics Analyzer

```python
from src.statistics import StatisticsAnalyzer
from src.metatrader.models import Trade

analyzer = StatisticsAnalyzer()
analyzer.add_trades(trades_list)

# Calculate metrics
metrics = analyzer.calculate_metrics()
print(f"Win Rate: {metrics.win_rate}%")
print(f"Profit Factor: {metrics.profit_factor}")
print(f"Max Drawdown: {metrics.max_drawdown}")
print(f"Sharpe Ratio: {metrics.sharpe_ratio}")

# Generate full report
report = analyzer.generate_report(symbol_filter="EURUSD")
```

### Notion Client

```python
from src.notion import NotionClient
from src.notion.models import NotionTradeRecord

notion = NotionClient()
if notion.connect():
    # Create trade record
    record = NotionTradeRecord(symbol="EURUSD", ...)
    page_id = notion.create_trade_record(record)
    
    # Query trades
    trades = notion.query_trades(symbol="EURUSD")
    
    notion.disconnect()
```

## CI/CD Pipeline

### GitHub Actions Workflows

- **tests.yml** — Run pytest on Python 3.9, 3.10, 3.11
- **lint.yml** — Code quality checks (black, isort, flake8, mypy)
- **security.yml** — Security scanning (bandit, safety)
- **build.yml** — Package building and distribution

## Roadmap

- [x] Core project structure
- [x] MetaTrader 5 API integration
- [x] Notion syncing models
- [x] Statistics engine
- [x] CLI interface
- [x] GitHub Actions CI/CD
- [ ] Implement Notion API sync
- [ ] Add Windows schedule integration
- [ ] Build GUI dashboard
- [ ] Advanced statistics (Monte Carlo, VAR)
- [ ] Mobile companion app

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests and linting (`make test lint`)
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions, please open a GitHub issue.

## Author

Jobberniecortejo09
