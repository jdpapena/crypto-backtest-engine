import csv
from datetime import datetime, timezone
from pathlib import Path


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


def export_events(events, output_file):
    """Export detected market events to CSV."""

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "Timestamp",
                "Event Type",
                "Price in USD",
                "Price Change in USD",
                "Percentage Change",
                "Market Session",
                "Notes",
            ]
        )

        for event in events:
            writer.writerow(
                [
                    event["timestamp"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    event["type"],
                    f"{event['price']:.2f}",
                    f"{event['price_change']:.2f}",
                    f"{event['percentage_change']:.4f}",
                    event["session"],
                    "",
                ]
            )


def process_candles(
    candles,
    max_drop=-1500.0,
    max_pump=1500.0,
    threshold_mode="USD",
    output_file=None,
    verbose=True,
):
    """Detect abrupt open-to-open market movements."""

    events = []
    past_price = None

    if verbose:
        print("\nProcessing historical data...")

    for candle in candles:
        unix_ms = int(candle[0])
        current_price = float(candle[1])

        dt_object = datetime.fromtimestamp(
            unix_ms / 1000,
            tz=timezone.utc,
        )

        session_tag = get_market_session(
            dt_object.hour
        )

        if past_price is not None:
            price_change = (
                current_price - past_price
            )

            percentage_change = (
                price_change / past_price
            ) * 100

            move_type = None

            if threshold_mode == "Percentage":
                if percentage_change <= max_drop:
                    move_type = "DUMP"

                elif percentage_change >= max_pump:
                    move_type = "PUMP"

            else:
                if price_change <= max_drop:
                    move_type = "DUMP"

                elif price_change >= max_pump:
                    move_type = "PUMP"

            if move_type:
                event = {
                    "timestamp": dt_object,
                    "type": move_type,
                    "price": current_price,
                    "price_change": price_change,
                    "percentage_change": percentage_change,
                    "session": session_tag,
                }

                events.append(event)

                if verbose:
                    display_type = (
                        "DROP"
                        if move_type == "DUMP"
                        else "PUMP"
                    )

                    print(
                        f"FLASH {display_type}: "
                        f"{dt_object.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
                        f"Move: ${price_change:+,.2f} "
                        f"({percentage_change:+.2f}%) | "
                        f"Session: {session_tag}"
                    )

        past_price = current_price

    if output_file:
        export_events(
            events,
            output_file,
        )

    return events