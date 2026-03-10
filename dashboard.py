"""
dashboard.py
-------------

Streamlit-based real-time dashboard for visualizing PLC data read via python-snap7.

Features:
- Reuses the PLCReader class from plc_client.py to connect to the mock PLC.
- Continuously polls DB1.DBD0 on 127.0.0.1:1102.
- Stores the last N readings in st.session_state as a Pandas DataFrame.
- Computes live statistics (current, moving average, min, max).
- Displays metrics using st.metric and a live-updating Plotly line chart.
"""

import datetime as dt
import time
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from plc_client import PLCReader


# Maximum number of historical points to keep in memory.
MAX_POINTS = 200

# Moving average window size (number of samples).
MA_WINDOW = 10

# Poll interval in seconds (how often to query the PLC).
POLL_INTERVAL = 0.5


def get_or_create_plc_reader(ip: str, rack: int, slot: int, tcp_port: int) -> PLCReader:
    """
    Create (or reuse) a PLCReader instance for the given connection parameters.

    If the configuration changes (e.g. switching between mock and real PLC),
    a new reader is created and the old one is disconnected.
    """
    new_cfg = {
        "ip": ip,
        "rack": int(rack),
        "slot": int(slot),
        "tcp_port": int(tcp_port),
    }

    existing_cfg = st.session_state.get("plc_config")
    existing_reader: Optional[PLCReader] = st.session_state.get("plc_reader")

    if existing_reader is not None and existing_cfg == new_cfg:
        # Ensure the existing reader is actually connected; reconnect if needed.
        if not existing_reader.is_connected():
            existing_reader.connect()
        return existing_reader

    # Config changed or no reader yet: disconnect previous reader if present.
    if existing_reader is not None:
        try:
            existing_reader.disconnect()
        except Exception:
            pass

    reader = PLCReader(
        ip=new_cfg["ip"],
        rack=new_cfg["rack"],
        slot=new_cfg["slot"],
        tcp_port=new_cfg["tcp_port"],
    )
    reader.connect()

    st.session_state["plc_reader"] = reader
    st.session_state["plc_config"] = new_cfg
    return reader


def init_session_state() -> None:
    """
    Initialize session_state structures for storing time series data.
    """
    if "data" not in st.session_state:
        st.session_state["data"] = pd.DataFrame(columns=["timestamp", "value"])


def append_reading(timestamp: dt.datetime, value: float) -> None:
    """
    Append a new reading to the session_state DataFrame and trim to MAX_POINTS.
    """
    df: pd.DataFrame = st.session_state["data"]
    new_row = pd.DataFrame(
        {
            "timestamp": [timestamp],
            "value": [value],
        }
    )
    # Avoid concat-on-empty warning by handling the initial case explicitly.
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row], ignore_index=True)

    # Keep only the last MAX_POINTS rows to control memory usage.
    if len(df) > MAX_POINTS:
        df = df.iloc[-MAX_POINTS:].reset_index(drop=True)

    st.session_state["data"] = df


def compute_stats(df: pd.DataFrame) -> dict:
    """
    Compute basic statistics from the current DataFrame.
    Returns a dict with keys: current, ma, min, max.
    """
    if df.empty:
        return {"current": None, "ma": None, "min": None, "max": None}

    current = float(df["value"].iloc[-1])
    ma = float(df["value"].tail(MA_WINDOW).mean())
    vmin = float(df["value"].min())
    vmax = float(df["value"].max())
    return {"current": current, "ma": ma, "min": vmin, "max": vmax}


def main() -> None:
    st.set_page_config(
        page_title="PLC Real-Time Dashboard",
        layout="wide",
    )

    st.title("PLC Real-Time Dashboard")

    # Sidebar: choose between mock PLC and real PLC.
    with st.sidebar:
        st.header("Connection")
        mode = st.radio(
            "PLC source",
            ["Mock (local)", "Real PLC"],
            index=0,
        )
        if mode == "Mock (local)":
            ip = "127.0.0.1"
            rack = 0
            slot = 1
            tcp_port = 1102
            st.caption("Using local mock PLC started by mock_server.py on port 1102.")
        else:
            ip = st.text_input("PLC IP address", value=st.session_state.get("real_plc_ip", "192.168.0.1"))
            rack = int(
                st.number_input(
                    "Rack",
                    min_value=0,
                    max_value=7,
                    value=int(st.session_state.get("real_plc_rack", 0)),
                    step=1,
                )
            )
            slot = int(
                st.number_input(
                    "Slot",
                    min_value=0,
                    max_value=15,
                    value=int(st.session_state.get("real_plc_slot", 1)),
                    step=1,
                )
            )
            tcp_port = int(
                st.number_input(
                    "TCP port",
                    min_value=1,
                    max_value=65535,
                    value=int(st.session_state.get("real_plc_port", 102)),
                    step=1,
                )
            )
            # Persist the last used real PLC settings.
            st.session_state["real_plc_ip"] = ip
            st.session_state["real_plc_rack"] = rack
            st.session_state["real_plc_slot"] = slot
            st.session_state["real_plc_port"] = tcp_port

    if mode == "Mock (local)":
        st.caption("Source: Mock PLC @ 127.0.0.1:1102 — DB1.DBD0 (REAL)")
    else:
        st.caption(f"Source: Real PLC @ {ip}:{tcp_port} (rack={rack}, slot={slot}) — DB1.DBD0 (REAL)")

    init_session_state()

    # Connect (or reuse) PLCReader based on selected mode/config.
    try:
        reader = get_or_create_plc_reader(ip, rack, slot, tcp_port)
    except Exception as exc:
        st.error(f"Failed to connect to PLC: {exc}")
        st.stop()

    # Poll one new value from the PLC on each run.
    try:
        value = reader.read_value()
        ts = dt.datetime.now()
        append_reading(ts, value)
    except Exception as exc:
        st.error(f"Error reading from PLC: {exc}")

    df: pd.DataFrame = st.session_state["data"]
    stats = compute_stats(df)

    # Layout: top row with metrics, bottom with chart and table.
    col1, col2, col3, col4 = st.columns(4)

    if stats["current"] is not None:
        col1.metric("Current Value", f"{stats['current']:.2f}")
        col2.metric("Moving Avg (last 10)", f"{stats['ma']:.2f}")
        col3.metric("Minimum", f"{stats['min']:.2f}")
        col4.metric("Maximum", f"{stats['max']:.2f}")
    else:
        col1.metric("Current Value", "—")
        col2.metric("Moving Avg (last 10)", "—")
        col3.metric("Minimum", "—")
        col4.metric("Maximum", "—")

    st.markdown("---")

    # Time series chart (Plotly).
    if not df.empty:
        fig = px.line(df, x="timestamp", y="value", title="PLC Value Over Time")
        fig.update_layout(xaxis_title="Time", yaxis_title="Value")
        # `use_container_width` is deprecated; use width="stretch".
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Waiting for data from PLC...")

    # Optional: show raw data table for debugging/inspection.
    with st.expander("Raw Data (last points)"):
        st.dataframe(df.tail(50), width="stretch")

    # Simple auto-refresh loop: wait, then rerun the script.
    time.sleep(POLL_INTERVAL)
    st.rerun()


if __name__ == "__main__":
    main()

