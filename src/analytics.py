from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import pandas as pd


SESSION_ORDER = [
    "Asian",
    "London",
    "New York AM",
    "New York PM",
]


def calculate_summary(events):
    if not events:
        return {
            "total_events": 0,
            "pumps": 0,
            "dumps": 0,
            "average_move": 0.0,
            "median_move": 0.0,
            "largest_move": 0.0,
        }

    absolute_movements = [
        abs(event["price_change"])
        for event in events
    ]

    largest_event = max(
        events,
        key=lambda event: abs(event["price_change"]),
    )

    return {
        "total_events": len(events),
        "pumps": sum(
            event["type"] == "PUMP"
            for event in events
        ),
        "dumps": sum(
            event["type"] == "DUMP"
            for event in events
        ),
        "average_move": (
            sum(absolute_movements)
            / len(absolute_movements)
        ),
        "median_move": median(
            absolute_movements
        ),
        "largest_move": largest_event[
            "price_change"
        ],
    }


def calculate_session_counts(events):
    counts = Counter(
        event["session"]
        for event in events
    )

    return {
        session: counts.get(session, 0)
        for session in SESSION_ORDER
    }


def calculate_monthly_counts(events):
    counts = Counter(
        event["timestamp"].strftime("%Y-%m")
        for event in events
    )

    return dict(
        sorted(counts.items())
    )

def calculate_volatility_rankings(events):
    """
    Rank detected events by average absolute
    percentage movement across hour, session,
    month, and year.
    """

    if not events:
        return {
            "hour": pd.DataFrame(),
            "session": pd.DataFrame(),
            "month": pd.DataFrame(),
            "year": pd.DataFrame(),
        }

    df = pd.DataFrame(events)

    df["abs_percentage_change"] = (
        df["percentage_change"].abs()
    )

    df["hour"] = df["timestamp"].dt.hour

    df["month"] = (
        df["timestamp"]
        .dt.strftime("%Y-%m")
    )

    df["year"] = df["timestamp"].dt.year

    hourly = (
        df.groupby("hour")
        .agg(
            average_move=(
                "abs_percentage_change",
                "mean",
            ),
            events=(
                "abs_percentage_change",
                "size",
            ),
        )
        .reset_index()
        .sort_values(
            "average_move",
            ascending=False,
        )
    )

    session = (
        df.groupby("session")
        .agg(
            average_move=(
                "abs_percentage_change",
                "mean",
            ),
            events=(
                "abs_percentage_change",
                "size",
            ),
        )
        .reset_index()
        .sort_values(
            "average_move",
            ascending=False,
        )
    )

    monthly = (
        df.groupby("month")
        .agg(
            average_move=(
                "abs_percentage_change",
                "mean",
            ),
            events=(
                "abs_percentage_change",
                "size",
            ),
        )
        .reset_index()
        .sort_values(
            "average_move",
            ascending=False,
        )
    )

    yearly = (
        df.groupby("year")
        .agg(
            average_move=(
                "abs_percentage_change",
                "mean",
            ),
            events=(
                "abs_percentage_change",
                "size",
            ),
        )
        .reset_index()
        .sort_values(
            "average_move",
            ascending=False,
        )
    )

    return {
        "hour": hourly,
        "session": session,
        "month": monthly,
        "year": yearly,
    }

def print_summary(candles, events):
    summary = calculate_summary(events)
    session_counts = calculate_session_counts(
        events
    )

    print("\nANALYTICS")
    print("=" * 50)
    print(
        f"Candles processed: "
        f"{len(candles):,}"
    )
    print(
        f"Events detected:   "
        f"{summary['total_events']:,}"
    )
    print(
        f"Pumps:             "
        f"{summary['pumps']:,}"
    )
    print(
        f"Drops:             "
        f"{summary['dumps']:,}"
    )
    print(
        f"Average event:     "
        f"${summary['average_move']:,.2f}"
    )
    print(
        f"Median event:      "
        f"${summary['median_move']:,.2f}"
    )
    print(
        f"Largest event:     "
        f"${summary['largest_move']:+,.2f}"
    )

    print("\nEVENTS BY SESSION")
    print("-" * 50)

    for session, count in session_counts.items():
        percentage = (
            count
            / summary["total_events"]
            * 100
            if summary["total_events"]
            else 0
        )

        print(
            f"{session:<20}"
            f"{count:>4} "
            f"({percentage:>5.1f}%)"
        )

    print("=" * 50)


def ensure_output_directory(output_file):
    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_path


def create_price_chart(
    candles,
    events,
    output_file=(
        "reports/btc_market_events.png"
    ),
):
    if not candles:
        return

    output_path = ensure_output_directory(
        output_file
    )

    timestamps = [
        datetime.fromtimestamp(
            candle[0] / 1000,
            tz=timezone.utc,
        )
        for candle in candles
    ]

    open_prices = [
        float(candle[1])
        for candle in candles
    ]

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.plot(
        timestamps,
        open_prices,
        linewidth=1.2,
        label="BTC/USDT Open",
    )

    pumps = [
        event
        for event in events
        if event["type"] == "PUMP"
    ]

    drops = [
        event
        for event in events
        if event["type"] == "DUMP"
    ]

    if pumps:
        ax.scatter(
            [
                event["timestamp"]
                for event in pumps
            ],
            [
                event["price"]
                for event in pumps
            ],
            marker="^",
            s=45,
            label="Pump Event",
            zorder=3,
        )

    if drops:
        ax.scatter(
            [
                event["timestamp"]
                for event in drops
            ],
            [
                event["price"]
                for event in drops
            ],
            marker="v",
            s=45,
            label="Drop Event",
            zorder=3,
        )

    ax.set_title(
        "BTC/USDT Historical Market Events"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid(alpha=0.2)
    ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"Chart saved to '{output_path}'"
    )