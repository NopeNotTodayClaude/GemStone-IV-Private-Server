from typing import Optional
"""
sync_client.py
--------------
Background sync client for the GemStone IV HUD.

Maintains a persistent TCP connection to the server's real-time sync port
(default 4902).  Runs entirely in a daemon thread — never blocks the Tkinter
main thread.  All state updates arrive via a queue consumed by _poll().

Usage (from HUDApp):
    self._sync = SyncClient(host, port=4902, rx_q=self.sync_q)
    self._sync.connect(token)   # called when SYNC control line arrives
    self._sync.stop()           # called on HUD disconnect

The queue delivers (event_type, payload) tuples:
    ("sync_state",  dict)   -- full state snapshot
    ("sync_event",  dict)   -- one-shot server event (future use)
    ("sync_error",  str)    -- connection/parse error
    ("sync_closed", None)   -- connection dropped
"""

import socket
import threading
import json
import queue
import time
import logging

log = logging.getLogger(__name__)

CONNECT_TIMEOUT   = 8.0     # seconds to establish TCP
AUTH_TIMEOUT      = 6.0     # seconds to receive auth OK
RECV_TIMEOUT      = 45.0    # idle timeout — server pushes every ~1s
RECONNECT_DELAY   = 5.0     # seconds between reconnect attempts
MAX_LINE_BYTES    = 65536   # ignore runaway lines


class SyncClient:
    """
    Daemon thread that stays connected to the sync port and feeds
    (type, payload) tuples into rx_q for the HUD _poll() loop.
    """

    def __init__(self, host: str, port: int, rx_q: queue.Queue):
        self.host  = host
        self.port  = port
        self.rx_q  = rx_q

        self._token:   Optional[str]       = None
        self._sock:    socket.socket | None = None
        self._thread:  threading.Thread | None = None
        self._running: bool = False
        self._lock = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────────

    def connect(self, token: str):
        """
        Start (or restart) the sync connection with the given auth token.
        Safe to call multiple times — stops the old thread first.
        """
        self.stop()
        with self._lock:
            self._token   = token
            self._running = True
        self._thread = threading.Thread(
            target=self._run,
            name="SyncClient",
            daemon=True
        )
        self._thread.start()
        log.debug("SyncClient: started for %s:%d", self.host, self.port)

    def stop(self):
        """Shut down the sync connection cleanly."""
        with self._lock:
            self._running = False
        self._close_socket()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def send_event(self, payload: dict) -> bool:
        """Send one post-auth sync event to the server."""
        with self._lock:
            sock = self._sock
            running = self._running
        if not running or not sock:
            return False
        try:
            line = json.dumps(payload, separators=(",", ":")) + "\n"
            sock.sendall(line.encode("utf-8"))
            return True
        except OSError:
            return False

    # ── Internal ─────────────────────────────────────────────────────────────

    def _run(self):
        """Main loop: connect → auth → recv → reconnect on drop."""
        while self.is_running():
            try:
                if self._connect_and_auth():
                    self._recv_loop()
            except Exception as e:
                log.debug("SyncClient: unexpected error: %s", e)

            if not self.is_running():
                break

            self.rx_q.put(("sync_closed", None))
            log.debug("SyncClient: reconnecting in %.0fs...", RECONNECT_DELAY)
            time.sleep(RECONNECT_DELAY)

    def _connect_and_auth(self) -> bool:
        """
        Open the TCP connection and complete the auth handshake.
        Returns True if auth succeeded, False otherwise.
        """
        with self._lock:
            token = self._token
        if not token:
            return False

        try:
            sock = socket.create_connection((self.host, self.port),
                                            timeout=CONNECT_TIMEOUT)
        except (OSError, ConnectionRefusedError) as e:
            log.debug("SyncClient: connect failed: %s", e)
            self.rx_q.put(("sync_error", f"Cannot reach sync server: {e}"))
            return False

        sock.settimeout(AUTH_TIMEOUT)
        self._sock = sock

        # Send auth
        auth_line = json.dumps({"auth": token}, separators=(",", ":")) + "\n"
        try:
            sock.sendall(auth_line.encode("utf-8"))
        except OSError as e:
            log.debug("SyncClient: auth send failed: %s", e)
            self._close_socket()
            return False

        # Read auth response
        try:
            raw = self._readline()
        except (OSError, TimeoutError) as e:
            log.debug("SyncClient: auth response timeout: %s", e)
            self._close_socket()
            return False

        if not raw:
            self._close_socket()
            return False

        try:
            resp = json.loads(raw)
        except json.JSONDecodeError:
            log.debug("SyncClient: bad auth response: %r", raw)
            self._close_socket()
            return False

        if not resp.get("ok"):
            reason = resp.get("reason", "unknown")
            log.warning("SyncClient: auth rejected: %s", reason)
            self.rx_q.put(("sync_error", f"Sync auth rejected: {reason}"))
            self._close_socket()
            return False

        # Switch to longer recv timeout now that we're authenticated
        sock.settimeout(RECV_TIMEOUT)
        log.debug("SyncClient: authenticated as %s", resp.get("character", "?"))
        return True

    def _recv_loop(self):
        """Read JSON lines from server and push to rx_q."""
        while self.is_running():
            try:
                raw = self._readline()
            except socket.timeout:
                # Server should push every 1s; if we time out after 45s something's wrong
                log.debug("SyncClient: recv timeout — server silent, dropping")
                break
            except (OSError, ConnectionResetError, BrokenPipeError):
                break

            if not raw:
                break  # clean close

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                log.debug("SyncClient: bad JSON line: %r", raw[:120])
                continue

            msg_type = msg.get("type", "state")
            if msg_type == "state":
                self.rx_q.put(("sync_state", msg))
            else:
                self.rx_q.put(("sync_event", msg))

        self._close_socket()

    def _readline(self) -> Optional[str]:
        """
        Read one newline-terminated line from the socket.
        Returns the stripped string, or None on clean close.
        Raises OSError / socket.timeout on errors.
        """
        buf = b""
        while True:
            chunk = self._sock.recv(1)
            if not chunk:
                return None
            buf += chunk
            if len(buf) > MAX_LINE_BYTES:
                log.warning("SyncClient: oversized line, dropping")
                buf = b""
                continue
            if b"\n" in buf:
                return buf.rstrip(b"\n\r").decode("utf-8", errors="replace")

    def _close_socket(self):
        sock = self._sock
        self._sock = None
        if sock:
            try:
                sock.close()
            except Exception:
                pass
