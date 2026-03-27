"""
player_api.py
-------------
Wraps a Session object so Lua scripts can interact with it via clean methods.

Usage in Lua hooks:
  function Room.onEnter(player)
      player:message("You enter the room.")
      player:roomMessage("Someone arrives.", player)
  end

Create one per-call:
  api = LuaPlayerAPI(session, server)
  lua_engine.call_hook(room_table, "onEnter", api)
"""

import logging

log = logging.getLogger(__name__)


class LuaPlayerAPI:
    """Thin wrapper around Session exposing a stable API to Lua scripts."""

    def __init__(self, session, server):
        self._session = session
        self._server  = server

    # ── Identity ──────────────────────────────────────────────────────────────

    def getId(self) -> int:
        return getattr(self._session, "character_id", 0) or 0

    def getName(self) -> str:
        return getattr(self._session, "character_name", "unknown") or "unknown"

    def getLevel(self) -> int:
        return int(getattr(self._session, "level", 1) or 1)

    def getRaceId(self) -> int:
        return int(getattr(self._session, "race_id", 1) or 1)

    def getProfessionId(self) -> int:
        return int(getattr(self._session, "profession_id", 1) or 1)

    def getRoomId(self) -> int:
        return int(getattr(self._session, "current_room_id", 0) or 0)

    # ── Economy ───────────────────────────────────────────────────────────────

    def getSilver(self) -> int:
        return int(getattr(self._session, "silver", 0) or 0)

    def deductSilver(self, amount: int):
        amount = int(amount)
        current = int(getattr(self._session, "silver", 0) or 0)
        self._session.silver = max(0, current - amount)
        self._save_silver()

    def addSilver(self, amount: int):
        amount = int(amount)
        current = int(getattr(self._session, "silver", 0) or 0)
        self._session.silver = current + amount
        self._save_silver()

    def _save_silver(self):
        try:
            db = self._server.db
            db.execute_query(
                "UPDATE characters SET silver = %s WHERE id = %s",
                (self._session.silver, self._session.character_id)
            )
        except Exception as e:
            log.error("LuaPlayerAPI._save_silver error: %s", e)

    # ── Messaging ─────────────────────────────────────────────────────────────

    def message(self, text: str):
        """Send a message to this player only."""
        import asyncio
        session = self._session
        if hasattr(session, "send"):
            coro = session.send(str(text) + "\r\n")
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(coro, loop=loop)
            except Exception as e:
                log.error("LuaPlayerAPI.message error: %s", e)

    def roomMessage(self, text: str, exclude=None):
        """Send a message to all players in the same room, optionally excluding one."""
        try:
            room_id = self.getRoomId()
            world   = self._server.world
            sessions = world.get_players_in_room(room_id)
            for s in sessions:
                if exclude is not None and s is exclude._session:
                    continue
                import asyncio
                coro = s.send(str(text) + "\r\n")
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(coro, loop=loop)
                except Exception:
                    pass
        except Exception as e:
            log.error("LuaPlayerAPI.roomMessage error: %s", e)

    # ── Inventory ─────────────────────────────────────────────────────────────

    def giveItem(self, lua_item):
        """Add a LuaItem to this player's inventory."""
        from server.core.scripting.lua_bindings.items_api import LuaItem
        if not isinstance(lua_item, LuaItem):
            log.warning("giveItem called with non-LuaItem: %s", type(lua_item))
            return
        try:
            db    = self._server.db
            data  = lua_item._data
            item_id = data.get("item_id") or data.get("id")
            if item_id:
                db.add_item_to_inventory(self._session.character_id, item_id)
        except Exception as e:
            log.error("LuaPlayerAPI.giveItem error: %s", e)

    def findHeldItem(self, search: str):
        """Find an item in the player's hands matching a noun/name fragment."""
        try:
            db    = self._server.db
            inv   = db.get_character_inventory(self._session.character_id)
            q     = str(search).lower()
            for row in inv:
                slot = (row.get("slot") or "").lower()
                name = (row.get("name") or "").lower()
                noun = (row.get("noun") or "").lower()
                if slot in ("right_hand", "left_hand"):
                    if q in name or q in noun:
                        from server.core.scripting.lua_bindings.items_api import LuaItem
                        row["item_id"] = row.get("item_id") or row.get("id")
                        item = LuaItem(row, self._server)
                        item._inv_id = row.get("inv_id", 0)
                        return item
        except Exception as e:
            log.error("LuaPlayerAPI.findHeldItem error: %s", e)
        return None

    def removeheldItem(self, lua_item):
        """Remove a held item from inventory by its inv_id."""
        from server.core.scripting.lua_bindings.items_api import LuaItem
        if not isinstance(lua_item, LuaItem):
            return
        try:
            db = self._server.db
            if lua_item._inv_id:
                db.remove_item_from_inventory(lua_item._inv_id)
        except Exception as e:
            log.error("LuaPlayerAPI.removeheldItem error: %s", e)

    # ── Misc ──────────────────────────────────────────────────────────────────

    def getSession(self):
        """Escape hatch for advanced Python code that needs the raw session."""
        return self._session
