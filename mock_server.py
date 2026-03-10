"""
mock_server.py
---------------

A simple mock Siemens S7 PLC implemented with python-snap7's Server.

It:
- Starts a local Snap7 server on TCP port 102.
- Registers DB1 with 4 bytes to hold a single REAL (float) value.
- Continuously updates the DB value with a simulated sensor signal (sine wave).
- Handles graceful shutdown on Ctrl+C.
"""

import math
import signal
import sys
import threading
import time
from typing import Optional

import snap7
from snap7.server import Server
from snap7.server import SrvArea
from snap7.type import WordLen
from snap7.util import set_real


# Configuration constants
DB_NUMBER = 1          # Data Block number
DB_SIZE = 4            # 4 bytes for a single REAL (float32)
DB_START_OFFSET = 0    # byte offset inside the DB
UPDATE_INTERVAL = 0.5  # seconds between updates
# NOTE: Port 102 is privileged on Linux (requires root). Use 1102 for local PoC.
TCP_PORT = 1102


class MockPLCServer:
    """
    Encapsulates a python-snap7 Server that exposes a single DB with a float value.
    """

    def __init__(self, tcp_port: int = TCP_PORT):
        self.tcp_port = tcp_port
        self.server: Optional[Server] = None
        self._running = threading.Event()
        # Use the same ctype that python-snap7's server examples use.
        self._data = (WordLen.Byte.ctype * DB_SIZE)()

    def _register_db(self) -> None:
        """
        Register DB1 with the server so clients can read it.
        """
        assert self.server is not None
        # NOTE: Server.register_area uses *SrvArea* (server-side area codes),
        # not the client-side Area/Areas enum.
        self.server.register_area(SrvArea.DB, DB_NUMBER, self._data)

    def start(self) -> None:
        """
        Create and start the Snap7 server.
        """
        self.server = Server()
        self._register_db()

        # Start the server listening on the specified TCP port.
        # The underlying C library uses port 102 by default, but we pass it explicitly.
        self.server.start(tcp_port=self.tcp_port)
        self._running.set()
        print(f"[SERVER] Mock PLC started on 127.0.0.1:{self.tcp_port}, DB{DB_NUMBER}, size={DB_SIZE} bytes")

    def stop(self) -> None:
        """
        Stop the server and clean up resources.
        """
        if self.server is not None:
            print("[SERVER] Stopping mock PLC server...")
            try:
                self.server.stop()
            except Exception as exc:  # best-effort shutdown
                print(f"[SERVER] Error while stopping server: {exc}")
            try:
                self.server.destroy()
            except Exception as exc:
                print(f"[SERVER] Error while destroying server: {exc}")
        self._running.clear()
        print("[SERVER] Mock PLC server stopped.")

    def update_loop(self) -> None:
        """
        Continuously update the DB value with a simulated sensor signal.
        Here we use a sine wave that varies over time.
        """
        t0 = time.time()
        print(f"[SERVER] Starting update loop with interval={UPDATE_INTERVAL}s.")

        while self._running.is_set():
            # Simulated sensor value: sine wave between 0 and 100.
            elapsed = time.time() - t0
            raw_value = math.sin(elapsed)  # range [-1, 1]
            value = 50.0 + 50.0 * raw_value  # range [0, 100]

            # Write the float into DB1 starting at byte 0.
            set_real(self._data, DB_START_OFFSET, float(value))

            print(f"[SERVER] Wrote value {value:.2f} to DB{DB_NUMBER}.DBD{DB_START_OFFSET}")
            time.sleep(UPDATE_INTERVAL)


def main() -> None:
    server = MockPLCServer(tcp_port=TCP_PORT)

    # Graceful shutdown handling (Ctrl+C).
    def handle_signal(signum, frame):
        print(f"\n[SERVER] Caught signal {signum}, shutting down...")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    server.start()

    # Run the update loop in the main thread; the Server runs in background threads.
    try:
        server.update_loop()
    except KeyboardInterrupt:
        # Fallback if signal handling didn't trigger
        handle_signal(signal.SIGINT, None)


if __name__ == "__main__":
    main()

