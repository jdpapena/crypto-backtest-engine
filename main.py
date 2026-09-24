from src.analytics import (
    create_price_chart,
    print_summary,
)
from src.data import fetch_ccxt_data
from src.engine import process_candles


def run_backtest():
    print("=" * 50)
    print("Binance Historical Market Event Engine")
    print("=" * 50)

    candles = fetch_ccxt_data(
        exchange_id="binanceus",
        symbol="BTC/USDT",
        timeframe="1h",
        start_date="2025-06-01",
        end_date="2026-06-01",
    )

    if not candles:
        print("No market data was retrieved.")
        return

    events = process_candles(
        candles,
        max_drop=-1500.0,
        max_pump=1500.0,
        output_file="data/backtest_flash_log.csv",
    )

    print("=" * 50)
    print(f"RESULTS: Processed {len(candles):,} candles.")
    print(f"Detected {len(events)} market events.")
    print("Saved results to 'data/backtest_flash_log.csv'")
    print("=" * 50)

    print_summary(
        candles,
        events,
    )

    create_price_chart(
        candles,
        events,
    )


if __name__ == "__main__":
    run_backtest()