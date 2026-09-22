# Real-Time In-Memory Crypto Backtest Engine

A Python backtesting application engineered to process abrupt movements of historical time-series prices using CCXT. The application features a pagination loop to follow rate limits, compiling market datasets into memory and also, to trigger an algorithm whenever there's volatility (abrupt pump or dump) on a certain symbol.

This was done to practice how to fetch market data from CCXT API for future version of backtesting. Also, categorizing abrupt movements per session gives us an idea on what session the price is more volatile.

## Features

- **Data Pagination:** Dynamically tracks execution coordinates via a universal milestone bookmarking loop (+1ms progression) to prevent data duplication.
- **Volatilty Tracker Logic:** Evaluates candle-to-candle price change against volatility thresholds set (`MAX_PUMP` / `MAX_DROP`).
- **Categorical Session Tagging:** Parses standardized global UTC timestamps into human-readable regional market sessions (Asian, London, New York AM/PM) to map cyclical volatility trends.

## Technologies

- **Language:** Python 3.11+
- **Core API:** CCXT (Crypto Currency eXchange Trading Library)
- **Data Models:** In-Memory List Matrices, JSON Configurations, Structured CSV Logs

## How it works

The script decouples the ingestion layer from the strategy evaluation loops:

1. **Syncs Registry:** Downloads global exchange parameters to ensure valid symbol mappings.
2. **Sequential Download:** Paginate historical data blocks using strict `while bookmark < stop_ms:` safety parameters.
3. **Array Processing:** Iterates over the raw matrix sitting inside RAM to analyze consecutive close/open price variations.
4. **Persistent Storage:** Appends any isolated anomalies cleanly into a structured layout: `backtest_flash_log.csv`.

## Installation & Usage

### 1. Clone the Workspace

```bash
git clone [https://github.com/yourusername/live-btc-price.git](https://github.com/yourusername/live-btc-price.git)
cd live-btc-price
```

### 2. Install Dependencies

```bash
python -m pip install ccxt
```

### 3. Run the Backtester

```bash
python pump-dump-logger.py
```

## Sample Output

```bash
==================================================
Real-Time Binance In-Memory Backtest Engine
==================================================
BTC/USDT (1h) from 2026-05-01 to 2026-06-01

Stored 500 candles. Progress reached: 2026-05-21 19:00:00 UTC

Stored 777 candles. Progress reached: 2026-06-02 00:00:00 UTC

Processing historical data...
FLASH DROP: 2026-05-15 14:00:00 UTC | Move: -$1,613.77 | Session: New York AM
==================================================
RESULTS: Processed 777 candles.
Saved 1 flash movement to 'backtest_flash_log.csv'
==================================================
```

## Output File Format

```bash
Timestamp,Event Type,Price in USD,Price Change in USD,Market Session,Notes
2026-05-15 14:00:00,DUMP,78700.00,-1613.77,New York AM,
```
