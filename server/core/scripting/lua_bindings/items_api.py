"""
items_api.py
------------
Exposes item creation and cloning to Lua scripts.

Injected into Lua globals as _ITEMS_BRIDGE.
Consumed by scripts/globals/utils/items.lua.

The LuaItem wrapper lets Lua call:
  item:getName()
  item:getValue()
  item:getBaseItemId()
  item:setName(name)
  item:setMaterial(mat)
  item:setColor(color)
  item:setEnchantBonus(bonus)
"""

import logging

log = logging.getLogger(__name__)


class LuaItem:
    """
    Wrapper around a live item row / item dict so Lua can manipulate it
    before it is handed to a player.
    """

    def __init__(self, item_data: dict, server=None):
        self._data   = dict(item_data)   # mutable copy
        self._server = server
        self._inv_id: int = item_data.get("inv_id", 0)

    # ── Getters ───────────────────────────────────────────────────────────────

    def getName(self) -> str:
        return self._data.get("name", "an unknown item")

    def getValue(self) -> int:
        return int(self._data.get("value", 0))

    def getBaseItemId(self) -> int:
        return int(self._data.get("item_id", 0))

    def getWeight(self) -> float:
        return float(self._data.get("weight", 0))

    def getType(self) -> str:
        return self._data.get("item_type", "misc")

    def getNoun(self) -> str:
        return self._data.get("noun", "item")

    def getInvId(self) -> int:
        return self._inv_id

    def get(self, key: str):
        return self._data.get(key)

    # ── Setters (pre-delivery customisation) ──────────────────────────────────

    def setName(self, name: str):
        self._data["name"] = name

    def setMaterial(self, material: str):
        self._data["material"] = material

    def setColor(self, color: str):
        self._data["color"] = color

    def setEnchantBonus(self, bonus: int):
        self._data["enchant_bonus"] = int(bonus)

    def set(self, key: str, val):
        self._data[key] = val


class LuaItemsBridge:
    """Python-side items bridge.  One instance shared by all Lua scripts."""

    def __init__(self, server, lua_runtime):
        self._server = server
        self._lua    = lua_runtime

    def clone(self, item_id: int) -> LuaItem:
        """
        Clone a base item template from the DB by its items.id.
        Returns a LuaItem wrapper ready for delivery to a player.
        Usage in Lua:  local item = Items.clone(row.item_id)
        """
        try:
            db   = self._server.db
            conn = db._get_conn()
            try:
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM items WHERE id = %s", (int(item_id),))
                row = cur.fetchone()
            finally:
                conn.close()

            if not row:
                log.warning("LuaItemsBridge.clone: item_id %s not found", item_id)
                return LuaItem({"name": "a missing item", "value": 0, "item_id": item_id})
            row["item_id"] = row["id"]
            return LuaItem(row, self._server)
        except Exception as e:
            log.error("LuaItemsBridge.clone error: %s", e)
            return LuaItem({"name": "a broken item", "value": 0, "item_id": item_id})

    def create(self, props) -> LuaItem:
        """
        Create an ad-hoc item from a Lua property table.
        Usage in Lua:  local item = Items.create({ name="a coin", value=1 })
        """
        try:
            import lupa
            if lupa.lua_type(props) == "table":
                data = {k: v for k, v in props.items()}
            elif isinstance(props, dict):
                data = dict(props)
            else:
                data = {}
            return LuaItem(data, self._server)
        except Exception as e:
            log.error("LuaItemsBridge.create error: %s", e)
            return LuaItem({})
