from datetime import date

import pandas as pd
import streamlit as st

from src.analytics import (
    calculate_monthly_counts,
    calculate_session_counts,
    calculate_summary,
    calculate_volatility_rankings,
)

from src.data import fetch_ccxt_data
from src.engine import process_candles


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Crypto Market Event Analytics",
    layout="wide",
)


# ---------------------------------------------------------
# LIGHT VISUAL CLEANUP
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1250px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }

        h1 {
            font-size: 2rem !important;
            font-weight: 650 !important;
            letter-spacing: -0.02em;
        }

        h2, h3 {
            letter-spacing: -0.01em;
        }

        [data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 6px;
            padding: 0.9rem 1rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.82rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.55rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        hr {
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------

@st.cache_data(
    show_spinner=False,
    ttl=3600,
)
def load_market_data(
    symbol,
    timeframe,
    start_date,
    end_date,
):
    """Download and cache historical OHLCV data."""

    return fetch_ccxt_data(
        exchange_id="binanceus",
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
    )


def events_to_dataframe(events):
    """Convert detected events into a DataFrame."""

    if not events:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "type",
                "price",
                "price_change",
                "percentage_change",
                "session",
            ]
        )

    return pd.DataFrame(events)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("Controls")

symbol = st.sidebar.selectbox(
    "Market",
    [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ],
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1h"],
)

st.sidebar.subheader("Period")

start_date = st.sidebar.date_input(
    "Start",
    value=date(2025, 6, 1),
)

end_date = st.sidebar.date_input(
    "End",
    value=date(2026, 6, 1),
)

st.sidebar.divider()

st.sidebar.subheader("Event Definition")

threshold_mode = st.sidebar.radio(
    "Threshold type",
    [
        "Percentage",
        "USD",
    ],
    horizontal=True,
)

if threshold_mode == "Percentage":
    pump_threshold = st.sidebar.slider(
        "Pump threshold",
        min_value=0.25,
        max_value=5.0,
        value=1.5,
        step=0.25,
        format="%.2f%%",
    )

    drop_threshold = st.sidebar.slider(
        "Drop threshold",
        min_value=0.25,
        max_value=5.0,
        value=1.5,
        step=0.25,
        format="%.2f%%",
    )

    threshold_description = (
        f"+{pump_threshold:.2f}% / "
        f"-{drop_threshold:.2f}%"
    )

else:
    pump_threshold = st.sidebar.slider(
        "Pump threshold",
        min_value=100,
        max_value=5000,
        value=1500,
        step=100,
        format="$%d",
    )

    drop_threshold = st.sidebar.slider(
        "Drop threshold",
        min_value=100,
        max_value=5000,
        value=1500,
        step=100,
        format="$%d",
    )

    threshold_description = (
        f"+${pump_threshold:,} / "
        f"-${drop_threshold:,}"
    )


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if start_date >= end_date:
    st.error(
        "Start date must be earlier than end date."
    )
    st.stop()


# ---------------------------------------------------------
# LOAD MARKET DATA
# ---------------------------------------------------------

with st.spinner(
    f"Loading {symbol} market data..."
):
    candles = load_market_data(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )


if not candles:
    st.warning(
        "No market data was returned for this period."
    )
    st.stop()


# ---------------------------------------------------------
# PROCESS EVENTS
# ---------------------------------------------------------

events = process_candles(
    candles,
    max_drop=-float(drop_threshold),
    max_pump=float(pump_threshold),
    threshold_mode=threshold_mode,
    verbose=False,
)

summary = calculate_summary(events)

session_counts = calculate_session_counts(
    events
)

monthly_counts = calculate_monthly_counts(
    events
)

volatility_rankings = (
    calculate_volatility_rankings(events)
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("Crypto Market Event Analytics")

st.write(
    "Historical cryptocurrency event detection using "
    "configurable open-to-open movement thresholds."
)

st.caption(
    f"{symbol}  •  {timeframe.upper()}  •  "
    f"{start_date} → {end_date}  •  "
    f"{threshold_mode}: {threshold_description}"
)

st.divider()


# ---------------------------------------------------------
# PRIMARY METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Candles Processed",
    f"{len(candles):,}",
)

col2.metric(
    "Events Detected",
    f"{summary['total_events']:,}",
)

col3.metric(
    "Pumps",
    f"{summary['pumps']:,}",
)

col4.metric(
    "Drops",
    f"{summary['dumps']:,}",
)


col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Movement",
    f"${summary['average_move']:,.2f}",
)

col2.metric(
    "Median Movement",
    f"${summary['median_move']:,.2f}",
)

col3.metric(
    "Largest Movement",
    f"${abs(summary['largest_move']):,.2f}",
)


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

st.divider()

st.subheader("Event Distribution")

left_column, right_column = st.columns(2)


with left_column:
    st.markdown("#### By Month")

    if monthly_counts:
        monthly_df = pd.DataFrame(
            {
                "Month": list(
                    monthly_counts.keys()
                ),
                "Events": list(
                    monthly_counts.values()
                ),
            }
        )

        st.bar_chart(
            monthly_df,
            x="Month",
            y="Events",
            width="stretch",
        )

    else:
        st.info(
            "No events detected."
        )


with right_column:
    st.markdown("#### By Market Session")

    if session_counts:
        session_df = pd.DataFrame(
            {
                "Session": list(
                    session_counts.keys()
                ),
                "Events": list(
                    session_counts.values()
                ),
            }
        )

        st.bar_chart(
            session_df,
            x="Session",
            y="Events",
            width="stretch",
        )

    else:
        st.info(
            "No events detected."
        )

# ---------------------------------------------------------
# VOLATILITY RANKINGS
# ---------------------------------------------------------

st.divider()

st.subheader("Volatility Rankings")

st.caption(
    "Periods ranked by average absolute percentage "
    "movement among detected events."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "By Hour",
        "By Session",
        "By Month",
        "By Year",
    ]
)

def prepare_ranking_table(
    dataframe,
    period_column,
    period_name,
):
    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    result["average_move"] = (
        result["average_move"]
        .map(
            lambda value:
            f"{value:.2f}%"
        )
    )

    result = result.rename(
        columns={
            period_column: period_name,
            "average_move":
                "Avg. Movement",
            "events":
                "Events",
        }
    )

    return result

with tab1:
    hourly_table = prepare_ranking_table(
        volatility_rankings["hour"],
        "hour",
        "Hour (UTC)",
    )

    if not hourly_table.empty:
        hourly_table["Hour (UTC)"] = (
            hourly_table["Hour (UTC)"]
            .map(
                lambda hour:
                f"{int(hour):02d}:00"
            )
        )

        st.dataframe(
            hourly_table,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info("No events detected.")


with tab2:
    session_table = prepare_ranking_table(
        volatility_rankings["session"],
        "session",
        "Session",
    )

    if not session_table.empty:
        st.dataframe(
            session_table,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info("No events detected.")


with tab3:
    monthly_table = prepare_ranking_table(
        volatility_rankings["month"],
        "month",
        "Month",
    )

    if not monthly_table.empty:
        st.dataframe(
            monthly_table,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info("No events detected.")


with tab4:
    yearly_table = prepare_ranking_table(
        volatility_rankings["year"],
        "year",
        "Year",
    )

    if not yearly_table.empty:
        st.dataframe(
            yearly_table,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info("No events detected.")

# ---------------------------------------------------------
# EVENT TABLE
# ---------------------------------------------------------

st.divider()

st.subheader("Detected Events")

st.caption(
    "Individual movements matching the selected "
    "event definition."
)

events_df = events_to_dataframe(events)


if events_df.empty:
    st.info(
        "No events matched the selected thresholds."
    )

else:
    display_df = events_df.copy()

    display_df["timestamp"] = (
        display_df["timestamp"]
        .dt.strftime(
            "%Y-%m-%d %H:%M"
        )
    )

    display_df["price"] = (
        display_df["price"]
        .map(
            lambda value:
            f"${value:,.2f}"
        )
    )

    display_df["price_change"] = (
        display_df["price_change"]
        .map(
            lambda value:
            f"${value:+,.2f}"
        )
    )

    display_df["percentage_change"] = (
        display_df["percentage_change"]
        .map(
            lambda value:
            f"{value:+.2f}%"
        )
    )

    display_df = display_df.rename(
        columns={
            "timestamp": "Timestamp (UTC)",
            "type": "Event",
            "price": "Price",
            "price_change": "USD Change",
            "percentage_change": "% Change",
            "session": "Session",
        }
    )

    display_df = display_df[
        [
            "Timestamp (UTC)",
            "Event",
            "Price",
            "USD Change",
            "% Change",
            "Session",
        ]
    ]

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=390,
    )


# ---------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------

st.divider()

with st.expander(
    "Methodology"
):
    st.markdown(
        """
The engine processes historical OHLCV candles
sequentially and compares each candle's **open price**
with the previous candle's open price.

**USD mode** detects events when the absolute dollar
movement exceeds the selected threshold.

**Percentage mode** detects events when the relative
percentage movement exceeds the selected threshold.

Events are classified into four UTC market-session
windows:

- **Asian:** 01:00–06:59 UTC
- **London:** 07:00–13:59 UTC
- **New York AM:** 14:00–18:59 UTC
- **New York PM:** 19:00–00:59 UTC

This project is intended for historical market-data
analysis and software demonstration.
        """
    )


st.caption(
    "Data retrieved through CCXT using Binance US "
    "historical OHLCV market data."
)