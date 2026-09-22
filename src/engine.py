import csv
import os
from datetime import datetime, timezone


def get_market_session(hour):
    """Classify a UTC hour into a market-session label."""

    if 1 <= hour < 7:
        return "Asian"

    if 7 <= hour < 14:
        return "London"

    if 14 <= hour < 19:
        return "New York AM"

    if hour >= 19 or hour == 0:
        return "New York PM"

    return "No active session"


def log_backtest_change(
    file_name,
    timestamp,
    move_type,
    price,
    move_amount,
    session,
):
    """Append one detected market event to the CSV output."""

    file_exists = os.path.exists(file_name)

    with open(file_name, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "Timestamp",
                    "Event Type",
                    "Price in USD",
                    "Price Change in USD",
                    "Market Session",
                    "Notes",
                ]
            )

        writer.writerow(
            [
                timestamp,
                move_type,
                f"{price:.2f}",
                f"{move_amount:.2f}",
                session,
                "",
            ]
        )


def process_candles(
    candles,
    output_file="data/backtest_flash_log.csv",
    max_drop=-1500.0,
    max_pump=1500.0,
):
    """Process historical candles and record abrupt open-to-open moves."""

    if os.path.exists(output_file):
        os.remove(output_file)

    past_price = None
    abrupt_move = 0

    print("\nProcessing historical data...")

    for candle in candles:
        unix_ms = int(candle[0])

        # candle[1] is the candle OPEN price.
        current_price = float(candle[1])

        dt_object = datetime.fromtimestamp(
            unix_ms / 1000,
            tz=timezone.utc,
        )

        timestamp_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        session_tag = get_market_session(dt_object.hour)

        if past_price is not None:
            price_change = current_price - past_price

            if price_change <= max_drop:
                print(
                    f"FLASH DROP: {timestamp_str} UTC | "
                    f"Move: ${price_change:+,.2f} | "
                    f"Session: {session_tag}"
                )

                log_backtest_change(
                    output_file,
                    timestamp_str,
                    "DUMP",
                    current_price,
                    price_change,
                    session_tag,
                )

                abrupt_move += 1

            elif price_change >= max_pump:
                print(
                    f"FLASH PUMP: {timestamp_str} UTC | "
                    f"Move: ${price_change:+,.2f} | "
                    f"Session: {session_tag}"
                )

                log_backtest_change(
                    output_file,
                    timestamp_str,
                    "PUMP",
                    current_price,
                    price_change,
                    session_tag,
                )

                abrupt_move += 1

        past_price = current_price

    return abrupt_move