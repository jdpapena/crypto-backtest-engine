import time
import ccxt
import os
from datetime import datetime, timezone

# NOTE: Do not use "binance" always use "binanceus"
def fetch_ccxt_data(exchange_id="binanceus", symbol="BTC/USDT", timeframe="1m", start_date="2026-05-01", end_date="2026-05-05"): # Default values
    # 1. Initialize what exchange to be used
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'timeout': 30000,
        'enableRateLimit': True
    })
    
    # 2. Convert date to ms for CCXT
    start_ms = exchange.parse8601(f"{start_date}T00:00:00Z")
    stop_ms = exchange.parse8601(f"{end_date}T00:00:00Z")
    
    all_candles = []
    
    print(f"{symbol} ({timeframe}) from {start_date} to {end_date}")
    
    # 3. Fetching candles and storing it
    while start_ms < stop_ms:
        try:
            # fetch_ohlcv - [Timestamp, Open, High, Low, Close, Volume]
            candles_batch = exchange.fetch_ohlcv(symbol, timeframe, since=start_ms)
            
            if not candles_batch:
                break # Exchange has no more data to process
                
            all_candles.extend(candles_batch)
            last_candle = candles_batch[-1][0]
            
            # Show update of candles processed
            reached_dt = datetime.fromtimestamp(last_candle / 1000, tz=timezone.utc)
            print(f"Stored {len(all_candles):,} candles. Progress reached: {reached_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Candle reach end date, then stop
            if last_candle >= stop_ms:
                break
                
            # Move 1 step forward for sequence
            start_ms = last_candle + 1
            time.sleep(exchange.rateLimit / 1000)
            
        except Exception as e:
            print(f"CCXT Data Error: {e}")
            break
            
    return all_candles

def get_market_session(hour):
    # Different sessions for tracking to note when it abruptly moves the most.
    if 1 <= hour < 7:
        return "Asian"
    elif 7 <= hour < 14:
        return "London"
    elif 14 <= hour < 19:
        return "New York AM"
    elif hour >= 19 or hour == 0:
        return "New York PM"
    return "No active session."

def log_backtest_change(timestamp, move_type, price, move_amount, session):
    # CHANGE: File name that will be shown on your local drive
    file_name = "backtest_flash_log.csv"
    
    with open(file_name, "a") as file:
        if not os.path.exists(file_name):
            # Column header
            file.write("Timestamp,Event Type,Price in USD,Price Change in USD,Market Session,Notes\n")
        
        # Adding the data into the rows
        file.write(f"{timestamp},{move_type},{price:.2f},{move_amount:+.2f},{session},\n")

def run_backtest():
    print("==================================================")
    print("Real-Time Binance In-Memory Backtest Engine")
    print("==================================================")
    
    # Limits
    MAX_DROP = -1500.0
    MAX_PUMP = 1500.0
    
    # 1. Fetch data from market
    # CHANGE HERE: 
    candles = fetch_ccxt_data(
        exchange_id="binanceus", 
        symbol="BTC/USDT", 
        timeframe="1h", 
        start_date="2026-05-01",
        end_date="2026-06-01"
    )
    
    if not candles:
        print("Missing source of data from Binance.")
        return

    print("\nProcessing historical data...")
    
    past_price = None
    abrupt_move = 0
    
    # For existing data, delete it for new data to come in
    if os.path.exists("backtest_flash_log.csv"):
        os.remove("backtest_flash_log.csv")

    # 2. Loop through memory (candles)
    for candle in candles:
        # candle[0] is time & candle[1] is price
        unix_ms = int(candle[0])
        current_price = float(candle[1])
        
        # Parse the timestamp elements from the dataset item
        dt_object = datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc)
        timestamp_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        session_tag = get_market_session(dt_object.hour)
        
        if past_price is not None:
            price_change = current_price - past_price
            
            # CHANGE: Conditions to be considered volatility.
            if price_change <= MAX_DROP:
                print(f"FLASH DROP: {timestamp_str} UTC | Move: ${price_change:+,.2f} | Session: {session_tag}")
                log_backtest_change(timestamp_str, "DUMP", current_price, price_change, session_tag)
                abrupt_move += 1
                
            elif price_change >= MAX_PUMP:
                print(f"FLASH PUMP: {timestamp_str} UTC | Move: ${price_change:+,.2f} | Session: {session_tag}")
                log_backtest_change(timestamp_str, "PUMP", current_price, price_change, session_tag)
                abrupt_move += 1
                
        past_price = current_price

    print("==================================================")
    print(f"RESULTS: Processed {len(candles)} candles.")
    print(f"Saved {abrupt_move} flash movement to 'backtest_flash_log.csv'")
    print("==================================================")

if __name__ == "__main__":
    run_backtest()