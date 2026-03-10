"""
plc_client.py
--------------

Simple Snap7 client that connects to the local mock PLC server and
reads a simulated sensor value from DB1 in a loop.

This PoC is intentionally modular so the data extraction logic can later be
plugged into Pandas/Numpy/Streamlit/Dash for analytics and visualization.
"""

import datetime as dt
import sys
import time
from typing import Optional

import snap7
from snap7.client import Client
from snap7.type import Areas
from snap7.util import get_real


# Connection configuration (must match mock_server.py)
PLC_IP = "127.0.0.1"
RACK = 0
SLOT = 1
# NOTE: Port 102 is privileged on Linux (requires root). Use 1102 for local PoC.
TCP_PORT = 1102  # must match mock_server.py

# Data Block configuration (must match mock_server.py)
DB_NUMBER = 1          # DB1
DB_SIZE = 4            # 4 bytes for a single REAL
DB_START_OFFSET = 0    # start at byte 0

# Polling interval
POLL_INTERVAL = 0.5    # seconds


class PLCReader:
    """
    Encapsulates Snap7 client operations for reading a single REAL value
    from a Data Block. This can be extended to support multiple tags.
    """

    def __init__(
        self,
        ip: str = PLC_IP,
        rack: int = RACK,
        slot: int = SLOT,
        db_number: int = DB_NUMBER,
        start_offset: int = DB_START_OFFSET,
        size: int = DB_SIZE,
        tcp_port: int = TCP_PORT,
    ) -> None:
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.db_number = db_number
        self.start_offset = start_offset
        self.size = size
        self.tcp_port = tcp_port
        self.client: Optional[Client] = None

    def connect(self) -> None:
        """
        Establish a connection to the PLC (mock server).
        """
        if self.client is None:
            self.client = Client()

        print(f"[CLIENT] Connecting to {self.ip}:{self.tcp_port} (rack={self.rack}, slot={self.slot})...")
        self.client.connect(self.ip, self.rack, self.slot, self.tcp_port)
        if not self.client.get_connected():
            raise RuntimeError("[CLIENT] Failed to connect to PLC.")
        print("[CLIENT] Connected to PLC.")

    def disconnect(self) -> None:
        """
        Disconnect from the PLC.
        """
        if self.client is not None:
            print("[CLIENT] Disconnecting from PLC...")
            try:
                self.client.disconnect()
            except Exception as exc:
                print(f"[CLIENT] Error while disconnecting: {exc}")
            self.client = None
            print("[CLIENT] Disconnected.")

    def read_raw(self) -> bytes:
        """
        Read raw bytes from the configured DB and offset.
        """
        if self.client is None or not self.client.get_connected():
            raise RuntimeError("[CLIENT] Not connected to PLC.")

        data = self.client.read_area(
            Areas.DB,
            self.db_number,
            self.start_offset,
            self.size,
        )
        return bytes(data)

    def read_value(self) -> float:
        """
        Read and decode the REAL value from DB.

        Returns:
            Float value read from DB.
        """
        if self.client is None or not self.client.get_connected():
            raise RuntimeError("[CLIENT] Not connected to PLC.")

        data = self.client.read_area(
            Areas.DB,
            self.db_number,
            self.start_offset,
            self.size,
        )
        value = get_real(data, 0)
        return float(value)

    def is_connected(self) -> bool:
        """
        Helper to check whether the underlying Snap7 client is connected.
        """
        if self.client is None:
            return False
        try:
            return bool(self.client.get_connected())
        except Exception:
            return False


def run_polling_loop(poll_interval: float = POLL_INTERVAL) -> None:
    """
    Continuously read the value from the mock PLC and print it with a timestamp.
    """
    reader = PLCReader()

    try:
        reader.connect()
    except Exception as exc:
        print(f"[CLIENT] Failed to connect to PLC: {exc}")
        sys.exit(1)

    print(f"[CLIENT] Starting polling loop, interval={poll_interval}s. Press Ctrl+C to stop.")

    try:
        while True:
            try:
                value = reader.read_value()
                ts = dt.datetime.now().isoformat(timespec="milliseconds")
                print(f"[{ts}] DB{DB_NUMBER}.DBD{DB_START_OFFSET} = {value:.2f}")
            except Exception as exc:
                print(f"[CLIENT] Error during read: {exc}")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\n[CLIENT] Caught Ctrl+C, stopping...")
    finally:
        reader.disconnect()


def main() -> None:
    run_polling_loop()


if __name__ == "__main__":
    main()

