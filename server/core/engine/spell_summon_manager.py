from __future__ import annotations

import json
import logging
import time
from math import ceil
from typing import Optional

from server.core.protocol.colors import item_name as fmt_item_name

log = logging.getLogger(__name__)


class SpellSummonManager:
    def __init__(self, server):
        self.server = server
        self.cfg: dict = {}
        self._template_cache: dict[str, dict] = {}

    async def initialize(self):
        cfg = getattr(self.server.lua, "get_spell_summons", lambda: None)()
        if not isinstance(cfg, dict) or not (cfg.get("by_spell") or {}):
            raise RuntimeError("SpellSummonManager: spell_summons.lua failed to load or returned empty data")
        self.cfg = cfg
        self._template_cache = {}
        log.info("SpellSummonManager ready (%d summon spell defs)", len(self.by_spell()))

    def by_spell(self) -> dict:
        return self.cfg.get("by_spell") or {}

    def _now(self) -> int:
        return int(time.time())

    def _spell_cfg(self, spell_number: int | str) -> dict:
        return self.by_spell().get(str(spell_number)) or {}

    def _template_for_short_name(self, short_name: str) -> Optional[dict]:
        if not short_name:
            return None
        cached = self._template_cache.get(short_name)
        if cached:
            return cached
        db = getattr(self.server, "db", None)
        if not db:
            return None
        row = db.get_item_template_by_short_name(short_name)
        if row:
            self._template_cache[short_name] = row
        return row

    def _active_summon_buffs(self, character_id: int) -> dict[int, dict]:
        db = getattr(self.server, "db", None)
        if not db or not character_id:
            return {}
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            spell_numbers = [int(key) for key in self.by_spell().keys()]
            placeholders = ",".join(["%s"] * len(spell_numbers))
            cur.execute(
                f"""
                SELECT id, spell_number, effects_json, expires_at
                FROM character_active_buffs
                WHERE character_id = %s
                  AND spell_number IN ({placeholders})
                  AND (expires_at IS NULL OR expires_at > NOW())
                """,
                (int(character_id), *spell_numbers),
            )
            out = {}
            for row in cur.fetchall():
                try:
                    row["effects"] = json.loads(row.get("effects_json") or "{}")
                except Exception:
                    row["effects"] = {}
                out[int(row["spell_number"])] = row
            return out
        finally:
            conn.close()

    def _find_summon_item(self, session, summon_key: str):
        for item in getattr(session, "inventory", []) or []:
            if str(item.get("spell_summon_key") or "") == str(summon_key):
                return item
        return None

    def _children_for(self, session, parent_inv_id: int) -> list[dict]:
        result = []
        for item in getattr(session, "inventory", []) or []:
            try:
                if int(item.get("container_id") or 0) == int(parent_inv_id or 0):
                    result.append(item)
            except Exception:
                continue
        return result

    def _nested_inline_item_count(self, item: dict) -> int:
        total = 1
        for child in item.get("contents") or []:
            total += self._nested_inline_item_count(child)
        return total

    def _nested_item_count(self, session, item: dict) -> int:
        total = 1
        for child in self._children_for(session, item.get("inv_id")):
            total += self._nested_item_count(session, child)
        for child in item.get("contents") or []:
            total += self._nested_inline_item_count(child)
        return total

    def _inline_weight_total(self, item: dict) -> int:
        total = int(item.get("weight") or 0) * max(1, int(item.get("quantity") or 1))
        for child in item.get("contents") or []:
            total += self._inline_weight_total(child)
        return total

    def _item_weight_total(self, session, item: dict) -> int:
        total = int(item.get("weight") or 0) * max(1, int(item.get("quantity") or 1))
        for child in self._children_for(session, item.get("inv_id")):
            total += self._item_weight_total(session, child)
        for child in item.get("contents") or []:
            total += self._inline_weight_total(child)
        return total

    def _snapshot_inline_tree(self, item: dict) -> dict:
        snapshot = {
            key: value for key, value in dict(item or {}).items()
            if key not in {"inv_id", "slot", "container_id", "ground_id", "room_id", "created_at", "expires_at"}
        }
        children = [self._snapshot_inline_tree(child) for child in item.get("contents") or []]
        if children:
            snapshot["contents"] = children
        return snapshot

    def _snapshot_item_tree(self, session, item: dict) -> dict:
        snapshot = {
            key: value for key, value in dict(item or {}).items()
            if key not in {"inv_id", "slot", "container_id", "ground_id", "room_id", "created_at", "expires_at"}
        }
        children = [self._snapshot_item_tree(session, child) for child in self._children_for(session, item.get("inv_id"))]
        children.extend(self._snapshot_inline_tree(child) for child in item.get("contents") or [])
        if children:
            snapshot["contents"] = children
        return snapshot

    def _remove_item_tree(self, session, item: dict):
        for child in list(self._children_for(session, item.get("inv_id"))):
            self._remove_item_tree(session, child)
        inv_id = item.get("inv_id")
        if inv_id and getattr(self.server, "db", None):
            self.server.db.remove_item_from_inventory(inv_id)
        if item in getattr(session, "inventory", []):
            session.inventory.remove(item)

    def _dump_container_contents_to_ground(self, session, container: dict, room_id: int):
        top_level = list(self._children_for(session, container.get("inv_id")))
        dropped = 0
        for item in top_level:
            snapshot = self._snapshot_item_tree(session, item)
            self.server.world.add_ground_item(
                room_id,
                snapshot,
                dropped_by_character_id=getattr(session, "character_id", None),
                dropped_by_name=getattr(session, "character_name", None),
                source="spell_summon",
            )
            self._remove_item_tree(session, item)
            dropped += 1
        return dropped

    def _remove_summon_buff(self, character_id: int, spell_number: int):
        db = getattr(self.server, "db", None)
        if db:
            db.execute_update(
                "DELETE FROM character_active_buffs WHERE character_id = %s AND spell_number = %s",
                (int(character_id), int(spell_number)),
            )

    def _persist_extra(self, inv_id: int, extra: dict):
        if getattr(self.server, "db", None):
            self.server.db.save_item_extra_data(inv_id, extra)

    def _create_summon_item(self, session, spell_number: int, buff_row: dict, cfg: dict):
        template = self._template_for_short_name(cfg.get("template_short_name"))
        db = getattr(self.server, "db", None)
        if not template or not db or not getattr(session, "character_id", None):
            return None
        inv_id = db.insert_inventory_item_instance(
            session.character_id,
            int(template["id"]),
            slot=cfg.get("slot"),
        )
        if not inv_id:
            return None
        effects = buff_row.get("effects") or {}
        extra = {
            "spell_summon_key": effects.get("summon_key") or cfg.get("summon_key"),
            "summoned_spell_number": int(spell_number),
            "summoned_by": int(getattr(session, "character_id", 0) or 0),
            "summoned_owner_name": getattr(session, "character_name", "") or "",
            "opened": True,
        }
        if spell_number == 511:
            extra.update({
                "container_capacity": int(effects.get("item_capacity") or cfg.get("default_capacity") or 8),
                "max_weight_units": int(effects.get("max_weight") or cfg.get("max_weight") or 500),
                "floating_disk": True,
            })
        elif spell_number == 218:
            extra.update({
                "container_capacity": int(effects.get("hand_capacity") or cfg.get("hand_capacity") or 2),
                "max_item_units": int(effects.get("hand_capacity") or cfg.get("hand_capacity") or 2),
                "spirit_servant": True,
                "servant_room_id": int(getattr(getattr(session, "current_room", None), "id", 0) or 0),
                "servant_following": True,
                "preservation_seconds": int(effects.get("preservation_seconds") or 0),
            })
        self._persist_extra(inv_id, extra)
        from server.core.commands.player.inventory import restore_inventory_state
        restore_inventory_state(self.server, session)
        return self._find_summon_item(session, extra["spell_summon_key"])

    async def _expire_summon(self, session, spell_number: int, item: Optional[dict], *, reason: str = ""):
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if item and spell_number == 218:
            room_id = int(item.get("servant_room_id") or room_id or 0)
        if item and room_id:
            self._dump_container_contents_to_ground(session, item, room_id)
            if item.get("inv_id") and getattr(self.server, "db", None):
                self.server.db.remove_item_from_inventory(item["inv_id"])
            if item in getattr(session, "inventory", []):
                session.inventory.remove(item)
        if getattr(session, "character_id", None):
            self._remove_summon_buff(session.character_id, spell_number)
        if reason:
            await session.send_line(reason)

    async def _reconcile_session(self, session, now: int):
        buffs = self._active_summon_buffs(getattr(session, "character_id", 0))
        for key, cfg in self.by_spell().items():
            spell_number = int(key)
            item = self._find_summon_item(session, cfg.get("summon_key"))
            buff_row = buffs.get(spell_number)
            if spell_number == 511 and getattr(session, "is_dead", False):
                buff_row = None
            if buff_row and not item:
                item = self._create_summon_item(session, spell_number, buff_row, cfg)
                if item and spell_number == 511:
                    await session.send_line("A small circular container suddenly appears and floats serenely over to you.")
                elif item and spell_number == 218:
                    await session.send_line("A translucent servant-spirit glides into place, awaiting your direction.")
            elif not buff_row and item:
                reason = (
                    "The floating disk disintegrates, dropping everything to the ground."
                    if spell_number == 511 else
                    "The spirit servant fades back into the unseen, relinquishing what it carries."
                )
                await self._expire_summon(session, spell_number, item, reason=reason)
                continue

            if item and buff_row:
                effects = buff_row.get("effects") or {}
                following = bool(item.get("servant_following", True))
                servant_room_id = int(item.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
                if spell_number == 218 and following:
                    servant_room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
                payload = {
                    "spell_summon_key": cfg.get("summon_key"),
                    "summoned_spell_number": spell_number,
                    "summoned_by": int(getattr(session, "character_id", 0) or 0),
                    "summoned_owner_name": getattr(session, "character_name", "") or "",
                    "opened": True,
                }
                if spell_number == 511:
                    item["container_capacity"] = int(effects.get("item_capacity") or cfg.get("default_capacity") or item.get("container_capacity") or 8)
                    item["max_weight_units"] = int(effects.get("max_weight") or cfg.get("max_weight") or item.get("max_weight_units") or 500)
                    payload.update({
                        "container_capacity": item["container_capacity"],
                        "max_weight_units": item["max_weight_units"],
                        "floating_disk": True,
                    })
                else:
                    item["container_capacity"] = int(effects.get("hand_capacity") or cfg.get("hand_capacity") or 2)
                    item["max_item_units"] = int(effects.get("hand_capacity") or cfg.get("hand_capacity") or 2)
                    item["servant_room_id"] = servant_room_id
                    item["servant_following"] = following
                    payload.update({
                        "container_capacity": item["container_capacity"],
                        "max_item_units": item["max_item_units"],
                        "servant_room_id": servant_room_id,
                        "servant_following": following,
                        "spirit_servant": True,
                        "preservation_seconds": int(effects.get("preservation_seconds") or item.get("preservation_seconds") or 0),
                    })
                self._persist_extra(item["inv_id"], payload)

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return
        now = self._now()
        for session in self.server.sessions.playing():
            try:
                await self._reconcile_session(session, now)
            except Exception as e:
                log.error("SpellSummonManager tick error for %s: %s", getattr(session, "character_name", "?"), e, exc_info=True)

    async def on_player_login(self, session):
        await self._reconcile_session(session, self._now())

    async def on_player_logout(self, session):
        disk = self._find_summon_item(session, "floating_disk")
        if disk:
            await self._expire_summon(session, 511, disk)
        servant = self._find_summon_item(session, "spirit_servant")
        if servant:
            await self._expire_summon(session, 218, servant)

    def _item_units_for_container(self, session, item: dict, summon_key: str) -> int:
        if summon_key == "floating_disk":
            noun = str(item.get("noun") or "").lower()
            if bool(item.get("is_locked")) and noun in {"box", "coffer", "chest", "strongbox", "trunk", "crate"}:
                return max(1, ceil(max(1, self._nested_item_count(session, item)) / 3.0))
        return max(1, self._nested_item_count(session, item))

    def _container_units_used(self, session, container: dict) -> int:
        summon_key = str(container.get("spell_summon_key") or "")
        return sum(self._item_units_for_container(session, item, summon_key) for item in self._children_for(session, container.get("inv_id")))

    def _container_weight_used(self, session, container: dict) -> int:
        return sum(self._item_weight_total(session, item) for item in self._children_for(session, container.get("inv_id")))

    def _disk_capacity_status(self, session, disk: dict) -> tuple[int, int, int, int]:
        return (
            self._container_units_used(session, disk),
            int(disk.get("container_capacity") or 8),
            self._container_weight_used(session, disk),
            int(disk.get("max_weight_units") or 500),
        )

    def get_visible_entities_in_room(self, room_id: int, *, viewer=None) -> list[dict]:
        room_id = int(room_id or 0)
        entities = []
        for session in self.server.sessions.playing():
            for key, cfg in self.by_spell().items():
                item = self._find_summon_item(session, cfg.get("summon_key"))
                if not item:
                    continue
                if int(key) == 511:
                    entity_room = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
                else:
                    entity_room = int(item.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
                if entity_room == room_id:
                    entities.append({"owner": session, "item": item, "cfg": cfg, "spell_number": int(key)})
        return entities

    def format_room_line(self, entity: dict) -> str:
        cfg = entity.get("cfg") or {}
        owner = entity.get("owner")
        item = entity.get("item") or {}
        if int(entity.get("spell_number") or 0) == 218 and not bool(item.get("servant_following", True)):
            return cfg.get("away_room_line") or "You also see a translucent spirit servant hovering here."
        owner_name = getattr(owner, "character_name", "someone")
        line = cfg.get("room_line") or "You also see something summoned near %s."
        return line % owner_name

    def find_visible_entity(self, room_id: int, target: str, *, viewer=None) -> Optional[dict]:
        target = (target or "").strip().lower()
        for entity in self.get_visible_entities_in_room(room_id, viewer=viewer):
            owner = entity.get("owner")
            item = entity.get("item") or {}
            names = {
                str(item.get("short_name") or "").lower(),
                str(item.get("name") or "").lower(),
                str(item.get("noun") or "").lower(),
            }
            names.update({"servant", "spirit servant"} if int(entity.get("spell_number") or 0) == 218 else {"disk", "floating disk"})
            if owner and owner.character_name:
                names.add(f"{owner.character_name.lower()}'s {item.get('noun', '')}".strip())
            if any(target == name or target in name for name in names if name):
                return entity
        return None

    def look_lines_for_entity(self, entity: dict) -> list[str]:
        cfg = entity.get("cfg") or {}
        owner = entity.get("owner")
        item = entity.get("item") or {}
        lines = list(cfg.get("look_lines") or [])
        if int(entity.get("spell_number") or 0) == 511:
            used, cap, weight_used, weight_cap = self._disk_capacity_status(owner, item)
            lines.append(f"  Capacity: {used}/{cap} item units.")
            lines.append(f"  Weight: {weight_used}/{weight_cap} pounds.")
        else:
            carried = len(self._children_for(owner, item.get("inv_id")))
            lines.append(f"  Servant hands occupied: {carried}/{int(item.get('container_capacity') or 2)}.")
            if not bool(item.get("servant_following", True)):
                lines.append("  It is currently away from its master, carrying out the last command it was given.")
        return lines

    async def handle_dismiss(self, session, args: str) -> bool:
        target = (args or "").strip().lower()
        if target in {"", "disk", "floating disk"}:
            disk = self._find_summon_item(session, "floating_disk")
            if disk:
                await self._expire_summon(session, 511, disk, reason="The floating disk disintegrates, dropping everything to the ground.")
                return True
        if target in {"", "servant", "spirit servant"}:
            servant = self._find_summon_item(session, "spirit_servant")
            if servant:
                await self._expire_summon(session, 218, servant, reason="The spirit servant bows once and fades from sight.")
                return True
        return False

    async def handle_turn(self, session, args: str) -> bool:
        if (args or "").strip().lower() not in {"disk", "floating disk"}:
            return False
        disk = self._find_summon_item(session, "floating_disk")
        if not disk:
            await session.send_line("You do not currently have a floating disk.")
            return True
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        dropped = self._dump_container_contents_to_ground(session, disk, room_id)
        await session.send_line(f"You turn the floating disk, spilling {dropped} item(s) onto the ground.")
        return True

    async def handle_recover(self, session, args: str) -> bool:
        servant = self._find_summon_item(session, "spirit_servant")
        if not servant:
            return False
        contents = self._children_for(session, servant.get("inv_id"))
        if not contents:
            await session.send_line("Your spirit servant is not holding anything to recover.")
            return True
        query = (args or "").strip().lower()
        target_item = contents[0]
        if query:
            target_item = None
            for item in contents:
                haystack = " ".join(str(item.get(key) or "") for key in ("name", "short_name", "noun")).lower()
                if query in haystack:
                    target_item = item
                    break
        if not target_item:
            await session.send_line("Your spirit servant is not holding that.")
            return True
        await self._servant_give_item(session, servant, target_item, None)
        return True

    async def handle_tell(self, session, args: str) -> bool:
        text = (args or "").strip()
        lower_text = text.lower()
        rest = None
        for prefix in ("spirit servant", "servant", "spirit"):
            if lower_text.startswith(prefix):
                rest = text[len(prefix):].strip()
                break
        if rest is None:
            return False
        servant = self._find_summon_item(session, "spirit_servant")
        if not servant:
            await session.send_line("You have no spirit servant to command.")
            return True
        if rest.lower().startswith("to "):
            rest = rest[3:].strip()
        lower = rest.lower()
        if not lower:
            await session.send_line("Tell your servant to do what?  GET, GIVE, DROP, GO, REPORT, RETURN, or LEAVE.")
            return True
        if lower in {"leave", "dismiss"}:
            await self._expire_summon(session, 218, servant, reason="The spirit servant inclines its head and fades from sight.")
            return True
        if lower in {"return", "follow", "come back", "come"}:
            servant["servant_following"] = True
            servant["servant_room_id"] = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
            self._persist_extra(servant["inv_id"], {
                "spell_summon_key": "spirit_servant", "summoned_spell_number": 218,
                "summoned_by": int(getattr(session, "character_id", 0) or 0),
                "summoned_owner_name": getattr(session, "character_name", "") or "",
                "container_capacity": int(servant.get("container_capacity") or 2),
                "max_item_units": int(servant.get("max_item_units") or 2),
                "servant_room_id": int(servant["servant_room_id"]), "servant_following": True,
                "opened": True, "spirit_servant": True, "preservation_seconds": int(servant.get("preservation_seconds") or 0),
            })
            await session.send_line("Your spirit servant glides back to your side.")
            return True
        if lower in {"report", "look", "status"}:
            await self._report_servant_room(session, servant)
            return True
        if lower.startswith("go "):
            await self._servant_go_direction(session, servant, lower[3:].strip())
            return True
        if lower.startswith("get "):
            await self._servant_get_ground_item(session, servant, rest[4:].strip())
            return True
        if lower.startswith("drop "):
            await self._servant_drop_item(session, servant, rest[5:].strip())
            return True
        if lower.startswith("give "):
            payload = rest[5:].strip()
            item_name, target_name = payload, None
            if " to " in payload.lower():
                item_name, target_name = payload.rsplit(" to ", 1)
                item_name = item_name.strip()
                target_name = target_name.strip()
            await self._servant_give_named_item(session, servant, item_name, target_name)
            return True
        await session.send_line("Your spirit servant does not understand that command.")
        return True

    async def _report_servant_room(self, session, servant: dict):
        room_id = int(servant.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
        room = self.server.world.get_room(room_id)
        if not room:
            await session.send_line("You lose the thread of your servant's surroundings.")
            return
        players = [s for s in self.server.world.get_players_in_room(room_id) if s is not session]
        creatures = getattr(self.server.creatures, "get_creatures_in_room", lambda _rid: [])(room_id)
        npcs = getattr(self.server.npcs, "get_npcs_in_room", lambda _rid: [])(room_id)
        exits = ", ".join(room.get_display_exit_names(session)) if hasattr(room, "get_display_exit_names") else ""
        await session.send_line(f"Your spirit servant reports from {room.title}  #{room.id}.")
        await session.send_line(f"  Creatures: {len(creatures)}   NPCs: {len(npcs)}   Other adventurers: {len(players)}")
        if exits:
            await session.send_line(f"  Exits: {exits}")

    async def _servant_go_direction(self, session, servant: dict, direction: str):
        room_id = int(servant.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
        room = self.server.world.get_room(room_id) if room_id else None
        if not room:
            await session.send_line("Your servant has nowhere to go from here.")
            return
        exit_key = direction.lower().replace(" ", "_")
        target_room_id = room.exits.get(exit_key)
        if not target_room_id:
            for key, value in room.exits.items():
                if key.lower() == direction.lower():
                    exit_key, target_room_id = key, value
                    break
        if not target_room_id:
            await session.send_line("Your servant cannot find a way to go that direction.")
            return
        servant["servant_following"] = False
        servant["servant_room_id"] = int(target_room_id)
        self._persist_extra(servant["inv_id"], {
            "spell_summon_key": "spirit_servant", "summoned_spell_number": 218,
            "summoned_by": int(getattr(session, "character_id", 0) or 0),
            "summoned_owner_name": getattr(session, "character_name", "") or "",
            "container_capacity": int(servant.get("container_capacity") or 2),
            "max_item_units": int(servant.get("max_item_units") or 2),
            "servant_room_id": int(target_room_id), "servant_following": False,
            "opened": True, "spirit_servant": True, "preservation_seconds": int(servant.get("preservation_seconds") or 0),
        })
        await session.send_line(f"Your spirit servant drifts {exit_key.replace('_', ' ')} to scout ahead.")
        await self._report_servant_room(session, servant)

    async def _servant_get_ground_item(self, session, servant: dict, query: str):
        room_id = int(servant.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
        found = None
        query_l = (query or "").strip().lower()
        for item in self.server.world.get_ground_items(room_id):
            haystack = " ".join(str(item.get(key) or "") for key in ("name", "short_name", "noun")).lower()
            if query_l and query_l in haystack:
                found = item
                break
        if not found:
            await session.send_line("Your servant cannot find that item.")
            return
        if len(self._children_for(session, servant.get("inv_id"))) >= int(servant.get("container_capacity") or 2):
            await session.send_line("Your servant's ghostly hands are already full.")
            return
        self.server.world.remove_ground_item(room_id, found)
        if getattr(self.server, "db", None) and getattr(session, "character_id", None) and found.get("item_id"):
            inv_id = self.server.db.insert_inventory_item_instance(session.character_id, int(found["item_id"]), container_id=int(servant["inv_id"]))
            extra = {
                key: value for key, value in dict(found).items()
                if key not in {
                    "inv_id", "item_id", "name", "short_name", "noun", "article",
                    "item_type", "weight", "value", "slot", "container_id", "description",
                    "ground_id", "room_id", "dropped_source", "created_at", "expires_at",
                }
            }
            if inv_id and extra:
                self.server.db.save_item_extra_data(inv_id, extra)
        from server.core.commands.player.inventory import restore_inventory_state
        restore_inventory_state(self.server, session)
        await session.send_line(f"Your spirit servant retrieves {fmt_item_name(found.get('short_name') or found.get('name') or 'something')}.")

    async def _servant_drop_item(self, session, servant: dict, query: str):
        query_l = (query or "").strip().lower()
        target = None
        for item in self._children_for(session, servant.get("inv_id")):
            haystack = " ".join(str(item.get(key) or "") for key in ("name", "short_name", "noun")).lower()
            if query_l and query_l in haystack:
                target = item
                break
        if not target:
            await session.send_line("Your spirit servant is not holding that.")
            return
        room_id = int(servant.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
        snapshot = self._snapshot_item_tree(session, target)
        self.server.world.add_ground_item(room_id, snapshot, dropped_by_character_id=getattr(session, "character_id", None), dropped_by_name=getattr(session, "character_name", None), source="spell_summon")
        self._remove_item_tree(session, target)
        await session.send_line(f"Your spirit servant releases {fmt_item_name(snapshot.get('short_name') or snapshot.get('name') or 'something')} to the ground.")

    async def _servant_give_named_item(self, session, servant: dict, item_name: str, target_name: Optional[str]):
        query_l = (item_name or "").strip().lower()
        target_item = None
        for item in self._children_for(session, servant.get("inv_id")):
            haystack = " ".join(str(item.get(key) or "") for key in ("name", "short_name", "noun")).lower()
            if query_l and query_l in haystack:
                target_item = item
                break
        if not target_item:
            await session.send_line("Your spirit servant is not holding that.")
            return
        await self._servant_give_item(session, servant, target_item, target_name)

    async def _servant_give_item(self, session, servant: dict, item: dict, target_name: Optional[str]):
        target_session = session
        room_id = int(servant.get("servant_room_id") or getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if target_name:
            target_session = self.server.sessions.find_by_name(target_name) or session
            if not getattr(target_session, "current_room", None) or int(target_session.current_room.id) != room_id:
                await session.send_line("That person is not where your servant is hovering.")
                return
        from server.core.commands.player.inventory import _ensure_hands, _pick_up_to_hand
        _ensure_hands(target_session)
        hand = _pick_up_to_hand(target_session, item)
        if not hand:
            await session.send_line(f"{target_session.character_name}'s hands are full.")
            return
        item["container_id"] = None
        item["slot"] = "right_hand" if hand == "right" else "left_hand"
        if getattr(self.server, "db", None) and item.get("inv_id") and getattr(target_session, "character_id", None):
            self.server.db.transfer_inventory_item(item["inv_id"], target_session.character_id, slot=item["slot"], container_id=None)
        if item in getattr(session, "inventory", []):
            session.inventory.remove(item)
        if item not in getattr(target_session, "inventory", []):
            target_session.inventory.append(item)
        if hand == "right":
            target_session.right_hand = item
        else:
            target_session.left_hand = item
        await session.send_line(f"Your spirit servant places {fmt_item_name(item.get('short_name') or item.get('name') or 'something')} into {target_session.character_name}'s hand.")
        if target_session is not session:
            await target_session.send_line(f"A spirit servant places {fmt_item_name(item.get('short_name') or item.get('name') or 'something')} into your hand.")
