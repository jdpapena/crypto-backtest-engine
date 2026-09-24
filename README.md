# Crypto Backtest Engine

A Python historical market engine built to process abrupt movements in cryptocurrency time-series data using CCXT. The application retrieves historical OHLCV candles through a pagination loop, compiles the market dataset in memory, and detects volatility events whenever a configurable pump or dump threshold is reached.

This project was originally built to practice retrieving historical market data from the CCXT API for future backtesting applications. It was later expanded with an interactive analytics dashboard to explore detected volatility events across different cryptocurrency pairs, time periods, and market sessions.

## Features

- **Historical Data Pagination:** Retrieves OHLCV candles in sequential batches while respecting rate limits and advancing request timestamps to prevent duplicate entries.
- **Volatility Tracker Logic:** Evaluates candle-to-candle open price changes against configurable pump and drop thresholds.
- **USD & Percentage Thresholds:** Detects events using either absolute USD movements or percentage price changes.
- **Multiple Trading Pairs:** Supports BTC/USDT, ETH/USDT, and SOL/USDT historical analysis.
- **Market Session Tagging:** Parses UTC timestamps into Asian, London, New York AM, and New York PM sessions.
- **Market Analytics:** Summarizes detected events by month and market session and ranks event magnitude by hour, session, month, and year.
- **Interactive Dashboard:** Uses Streamlit to adjust the market, date range, and volatility thresholds and inspect the resulting events.
- **Modular Pipeline:** Separates market-data retrieval, event processing, analytics, and dashboard presentation into independent Python modules.

## Technologies

- **Language:** Python 3
- **Core API:** CCXT (CryptoCurrency eXchange Trading Library), Binance US
- **Analytics:** Pandas, Matplotlib
- **Dashboard:** Streamlit
- **Data Models:** In-memory OHLCV data, structured CSV logs
- **Architecture:** Modular data retrieval, event-processing, and analytics pipeline

## How It Works

The application separates market-data ingestion from event detection and analytics:

1. **Exchange Initialization:** Connects to Binance US through CCXT and loads the required exchange configuration.
2. **Sequential Download:** Retrieves historical OHLCV candles in batches between the selected start and end dates.
3. **In-Memory Processing:** Iterates through the retrieved candle dataset and calculates consecutive open-to-open price movements.
4. **Event Detection:** Identifies movements that exceed the configured upward or downward USD or percentage thresholds.
5. **Session Classification:** Assigns each detected event to its corresponding market session based on UTC time.
6. **Analytics:** Groups detected events by time period and session to analyze event frequency and average percentage movement.
7. **Interactive Exploration:** Displays the results through a Streamlit dashboard with configurable market and threshold controls.
8. **Persistent Storage:** Supports exporting detected events into structured CSV format for further analysis.

## Installation & Usage

### 1. Clone the Workspace

```bash
git clone https://github.com/jdpapena/crypto-backtest-engine.git
cd crypto-backtest-engine
```

### 2. Install Dependencies

```bash
python -m pip install ccxt pandas matplotlib streamlit
```

### 3. Run the Dashboard

```bash
python -m streamlit run dashboard.py
```

The dashboard allows the market, historical period, threshold type, and pump/drop thresholds to be adjusted interactively.

### 4. Run the Backtester

The original command-line workflow is still available:

```bash
python main.py
```

## Sample Output

Using BTC/USDT 1-hour candles from June 1, 2025 to June 1, 2026 with a ±$1,500 open-to-open threshold:

```text
==================================================
Binance Historical Market Event Engine
==================================================
BTC/USDT (1h) from 2025-06-01 to 2026-06-01

Processing historical data...
==================================================
RESULTS: Processed 8,760 candles.
Detected 82 market events.
Saved results to 'data/backtest_flash_log.csv'
==================================================

ANALYTICS
==================================================
Candles processed: 8,760
Events detected:   82
Pumps:             33
Drops:             49
Average event:     $1,960.64
Median event:      $1,855.97
Largest event:     $3,670.84

EVENTS BY SESSION
--------------------------------------------------
Asian                 15 (18.3%)
London                 8 ( 9.8%)
New York AM           41 (50.0%)
New York PM           18 (22.0%)
==================================================
```

These results represent this specific historical period and event definition and are not intended to describe cryptocurrency volatility in general.

## Dashboard Analytics

The interactive dashboard provides:

- Total candles processed
- Total pump and drop events
- Average, median, and largest detected movement
- Events by month
- Events by market session
- Volatility rankings by hour
- Volatility rankings by market session
- Volatility rankings by month
- Volatility rankings by year
- Detailed detected-event table

Volatility rankings use the **average absolute percentage movement of detected events** within each period.

## Output File Format

```text
Timestamp,Event Type,Price in USD,Price Change in USD,Percentage Change,Market Session,Notes
2026-05-15 14:00:00,DUMP,103754.59,-1613.77,-1.53,New York AM,
```

## Project Structure

```text
crypto-backtest-engine/
├── main.py
├── dashboard.py
├── README.md
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── engine.py
│   └── analytics.py
├── data/
│   └── .gitkeep
└── reports/
    └── .gitkeep
```

## Disclaimer

This project is intended for educational, historical market analysis, and software-development purposes only. It does not provide trading signals or financial advice.
