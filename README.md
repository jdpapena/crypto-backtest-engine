# Abrupt Price Recording and Observation Network (APRON)

A Python backtesting application engineered to process abrupt movements of historical time-series prices using CCXT. The application features a pagination loop to follow rate limits, compiling market datasets into memory and also, to trigger an algorithm whenever there's volatility (abrupt pump or dump) on a certain symbol.

This was done to practice how to fetch market data from the CCXT API for the future version of backtesting. Also, categorizing abrupt movements per session gives us an idea of which session the price is more volatile.

---

## Features

- **Data Pagination:** Dynamically tracks past price to prevent data duplication and to comply with API request limits.
- **Volatilty Tracker Logic:** Evaluates candle-to-candle price change against volatility thresholds set (`MAX_PUMP` / `MAX_DROP`).
- **Categorical Session Tagging:** Parses standardized global UTC timestamps into tradable market sessions (Asian, London, New York AM/PM) to record volatility trends.

---

## Technologies

- **Language:** Python
- **Core API:** CCXT (Crypto Currency eXchange Trading Library)
- **Data Models:** In-Memory List Matrices, JSON Configurations, Structured CSV Logs

---

## How it works

The script handles the data in four steps:

1. **Connects to Exchange:** Downloads the market list to make sure the trading pair to be processed is valid and available.
2. **Sequential Download:** Pulls historical price data in chunks using a time-tracking loop so no data is duplicated or skipped.
3. **Array Processing:** Reads through the downloaded price history directly inside your memory to calculate abrupt price changes from one candle to another.
4. **Saves locally:** Automatically records any massive price pumps or dumps into a structured file: `backtest_flash_log.csv`.

---

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

---

## Directory

```
├── pump-dump-logger.py     # Main application and engine logic
└── README.md               # Project documentation
```
