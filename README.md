# Real-Time In-Memory Crypto Backtest Engine

A Python historical market engine built to process abrupt movements of historical time-series prices using CCXT. The application features a pagination loop to follow rate limits, compiling market datasets into memory and also, to trigger an algorithm whenever there's volatility (abrupt pump or dump) on a certain symbol.

This was done to practice how to fetch market data from CCXT API for future version of backtesting. Also, categorizing abrupt movements per session gives us an idea on what session the price is more volatile. This is also testing a single pair, for future references: change the trading pair to be retrieved from CCXT.

## Features

- **Historical Data Pagination:** Retrieves OHLCV candles in sequential batches while respecting rate limits and advancing request timestamp to prevent duplicate entries.
- **Volatilty Tracker Logic:** Evaluates candle-to-candle price change against configurable volatility thresholds set (`MAX_PUMP` / `MAX_DROP`).
- **Market Session Tagging:** Parses standardized global UTC timestamps into human-readable regional market sessions (Asian, London, New York AM/PM) to map cyclical volatility trends.
- **Modular Pipeline:** Separates market-data retrieval, event processing, and future analytics into independent Python modules.

## Technologies

- **Language:** Python 3
- **Core API:** CCXT (Crypto Currency eXchange Trading Library), Binance US
- **Data Models:** In-Memory List Matrices, Structured CSV Logs
- **Architecture:** Modular Data Retrieval and Event-Processing Pipeline

## How it works

The script decouples the ingestion layer from the strategy evaluation loops:

1. **Exchange Initialization:** Connects to Binance US through CCXT and loads the required exchange configuration.
2. **Sequential Download:** Retrieves historical OHLCV candles in batches between the set start and end dates.
3. **In-Memory Processing:** Iterates through the retrieved candle dataset and calculates consecutive open-to-open price movements.
4. **Event Detection:** Identifies movements that exceed the configured upward or downward USD thresholds.
5. **Session Classification:** Assigns each detected event to its corresponding market session based on UTC time.
6. **Persistent Storage:** Exports detected events into `data/backtest_flash_log.csv` for further analysis.

## Installation & Usage

### 1. Clone the Workspace

```bash
git clone https://github.com/jdpapena/crypto-backtest-engine.git
cd crypto-backtest-engine
```

### 2. Install Dependencies

```bash
python -m pip install ccxt
```

### 3. Run the Backtester

```bash
python main.py
```

## Sample Output

```bash
==================================================
Binance Historical Market Event Engine
==================================================
BTC/USDT (1h) from 2026-05-01 to 2026-06-01
Stored 500 candles. Progress reached: 2026-05-21 19:00:00 UTC
Stored 1,000 candles. Progress reached: 2026-06-11 15:00:00 UTC

Processing historical data...
FLASH DROP: 2026-05-15 14:00:00 UTC | Move: $-1,613.77 | Session: New York AM
FLASH DROP: 2026-06-05 19:00:00 UTC | Move: $-1,623.78 | Session: New York PM
==================================================
RESULTS: Processed 1,000 candles.
Detected 2 market events.
Saved results to 'data/backtest_flash_log.csv'
==================================================
```

## Output File Format

```text
Timestamp,Event Type,Price in USD,Price Change in USD,Market Session,Notes
2026-05-15 14:00:00,DUMP,103754.59,-1613.77,New York AM,
2026-06-05 19:00:00,DUMP,101547.50,-1623.78,New York PM,
```

