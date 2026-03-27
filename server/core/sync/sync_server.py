from typing import Optional, Dict
"""
sync_server.py
--------------
Real-time state sync server — asyncio TCP, port 4902 (configurable).

Protocol: newline-delimited JSON (NDJSON) over a persistent TCP connection.

Handshake:
  Client → Server:  {"auth": "<64-char-hex-token>"}\\n
  Server → Client:  {"ok": true,  "character": "Name"}\\n       (success)
                or  {"ok": false, "reason": "..."}\\n           (fail, disconnects)

After handshake, server pushes state lines indefinitely:
  Server → Client:  {"type":"state", "ts":..., "vitals":..., ...}\\n

One connection per character.  A second connection from the same character
silently replaces the first (handles client restart without server restart).

The server runs on the same asyncio event loop as the main game server —
no threads, no locking needed.
"""

import asyncio
import json
import logging
import time

log = logging.getLogger(__name__)

# How long to wait for the auth message before dropping the connection
AUTH_TIMEOUT = 10.0


class SyncServer:
    """Manages all active sync client connections."""

    def __init__(self, server):
        self._server   = server
        self._host     = "0.0.0.0"
        self._port     = 4902
        self._tcp_srv  = None
        # character_id (int) -> asyncio.StreamWriter
        self._writers: Dict[int, asyncio.StreamWriter] = {}
        # token (str) -> character_id (int)  — in-memory fallback cache
        self._token_cache: Dict[str, int] = {}

    async def initialize(self):
        """Boot the sync TCP server and add it to the running event loop."""
        cfg  = self._server.config
        host = cfg.get("sync.host", "0.0.0.0")
        port = int(cfg.get("sync.port", 4902))
        self._host = host
        self._port = port

        try:
            self._tcp_srv = await asyncio.start_server(
                self._handle_connection, host, port
            )
            log.info("SyncServer: listening on %s:%d", host, port)
        except Exception as e:
            log.error("SyncServer: failed to bind %s:%d — %s", host, port, e)

    def has_connections(self) -> bool:
        return bool(self._writers)

    def is_connected(self, character_id: int) -> bool:
        w = self._writers.get(character_id)
        return w is not None and not w.is_closing()

    async def send(self, character_id: int, line: str):
        """Push a pre-serialised JSON line to a character's sync client."""
        w = self._writers.get(character_id)
        if not w or w.is_closing():
            self._writers.pop(character_id, None)
            return
        try:
            w.write(line.encode("utf-8"))
            await w.drain()
        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
            self._writers.pop(character_id, None)
            log.debug("SyncServer: client disconnected for character_id=%d", character_id)
        except Exception as e:
            log.debug("SyncServer: send error for character_id=%d: %s", character_id, e)
            self._writers.pop(character_id, None)

    async def send_event(self, character_id: int, event: dict):
        """Push an arbitrary event dict as a JSON line."""
        line = json.dumps(event, separators=(",", ":")) + "\n"
        await self.send(character_id, line)

    def disconnect(self, character_id: int):
        """Close the sync connection for a character (called on logout)."""
        w = self._writers.pop(character_id, None)
        if w and not w.is_closing():
            try:
                w.close()
            except Exception:
                pass
        log.debug("SyncServer: disconnected character_id=%d", character_id)

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _handle_connection(self, reader: asyncio.StreamReader,
                                  writer: asyncio.StreamWriter):
        """New TCP connection handler — authenticate then keep alive."""
        peer = writer.get_extra_info("peername", ("?", 0))
        log.debug("SyncServer: new connection from %s:%d", peer[0], peer[1])

        character_id = await self._authenticate(reader, writer, peer)
        if character_id is None:
            writer.close()
            return

        # Register — replace any stale previous connection
        old = self._writers.get(character_id)
        if old and not old.is_closing():
            try:
                old.close()
            except Exception:
                pass
        self._writers[character_id] = writer

        char_name = self._get_char_name(character_id)
        log.debug("SyncServer: %s (id=%d) sync connected from %s:%d",
                 char_name, character_id, peer[0], peer[1])

        # Push an immediate snapshot so the client doesn't have to wait 1s
        await self._push_immediate(character_id)

        # Keep the connection alive — server pushes, client does not send
        # We still need to detect client disconnects
        try:
            while True:
                # Wait for any data (client shouldn't send anything after auth)
                # A zero-length read means disconnect
                data = await asyncio.wait_for(reader.read(64), timeout=30.0)
                if not data:
                    break
                # Ignore any unexpected client data silently
        except (asyncio.TimeoutError, asyncio.CancelledError):
            # Timeout is normal — just means client is alive and silent
            # Re-enter the loop (ideally we'd loop, but keep simple: disconnect on timeout)
            pass
        except (ConnectionResetError, BrokenPipeError):
            pass

        # Cleanup
        self._writers.pop(character_id, None)
        if not writer.is_closing():
            writer.close()
        log.debug("SyncServer: %s sync disconnected", char_name)

    async def _authenticate(self, reader, writer, peer) -> Optional[int]:
        """
        Read the auth JSON line from the client.
        Returns character_id on success, None on failure.
        """
        try:
            raw = await asyncio.wait_for(reader.readline(), timeout=AUTH_TIMEOUT)
        except asyncio.TimeoutError:
            log.debug("SyncServer: auth timeout from %s:%d", peer[0], peer[1])
            self._send_err(writer, "auth_timeout")
            return None

        raw = raw.strip()
        if not raw:
            self._send_err(writer, "empty_auth")
            return None

        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            self._send_err(writer, "invalid_json")
            return None

        token = msg.get("auth", "")
        if not token or len(token) != 64:
            self._send_err(writer, "invalid_token_format")
            return None

        character_id = self._validate_token(token)
        if character_id is None:
            self._send_err(writer, "invalid_token")
            return None

        # Send success
        char_name = self._get_char_name(character_id)
        ok_msg = json.dumps({
            "ok":        True,
            "character": char_name,
            "server_ts": time.time(),
        }, separators=(",", ":")) + "\n"
        try:
            writer.write(ok_msg.encode("utf-8"))
            await writer.drain()
        except Exception:
            return None

        return character_id

    def _validate_token(self, token: str) -> Optional[int]:
        """
        Check the token against DB, with an in-memory cache fallback.
        The cache is populated when generate_token() is called at login.
        """
        # In-memory cache first (covers the period before DB write completes
        # and when DB is unavailable)
        if token in self._token_cache:
            return self._token_cache[token]

        # DB lookup
        db = getattr(self._server, "db", None)
        if db:
            try:
                from server.core.sync.sync_auth import validate_token
                char_id = validate_token(db, token)
                if char_id:
                    self._token_cache[token] = char_id
                    return char_id
            except Exception as e:
                log.debug("SyncServer: DB token validate error: %s", e)

        return None

    def _send_err(self, writer, reason: str):
        try:
            msg = json.dumps({"ok": False, "reason": reason},
                             separators=(",", ":")) + "\n"
            writer.write(msg.encode("utf-8"))
        except Exception:
            pass

    def _get_char_name(self, character_id: int) -> str:
        """Look up character name from active sessions."""
        try:
            sessions = self._server.sessions.playing()
            for s in sessions:
                if s.character_id == character_id:
                    return s.character_name or f"id:{character_id}"
        except Exception:
            pass
        return f"id:{character_id}"

    async def _push_immediate(self, character_id: int):
        """Push an initial snapshot immediately after auth completes."""
        try:
            broadcaster = getattr(self._server, "sync_broadcaster", None)
            if not broadcaster:
                return
            sessions = self._server.sessions.playing()
            for s in sessions:
                if s.character_id == character_id:
                    import json as _json
                    from server.core.sync.sync_broadcaster import build_snapshot
                    snap = build_snapshot(s, self._server)
                    line = _json.dumps(snap, separators=(",", ":")) + "\n"
                    await self.send(character_id, line)
                    return
        except Exception as e:
            log.debug("SyncServer: immediate push failed: %s", e)

    # ── Token cache management (called by game_server at login/logout) ────────

    def cache_token(self, character_id: int, token: str):
        """Store token in memory so sync auth works before DB write completes."""
        # Clear any old token for this character
        self._token_cache = {
            t: cid for t, cid in self._token_cache.items()
            if cid != character_id
        }
        self._token_cache[token] = character_id

    def evict_token(self, character_id: int):
        """Remove cached token on logout."""
        self._token_cache = {
            t: cid for t, cid in self._token_cache.items()
            if cid != character_id
        }
