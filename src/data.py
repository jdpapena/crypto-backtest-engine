import time
from datetime import datetime, timezone

import ccxt


def fetch_ccxt_data(
    exchange_id="binanceus",
    symbol="BTC/USDT",
    timeframe="1m",
    start_date="2026-05-01",
    end_date="2026-05-05",
):
    """Fetch historical OHLCV candles from a CCXT-supported exchange."""

    exchange_class = getattr(ccxt, exchange_id)

    exchange = exchange_class(
        {
            "timeout": 30000,
            "enableRateLimit": True,
        }
    )

    start_ms = exchange.parse8601(f"{start_date}T00:00:00Z")
    stop_ms = exchange.parse8601(f"{end_date}T00:00:00Z")

    all_candles = []

    print(f"{symbol} ({timeframe}) from {start_date} to {end_date}")

    while start_ms < stop_ms:
        try:
            candles_batch = exchange.fetch_ohlcv(
                symbol,
                timeframe,
                since=start_ms,
            )

            if not candles_batch:
                break

            all_candles.extend(candles_batch)

            last_candle = candles_batch[-1][0]

            reached_dt = datetime.fromtimestamp(
                last_candle / 1000,
                tz=timezone.utc,
            )

            print(
                f"Stored {len(all_candles):,} candles. "
                f"Progress reached: "
                f"{reached_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )

            if last_candle >= stop_ms:
                break

            start_ms = last_candle + 1

            time.sleep(exchange.rateLimit / 1000)

        except Exception as error:
            print(f"CCXT Data Error: {error}")
            break

    return all_candles