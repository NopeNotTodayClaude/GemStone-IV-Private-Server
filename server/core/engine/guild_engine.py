"""
Guild progression and access helpers.

This engine keeps guild content data-driven from SQL while exposing a small
runtime API for commands and event hooks.
"""

from __future__ import annotations

import json
import logging
import random
import time
from datetime import datetime, timedelta

from server.core.entity.npc.npc import NPC
from server.core.protocol.colors import colorize, TextPresets, npc_speech

log = logging.getLogger(__name__)


class GuildEngine:
    """Runtime helper for guild access, tasks, and rank progression."""

    _ROGUE_GUILD_ID = "rogue"
    _ROGUE_SEQUENCE_TIMEOUT = 60
    _ENTRY_VERBS = {"lean", "look", "pull", "slap", "rub", "push", "turn", "open", "go", "out"}
    _ENTRY_ALIAS_TARGETS = {"door", "panel", "guild", "alley", "out"}
    _EXIT_PANEL_SEQUENCE = ["pull hoe", "pull rake", "pull shovel", "go panel"]

    def __init__(self, server):
        self.server = server
        self._quest_data_cache: dict[str, dict] = {}

    def get_adventurers_guild_config(self):
        lua = getattr(self.server, "lua", None)
        if not lua:
            return {}
        return lua.get_adventurers_guild() or {}

    def _get_adventurer_authority(self, npc):
        if not npc:
            return None
        config = self.get_adventurers_guild_config()
        authorities = config.get("authorities") or {}
        return authorities.get(getattr(npc, "template_id", "") or "")

    def _adventurer_rank_entry(self, points: int):
        points = max(0, int(points or 0))
        config = self.get_adventurers_guild_config()
        thresholds = config.get("rank_thresholds") or []
        current = {"rank": 1, "title": "Associate", "points": 0}
        for row in thresholds:
            try:
                if points >= int(row.get("points") or 0):
                    current = {
                        "rank": int(row.get("rank") or current["rank"]),
                        "title": str(row.get("title") or current["title"]),
                        "points": int(row.get("points") or current["points"]),
                    }
            except Exception:
                continue
        return current

    def _get_adventurer_bounty_pool(self, town_name: str):
        config = self.get_adventurers_guild_config()
        bounties = config.get("bounties") or {}
        return list(bounties.get(str(town_name or ""), []) or [])

    def _get_adventurer_profile(self, character_id: int):
        db = getattr(self.server, "db", None)
        if not db or not character_id:
            return None
        return db.get_character_adventurer_guild(character_id)

    def ensure_adventurer_registration(self, character_id: int, town_name: str):
        db = getattr(self.server, "db", None)
        if not db or not character_id:
            return None
        profile = db.ensure_character_adventurer_guild(character_id, town_name=town_name)
        if not profile:
            return None
        points = int(profile.get("rank_points") or 0)
        rank = self._adventurer_rank_entry(points)
        return db.update_character_adventurer_guild(
            character_id,
            town_name=town_name,
            rank_level=rank["rank"],
            rank_title=rank["title"],
            rank_points=points,
            lifetime_bounties=int(profile.get("lifetime_bounties") or 0),
        )

    def get_character_bounty(self, character_id: int):
        db = getattr(self.server, "db", None)
        if not db or not character_id:
            return None
        return db.get_character_bounty(character_id)

    async def turn_in_adventurer_bounty(self, session, npc):
        authority = self._get_adventurer_authority(npc)
        if not authority:
            return False, "This is not an Adventurer's Guild authority.", None
        active = self.get_character_bounty(session.character_id)
        if not active:
            return False, "You have no active Adventurer's Guild contract.", None
        status = str(active.get("status") or "").lower()
        if status != "completed":
            return False, self._format_adventurer_bounty(active), active

        silver = int(active.get("reward_silver") or 0)
        experience = int(active.get("reward_experience") or 0)
        fame = int(active.get("reward_fame") or 0)
        points = int(active.get("reward_points") or 0)

        if silver:
            session.silver = int(getattr(session, "silver", 0) or 0) + silver
            if getattr(self.server, "db", None):
                self.server.db.save_character_resources(
                    session.character_id,
                    getattr(session, "health_current", 100),
                    getattr(session, "mana_current", 0),
                    getattr(session, "spirit_current", 10),
                    getattr(session, "stamina_current", 100),
                    session.silver,
                )

        if experience and getattr(self.server, "experience", None):
            await self.server.experience.award_xp_to_pool(
                session,
                experience,
                source="bounty",
                fame_detail_text=f"Completed bounty against {active.get('target_display_name') or active.get('target')}.",
            )

        if fame:
            try:
                from server.core.commands.player.info import award_fame
                await award_fame(
                    session,
                    self.server,
                    fame,
                    "bounty_turnin",
                    detail_text=f"Completed Adventurer's Guild bounty: {active.get('target_display_name') or active.get('target')}.",
                    quiet=True,
                )
            except Exception:
                log.exception("Failed to award explicit bounty fame")

        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        current_points = int((profile or {}).get("rank_points") or 0)
        lifetime = int((profile or {}).get("lifetime_bounties") or 0) + 1
        new_points = current_points + points
        rank = self._adventurer_rank_entry(new_points)
        data = self._load_bounty_data(active)
        self._despawn_temp_npc(data, "escort")
        self._despawn_temp_npc(data, "rescue")
        updated_profile = self.server.db.update_character_adventurer_guild(
            session.character_id,
            town_name=authority.get("town_name") or "",
            rank_level=rank["rank"],
            rank_title=rank["title"],
            rank_points=new_points,
            lifetime_bounties=lifetime,
        )
        self.server.db.close_character_bounty(int(active["id"]))
        return True, None, {
            "silver": silver,
            "experience": experience,
            "fame": fame,
            "points": points,
            "profile": updated_profile or profile,
            "target": active.get("target_display_name") or active.get("target") or "target",
        }

    async def handle_adventurer_guild_topic(self, session, npc, topic: str):
        authority = self._get_adventurer_authority(npc)
        if not authority or not getattr(session, "character_id", None):
            return False

        topic_l = (topic or "").strip().lower()
        if topic_l in ("", "guild", "hello", "work", "assignment", "assignments", "contract", "contracts", "bounties",
                       "escort", "rescue", "bandit", "boss", "gem", "gems", "skin", "skins", "forage", "foraging", "heirloom"):
            topic_l = "bounty"

        if topic_l in ("register", "registration", "join", "ledger"):
            profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
            if not profile:
                await session.send_line(npc_speech(npc.display_name, 'says, "The registration ledger is unavailable right now."'))
                return True
            await session.send_line(
                npc_speech(
                    npc.display_name,
                    f'says, "You are now registered with the Adventurer\'s Guild at {authority.get("town_name")}.  Current rank: {profile.get("rank_title") or "Associate"}."'
                )
            )
            return True

        if topic_l in ("rank", "status"):
            profile = self._get_adventurer_profile(session.character_id)
            if not profile:
                await session.send_line(
                    npc_speech(npc.display_name, 'says, "You are not yet registered.  Ask me about REGISTER first."')
                )
                return True
            active = self.get_character_bounty(session.character_id)
            rank_title = profile.get("rank_title") or "Associate"
            points = int(profile.get("rank_points") or 0)
            lifetime = int(profile.get("lifetime_bounties") or 0)
            msg = (
                f"You are recorded as {rank_title} with {points} guild point{'s' if points != 1 else ''}.  "
                f"Completed contracts: {lifetime}."
            )
            if active:
                msg += "  " + self._format_adventurer_bounty(active)
            await session.send_line(npc_speech(npc.display_name, f'says, "{msg}"'))
            return True

        if topic_l in ("bounty", "work", "assignment", "contract", "contracts", "turnin", "turn-in", "complete", "report"):
            profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
            if not profile:
                await session.send_line(npc_speech(npc.display_name, 'says, "The contract ledger is unavailable right now."'))
                return True
            active = self.get_character_bounty(session.character_id)
            if active:
                status = str(active.get("status") or "").lower()
                if status == "completed":
                    ok, error, summary = await self.turn_in_adventurer_bounty(session, npc)
                    if not ok:
                        await session.send_line(npc_speech(npc.display_name, f'says, "{error}"'))
                        return True
                    profile = summary.get("profile") or profile
                    await session.send_line(
                        npc_speech(
                            npc.display_name,
                            f'says, "Good work.  The contract on {summary.get("target")} is closed.  Rank: {profile.get("rank_title") or "Associate"}."'
                        )
                    )
                    if int(summary.get("silver") or 0):
                        await session.send_line(colorize(f"  Bounty reward: {int(summary['silver'])} silver.", TextPresets.ITEM_NAME))
                    if int(summary.get("points") or 0):
                        await session.send_line(colorize(f"  Adventurer's Guild points: +{int(summary['points'])}.", TextPresets.SYSTEM))
                    return True

                await session.send_line(
                    npc_speech(npc.display_name, f'says, "{self._format_adventurer_bounty(active)}"')
                )
                return True

            ok, error, row = await self.assign_adventurer_bounty(session, npc)
            if not ok:
                line = error or (self._format_adventurer_bounty(row) if row else "I have nothing for you.")
                await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
                return True

            await session.send_line(
                npc_speech(
                    npc.display_name,
                    f'says, "I am assigning you a culling contract.  {self._format_adventurer_bounty(row)}  Report back when it is done."'
                )
            )
            return True

        return False

    def _get_adventurer_town(self, town_name: str):
        config = self.get_adventurers_guild_config()
        towns = config.get("towns") or {}
        return towns.get(str(town_name or ""), {})

    def _get_adventurer_officer_in_room(self, session, *, require_taskmaster=False):
        room = getattr(session, "current_room", None)
        npc_mgr = getattr(self.server, "npcs", None)
        if not room or not npc_mgr:
            return None, None
        for npc in npc_mgr.get_npcs_in_room(room.id):
            authority = self._get_adventurer_authority(npc)
            if not authority:
                continue
            if require_taskmaster and str(authority.get("role") or "").lower() != "taskmaster":
                continue
            return npc, authority
        return None, None

    @staticmethod
    def _normalize_text_list(value):
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, dict):
            out = []
            for key in sorted(value):
                text = str(value.get(key) or "").strip()
                if text:
                    out.append(text)
            return out
        text = str(value or "").strip()
        return [text] if text else []

    @staticmethod
    def _load_bounty_data(bounty_row):
        if not bounty_row:
            return {}
        data = bounty_row.get("bounty_data") or {}
        if isinstance(data, str):
            try:
                data = json.loads(data) if data else {}
            except Exception:
                data = {}
        return data if isinstance(data, dict) else {}

    def _build_bounty_data(self, bounty_row):
        return {
            "key": str(bounty_row.get("key") or ""),
            "type": str(bounty_row.get("type") or "cull"),
            "area": str(bounty_row.get("area") or ""),
            "target_item_type": str(bounty_row.get("target_item_type") or ""),
            "target_short_names": self._normalize_text_list(bounty_row.get("target_short_names")),
            "target_nouns": self._normalize_text_list(bounty_row.get("target_nouns")),
            "search_zone_names": self._normalize_text_list(bounty_row.get("search_zone_names")),
            "search_room_ids": [int(x) for x in self._normalize_text_list(bounty_row.get("search_room_ids")) if str(x).isdigit()],
            "destination_room_id": int(bounty_row.get("destination_room_id") or 0),
            "destination_name": str(bounty_row.get("destination_name") or ""),
            "report_room_id": int(bounty_row.get("report_room_id") or 0),
            "encounter_template_id": str(bounty_row.get("encounter_template_id") or bounty_row.get("target_template_id") or ""),
            "escort_enemy_template_id": str(bounty_row.get("escort_enemy_template_id") or "hobgoblin"),
            "rescue_enemy_template_id": str(bounty_row.get("rescue_enemy_template_id") or "hobgoblin"),
            "escort_npc_name": str(bounty_row.get("escort_npc_name") or ""),
            "escort_npc_description": str(bounty_row.get("escort_npc_description") or ""),
            "rescue_npc_name": str(bounty_row.get("rescue_npc_name") or bounty_row.get("target_name") or ""),
            "rescue_npc_description": str(bounty_row.get("rescue_npc_description") or ""),
            "active_creature_ids": [],
            "escort_npc_id": 0,
            "rescue_npc_id": 0,
            "encounter_room_id": 0,
            "last_spawn_at": 0,
            "phase": str(bounty_row.get("phase") or "assigned"),
        }

    def _save_bounty_data(self, active, data):
        if not active or not data:
            return
        self.server.db.update_character_bounty_data(int(active["id"]), data)

    def _alive_creature_ids(self, ids):
        out = []
        creature_mgr = getattr(self.server, "creatures", None)
        if not creature_mgr:
            return out
        for raw in ids or []:
            try:
                cid = int(raw)
            except Exception:
                continue
            creature = creature_mgr.get_creature(cid)
            if creature and getattr(creature, "alive", False):
                out.append(cid)
        return out

    def _eligible_spawn_rooms_for_template(self, template_id: str):
        creature_mgr = getattr(self.server, "creatures", None)
        if not creature_mgr or not template_id:
            return []
        rooms = []
        for cfg in getattr(creature_mgr, "_spawn_config", []) or []:
            if str(cfg.get("template_id") or "") != str(template_id):
                continue
            for room_id in cfg.get("rooms", []) or []:
                try:
                    room_id = int(room_id)
                except Exception:
                    continue
                if room_id not in rooms:
                    rooms.append(room_id)
        return rooms

    def _spawn_bounty_creature(self, session, template_id: str, room_id: int, *, display_name=None, hp_scale=1.0, as_bonus=0, ds_bonus=0):
        creature_mgr = getattr(self.server, "creatures", None)
        if not creature_mgr:
            return None
        creature = creature_mgr.spawn_creature(str(template_id or ""), int(room_id))
        if not creature:
            return None
        if display_name:
            words = str(display_name).split()
            first = words[0].lower() if words else ""
            if first in {"a", "an", "the"}:
                creature.article = first
                creature.name = " ".join(words[1:]) or creature.name
            else:
                creature.name = str(display_name)
        creature.health_max = max(1, int(creature.health_max * max(0.5, float(hp_scale or 1.0))))
        creature.health_current = creature.health_max
        creature.as_melee = int(getattr(creature, "as_melee", 0) or 0) + int(as_bonus or 0)
        creature.ds_melee = int(getattr(creature, "ds_melee", 0) or 0) + int(ds_bonus or 0)
        creature.ds_bolt = int(getattr(creature, "ds_bolt", 0) or 0) + max(0, int(ds_bonus or 0) // 2)
        creature.aggressive = True
        creature.in_combat = True
        creature.target = session
        return creature

    def _spawn_temp_bounty_npc(self, active, data, key: str, *, name: str, description: str, room_id: int):
        npc_mgr = getattr(self.server, "npcs", None)
        if not npc_mgr or not name or not room_id:
            return None
        npc = NPC({
            "template_id": f"bounty_{active['id']}_{key}_{int(time.time())}",
            "name": name,
            "article": "",
            "title": "",
            "description": description or "Someone attached to an Adventurer's Guild contract is here.",
            "room_id": int(room_id),
            "home_room_id": int(room_id),
            "can_combat": False,
            "can_shop": False,
            "can_wander": False,
            "can_emote": False,
            "can_chat": False,
            "can_loot": False,
            "is_guild": False,
            "is_quest": True,
            "aggressive": False,
            "attacks": [],
        })
        npc_mgr._place_npc(npc)
        data[f"{key}_npc_id"] = int(npc.id)
        return npc

    def _get_temp_npc(self, data, key: str):
        npc_id = int(data.get(f"{key}_npc_id") or 0)
        npc_mgr = getattr(self.server, "npcs", None)
        if not npc_mgr or not npc_id:
            return None
        return npc_mgr.get_npc(npc_id)

    def _move_temp_npc(self, data, key: str, room_id: int):
        npc = self._get_temp_npc(data, key)
        npc_mgr = getattr(self.server, "npcs", None)
        if not npc or not npc_mgr:
            return None
        npc_mgr._move_npc_index(npc, int(room_id))
        return npc

    def _despawn_temp_npc(self, data, key: str):
        npc = self._get_temp_npc(data, key)
        npc_mgr = getattr(self.server, "npcs", None)
        if npc and npc_mgr:
            npc_mgr._remove_npc(npc)
        data[f"{key}_npc_id"] = 0

    async def _maybe_spawn_field_encounter(self, session, active, data):
        room = getattr(session, "current_room", None)
        if not room or getattr(room, "safe", False):
            return False
        now = time.time()
        if now - float(data.get("last_spawn_at") or 0) < 12:
            return False
        data["active_creature_ids"] = self._alive_creature_ids(data.get("active_creature_ids") or [])
        if data["active_creature_ids"]:
            return False

        bounty_type = str(active.get("bounty_type") or data.get("type") or "").lower()
        target_template = str(data.get("encounter_template_id") or active.get("target_template_id") or "")
        eligible = set(data.get("search_room_ids") or []) or set(self._eligible_spawn_rooms_for_template(target_template))
        if bounty_type in {"bandit", "boss"} and eligible and int(room.id) not in {int(x) for x in eligible}:
            return False
        if bounty_type == "rescue" and data.get("search_room_ids") and int(room.id) not in {int(x) for x in data.get("search_room_ids") or []}:
            return False
        if bounty_type == "escort" and int(room.id) in {
            int(data.get("report_room_id") or 0),
            int(data.get("destination_room_id") or 0),
        }:
            return False

        if bounty_type == "boss":
            creature = self._spawn_bounty_creature(
                session,
                target_template,
                room.id,
                display_name=active.get("target_display_name") or active.get("target"),
                hp_scale=1.35,
                as_bonus=14,
                ds_bonus=10,
            )
            spawned = [creature] if creature else []
        else:
            count = 1 if bounty_type == "rescue" else random.randint(1, 2)
            if bounty_type == "bandit":
                count = random.randint(1, 2)
            if bounty_type == "escort":
                target_template = str(data.get("escort_enemy_template_id") or target_template or "hobgoblin")
            if bounty_type == "rescue":
                target_template = str(data.get("rescue_enemy_template_id") or target_template or "hobgoblin")
            spawned = []
            for _ in range(count):
                creature = self._spawn_bounty_creature(
                    session,
                    target_template,
                    room.id,
                    display_name=active.get("target_display_name") if bounty_type == "bandit" else None,
                    hp_scale=1.08 if bounty_type == "bandit" else 1.0,
                    as_bonus=6 if bounty_type == "bandit" else 2,
                    ds_bonus=4 if bounty_type == "bandit" else 0,
                )
                if creature:
                    spawned.append(creature)
        if not spawned:
            return False

        data["active_creature_ids"] = [int(c.id) for c in spawned]
        data["encounter_room_id"] = int(room.id)
        data["last_spawn_at"] = int(now)
        lines = {
            "bandit": f"  A bandit crew bursts from cover and closes on {session.character_name}!",
            "boss": f"  {spawned[0].full_name.capitalize()} strides into view, answering the guild contract!",
            "escort": f"  Highway ambushers surge out to intercept {session.character_name}'s charge!",
            "rescue": f"  Rough captors reveal themselves as you press deeper into the search area!",
        }
        await session.send_line(colorize(lines.get(bounty_type, "  Trouble finds you."), TextPresets.WARNING))
        if bounty_type in {"bandit", "escort"}:
            status = getattr(self.server, "status", None)
            if status and random.random() < 0.65:
                opener = random.choice([
                    ("webbed", 12, "  Hidden attackers spring a snaring ambush as they close in!"),
                    ("stunned", 4, "  A sudden crack from cover leaves you reeling as the attackers rush in!"),
                    ("demoralized", 14, "  The ambushers howl and surge in, rattling your confidence!"),
                ])
                status.apply(session, opener[0], duration=opener[1])
                await session.send_line(colorize(opener[2], TextPresets.WARNING))
        return True

    def _pick_adventurer_bounty(self, town_name: str, level: int, *, difficulty="normal", exclude_key=None):
        pool = self._get_adventurer_bounty_pool(town_name)
        if exclude_key:
            pool = [row for row in pool if str(row.get("key") or "") != str(exclude_key)]
        if not pool:
            return None
        level = max(1, int(level or 1))
        exact = [row for row in pool if int(row.get("min_level") or 1) <= level <= int(row.get("max_level") or 100)]
        pool = exact or pool

        def _distance(row):
            low = int(row.get("min_level") or 1)
            high = int(row.get("max_level") or 100)
            if level < low:
                return low - level
            if level > high:
                return level - high
            return 0

        def _midpoint(row):
            return (int(row.get("min_level") or 1) + int(row.get("max_level") or 100)) / 2.0

        diff_l = str(difficulty or "normal").strip().lower()
        ranked = sorted(pool, key=lambda row: (_distance(row), abs(_midpoint(row) - level)))
        if not ranked:
            return None
        if diff_l == "easier":
            return sorted(ranked, key=lambda row: (_distance(row), _midpoint(row), int(row.get("target_count") or 1)))[0]
        if diff_l == "harder":
            return sorted(
                ranked,
                key=lambda row: (_distance(row), -_midpoint(row), -int(row.get("reward_points") or 0), -int(row.get("target_count") or 1)),
            )[0]
        return random.choice(ranked[: min(3, len(ranked))])

    @classmethod
    def _format_adventurer_bounty(cls, bounty_row):
        if not bounty_row:
            return "No active bounty."
        data = cls._load_bounty_data(bounty_row)
        bounty_type = str(bounty_row.get("bounty_type") or data.get("type") or "cull").lower()
        target = bounty_row.get("target_display_name") or bounty_row.get("target") or "target"
        cur = int(bounty_row.get("current_count") or 0)
        goal = int(bounty_row.get("target_count") or 0)
        area = str(data.get("area") or bounty_row.get("town_name") or "").strip()
        status = str(bounty_row.get("status") or "active").lower()
        ready = "  It is ready to turn in." if status == "completed" else ""
        area_text = f" in {area}" if area else ""
        if bounty_type == "cull":
            return f"Contract: defeat {goal} {target}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "gem":
            return f"Contract: recover and sell {goal} gem{'s' if goal != 1 else ''}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "skin":
            return f"Contract: bring in {goal} skin{'s' if goal != 1 else ''}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "forage":
            return f"Contract: forage {goal} herb{'s' if goal != 1 else ''}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "heirloom":
            return f"Contract: search for {target}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "bandit":
            return f"Contract: break up {goal} bandit{'s' if goal != 1 else ''} by defeating {target}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "boss":
            return f"Contract: defeat the named threat {target}{area_text}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "escort":
            dest = str(data.get("destination_name") or target).strip() or target
            phase = str(data.get("phase") or "assigned").lower()
            if phase in {"assigned", "outbound"}:
                return f"Contract: carry the guild packet to {dest}{area_text}, then report back.  Progress: {cur}/{goal}.{ready}"
            return f"Contract: return to the taskmaster and report after reaching {dest}.  Progress: {cur}/{goal}.{ready}"
        if bounty_type == "rescue":
            phase = str(data.get("phase") or "assigned").lower()
            if phase in {"assigned", "search"}:
                return f"Contract: locate {target}{area_text}, then return to the taskmaster.  Progress: {cur}/{goal}.{ready}"
            return f"Contract: return to the taskmaster with news of {target}.  Progress: {cur}/{goal}.{ready}"
        return f"Contract: complete {goal} task step{'s' if goal != 1 else ''} for {target}{area_text}.  Progress: {cur}/{goal}.{ready}"

    def ensure_adventurer_registration(self, character_id: int, town_name: str):
        db = getattr(self.server, "db", None)
        if not db or not character_id:
            return None
        profile = db.ensure_character_adventurer_guild(character_id, town_name=town_name)
        if not profile:
            return None
        points = int(profile.get("rank_points") or 0)
        rank = self._adventurer_rank_entry(points)
        return db.update_character_adventurer_guild(
            character_id,
            town_name=town_name,
            rank_level=rank["rank"],
            rank_title=rank["title"],
            rank_points=points,
            lifetime_bounties=int(profile.get("lifetime_bounties") or 0),
            difficulty_preference=str(profile.get("difficulty_preference") or "normal"),
            vouchers=int(profile.get("vouchers") or 0),
            last_checkin_at=profile.get("last_checkin_at"),
            next_checkin_at=profile.get("next_checkin_at"),
        )

    def get_adventurer_status_text(self, session):
        profile = self._get_adventurer_profile(getattr(session, "character_id", None))
        if not profile:
            return "You are not yet registered with the Adventurer's Guild."
        active = self.get_character_bounty(session.character_id)
        rank_title = profile.get("rank_title") or "Associate"
        points = int(profile.get("rank_points") or 0)
        lifetime = int(profile.get("lifetime_bounties") or 0)
        vouchers = int(profile.get("vouchers") or 0)
        diff = str(profile.get("difficulty_preference") or "normal").capitalize()
        msg = (
            f"Rank: {rank_title}.  Guild points: {points}.  Completed contracts: {lifetime}.  "
            f"Vouchers: {vouchers}.  Difficulty preference: {diff}."
        )
        if active:
            msg += "  " + self._format_adventurer_bounty(active)
        return msg

    async def assign_adventurer_bounty(self, session, npc=None, *, exclude_key=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session, require_taskmaster=True)
        if not authority:
            return False, "You need to speak with a taskmaster for that.", None
        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        if not profile:
            return False, "The Adventurer's Guild ledger is unavailable right now.", None
        current = self.get_character_bounty(session.character_id)
        if current:
            status = str(current.get("status") or "active").lower()
            if status == "completed":
                return False, "You already have a finished contract waiting to be turned in.", current
            return False, "You already have an active bounty on the books.", current
        bounty = self._pick_adventurer_bounty(
            authority.get("town_name") or "",
            getattr(session, "level", 1),
            difficulty=profile.get("difficulty_preference") or "normal",
            exclude_key=exclude_key,
        )
        if not bounty:
            return False, "I do not have any contracts suited to you right now.", None
        row = self.server.db.assign_character_bounty(
            session.character_id,
            bounty,
            town_name=authority.get("town_name") or "",
            taskmaster_template_id=authority.get("template_id") or "",
            taskmaster_room_id=int(authority.get("room_id") or 0),
            bounty_data=self._build_bounty_data(bounty),
        )
        if not row:
            return False, "The guild contract board refuses to issue that bounty right now.", None
        await self._prime_bounty_runtime(session, row)
        return True, None, row

    async def _prime_bounty_runtime(self, session, active):
        if not active:
            return
        data = self._load_bounty_data(active)
        bounty_type = str(active.get("bounty_type") or data.get("type") or "").lower()
        room = getattr(session, "current_room", None)
        if not room:
            return
        if bounty_type == "escort" and not int(data.get("escort_npc_id") or 0):
            name = data.get("escort_npc_name") or "a nervous guild courier"
            desc = data.get("escort_npc_description") or "The traveler looks uneasy but determined to reach the destination alive."
            npc = self._spawn_temp_bounty_npc(active, data, "escort", name=name, description=desc, room_id=room.id)
            if npc:
                await session.send_line(colorize(f"  {npc.display_name} falls in beside you under guild protection.", TextPresets.SYSTEM))
                self._save_bounty_data(active, data)

    async def _record_adventurer_bounty_progress(self, session, active, *, increment=1, complete_text=None):
        updated = self.server.db.record_character_bounty_progress(int(active["id"]), increment=increment)
        if not updated:
            return None
        cur = int(updated.get("current_count") or 0)
        goal = int(updated.get("target_count") or 0)
        if str(updated.get("status") or "").lower() == "completed":
            await session.send_line(
                colorize(
                    complete_text or f"  Bounty complete: {updated.get('target_display_name') or updated.get('target')}.  Return to the taskmaster.",
                    TextPresets.COMBAT_HIT,
                )
            )
        else:
            await session.send_line(colorize(f"  Bounty progress: {cur}/{goal}.", TextPresets.SYSTEM))
        return updated

    def _item_matches_bounty(self, active, item, *, expected_type=None):
        if not active or not item:
            return False
        data = self._load_bounty_data(active)
        bounty_type = str(active.get("bounty_type") or data.get("type") or "").lower()
        if expected_type and bounty_type != expected_type:
            return False
        item_type = str(item.get("item_type") or "").lower()
        short_name = str(item.get("short_name") or item.get("name") or "").strip().lower()
        noun = str(item.get("noun") or "").strip().lower()
        target_item_type = str(data.get("target_item_type") or "").lower()
        target_short_names = [str(x).strip().lower() for x in data.get("target_short_names") or []]
        target_nouns = [str(x).strip().lower() for x in data.get("target_nouns") or []]
        if target_item_type and item_type != target_item_type:
            return False
        if target_short_names and short_name not in target_short_names:
            return False
        if target_nouns and noun not in target_nouns:
            return False
        return True

    async def record_bounty_kill(self, session, creature):
        if not getattr(session, "character_id", None) or not creature:
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        bounty_type = str(active.get("bounty_type") or "").lower()
        data = self._load_bounty_data(active)
        active_ids = self._alive_creature_ids(data.get("active_creature_ids") or [])
        if int(getattr(creature, "id", 0) or 0) in active_ids:
            active_ids = [cid for cid in active_ids if cid != int(getattr(creature, "id", 0) or 0)]
            data["active_creature_ids"] = active_ids
            self._save_bounty_data(active, data)
            if bounty_type == "rescue" and not active_ids and str(data.get("phase") or "").lower() in {"assigned", "search"}:
                room = getattr(session, "current_room", None)
                if room and not int(data.get("rescue_npc_id") or 0):
                    name = data.get("rescue_npc_name") or active.get("target_display_name") or active.get("target") or "a shaken survivor"
                    desc = data.get("rescue_npc_description") or "The missing traveler looks exhausted, but still capable of making the trip back with an escort."
                    npc = self._spawn_temp_bounty_npc(active, data, "rescue", name=name, description=desc, room_id=room.id)
                    if npc:
                        data["phase"] = "return"
                        self._save_bounty_data(active, data)
                        await session.send_line(colorize(f"  You find {npc.display_name} once the area is cleared.  They cling close, ready to follow you out.", TextPresets.COMBAT_HIT))
        if bounty_type not in {"cull", "bandit", "boss"}:
            return None
        target_template = str(active.get("target_template_id") or "").strip().lower()
        creature_template = str(getattr(creature, "template_id", "") or "").strip().lower()
        if not target_template or target_template != creature_template:
            return None
        return await self._record_adventurer_bounty_progress(session, active)

    async def record_bounty_sale(self, session, shop, item, npc=None):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        bounty_type = str(active.get("bounty_type") or "").lower()
        if bounty_type not in {"gem", "skin"}:
            return None
        if not self._item_matches_bounty(active, item, expected_type=bounty_type):
            return None
        return await self._record_adventurer_bounty_progress(session, active)

    async def record_bounty_skin(self, session, item):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        if str(active.get("bounty_type") or "").lower() != "skin":
            return None
        if not self._item_matches_bounty(active, item, expected_type="skin"):
            return None
        return await self._record_adventurer_bounty_progress(session, active)

    async def record_bounty_forage(self, session, item):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        if str(active.get("bounty_type") or "").lower() != "forage":
            return None
        if not self._item_matches_bounty(active, item, expected_type="forage"):
            return None
        return await self._record_adventurer_bounty_progress(session, active)

    def _search_bounty_matches_room(self, active, room):
        if not active or not room:
            return False
        data = self._load_bounty_data(active)
        room_id = int(getattr(room, "id", 0) or 0)
        zone_name = str(getattr(room, "zone_name", "") or "").strip().lower()
        search_room_ids = {int(x) for x in data.get("search_room_ids") or []}
        search_zone_names = [str(x).strip().lower() for x in data.get("search_zone_names") or []]
        return (search_room_ids and room_id in search_room_ids) or (search_zone_names and zone_name in search_zone_names)

    async def maybe_complete_search_bounty(self, session):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        if str(active.get("bounty_type") or "").lower() != "heirloom":
            return None
        if not self._search_bounty_matches_room(active, getattr(session, "current_room", None)):
            return None
        return await self._record_adventurer_bounty_progress(
            session,
            active,
            complete_text=f"  You uncover {active.get('target_display_name') or active.get('target')}.  Return to the taskmaster.",
        )

    async def maybe_complete_travel_bounty(self, session):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        bounty_type = str(active.get("bounty_type") or "").lower()
        if bounty_type not in {"escort", "rescue"}:
            return None

        room = getattr(session, "current_room", None)
        if not room:
            return None

        data = self._load_bounty_data(active)
        room_id = int(getattr(room, "id", 0) or 0)
        report_room_id = int(data.get("report_room_id") or active.get("taskmaster_room_id") or 0)
        phase = str(data.get("phase") or ("outbound" if bounty_type == "escort" else "search")).lower()

        if bounty_type == "escort":
            destination_room_id = int(data.get("destination_room_id") or 0)
            if phase in {"assigned", "outbound"} and destination_room_id and room_id == destination_room_id:
                if int(data.get("escort_npc_id") or 0):
                    self._despawn_temp_npc(data, "escort")
                data["phase"] = "return"
                self._save_bounty_data(active, data)
                return await self._record_adventurer_bounty_progress(
                    session,
                    active,
                    complete_text=f"  Your escorted charge reaches {data.get('destination_name') or 'the destination'} safely.  Return to the taskmaster for payment.",
                )
            if phase == "return" and report_room_id and room_id == report_room_id:
                return await self._record_adventurer_bounty_progress(
                    session,
                    active,
                    complete_text="  Escort report complete.  Your contract is ready to turn in.",
                )
            return None

        if phase in {"assigned", "search"} and int(data.get("rescue_npc_id") or 0):
            data["phase"] = "return"
            self._save_bounty_data(active, data)
            return await self._record_adventurer_bounty_progress(
                session,
                active,
                complete_text=f"  You locate {active.get('target_display_name') or active.get('target')} and lead them out.  Return to the taskmaster.",
            )
        if phase == "return" and report_room_id and room_id == report_room_id:
            if int(data.get("rescue_npc_id") or 0):
                self._despawn_temp_npc(data, "rescue")
                self._save_bounty_data(active, data)
            return await self._record_adventurer_bounty_progress(
                session,
                active,
                complete_text="  Rescue report complete.  Your contract is ready to turn in.",
            )
        return None

    async def on_character_enter_room(self, session, *, from_room=None, to_room=None):
        if not getattr(session, "character_id", None):
            return None
        active = self.get_character_bounty(session.character_id)
        if not active or str(active.get("status") or "").lower() not in ("active", "completed"):
            return None
        room = to_room or getattr(session, "current_room", None)
        if not room:
            return None

        data = self._load_bounty_data(active)
        bounty_type = str(active.get("bounty_type") or data.get("type") or "").lower()

        # Escort/rescue companions should actually follow the player room-to-room.
        creature_mgr = getattr(self.server, "creatures", None)
        room_hostiles = []
        if creature_mgr:
            room_hostiles = [
                c for c in creature_mgr.get_creatures_in_room(room.id)
                if getattr(c, "alive", False) and not getattr(c, "is_stunned", False)
            ]

        if bounty_type == "escort" and int(data.get("escort_npc_id") or 0):
            escort_npc = self._get_temp_npc(data, "escort")
            if escort_npc and from_room and int(getattr(escort_npc, "current_room_id", 0) or 0) == int(getattr(from_room, "id", 0) or 0):
                if room_hostiles:
                    await session.send_line(colorize("  Your escorted charge refuses to enter while hostile creatures still hold the room.", TextPresets.WARNING))
                else:
                    self._move_temp_npc(data, "escort", room.id)
        if bounty_type == "rescue" and int(data.get("rescue_npc_id") or 0):
            rescue_npc = self._get_temp_npc(data, "rescue")
            if rescue_npc and from_room and int(getattr(rescue_npc, "current_room_id", 0) or 0) == int(getattr(from_room, "id", 0) or 0):
                if room_hostiles:
                    await session.send_line(colorize("  The rescued traveler hangs back, unwilling to walk into active danger.", TextPresets.WARNING))
                else:
                    self._move_temp_npc(data, "rescue", room.id)

        if bounty_type in {"bandit", "boss", "escort", "rescue"}:
            await self._maybe_spawn_field_encounter(session, active, data)

        self._save_bounty_data(active, data)

        if bounty_type == "heirloom":
            return await self.maybe_complete_search_bounty(session)
        if bounty_type in {"escort", "rescue"}:
            return await self.maybe_complete_travel_bounty(session)
        return None

    async def checkin_adventurer_guild(self, session, npc=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session)
        if not authority:
            return False, "You need to be at an Adventurer's Guild office to check in.", None
        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        if not profile:
            return False, "The Adventurer's Guild ledger is unavailable right now.", None
        now = datetime.now()
        next_due = profile.get("next_checkin_at")
        if isinstance(next_due, datetime) and next_due > now:
            return False, f"You have already checked in recently.  Come back after {next_due.strftime('%Y-%m-%d %H:%M')}.", profile
        vouchers = int(profile.get("vouchers") or 0) + 1
        profile = self.server.db.update_character_adventurer_guild(
            session.character_id,
            town_name=authority.get("town_name") or "",
            vouchers=vouchers,
            last_checkin_at=now,
            next_checkin_at=now + timedelta(hours=12),
        )
        return True, None, profile

    async def set_adventurer_difficulty(self, session, preference: str, npc=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session)
        if not authority:
            return False, "You need to speak with a taskmaster or clerk for that.", None
        pref = str(preference or "normal").strip().lower()
        if pref not in {"easier", "normal", "harder"}:
            return False, "Valid difficulty preferences are EASIER, NORMAL, or HARDER.", None
        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        if not profile:
            return False, "The Adventurer's Guild ledger is unavailable right now.", None
        profile = self.server.db.update_character_adventurer_guild(
            session.character_id,
            town_name=authority.get("town_name") or "",
            difficulty_preference=pref,
        )
        return True, None, profile

    async def remove_adventurer_bounty(self, session, npc=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session, require_taskmaster=True)
        if not authority:
            return False, "Only a taskmaster can remove a contract from your ledger.", None
        active = self.get_character_bounty(session.character_id)
        if not active:
            return False, "You have no active Adventurer's Guild contract.", None
        data = self._load_bounty_data(active)
        self._despawn_temp_npc(data, "escort")
        self._despawn_temp_npc(data, "rescue")
        self.server.db.close_character_bounty(int(active["id"]))
        return True, None, active

    async def swap_adventurer_bounty(self, session, npc=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session, require_taskmaster=True)
        if not authority:
            return False, "Only a taskmaster can exchange a contract.", None
        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        if not profile:
            return False, "The Adventurer's Guild ledger is unavailable right now.", None
        vouchers = int(profile.get("vouchers") or 0)
        if vouchers < 1:
            return False, "You need at least one bounty voucher to swap contracts.", None
        active = self.get_character_bounty(session.character_id)
        if not active:
            return False, "You have no active contract to swap.", None
        self.server.db.close_character_bounty(int(active["id"]))
        profile = self.server.db.update_character_adventurer_guild(session.character_id, vouchers=max(0, vouchers - 1))
        ok, error, row = await self.assign_adventurer_bounty(session, npc, exclude_key=active.get("bounty_key"))
        if not ok:
            return False, error, None
        return True, None, {"bounty": row, "profile": profile}

    async def share_adventurer_bounty(self, session, target_session, npc=None):
        authority = self._get_adventurer_authority(npc) if npc else None
        if not authority:
            npc, authority = self._get_adventurer_officer_in_room(session, require_taskmaster=True)
        if not authority:
            return False, "Only a taskmaster can add another adventurer to your contract.", None
        active = self.get_character_bounty(session.character_id)
        if not active:
            return False, "You have no active contract to share.", None
        if self.get_character_bounty(target_session.character_id):
            return False, f"{target_session.character_name} already has an active contract.", None
        self.ensure_adventurer_registration(target_session.character_id, authority.get("town_name") or "")
        row = self.server.db.clone_character_bounty(
            active,
            target_session.character_id,
            taskmaster_template_id=authority.get("template_id") or "",
            taskmaster_room_id=int(authority.get("room_id") or 0),
        )
        if not row:
            return False, "The guild ledger refuses to add them to the contract right now.", None
        return True, None, row

    async def turn_in_adventurer_bounty(self, session, npc):
        authority = self._get_adventurer_authority(npc)
        if not authority:
            return False, "This is not an Adventurer's Guild authority.", None
        active = self.get_character_bounty(session.character_id)
        if not active:
            return False, "You have no active Adventurer's Guild contract.", None
        if str(active.get("status") or "").lower() != "completed":
            return False, self._format_adventurer_bounty(active), active

        silver = int(active.get("reward_silver") or 0)
        experience = int(active.get("reward_experience") or 0)
        fame = int(active.get("reward_fame") or 0)
        points = int(active.get("reward_points") or 0)
        if silver:
            session.silver = int(getattr(session, "silver", 0) or 0) + silver
            if getattr(self.server, "db", None):
                self.server.db.save_character_resources(
                    session.character_id,
                    getattr(session, "health_current", 100),
                    getattr(session, "mana_current", 0),
                    getattr(session, "spirit_current", 10),
                    getattr(session, "stamina_current", 100),
                    session.silver,
                )
        if experience and getattr(self.server, "experience", None):
            await self.server.experience.award_xp_to_pool(
                session,
                experience,
                source="bounty",
                fame_detail_text=f"Completed bounty against {active.get('target_display_name') or active.get('target')}.",
            )
        if fame:
            try:
                from server.core.commands.player.info import award_fame
                await award_fame(
                    session,
                    self.server,
                    fame,
                    "bounty_turnin",
                    detail_text=f"Completed Adventurer's Guild bounty: {active.get('target_display_name') or active.get('target')}.",
                    quiet=True,
                )
            except Exception:
                log.exception("Failed to award explicit bounty fame")

        profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
        current_points = int((profile or {}).get("rank_points") or 0)
        current_rank = int((profile or {}).get("rank_level") or 1)
        vouchers = int((profile or {}).get("vouchers") or 0)
        lifetime = int((profile or {}).get("lifetime_bounties") or 0) + 1
        new_points = current_points + points
        rank = self._adventurer_rank_entry(new_points)
        voucher_gain = 1 if lifetime % 5 == 0 else 0
        if rank["rank"] > current_rank:
            voucher_gain += 1
        updated_profile = self.server.db.update_character_adventurer_guild(
            session.character_id,
            town_name=authority.get("town_name") or "",
            rank_level=rank["rank"],
            rank_title=rank["title"],
            rank_points=new_points,
            lifetime_bounties=lifetime,
            vouchers=vouchers + voucher_gain,
        )
        self.server.db.close_character_bounty(int(active["id"]))
        return True, None, {
            "silver": silver,
            "experience": experience,
            "fame": fame,
            "points": points,
            "voucher_gain": voucher_gain,
            "profile": updated_profile or profile,
            "target": active.get("target_display_name") or active.get("target") or "target",
        }

    async def handle_adventurer_guild_topic(self, session, npc, topic: str):
        authority = self._get_adventurer_authority(npc)
        if not authority or not getattr(session, "character_id", None):
            return False
        topic_l = (topic or "").strip().lower()
        if topic_l in ("", "guild", "hello", "work", "assignment", "assignments", "contract", "contracts", "bounties"):
            topic_l = "bounty"
        if topic_l in ("register", "registration", "join", "ledger"):
            profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
            if not profile:
                await session.send_line(npc_speech(npc.display_name, 'says, "The registration ledger is unavailable right now."'))
                return True
            await session.send_line(npc_speech(npc.display_name, f'says, "You are now registered with the Adventurer\'s Guild at {authority.get("town_name")}.  Current rank: {profile.get("rank_title") or "Associate"}."'))
            return True
        if topic_l in ("checkin", "check-in"):
            ok, error, profile = await self.checkin_adventurer_guild(session, npc)
            if error:
                line = error
            else:
                line = f"Check-in recorded.  You now have {int(profile.get('vouchers') or 0)} vouchers on your record."
            await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
            return True
        if topic_l in ("voucher", "vouchers"):
            profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
            count = int((profile or {}).get("vouchers") or 0)
            await session.send_line(npc_speech(npc.display_name, f'says, "You currently have {count} bounty voucher{"s" if count != 1 else ""}.  Spend one to swap an active contract."'))
            return True
        if topic_l in ("easier", "harder", "normal"):
            ok, error, profile = await self.set_adventurer_difficulty(session, topic_l, npc)
            if error:
                line = error
            else:
                line = f"Very well.  Your future contracts will lean {str(profile.get('difficulty_preference') or 'normal')}."
            await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
            return True
        if topic_l in ("remove", "removal", "abandon", "cancel"):
            ok, error, active = await self.remove_adventurer_bounty(session, npc)
            if error:
                line = error
            else:
                line = f"The contract on {active.get('target_display_name') or active.get('target')} has been removed from your ledger."
            await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
            return True
        if topic_l in ("rank", "status"):
            await session.send_line(npc_speech(npc.display_name, f'says, "{self.get_adventurer_status_text(session)}"'))
            return True
        if topic_l in ("swap", "trade", "exchange"):
            ok, error, summary = await self.swap_adventurer_bounty(session, npc)
            if error:
                line = error
            else:
                line = f"Done.  One voucher has been spent.  {self._format_adventurer_bounty(summary.get('bounty'))}"
            await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
            return True
        if topic_l in ("share", "add", "partner"):
            await session.send_line(npc_speech(npc.display_name, 'says, "Use BOUNTY ADD <person> while you are both standing here if you want to share your current contract."'))
            return True
        if topic_l in ("bounty", "work", "assignment", "contract", "contracts", "turnin", "turn-in", "complete"):
            profile = self.ensure_adventurer_registration(session.character_id, authority.get("town_name") or "")
            if not profile:
                await session.send_line(npc_speech(npc.display_name, 'says, "The contract ledger is unavailable right now."'))
                return True
            active = self.get_character_bounty(session.character_id)
            if active:
                if str(active.get("status") or "").lower() == "completed":
                    ok, error, summary = await self.turn_in_adventurer_bounty(session, npc)
                    if not ok:
                        await session.send_line(npc_speech(npc.display_name, f'says, "{error}"'))
                        return True
                    profile = summary.get("profile") or profile
                    await session.send_line(npc_speech(npc.display_name, f'says, "Good work.  The contract on {summary.get("target")} is closed.  Rank: {profile.get("rank_title") or "Associate"}."'))
                    if int(summary.get("silver") or 0):
                        await session.send_line(colorize(f"  Bounty reward: {int(summary['silver'])} silver.", TextPresets.ITEM_NAME))
                    if int(summary.get("points") or 0):
                        await session.send_line(colorize(f"  Adventurer's Guild points: +{int(summary['points'])}.", TextPresets.SYSTEM))
                    if int(summary.get("voucher_gain") or 0):
                        await session.send_line(colorize(f"  Adventurer's Guild vouchers: +{int(summary['voucher_gain'])}.", TextPresets.SYSTEM))
                    return True
                await session.send_line(npc_speech(npc.display_name, f'says, "{self._format_adventurer_bounty(active)}"'))
                return True
            ok, error, row = await self.assign_adventurer_bounty(session, npc)
            if not ok:
                line = error or (self._format_adventurer_bounty(row) if row else "I have nothing for you.")
                await session.send_line(npc_speech(npc.display_name, f'says, "{line}"'))
                return True
            await session.send_line(npc_speech(npc.display_name, f'says, "Very well.  {self._format_adventurer_bounty(row)}  Report back when it is done."'))
            return True
        return False

    def handles_interaction(self, cmd: str) -> bool:
        return (cmd or "").lower() in self._ENTRY_VERBS

    def _get_conn(self):
        db = getattr(self.server, "db", None)
        if not db or not getattr(db, "_pool", None):
            return None
        return db._get_conn()

    def _save_quest_data(self, character_id: int, quest_id: int, quest_data: dict | None):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_quests
                SET quest_data = %s
                WHERE character_id = %s AND quest_id = %s
                """,
                (json.dumps(quest_data or {}), character_id, quest_id),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine._save_quest_data failed for %s/%s: %s", character_id, quest_id, e)
            return False
        finally:
            conn.close()

    @staticmethod
    def _normalize_quiz_answer(text: str) -> str:
        raw = (text or "").strip().lower()
        if not raw:
            return ""
        chars = []
        prev_sep = False
        for ch in raw:
            if ch.isalnum():
                chars.append(ch)
                prev_sep = False
            elif not prev_sep:
                chars.append(" ")
                prev_sep = True
        return "".join(chars).strip()

    def _get_room_quiz_quest(self, session):
        room = getattr(session, "current_room", None)
        if not room or not getattr(session, "character_id", None):
            return None, None, None

        for active in self.get_active_quests(session.character_id, general_only=True):
            stage = active.get("current_stage") or {}
            questions = stage.get("quiz_questions") or []
            if not questions:
                continue
            if not self._quest_matches_room(active, room):
                continue
            npc = self._find_local_quest_npc(session, active, phase="start")
            if (active.get("start_npc_template_ids") or []) and not npc:
                continue
            return active, questions, npc
        return None, None, None

    async def _send_quiz_prompt(self, session, active, questions, npc, *, prefix: str | None = None):
        if not questions:
            return
        quest_data = dict(active.get("quest_data") or {})
        index = max(0, int(quest_data.get("quiz_index") or 0))
        if index >= len(questions):
            index = len(questions) - 1
        prompt = str((questions[index] or {}).get("question") or "").strip()
        if not prompt:
            return

        message = prompt if not prefix else f"{prefix} {prompt}"
        if npc:
            await session.send_line(npc_speech(npc.display_name, f'says, "{message}"'))
        else:
            await session.send_line(message)

    async def answer_quiz(self, session, raw_answer: str):
        active, questions, npc = self._get_room_quiz_quest(session)
        if not active or not questions:
            await session.send_line("You are not currently being quizzed about anything here.")
            return

        current_stage = active.get("current_stage") or {}
        quest_data = dict(active.get("quest_data") or {})
        index = max(0, int(quest_data.get("quiz_index") or 0))
        if index >= len(questions):
            index = len(questions) - 1
            quest_data["quiz_index"] = index

        if not (raw_answer or "").strip():
            await self._send_quiz_prompt(session, active, questions, npc)
            return

        question = questions[index] or {}
        expected = question.get("answers") or question.get("accepted_answers") or []
        if isinstance(expected, str):
            expected = [expected]
        norm_answer = self._normalize_quiz_answer(raw_answer)
        accepted = {
            self._normalize_quiz_answer(str(option))
            for option in expected
            if self._normalize_quiz_answer(str(option))
        }

        if norm_answer not in accepted:
            wrong = str(question.get("wrong") or "No.  Think it through and try again.")
            if npc:
                await session.send_line(npc_speech(npc.display_name, f'says, "{wrong}"'))
            else:
                await session.send_line(wrong)
            await self._send_quiz_prompt(session, active, questions, npc)
            return

        right = str(question.get("right") or "That's right.")
        if npc:
            await session.send_line(npc_speech(npc.display_name, f'says, "{right}"'))
        else:
            await session.send_line(right)

        index += 1
        quest_data["quiz_index"] = index
        self._save_quest_data(session.character_id, int(active["id"]), quest_data)

        if index >= len(questions):
            event_name = (current_stage.get("objective_event") or "").strip()
            if event_name:
                await self.record_event(session, event_name)
            return

        active = self.get_quest_journal(session.character_id, quest_key=active.get("key_name"))[0]
        await self._send_quiz_prompt(session, active, questions, npc, prefix=str(question.get("next_prefix") or "Next question."))

    async def _apply_quest_completion_rewards(self, session, active):
        quest_meta = active.get("quest_meta") or {}
        rewards = quest_meta.get("rewards") or {}
        if not isinstance(rewards, dict):
            return

        silver = max(0, int(rewards.get("silver") or 0))
        experience = max(0, int(rewards.get("experience") or 0))
        items = rewards.get("items") or []
        if isinstance(items, (str, int)):
            items = [items]

        if silver:
            session.silver = int(getattr(session, "silver", 0) or 0) + silver
            if getattr(self.server, "db", None) and getattr(session, "character_id", None):
                self.server.db.save_character_resources(
                    session.character_id,
                    getattr(session, "health_current", 100),
                    getattr(session, "mana_current", 0),
                    getattr(session, "spirit_current", 10),
                    getattr(session, "stamina_current", 100),
                    session.silver,
                )
            await session.send_line(colorize(f"  Quest reward: {silver} silver.", TextPresets.ITEM_NAME))

        if experience and getattr(self.server, "experience", None):
            await self.server.experience.award_xp_to_pool(
                session,
                experience,
                source="quest",
                fame_detail_text=f"Completed quest: {active.get('title') or active.get('key_name') or 'unknown quest'}.",
            )

        if items and getattr(self.server, "db", None) and getattr(session, "character_id", None):
            for raw_item in items:
                item_id = self._resolve_item_reference(raw_item)
                if not item_id:
                    continue
                inv_id = self.server.db.add_item_to_inventory(session.character_id, item_id, slot=None)
                if not inv_id:
                    continue
                await session.send_line(colorize(f"  Quest reward: item #{item_id}.", TextPresets.ITEM_NAME))

    def _resolve_item_reference(self, raw_item):
        if raw_item is None or not getattr(self.server, "db", None):
            return None
        try:
            return int(raw_item)
        except Exception:
            pass

        short_name = None
        noun = None
        if isinstance(raw_item, str):
            short_name = raw_item.strip()
        elif isinstance(raw_item, dict):
            short_name = str(raw_item.get("short_name") or raw_item.get("name") or "").strip() or None
            noun = str(raw_item.get("noun") or "").strip() or None
        if not short_name:
            return None

        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            if noun:
                cur.execute(
                    "SELECT id FROM items WHERE short_name = %s AND (%s = '' OR noun = %s) LIMIT 1",
                    (short_name, noun, noun),
                )
            else:
                cur.execute(
                    "SELECT id FROM items WHERE short_name = %s LIMIT 1",
                    (short_name,),
                )
            row = cur.fetchone()
            return int(row[0]) if row else None
        except Exception as e:
            log.error("GuildEngine._resolve_item_reference failed for %s: %s", raw_item, e)
            return None
        finally:
            conn.close()

    async def prepare_started_quest(self, session, quest, *, actor_npc=None):
        if not quest or not getattr(session, "character_id", None):
            return True, None

        quest_meta = quest.get("quest_meta") or {}
        start_items = quest_meta.get("start_items") or []
        if isinstance(start_items, (str, int, dict)):
            start_items = [start_items]

        if start_items:
            from server.core.commands.player.inventory import auto_stow_item

            for raw_item in start_items:
                item_id = self._resolve_item_reference(raw_item)
                if not item_id:
                    return False, "That quest could not prepare its handoff materials."

                conn = self._get_conn()
                if not conn:
                    return False, "The quest ledger is unavailable right now."
                try:
                    cur = conn.cursor(dictionary=True)
                    cur.execute(
                        """
                        SELECT id, name, short_name, noun, article, item_type, weight, value, description
                        FROM items
                        WHERE id = %s
                        LIMIT 1
                        """,
                        (item_id,),
                    )
                    item_row = cur.fetchone()
                except Exception as e:
                    log.error("GuildEngine.prepare_started_quest failed loading item %s: %s", item_id, e)
                    item_row = None
                finally:
                    conn.close()

                if not item_row:
                    return False, "That quest could not find the materials it was meant to issue."

                success, location, fail_msg = auto_stow_item(session, self.server, dict(item_row))
                if not success:
                    return False, fail_msg or "You need a free hand or some carrying room before taking that work."
                await session.send_line(colorize(f"  You receive {item_row.get('name')}.  It is placed in your {location}.", TextPresets.ITEM_NAME))

        start_text = str(quest_meta.get("start_message") or "").strip()
        if start_text:
            if actor_npc:
                await session.send_line(npc_speech(actor_npc.display_name, f'says, "{start_text}"'))
            else:
                await session.send_line(start_text)

        current_stage = quest.get("current_stage") or {}
        questions = current_stage.get("quiz_questions") or []
        if questions:
            await session.send_line(colorize("  Use ANSWER <response> to reply.", TextPresets.SYSTEM))
            npc = actor_npc or self._find_local_quest_npc(session, quest, phase="start")
            await self._send_quiz_prompt(session, quest, questions, npc)
        return True, None

    def _get_access_point_for_room(self, room_id: int, guild_id: str | None = None):
        rewards_pending = False
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT *
                FROM guild_access_points
                WHERE is_active = 1 AND (%s IS NULL OR guild_id = %s)
                  AND (entry_room_id = %s OR target_room_id = %s)
                ORDER BY id
                LIMIT 1
            """
            cur.execute(sql, (guild_id, guild_id, room_id, room_id))
            return cur.fetchone()
        finally:
            conn.close()

    def get_primary_access_point(self, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM guild_access_points
                WHERE guild_id = %s AND is_active = 1
                ORDER BY id
                LIMIT 1
                """,
                (guild_id,),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def get_access_point_for_city(self, guild_id: str, city_name: str):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM guild_access_points
                WHERE guild_id = %s AND city_name = %s AND is_active = 1
                ORDER BY id
                LIMIT 1
                """,
                (guild_id, city_name),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def get_access_point_for_entry_room(self, guild_id: str, room_id: int):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM guild_access_points
                WHERE guild_id = %s AND entry_room_id = %s AND is_active = 1
                ORDER BY id
                LIMIT 1
                """,
                (guild_id, room_id),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def get_access_row(self, character_id: int, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM character_guild_access
                WHERE character_id = %s AND guild_id = %s
                LIMIT 1
                """,
                (character_id, guild_id),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def ensure_access_row(self, character_id: int, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_access (character_id, guild_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP
                """,
                (character_id, guild_id),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine.ensure_access_row failed for %s/%s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def issue_invite(
        self,
        character_id: int,
        guild_id: str,
        *,
        actor_character_id=None,
        actor_template_id=None,
        password_known=False,
        notes=None,
    ):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_access (
                    character_id, guild_id, is_invited, password_known, invited_at,
                    invited_by_template_id, invited_by_character_id, password_shared_at,
                    sequence_step, sequence_room_id, sequence_started_at
                ) VALUES (%s, %s, 1, %s, NOW(), %s, %s, %s, 0, NULL, NULL)
                ON DUPLICATE KEY UPDATE
                    is_invited = 1,
                    password_known = GREATEST(password_known, VALUES(password_known)),
                    invited_at = NOW(),
                    invited_by_template_id = COALESCE(VALUES(invited_by_template_id), invited_by_template_id),
                    invited_by_character_id = COALESCE(VALUES(invited_by_character_id), invited_by_character_id),
                    password_shared_at = COALESCE(VALUES(password_shared_at), password_shared_at),
                    sequence_step = 0,
                    sequence_room_id = NULL,
                    sequence_started_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    character_id,
                    guild_id,
                    1 if password_known else 0,
                    actor_template_id,
                    actor_character_id,
                    datetime.utcnow() if password_known else None,
                ),
            )
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'invite', 0, %s, %s)
                """,
                (character_id, guild_id, actor_template_id, notes or "Guild invitation recorded."),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine.issue_invite failed for %s/%s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def issue_remote_invite(self, character_id: int, guild_id: str, *, actor_template_id=None, notes=None):
        return self.issue_invite(
            character_id,
            guild_id,
            actor_template_id=actor_template_id,
            password_known=True,
            notes=notes or "Remote guild invitation recorded.",
        )

    def grant_member_access(self, character_id: int, guild_id: str, *, actor_template_id=None):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_access (
                    character_id, guild_id, is_invited, password_known, invited_at,
                    invited_by_template_id, sequence_step, sequence_room_id, sequence_started_at
                ) VALUES (%s, %s, 1, 1, NOW(), %s, 0, NULL, NULL)
                ON DUPLICATE KEY UPDATE
                    is_invited = 1,
                    password_known = 1,
                    invited_by_template_id = COALESCE(VALUES(invited_by_template_id), invited_by_template_id),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (character_id, guild_id, actor_template_id),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine.grant_member_access failed for %s/%s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def share_password(self, character_id: int, guild_id: str, *, actor_character_id=None, actor_template_id=None):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_access (
                    character_id, guild_id, is_invited, password_known, invited_at,
                    invited_by_template_id, invited_by_character_id, password_shared_at
                ) VALUES (%s, %s, 1, 1, NOW(), %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    is_invited = 1,
                    password_known = 1,
                    invited_by_template_id = COALESCE(VALUES(invited_by_template_id), invited_by_template_id),
                    invited_by_character_id = COALESCE(VALUES(invited_by_character_id), invited_by_character_id),
                    password_shared_at = NOW(),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (character_id, guild_id, actor_template_id, actor_character_id),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine.share_password failed for %s/%s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def _set_sequence_state(self, character_id: int, guild_id: str, *, step: int, room_id: int | None, started_at=None):
        conn = self._get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_access (
                    character_id, guild_id, sequence_step, sequence_room_id, sequence_started_at
                ) VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sequence_step = VALUES(sequence_step),
                    sequence_room_id = VALUES(sequence_room_id),
                    sequence_started_at = VALUES(sequence_started_at),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (character_id, guild_id, step, room_id, started_at),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("GuildEngine._set_sequence_state failed for %s/%s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def _parse_sequence(self, access_point) -> list[str]:
        raw = (access_point.get("pass_sequence") or "").strip()
        return [part.strip().lower() for part in raw.split(",") if part.strip()]

    def get_password_text(self, guild_id: str) -> str | None:
        access_point = self.get_primary_access_point(guild_id)
        if not access_point:
            return None
        primer = (access_point.get("primer_verb") or "lean").upper()
        seq = [part.upper() for part in self._parse_sequence(access_point)]
        if not seq:
            return primer
        return f"{primer}, then " + ", ".join(seq)

    def _get_rogue_profession_guild(self, session):
        db = getattr(self.server, "db", None)
        profession_id = int(getattr(session, "profession_id", 0) or 0)
        if not db or not profession_id:
            return None
        guild_def = db.get_guild_definition_for_profession(profession_id) or {}
        if str(guild_def.get("guild_id") or "").lower() != self._ROGUE_GUILD_ID:
            return None
        return guild_def

    def _get_localized_rogue_access_point(self, session):
        room = getattr(session, "current_room", None)
        zone = getattr(room, "zone", None)
        city_name = str(getattr(zone, "name", "") or "").strip()
        if city_name:
            point = self.get_access_point_for_city(self._ROGUE_GUILD_ID, city_name)
            if point:
                return point
        return self.get_primary_access_point(self._ROGUE_GUILD_ID)

    async def _send_rogue_invite_notice(self, session, access_point=None):
        access_point = access_point or self._get_localized_rogue_access_point(session) or {}
        city_name = str(access_point.get("city_name") or "").strip()
        password_text = self.get_password_text(self._ROGUE_GUILD_ID) or "LEAN, then PULL, PULL, SLAP, RUB, RUB, PUSH, TURN"
        city_hint = f" in {city_name}" if city_name else ""

        await session.send_line("")
        await session.send_line(
            colorize(
                "A quick-moving courier slips through the crowd long enough to press a folded note into your hand before disappearing again.",
                TextPresets.SYSTEM,
            )
        )
        await session.send_line(colorize("Unfolding it, you read:", TextPresets.SYSTEM))
        await session.send_line(
            colorize(
                f'  "Your work has drawn the attention of the Rogue Guild.  When you are ready, seek the hidden entry{city_hint}, LEAN close, and use the sequence {password_text}."',
                TextPresets.ITEM_NAME,
            )
        )
        await session.send_line(colorize("The note bears no signature.", TextPresets.SYSTEM))
        await session.send_line("")

    async def maybe_issue_rogue_auto_invite(self, session, *, source: str = "system"):
        if not getattr(session, "character_id", None):
            return False

        guild_def = self._get_rogue_profession_guild(session)
        if not guild_def:
            return False

        join_level = int(guild_def.get("join_level") or 15)
        if int(getattr(session, "level", 0) or 0) < join_level:
            return False

        membership = self.server.db.get_character_guild_membership(session.character_id) if getattr(self.server, "db", None) else None
        if membership and str(membership.get("guild_id") or "").lower() == self._ROGUE_GUILD_ID:
            return False

        access = self.get_access_row(session.character_id, self._ROGUE_GUILD_ID) or {}
        if access.get("is_invited"):
            return False

        access_point = self._get_localized_rogue_access_point(session)
        notes = f"Automated rogue invitation issued at level {getattr(session, 'level', 0)} ({source})."
        if not self.issue_remote_invite(
            session.character_id,
            self._ROGUE_GUILD_ID,
            actor_template_id=(access_point or {}).get("npc_template_id"),
            notes=notes,
        ):
            return False

        await self._send_rogue_invite_notice(session, access_point)
        return True

    def normalize_skill_name(self, guild_id: str, raw_skill: str):
        query = (raw_skill or "").strip().lower()
        if not query:
            return None
        defs = self.server.db.get_guild_skill_definitions(guild_id) if getattr(self.server, "db", None) else []
        for row in defs:
            skill = row.get("skill_name", "")
            display = row.get("display_name", "")
            if query == skill.lower() or query == display.lower():
                return skill
        for row in defs:
            skill = row.get("skill_name", "")
            display = row.get("display_name", "")
            if query in skill.lower() or query in display.lower():
                return skill
        return None

    def get_skill_def_map(self, guild_id: str):
        defs = self.server.db.get_guild_skill_definitions(guild_id) if getattr(self.server, "db", None) else []
        return {row["skill_name"]: row for row in defs}

    def _get_rank_definitions(self, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT guild_id, rank_level, rank_name, description,
                       min_total_skill_ranks, min_distinct_skills
                FROM guild_rank_definitions
                WHERE guild_id = %s
                ORDER BY rank_level ASC
                """,
                (guild_id,),
            )
            return cur.fetchall()
        finally:
            conn.close()

    def _get_active_task(self, character_id: int, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, guild_id, skill_name, task_code, task_type, task_text,
                       objective_event, target_count, progress_count, award_points,
                       repetitions_remaining, task_data, status, assigned_at, completed_at
                FROM character_guild_tasks
                WHERE character_id = %s AND guild_id = %s AND status IN ('assigned', 'ready')
                ORDER BY assigned_at DESC, id DESC
                LIMIT 1
                """,
                (character_id, guild_id),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def _load_quest_data(self, lua_script: str | None):
        if not lua_script:
            return {}
        cached = self._quest_data_cache.get(lua_script)
        if cached is not None:
            return dict(cached)
        lua = getattr(self.server, "lua", None)
        engine = getattr(lua, "engine", None) if lua else None
        if not engine or not engine.available:
            return {}
        try:
            data = engine.load_data(lua_script)
            normalized = data if isinstance(data, dict) else {}
            self._quest_data_cache[lua_script] = dict(normalized)
            return dict(normalized)
        except Exception as e:
            log.error("GuildEngine failed to load quest script %s: %s", lua_script, e)
            return {}

    @staticmethod
    def _as_list(value):
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, dict):
            ordered = []
            for key in sorted(value):
                raw = value.get(key)
                text = str(raw).strip()
                if text:
                    ordered.append(text)
            return ordered
        text = str(value).strip()
        return [text] if text else []

    @staticmethod
    def _coerce_int_set(values):
        out = set()
        for raw in values or []:
            try:
                out.add(int(raw))
            except Exception:
                continue
        return out

    def _quest_has_guild_scope(self, row) -> bool:
        if not row:
            return False
        meta = row.get("quest_meta") or {}
        if meta.get("guild_id"):
            return True
        key_name = str(row.get("key_name") or "")
        return "_" in key_name and key_name.split("_", 1)[0] in {"rogue", "warrior", "wizard", "cleric", "sorcerer", "ranger", "paladin", "bard", "monk", "empath"}

    def _is_general_quest(self, row) -> bool:
        return bool(row) and not self._quest_has_guild_scope(row)

    def _normalize_quest_row(self, row):
        if not row:
            return None
        meta = row.get("quest_meta") or {}
        start_npcs = self._as_list(
            meta.get("start_npc_template_ids")
            or meta.get("start_npcs")
            or meta.get("start_npc_template_id")
            or meta.get("start_npc")
            or meta.get("quest_giver")
        )
        turnin_npcs = self._as_list(
            meta.get("turnin_npc_template_ids")
            or meta.get("turnin_npcs")
            or meta.get("turnin_npc_template_id")
            or meta.get("turnin_npc")
            or meta.get("quest_turnin")
        )
        start_rooms = self._coerce_int_set(
            self._as_list(meta.get("start_room_ids") or meta.get("start_room_id"))
        )
        turnin_rooms = self._coerce_int_set(
            self._as_list(meta.get("turnin_room_ids") or meta.get("turnin_room_id"))
        )
        start_lich_rooms = self._coerce_int_set(
            self._as_list(meta.get("start_lich_room_ids") or meta.get("start_lich_room_id"))
        )
        turnin_lich_rooms = self._coerce_int_set(
            self._as_list(meta.get("turnin_lich_room_ids") or meta.get("turnin_lich_room_id"))
        )
        row["quest_type"] = str(meta.get("quest_type") or ("guild" if self._quest_has_guild_scope(row) else "general")).lower()
        row["start_npc_template_ids"] = start_npcs
        row["turnin_npc_template_ids"] = turnin_npcs
        row["start_topics"] = self._as_list(meta.get("start_topics") or ["quest", "work", "assignment"])
        row["turnin_topics"] = self._as_list(meta.get("turnin_topics") or ["quest", "work", "progress", "hint"])
        row["start_room_ids"] = start_rooms
        row["turnin_room_ids"] = turnin_rooms
        row["start_lich_room_ids"] = start_lich_rooms
        row["turnin_lich_room_ids"] = turnin_lich_rooms
        row["prereq_quests"] = self._as_list(meta.get("prereq_quests") or meta.get("requires_quests"))
        return row

    def _get_quest_rows(self, character_id: int, guild_id: str | None = None, key_prefix: str | None = None, quest_key: str | None = None):
        if guild_id and not key_prefix:
            key_prefix = f"{guild_id}_"
        key_pattern = f"{key_prefix}%" if key_prefix else None
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT qd.id, qd.key_name, qd.title, qd.description, qd.min_level, qd.max_level,
                       qd.is_repeatable, qd.lua_script,
                       cq.status, cq.stage, cq.progress_count, cq.target_count,
                       cq.quest_data, cq.started_at, cq.completed_at, cq.updated_at
                FROM quest_definitions qd
                LEFT JOIN character_quests cq
                  ON cq.quest_id = qd.id AND cq.character_id = %s
                WHERE (%s IS NULL OR qd.key_name LIKE %s)
                  AND (%s IS NULL OR qd.key_name = %s)
                ORDER BY qd.id ASC
                """,
                (character_id, key_pattern, key_pattern, quest_key, quest_key),
            )
            return cur.fetchall() or []
        finally:
            conn.close()

    def _hydrate_quest_row(self, row):
        if not row:
            return None
        data = self._load_quest_data(row.get("lua_script"))
        stages = data.get("stages") or []
        if isinstance(stages, dict):
            stages = [stages[k] for k in sorted(stages)]
        stage_num = int(row.get("stage") or 0)
        current_stage = stages[stage_num - 1] if stage_num > 0 and stage_num <= len(stages) else None
        quest_data = row.get("quest_data")
        if isinstance(quest_data, str) and quest_data:
            try:
                quest_data = json.loads(quest_data)
            except Exception:
                quest_data = {}
        elif quest_data is None:
            quest_data = {}
        hydrated = dict(row)
        hydrated["quest_meta"] = data
        hydrated["stages"] = stages
        hydrated["current_stage"] = current_stage
        hydrated["quest_data"] = quest_data if isinstance(quest_data, dict) else {}
        if current_stage:
            hydrated["objective"] = current_stage.get("objective") or hydrated.get("description") or hydrated.get("title")
            hydrated["hint"] = current_stage.get("hint") or ""
            hydrated["objective_event"] = current_stage.get("objective_event") or ""
            if not hydrated.get("target_count"):
                hydrated["target_count"] = int(current_stage.get("required_count") or 1)
        return self._normalize_quest_row(hydrated)

    def get_quest_journal(self, character_id: int, guild_id: str | None = None, *, key_prefix: str | None = None, quest_key: str | None = None):
        return [
            hydrated
            for hydrated in (self._hydrate_quest_row(row) for row in self._get_quest_rows(character_id, guild_id, key_prefix, quest_key))
            if hydrated
        ]

    def get_active_quest(self, character_id: int, guild_id: str | None = None, *, key_prefix: str | None = None):
        journal = self.get_quest_journal(character_id, guild_id, key_prefix=key_prefix)
        for row in journal:
            if (row.get("status") or "").lower() == "active":
                return row
        return None

    def get_active_quests(self, character_id: int, guild_id: str | None = None, *, key_prefix: str | None = None, general_only: bool = False):
        journal = self.get_quest_journal(character_id, guild_id, key_prefix=key_prefix)
        active = [row for row in journal if (row.get("status") or "").lower() == "active"]
        if general_only:
            active = [row for row in active if self._is_general_quest(row)]
        return active

    def get_general_quest_journal(self, character_id: int):
        return [row for row in self.get_quest_journal(character_id) if self._is_general_quest(row)]

    def _quest_matches_room(self, quest, room) -> bool:
        if not quest or not room:
            return False
        room_id = int(getattr(room, "id", 0) or 0)
        lich_uid = int(getattr(room, "lich_uid", 0) or 0)
        start_rooms = quest.get("start_room_ids") or set()
        start_lich_rooms = quest.get("start_lich_room_ids") or set()
        if not start_rooms and not start_lich_rooms:
            return True
        return (room_id and room_id in start_rooms) or (lich_uid and lich_uid in start_lich_rooms)

    def _quest_matches_npc(self, quest, npc, *, phase: str = "start") -> bool:
        if not quest or not npc:
            return False
        key = "turnin_npc_template_ids" if phase == "turnin" else "start_npc_template_ids"
        ids = quest.get(key) or []
        if not ids and phase == "turnin":
            ids = quest.get("start_npc_template_ids") or []
        return not ids or getattr(npc, "template_id", None) in ids

    def _find_local_quest_npc(self, session, quest, *, phase: str = "start"):
        room = getattr(session, "current_room", None)
        npc_mgr = getattr(self.server, "npcs", None)
        if not room or not npc_mgr:
            return None
        ids = quest.get("turnin_npc_template_ids" if phase == "turnin" else "start_npc_template_ids") or []
        if not ids and phase == "turnin":
            ids = quest.get("start_npc_template_ids") or []
        if not ids:
            return None
        for npc in npc_mgr.get_npcs_in_room(room.id):
            if self._quest_matches_npc(quest, npc, phase=phase):
                return npc
        return None

    def _quest_start_error(self, session, quest, actor_npc=None):
        if not quest:
            return "That quest could not be found."
        status = (quest.get("status") or "available").lower()
        if status == "active":
            return "You are already working on that quest."
        if status == "complete" and not bool(quest.get("is_repeatable")):
            return "You have already completed that quest."
        level = int(getattr(session, "level", 0) or 0)
        if level < int(quest.get("min_level") or 1):
            return "You are not yet experienced enough for that quest."
        if level > int(quest.get("max_level") or 100):
            return "That quest is no longer appropriate for your current level."
        quest_meta = quest.get("quest_meta") or {}
        required_guild = quest_meta.get("guild_id")
        if required_guild:
            membership = getattr(session, "guild_membership", None) or {}
            if membership.get("guild_id") != required_guild:
                return "You are not currently eligible to begin that guild quest."
        if quest.get("prereq_quests"):
            journal = {row.get("key_name"): row for row in self.get_quest_journal(session.character_id)}
            missing = []
            for key in quest.get("prereq_quests") or []:
                row = journal.get(key)
                if (row.get("status") or "").lower() != "complete":
                    missing.append(key)
            if missing:
                return "You are not yet ready for that quest."
        room = getattr(session, "current_room", None)
        if not self._quest_matches_room(quest, room):
            return "You must be in the proper place to begin that quest."
        required_npcs = quest.get("start_npc_template_ids") or []
        if required_npcs:
            if actor_npc and self._quest_matches_npc(quest, actor_npc, phase="start"):
                return None
            return "You must speak with the proper quest giver to begin that quest."
        start_items = quest_meta.get("start_items") or []
        if start_items:
            if getattr(session, "right_hand", None) and getattr(session, "left_hand", None):
                return "Your hands are full.  Free a hand before taking that work."
        return None

    def get_npc_startable_quests(self, session, npc):
        if not getattr(session, "character_id", None):
            return []
        offers = []
        for row in self.get_general_quest_journal(session.character_id):
            if not (row.get("start_npc_template_ids") or []):
                continue
            if not self._quest_matches_npc(row, npc, phase="start"):
                continue
            if self._quest_start_error(session, row, npc):
                continue
            offers.append(row)
        return offers

    def get_npc_related_active_quests(self, session, npc):
        if not getattr(session, "character_id", None):
            return []
        related = []
        for row in self.get_active_quests(session.character_id, general_only=True):
            if not ((row.get("start_npc_template_ids") or []) or (row.get("turnin_npc_template_ids") or [])):
                continue
            if self._quest_matches_npc(row, npc, phase="start") or self._quest_matches_npc(row, npc, phase="turnin"):
                related.append(row)
        return related

    def get_npc_quest_response(self, session, npc, topic):
        topic_l = (topic or "quest").strip().lower()
        quest_words = {"quest", "quests", "work", "assignment", "assignments", "task", "tasks", "job", "jobs", "help", "hint"}
        offers = self.get_npc_startable_quests(session, npc)
        active = self.get_npc_related_active_quests(session, npc)
        matches_specific = False
        for row in offers + active:
            key_name = str(row.get("key_name") or "").lower()
            title = str(row.get("title") or "").lower()
            if topic_l == key_name or topic_l == title:
                matches_specific = True
                break
        if topic_l not in quest_words and not matches_specific:
            return None
        if active:
            quest = active[0]
            objective = quest.get("objective") or quest.get("description") or quest.get("title", "your work")
            hint = quest.get("hint") or ""
            if hint:
                return f'You are already working on "{quest.get("title", "that quest")}".  {objective}  Hint: {hint}'
            return f'You are already working on "{quest.get("title", "that quest")}".  {objective}'
        if len(offers) == 1:
            quest = offers[0]
            return f'I may have work for you.  "{quest.get("title", "Quest")}" is available.  Use QUEST START {quest.get("key_name")} if you are ready.'
        if offers:
            titles = ", ".join(f'"{row.get("title", "Quest")}"' for row in offers[:3])
            return f'I have work available for you: {titles}.  Use QUESTS to review it or QUEST START <quest key> to begin.'
        return "I have no work to offer you right now."

    def start_quest(self, session, quest_key: str, *, actor_npc=None):
        quest_key = (quest_key or "").strip().lower()
        if not quest_key:
            return False, "You must specify which quest you want to begin.", None
        rows = self.get_quest_journal(session.character_id, quest_key=quest_key)
        quest = rows[0] if rows else None
        error = self._quest_start_error(session, quest, actor_npc)
        if error:
            return False, error, None

        stages = quest.get("stages") or []
        if not stages:
            return False, "That quest is not configured correctly.", None

        first_stage = stages[0]
        target_count = max(1, int(first_stage.get("required_count") or 1))

        conn = self._get_conn()
        if not conn:
            return False, "The quest ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_quests (
                    character_id, quest_id, status, stage, progress_count, target_count, quest_data, started_at, completed_at
                ) VALUES (%s, %s, 'active', 1, 0, %s, JSON_OBJECT(), NOW(), NULL)
                ON DUPLICATE KEY UPDATE
                    status = 'active',
                    stage = 1,
                    progress_count = 0,
                    target_count = VALUES(target_count),
                    quest_data = JSON_OBJECT(),
                    started_at = NOW(),
                    completed_at = NULL
                """,
                (session.character_id, int(quest["id"]), target_count),
            )
            conn.commit()
        except Exception as e:
            log.error("GuildEngine.start_quest failed for %s/%s: %s", session.character_id, quest_key, e)
            return False, "The quest ledger refuses to assign that work right now.", None
        finally:
            conn.close()

        return True, None, self.get_quest_journal(session.character_id, quest_key=quest_key)[0]

    def start_next_quest(self, session, guild_id: str):
        membership = getattr(session, "guild_membership", None) or {}
        if membership.get("guild_id") != guild_id:
            return False, "You are not currently a member of that guild.", None

        if self.get_active_quest(session.character_id, guild_id):
            return False, "You already have an active guild quest.", None

        journal = self.get_quest_journal(session.character_id, guild_id)
        next_row = None
        level = int(getattr(session, "level", 0) or 0)
        for row in journal:
            status = (row.get("status") or "available").lower()
            if status == "complete":
                continue
            if level < int(row.get("min_level") or 1) or level > int(row.get("max_level") or 100):
                continue
            next_row = row
            break
        if not next_row:
            return False, "There are no additional rogue guild quests currently available to you.", None

        stages = next_row.get("stages") or []
        if not stages:
            return False, "That guild quest is not configured correctly.", None

        first_stage = stages[0]
        target_count = max(1, int(first_stage.get("required_count") or 1))

        conn = self._get_conn()
        if not conn:
            return False, "The guild quest ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_quests (
                    character_id, quest_id, status, stage, progress_count, target_count, quest_data, started_at, completed_at
                ) VALUES (%s, %s, 'active', 1, 0, %s, JSON_OBJECT(), NOW(), NULL)
                ON DUPLICATE KEY UPDATE
                    status = 'active',
                    stage = 1,
                    progress_count = 0,
                    target_count = VALUES(target_count),
                    quest_data = JSON_OBJECT(),
                    started_at = NOW(),
                    completed_at = NULL
                """,
                (session.character_id, int(next_row["id"]), target_count),
            )
            conn.commit()
        except Exception as e:
            log.error("GuildEngine.start_next_quest failed for %s/%s: %s", session.character_id, guild_id, e)
            return False, "The guild quest ledger refuses to assign that work right now.", None
        finally:
            conn.close()

        return True, None, self.get_active_quest(session.character_id, guild_id)

    async def _record_single_quest_event(self, session, active):
        current_stage = active.get("current_stage") or {}
        stage_num = int(active.get("stage") or 1)
        target_count = max(1, int(active.get("target_count") or current_stage.get("required_count") or 1))
        new_progress = min(target_count, int(active.get("progress_count") or 0) + 1)
        stages = active.get("stages") or []
        quest_id = int(active["id"])
        quest_meta = active.get("quest_meta") or {}
        guild_id = quest_meta.get("guild_id")
        label_prefix = "Guild quest" if guild_id else "Quest"
        rewards_pending = False

        conn = self._get_conn()
        if not conn:
            return
        try:
            cur = conn.cursor()
            if new_progress >= target_count:
                if stage_num >= len(stages):
                    cur.execute(
                        """
                        UPDATE character_quests
                        SET status = 'complete',
                            progress_count = %s,
                            target_count = %s,
                            completed_at = NOW()
                        WHERE character_id = %s AND quest_id = %s
                        """,
                        (target_count, target_count, session.character_id, quest_id),
                    )
                    if guild_id:
                        cur.execute(
                            """
                            INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                            VALUES (%s, %s, 'quest', 0, NULL, %s)
                            """,
                            (session.character_id, guild_id, f"Completed guild quest {active.get('key_name')}."),
                        )
                    conn.commit()
                    rewards_pending = True
                    await session.send_line(
                        colorize(
                            f"  {label_prefix} complete: {active.get('title', 'Quest')}.",
                            TextPresets.COMBAT_HIT,
                        )
                    )
                else:
                    next_stage = stages[stage_num]
                    next_target = max(1, int(next_stage.get("required_count") or 1))
                    cur.execute(
                        """
                        UPDATE character_quests
                        SET stage = %s,
                            progress_count = 0,
                            target_count = %s
                        WHERE character_id = %s AND quest_id = %s
                        """,
                        (stage_num + 1, next_target, session.character_id, quest_id),
                    )
                    conn.commit()
                    if next_stage.get("quiz_questions"):
                        self._save_quest_data(
                            session.character_id,
                            quest_id,
                            {"quiz_index": 0},
                        )
                    await session.send_line(
                        colorize(
                            f"  {label_prefix} advanced: {next_stage.get('objective', active.get('title', 'Continue your work.'))}",
                            TextPresets.SYSTEM,
                        )
                    )
                    if next_stage.get("quiz_questions"):
                        refreshed = self.get_quest_journal(session.character_id, quest_key=active.get("key_name"))[0]
                        _, questions, npc = self._get_room_quiz_quest(session)
                        await session.send_line(
                            colorize("  Use ANSWER <response> to reply.", TextPresets.SYSTEM)
                        )
                        await self._send_quiz_prompt(session, refreshed, questions or next_stage.get("quiz_questions") or [], npc)
            else:
                cur.execute(
                    """
                    UPDATE character_quests
                    SET progress_count = %s
                    WHERE character_id = %s AND quest_id = %s
                    """,
                    (new_progress, session.character_id, quest_id),
                )
                conn.commit()
                await session.send_line(
                    colorize(
                        f"  {label_prefix} progress: {new_progress}/{target_count}.",
                        TextPresets.SYSTEM,
                    )
                )
        except Exception as e:
            log.error("GuildEngine._record_single_quest_event failed for %s/%s: %s", session.character_id, active.get("key_name"), e)
        finally:
            conn.close()
        if rewards_pending:
            await self._apply_quest_completion_rewards(session, active)

    async def _record_quest_event(self, session, event_name: str):
        if not getattr(session, "character_id", None):
            return
        event_name_l = (event_name or "").lower()
        active_quests = self.get_active_quests(session.character_id)
        for active in active_quests:
            current_stage = active.get("current_stage") or {}
            if (current_stage.get("objective_event") or "").lower() != event_name_l:
                continue
            await self._record_single_quest_event(session, active)

    def _choose_task_definition(self, guild_id: str, skill_name: str, current_ranks: int):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, guild_id, skill_name, task_code, title, description,
                       objective_event, required_count, base_points, min_rank, max_rank,
                       practice_room_id, requires_guild_authority, is_active
                FROM guild_task_definitions
                WHERE guild_id = %s AND skill_name = %s AND is_active = 1
                  AND min_rank <= %s AND (max_rank IS NULL OR max_rank >= %s)
                ORDER BY min_rank DESC, base_points DESC, id ASC
                """,
                (guild_id, skill_name, current_ranks, current_ranks),
            )
            rows = cur.fetchall() or []
            if not rows:
                return None
            live_rows = [row for row in rows if (row.get("objective_event") or "").lower() != "guild_practice"]
            return (live_rows or rows)[0]
        finally:
            conn.close()

    def _get_membership_row(self, character_id: int, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM character_guild_membership
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                LIMIT 1
                """,
                (character_id, guild_id),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def _get_skill_rows_for_character(self, character_id: int, guild_id: str):
        conn = self._get_conn()
        if not conn:
            return {}
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT skill_name, ranks, training_points, is_mastered, last_trained_at
                FROM character_guild_skills
                WHERE character_id = %s AND guild_id = %s
                """,
                (character_id, guild_id),
            )
            return {row["skill_name"]: row for row in (cur.fetchall() or [])}
        finally:
            conn.close()

    def _effective_total_ranks(self, skill_rows: dict) -> int:
        total = 0
        for row in (skill_rows or {}).values():
            ranks = int(row.get("ranks", 0) or 0)
            if ranks > 0:
                total += max(0, ranks - 1)
        return total

    def _has_mastered_skill(self, guild_id: str, skill_rows: dict) -> bool:
        skill_defs = self.get_skill_def_map(guild_id)
        for skill_name, row in (skill_rows or {}).items():
            if int(row.get("is_mastered", 0) or 0):
                return True
            max_rank = int((skill_defs.get(skill_name, {}) or {}).get("max_rank") or 63)
            if int(row.get("ranks", 0) or 0) >= max_rank:
                return True
        return False

    def is_guildmaster_eligible(self, character_id: int, guild_id: str):
        membership = self._get_membership_row(character_id, guild_id)
        if not membership:
            return False, 0, False
        skill_rows = self._get_skill_rows_for_character(character_id, guild_id)
        total_ranks = self._effective_total_ranks(skill_rows)
        mastered = self._has_mastered_skill(guild_id, skill_rows)
        return total_ranks >= 125 and mastered, total_ranks, mastered

    def get_guildmaster_nominations(self, guild_id: str, nominee_character_id: int):
        conn = self._get_conn()
        if not conn:
            return []
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM guild_guildmaster_nominations
                WHERE guild_id = %s AND nominee_character_id = %s AND status = 'active'
                ORDER BY nominated_at ASC
                """,
                (guild_id, nominee_character_id),
            )
            return cur.fetchall() or []
        finally:
            conn.close()

    def nominate_guildmaster(self, nominator_character_id: int, nominee_character_id: int, guild_id: str):
        eligible, _, _ = self.is_guildmaster_eligible(nominator_character_id, guild_id)
        nominator_membership = self._get_membership_row(nominator_character_id, guild_id) or {}
        if not (eligible or int(nominator_membership.get("is_guildmaster", 0) or 0)):
            return False, "You are not eligible to nominate a guildmaster candidate.", 0

        nominee_membership = self._get_membership_row(nominee_character_id, guild_id)
        if not nominee_membership:
            return False, "That person is not an active member of your guild.", 0
        if int(nominee_membership.get("is_guildmaster", 0) or 0):
            return False, "That guild member already holds guildmaster status.", 0

        nominee_ok, _, nominee_mastered = self.is_guildmaster_eligible(nominee_character_id, guild_id)
        if not nominee_ok or not nominee_mastered:
            return False, "That member has not yet met the guildmaster requirements.", 0

        conn = self._get_conn()
        if not conn:
            return False, "The guild nomination ledger is unavailable right now.", 0
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO guild_guildmaster_nominations (
                    guild_id, nominee_character_id, nominator_character_id, status, notes
                ) VALUES (%s, %s, %s, 'active', %s)
                ON DUPLICATE KEY UPDATE
                    status = 'active',
                    notes = VALUES(notes),
                    nominated_at = CURRENT_TIMESTAMP,
                    used_at = NULL
                """,
                (guild_id, nominee_character_id, nominator_character_id, "Guildmaster nomination recorded."),
            )
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'nominate', 0, NULL, %s)
                """,
                (nominee_character_id, guild_id, f"Nominated for guildmaster by character {nominator_character_id}."),
            )
            conn.commit()
        except Exception as e:
            log.error(
                "GuildEngine.nominate_guildmaster failed for nominator=%s nominee=%s guild=%s: %s",
                nominator_character_id,
                nominee_character_id,
                guild_id,
                e,
            )
            return False, "The nomination ledger refuses to record that nomination right now.", 0
        finally:
            conn.close()

        count = len(self.get_guildmaster_nominations(guild_id, nominee_character_id))
        return True, None, count

    def promote_guildmaster(self, promoter_character_id: int, nominee_character_id: int, guild_id: str):
        promoter_membership = self._get_membership_row(promoter_character_id, guild_id) or {}
        promoter_is_master = bool(int(promoter_membership.get("is_guildmaster", 0) or 0))
        promoter_eligible, _, _ = self.is_guildmaster_eligible(promoter_character_id, guild_id)
        if not promoter_is_master and not promoter_eligible:
            return False, "You are not authorized to complete a guildmaster promotion.", None

        nominee_membership = self._get_membership_row(nominee_character_id, guild_id)
        if not nominee_membership:
            return False, "That person is not an active member of your guild.", None
        if int(nominee_membership.get("is_guildmaster", 0) or 0):
            return False, "That guild member already holds guildmaster status.", None

        nominee_ok, total_ranks, _ = self.is_guildmaster_eligible(nominee_character_id, guild_id)
        if not nominee_ok:
            return False, "That member has not yet satisfied the guildmaster requirements.", None

        nominations = self.get_guildmaster_nominations(guild_id, nominee_character_id)
        unique_nominators = {int(row.get("nominator_character_id") or 0) for row in nominations if int(row.get("nominator_character_id") or 0) > 0}
        if len(unique_nominators) < 2:
            return False, "Two eligible nominations are required before guildmaster status can be granted.", None

        conn = self._get_conn()
        if not conn:
            return False, "The guildmaster ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_guild_membership
                SET is_guildmaster = 1,
                    next_checkin_due_at = COALESCE(next_checkin_due_at, DATE_ADD(NOW(), INTERVAL 30 DAY))
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                """,
                (nominee_character_id, guild_id),
            )
            cur.execute(
                """
                UPDATE guild_guildmaster_nominations
                SET status = 'used', used_at = NOW()
                WHERE guild_id = %s AND nominee_character_id = %s AND status = 'active'
                """,
                (guild_id, nominee_character_id),
            )
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'guildmaster', %s, NULL, %s)
                """,
                (
                    nominee_character_id,
                    guild_id,
                    total_ranks,
                    f"Guildmaster status granted by character {promoter_character_id}.",
                ),
            )
            conn.commit()
        except Exception as e:
            log.error(
                "GuildEngine.promote_guildmaster failed for promoter=%s nominee=%s guild=%s: %s",
                promoter_character_id,
                nominee_character_id,
                guild_id,
                e,
            )
            return False, "The guildmaster ledger refuses to record that promotion right now.", None
        finally:
            conn.close()

        return True, None, {"total_ranks": total_ranks, "nominations": len(unique_nominators)}

    def promote_skill(self, promoter_character_id: int, target_character_id: int, guild_id: str, skill_name: str):
        promoter_membership = self._get_membership_row(promoter_character_id, guild_id) or {}
        target_membership = self._get_membership_row(target_character_id, guild_id)
        if not target_membership:
            return False, "That person is not an active member of your guild.", None
        if promoter_character_id == target_character_id:
            return False, "Guild promotions must be bestowed by another member.", None

        skill_defs = self.get_skill_def_map(guild_id)
        skill_def = skill_defs.get(skill_name)
        if not skill_def:
            return False, "That guild skill is not configured.", None

        promoter_is_master = bool(int(promoter_membership.get("is_guildmaster", 0) or 0))
        if not promoter_is_master:
            promoter_skill = (self._get_skill_rows_for_character(promoter_character_id, guild_id) or {}).get(skill_name, {})
            promoter_mastered = int(promoter_skill.get("is_mastered", 0) or 0)
            promoter_ranks = int(promoter_skill.get("ranks", 0) or 0)
            if not promoter_mastered and promoter_ranks < int(skill_def.get("max_rank") or 63):
                return False, "You must master that skill before you can promote another member in it.", None

        target_skills = self._get_skill_rows_for_character(target_character_id, guild_id)
        target_row = target_skills.get(skill_name, {})
        current_rank = int(target_row.get("ranks", 0) or 0)
        current_points = int(target_row.get("training_points", 0) or 0)
        max_rank = int(skill_def.get("max_rank") or 63)
        if current_rank >= max_rank:
            return False, "That member has already mastered that skill.", None

        new_rank = current_rank + 1
        points_per_rank = max(1, int(skill_def.get("points_per_rank") or 100))
        new_points = max(current_points, new_rank * points_per_rank)
        is_mastered = 1 if new_rank >= max_rank else 0

        conn = self._get_conn()
        if not conn:
            return False, "The guild promotion ledger is unavailable right now.", None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                INSERT INTO character_guild_skills (
                    character_id, guild_id, skill_name, ranks, training_points, is_mastered, last_trained_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    ranks = VALUES(ranks),
                    training_points = VALUES(training_points),
                    is_mastered = VALUES(is_mastered),
                    last_trained_at = NOW()
                """,
                (target_character_id, guild_id, skill_name, new_rank, new_points, is_mastered),
            )
            total_points, total_ranks, distinct, guild_rank = self._recompute_and_apply_rank(cur, target_character_id, guild_id)
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'promotion', %s, NULL, %s)
                """,
                (
                    target_character_id,
                    guild_id,
                    new_rank,
                    f"Promoted to rank {new_rank} in {skill_name} by character {promoter_character_id}.",
                ),
            )
            conn.commit()
        except Exception as e:
            log.error(
                "GuildEngine.promote_skill failed for promoter=%s target=%s guild=%s skill=%s: %s",
                promoter_character_id,
                target_character_id,
                guild_id,
                skill_name,
                e,
            )
            return False, "The guild ledger refuses to record that promotion right now.", None
        finally:
            conn.close()

        return True, None, {
            "skill_name": skill_name,
            "skill_rank": new_rank,
            "guild_rank": guild_rank,
            "total_points": total_points,
            "total_ranks": total_ranks,
            "distinct_skills": distinct,
        }

    def abandon_active_task(self, session):
        membership = getattr(session, "guild_membership", None)
        if not membership:
            return False, "You are not currently a member of a profession guild.", None

        guild_id = membership["guild_id"]
        task = self._get_active_task(session.character_id, guild_id)
        if not task:
            return False, "You do not currently have an active guild task.", None

        conn = self._get_conn()
        if not conn:
            return False, "The guild task ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_guild_tasks
                SET status = 'abandoned', completed_at = NOW(), repetitions_remaining = 0
                WHERE id = %s
                """,
                (task["id"],),
            )
            conn.commit()
        except Exception as e:
            log.error("GuildEngine.abandon_active_task failed for task %s: %s", task.get("id"), e)
            return False, "The guild ledger refuses to abandon that task right now.", None
        finally:
            conn.close()

        return True, None, task

    def swap_active_task(self, session, guild_id: str, skill_name: str | None = None):
        membership = getattr(session, "guild_membership", None)
        if not membership or membership.get("guild_id") != guild_id:
            return False, "You are not currently a member of that guild.", None

        vouchers = int(membership.get("vouchers", 0) or 0)
        if vouchers <= 0:
            return False, "You do not currently have any task trading vouchers.", None

        task = self._get_active_task(session.character_id, guild_id)
        if not task:
            return False, "You do not currently have an active guild task to swap.", None

        conn = self._get_conn()
        if not conn:
            return False, "The guild task ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_guild_tasks
                SET status = 'abandoned', completed_at = NOW(), repetitions_remaining = 0
                WHERE id = %s
                """,
                (task["id"],),
            )
            cur.execute(
                """
                UPDATE character_guild_membership
                SET vouchers = GREATEST(0, vouchers - 1)
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                """,
                (session.character_id, guild_id),
            )
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'voucher', -1, NULL, %s)
                """,
                (
                    session.character_id,
                    guild_id,
                    f"Consumed a task voucher to swap task {task.get('task_code') or task.get('task_type') or task.get('id')}.",
                ),
            )
            conn.commit()
        except Exception as e:
            log.error("GuildEngine.swap_active_task voucher step failed for task %s: %s", task.get("id"), e)
            return False, "The guild ledger refuses to trade that task right now.", None
        finally:
            conn.close()

        return self.assign_task(session, guild_id, skill_name or task.get("skill_name"))

    def assign_task(self, session, guild_id: str, skill_name: str):
        membership = getattr(session, "guild_membership", None)
        if not membership or membership.get("guild_id") != guild_id:
            return False, "You are not currently a member of that guild.", None

        existing = self._get_active_task(session.character_id, guild_id)
        if existing:
            return False, "You already have an active guild task.", existing

        skill_rows = getattr(session, "guild_skills", {}) or {}
        current_row = skill_rows.get(skill_name, {})
        current_ranks = int(current_row.get("ranks", 0) or 0)

        task_def = self._choose_task_definition(guild_id, skill_name, current_ranks)
        if not task_def:
            return False, "No training task is currently defined for that skill.", None

        multiplier = float(membership.get("progression_multiplier") or 20.0)
        award_points = max(1, int(round(float(task_def.get("base_points") or 1) * multiplier)))
        task_text = task_def.get("description") or task_def.get("title") or "Complete a guild task."

        conn = self._get_conn()
        if not conn:
            return False, "The guild ledger is unavailable right now.", None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_guild_tasks (
                    character_id, guild_id, skill_name, task_code, task_type, task_text,
                    objective_event, target_count, progress_count, award_points,
                    repetitions_remaining, task_data, status, assigned_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, NULL, 'assigned', NOW())
                """,
                (
                    session.character_id,
                    guild_id,
                    skill_name,
                    task_def.get("task_code"),
                    task_def.get("title"),
                    task_text,
                    task_def.get("objective_event"),
                    int(task_def.get("required_count") or 1),
                    award_points,
                    int(task_def.get("required_count") or 1),
                ),
            )
            cur.execute(
                """
                UPDATE character_guild_membership
                SET active_skill_name = %s, last_task_at = NOW()
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                """,
                (skill_name, session.character_id, guild_id),
            )
            conn.commit()
            task_id = cur.lastrowid
        except Exception as e:
            log.error("GuildEngine.assign_task failed for %s/%s/%s: %s", session.character_id, guild_id, skill_name, e)
            return False, "The guild ledger refuses to assign a task right now.", None
        finally:
            conn.close()

        task = self._get_active_task(session.character_id, guild_id)
        if task:
            task["id"] = task_id
        return True, None, task

    async def practice_active_task(self, session):
        membership = getattr(session, "guild_membership", None)
        if not membership:
            return False, "You are not currently a member of a profession guild.", None

        guild_id = membership["guild_id"]
        task = self._get_active_task(session.character_id, guild_id)
        if not task:
            return False, "You do not currently have an active guild task.", None
        if (task.get("objective_event") or "").lower() != "guild_practice":
            return False, "Your current guild task must be completed in the field rather than through hall practice.", task

        conn = self._get_conn()
        if not conn:
            return False, "The guild task ledger is unavailable right now.", None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE character_guild_tasks
                SET progress_count = LEAST(target_count, progress_count + 1),
                    repetitions_remaining = GREATEST(0, target_count - LEAST(target_count, progress_count + 1)),
                    status = CASE
                        WHEN LEAST(target_count, progress_count + 1) >= target_count THEN 'ready'
                        ELSE 'assigned'
                    END
                WHERE id = %s
                """,
                (task["id"],),
            )
            conn.commit()
            cur.execute(
                """
                SELECT id, guild_id, skill_name, task_code, task_type, task_text,
                       objective_event, target_count, progress_count, award_points,
                       repetitions_remaining, task_data, status, assigned_at, completed_at
                FROM character_guild_tasks
                WHERE id = %s
                LIMIT 1
                """,
                (task["id"],),
            )
            updated = cur.fetchone()
        except Exception as e:
            log.error("GuildEngine.practice_active_task failed for task %s: %s", task.get("id"), e)
            return False, "The guild practice ledger refuses to update right now.", None
        finally:
            conn.close()

        skill_label = updated.get("skill_name", "guild skill")
        progress = int(updated.get("progress_count") or 0)
        target = int(updated.get("target_count") or 1)
        if updated.get("status") == "ready":
            await session.send_line(
                colorize(
                    f"  You finish the {skill_label} drill cleanly.  Return with GLD COMPLETE.",
                    TextPresets.COMBAT_HIT,
                )
            )
        else:
            await session.send_line(
                colorize(
                    f"  You work through another {skill_label} drill.  Progress: {progress}/{target}.",
                    TextPresets.SYSTEM,
                )
            )
        return True, None, updated

    async def record_event(self, session, event_name: str):
        membership = getattr(session, "guild_membership", None) or {}
        guild_id = membership.get("guild_id")

        if guild_id and getattr(session, "character_id", None):
            task = self._get_active_task(session.character_id, guild_id)
            if task and task.get("status") != "ready" and (task.get("objective_event") or "").lower() == (event_name or "").lower():
                conn = self._get_conn()
                if conn:
                    try:
                        cur = conn.cursor(dictionary=True)
                        cur.execute(
                            """
                            UPDATE character_guild_tasks
                            SET progress_count = LEAST(target_count, progress_count + 1),
                                repetitions_remaining = GREATEST(0, target_count - LEAST(target_count, progress_count + 1)),
                                status = CASE
                                    WHEN LEAST(target_count, progress_count + 1) >= target_count THEN 'ready'
                                    ELSE 'assigned'
                                END
                            WHERE id = %s
                            """,
                            (task["id"],),
                        )
                        conn.commit()
                        cur.execute(
                            """
                            SELECT progress_count, target_count, status, skill_name
                            FROM character_guild_tasks
                            WHERE id = %s
                            LIMIT 1
                            """,
                            (task["id"],),
                        )
                        updated = cur.fetchone()
                    except Exception as e:
                        log.error("GuildEngine.record_event failed for task %s: %s", task.get("id"), e)
                        updated = None
                    finally:
                        conn.close()

                    if updated:
                        progress = int(updated.get("progress_count") or 0)
                        target = int(updated.get("target_count") or 1)
                        if updated.get("status") == "ready":
                            await session.send_line(
                                colorize(
                                    f"  Guild task ready: {updated.get('skill_name', 'skill')} is complete.  Return with GLD COMPLETE.",
                                    TextPresets.COMBAT_HIT,
                                )
                            )
                        else:
                            await session.send_line(
                                colorize(
                                    f"  Guild task progress: {progress}/{target}.",
                                    TextPresets.SYSTEM,
                                )
                            )
        await self._record_quest_event(session, event_name)

    def _recompute_and_apply_rank(self, cur, character_id: int, guild_id: str):
        cur.execute(
            """
            SELECT skill_name, training_points, ranks
            FROM character_guild_skills
            WHERE character_id = %s AND guild_id = %s
            """,
            (character_id, guild_id),
        )
        skills = cur.fetchall() or []
        total_points = 0
        total_ranks = 0
        distinct = 0
        for row in skills:
            ranks = int(row.get("ranks") or 0)
            points = int(row.get("training_points") or 0)
            total_points += points
            if ranks > 0:
                distinct += 1
                total_ranks += max(0, ranks - 1)

        rank_defs = self._get_rank_definitions(guild_id)
        new_rank = 1
        for row in rank_defs:
            if total_ranks >= int(row.get("min_total_skill_ranks") or 0) and distinct >= int(row.get("min_distinct_skills") or 0):
                new_rank = int(row.get("rank_level") or new_rank)

        cur.execute(
            """
            UPDATE character_guild_membership
            SET guild_training_points = %s, rank_level = %s
            WHERE character_id = %s AND guild_id = %s AND status = 'active'
            """,
            (total_points, new_rank, character_id, guild_id),
        )
        return total_points, total_ranks, distinct, new_rank

    def complete_active_task(self, session):
        membership = getattr(session, "guild_membership", None)
        if not membership:
            return False, "You are not currently a member of a profession guild.", None

        guild_id = membership["guild_id"]
        task = self._get_active_task(session.character_id, guild_id)
        if not task:
            return False, "You do not currently have an active guild task.", None
        if task.get("status") != "ready" and int(task.get("progress_count") or 0) < int(task.get("target_count") or 1):
            return False, "Your current guild task is not complete yet.", task

        skill_defs = self.get_skill_def_map(guild_id)
        skill_def = skill_defs.get(task.get("skill_name"))
        if not skill_def:
            return False, "That guild skill is not properly configured yet.", None

        conn = self._get_conn()
        if not conn:
            return False, "The guild ledger is unavailable right now.", None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT rank_level
                FROM character_guild_membership
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                LIMIT 1
                """,
                (session.character_id, guild_id),
            )
            row = cur.fetchone() or {}
            old_rank = int(row.get("rank_level") or 1)

            cur.execute(
                """
                INSERT INTO character_guild_skills (
                    character_id, guild_id, skill_name, ranks, training_points, is_mastered, last_trained_at
                ) VALUES (%s, %s, %s, 0, %s, 0, NOW())
                ON DUPLICATE KEY UPDATE
                    training_points = training_points + VALUES(training_points),
                    last_trained_at = NOW()
                """,
                (
                    session.character_id,
                    guild_id,
                    task["skill_name"],
                    int(task.get("award_points") or 0),
                ),
            )

            cur.execute(
                """
                SELECT training_points
                FROM character_guild_skills
                WHERE character_id = %s AND guild_id = %s AND skill_name = %s
                LIMIT 1
                """,
                (session.character_id, guild_id, task["skill_name"]),
            )
            skill_row = cur.fetchone() or {}
            points = int(skill_row.get("training_points") or 0)
            points_per_rank = max(1, int(skill_def.get("points_per_rank") or 100))
            max_rank = max(1, int(skill_def.get("max_rank") or 63))
            new_skill_rank = min(max_rank, points // points_per_rank)
            is_mastered = 1 if new_skill_rank >= max_rank else 0

            cur.execute(
                """
                UPDATE character_guild_skills
                SET ranks = %s, is_mastered = %s
                WHERE character_id = %s AND guild_id = %s AND skill_name = %s
                """,
                (new_skill_rank, is_mastered, session.character_id, guild_id, task["skill_name"]),
            )

            cur.execute(
                """
                UPDATE character_guild_tasks
                SET status = 'complete', completed_at = NOW(), repetitions_remaining = 0
                WHERE id = %s
                """,
                (task["id"],),
            )

            cur.execute(
                """
                UPDATE character_guild_membership
                SET vouchers = vouchers + 1
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
                """,
                (session.character_id, guild_id),
            )

            total_points, total_ranks, distinct, new_rank = self._recompute_and_apply_rank(cur, session.character_id, guild_id)

            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'task', %s, NULL, %s)
                """,
                (
                    session.character_id,
                    guild_id,
                    int(task.get("award_points") or 0),
                    f"Completed guild task {task.get('task_code') or task.get('task_type') or 'task'} for {task.get('skill_name')}.",
                ),
            )
            if new_rank > old_rank:
                cur.execute(
                    """
                    INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                    VALUES (%s, %s, 'promotion', %s, NULL, %s)
                    """,
                    (
                        session.character_id,
                        guild_id,
                        new_rank,
                        f"Promoted from rank {old_rank} to rank {new_rank}.",
                    ),
                )
            cur.execute(
                """
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'voucher', 1, NULL, %s)
                """,
                (
                    session.character_id,
                    guild_id,
                    f"Earned a task voucher for completing {task.get('task_code') or task.get('task_type') or 'task'}.",
                ),
            )
            conn.commit()
        except Exception as e:
            log.error("GuildEngine.complete_active_task failed for %s/%s: %s", session.character_id, guild_id, e)
            return False, "The guild ledger refuses to finalize that task right now.", None
        finally:
            conn.close()

        updated_membership = self._get_membership_row(session.character_id, guild_id) or {}
        return True, None, {
            "skill_name": task.get("skill_name"),
            "award_points": int(task.get("award_points") or 0),
            "skill_rank": new_skill_rank,
            "total_points": total_points,
            "total_ranks": total_ranks,
            "distinct_skills": distinct,
            "old_rank": old_rank,
            "new_rank": new_rank,
            "vouchers": int(updated_membership.get("vouchers", 0) or 0),
        }

    async def try_handle_interaction(self, session, cmd: str, args: str):
        cmd_l = (cmd or "").lower().strip()
        if cmd_l not in self._ENTRY_VERBS:
            return False
        if not getattr(session, "character_id", None) or not getattr(session, "current_room", None):
            return False

        access_point = self._get_access_point_for_room(session.current_room.id, self._ROGUE_GUILD_ID)
        if not access_point:
            return False

        if session.current_room.id == int(access_point["entry_room_id"]):
            return await self._handle_rogue_entry(session, access_point, cmd_l, args)
        if session.current_room.id == int(access_point["target_room_id"]):
            return await self._handle_rogue_exit(session, access_point, cmd_l, args)
        return False

    async def _handle_rogue_entry(self, session, access_point, cmd_l: str, args: str):
        if cmd_l == "lean":
            return await self._handle_rogue_entry_lean(session, args)
        if cmd_l in {"pull", "slap", "rub", "push", "turn"}:
            return await self._handle_rogue_sequence_step(session, access_point, cmd_l)
        if cmd_l in {"open", "go"}:
            target = (args or "").strip().lower()
            if target and target not in self._ENTRY_ALIAS_TARGETS:
                return False
            await session.send_line("Nothing obvious yields.  You may need the proper pass sequence first.")
            return True
        return False

    async def _handle_rogue_exit(self, session, access_point, cmd_l: str, args: str):
        args_l = (args or "").strip().lower()
        if cmd_l == "look" and args_l in {"tool", "tools"}:
            self._set_sequence_state(
                session.character_id,
                self._ROGUE_GUILD_ID,
                step=0,
                room_id=session.current_room.id,
                started_at=datetime.utcnow(),
            )
            await session.send_line("You study the scattered tools closely, committing their odd arrangement to memory.")
            return True
        if cmd_l == "pull" and args_l in {"hoe", "rake", "shovel"}:
            return await self._handle_rogue_exit_sequence_step(session, f"pull {args_l}", access_point)
        if cmd_l == "go" and args_l == "panel":
            return await self._handle_rogue_exit_sequence_step(session, "go panel", access_point)
        if cmd_l not in {"out", "go"}:
            return False
        target = (args or "").strip().lower()
        if cmd_l == "go" and target and target not in self._ENTRY_ALIAS_TARGETS:
            return False

        membership = getattr(session, "guild_membership", None) or {}
        access = self.get_access_row(session.character_id, self._ROGUE_GUILD_ID) or {}
        if membership.get("guild_id") != self._ROGUE_GUILD_ID and not access.get("password_known"):
            await session.send_line("You do not know a safe way back out from here.")
            return True

        return await self._move_special(session, int(access_point["entry_room_id"]), "out")

    async def _handle_rogue_exit_sequence_step(self, session, token: str, access_point):
        access = self.get_access_row(session.character_id, self._ROGUE_GUILD_ID) or {}
        started_at = access.get("sequence_started_at")
        step = int(access.get("sequence_step") or 0)
        room_id = int(access.get("sequence_room_id") or 0)

        if room_id != session.current_room.id or not started_at or not isinstance(started_at, datetime):
            await session.send_line("You need to LOOK TOOL first if you want to work the hidden panel.")
            return True
        if datetime.utcnow() - started_at > timedelta(seconds=self._ROGUE_SEQUENCE_TIMEOUT):
            self._set_sequence_state(session.character_id, self._ROGUE_GUILD_ID, step=0, room_id=None, started_at=None)
            await session.send_line("You take too long and lose the feel of the hidden mechanism.")
            return True

        expected = self._EXIT_PANEL_SEQUENCE[step] if step < len(self._EXIT_PANEL_SEQUENCE) else None
        if token != expected:
            self._set_sequence_state(
                session.character_id,
                self._ROGUE_GUILD_ID,
                step=0,
                room_id=session.current_room.id,
                started_at=datetime.utcnow(),
            )
            await session.send_line("The tools settle with a faint scrape.  You will need to start again from LOOK TOOL.")
            return True

        new_step = step + 1
        if new_step >= len(self._EXIT_PANEL_SEQUENCE):
            self._set_sequence_state(session.character_id, self._ROGUE_GUILD_ID, step=0, room_id=None, started_at=None)
            await session.send_line("A concealed panel shifts and opens just enough to let you slip through.")
            return await self._move_special(session, int(access_point["entry_room_id"]), "panel")

        self._set_sequence_state(
            session.character_id,
            self._ROGUE_GUILD_ID,
            step=new_step,
            room_id=session.current_room.id,
            started_at=started_at,
        )
        await session.send_line(colorize("  The hidden mechanism gives slightly under your hand.", TextPresets.SYSTEM))
        return True

    async def _handle_rogue_entry_lean(self, session, args: str):
        membership = getattr(session, "guild_membership", None) or {}
        access = self.get_access_row(session.character_id, self._ROGUE_GUILD_ID) or {}
        invited = bool(access.get("is_invited"))
        password_known = bool(access.get("password_known"))
        is_member = membership.get("guild_id") == self._ROGUE_GUILD_ID

        if not invited and not is_member:
            await session.send_line(
                "You lean casually in the alley, but nothing answers.  Without a rogue invitation, the hidden catch stays still."
            )
            return True
        if not password_known and not is_member:
            await session.send_line("You know you were invited, but you do not yet know the password sequence.")
            return True

        self.ensure_access_row(session.character_id, self._ROGUE_GUILD_ID)
        self._set_sequence_state(
            session.character_id,
            self._ROGUE_GUILD_ID,
            step=0,
            room_id=session.current_room.id,
            started_at=datetime.utcnow(),
        )
        await session.send_line(
            colorize(
                "  You lean against the alley wall and wait.  Somewhere nearby, a hidden catch shifts.  You can begin the pass sequence now.",
                TextPresets.SYSTEM,
            )
        )
        return True

    async def _handle_rogue_sequence_step(self, session, access_point, cmd_l: str):
        access = self.get_access_row(session.character_id, self._ROGUE_GUILD_ID) or {}
        membership = getattr(session, "guild_membership", None) or {}
        if membership.get("guild_id") != self._ROGUE_GUILD_ID and not access.get("is_invited"):
            await session.send_line("Nothing happens.")
            return True
        if membership.get("guild_id") != self._ROGUE_GUILD_ID and not access.get("password_known"):
            await session.send_line("You do not know the proper sequence.")
            return True

        seq = self._parse_sequence(access_point)
        if not seq:
            await session.send_line("The rogue entry mechanism has not been configured yet.")
            return True

        started_at = access.get("sequence_started_at")
        step = int(access.get("sequence_step") or 0)
        room_id = int(access.get("sequence_room_id") or 0)

        if room_id != session.current_room.id or not started_at or not isinstance(started_at, datetime):
            await session.send_line("You need to LEAN first to start the pass sequence.")
            return True
        if datetime.utcnow() - started_at > timedelta(seconds=self._ROGUE_SEQUENCE_TIMEOUT):
            self._set_sequence_state(session.character_id, self._ROGUE_GUILD_ID, step=0, room_id=None, started_at=None)
            await session.send_line("You take too long and the hidden mechanism settles back into silence.")
            return True

        expected = seq[step] if step < len(seq) else None
        if cmd_l != expected:
            self._set_sequence_state(
                session.character_id,
                self._ROGUE_GUILD_ID,
                step=0,
                room_id=session.current_room.id,
                started_at=datetime.utcnow(),
            )
            await session.send_line(
                colorize(
                    "  A soft scrape tells you the sequence was wrong.  You will need to start again from the beginning.",
                    TextPresets.WARNING,
                )
            )
            return True

        new_step = step + 1
        if new_step >= len(seq):
            self._set_sequence_state(session.character_id, self._ROGUE_GUILD_ID, step=0, room_id=None, started_at=None)
            await session.send_line(
                colorize(
                    "  The hidden panel clicks open just enough for you to slip inside.",
                    TextPresets.COMBAT_HIT,
                )
            )
            moved = await self._move_special(session, int(access_point["target_room_id"]), "door")
            if moved:
                await self.record_event(session, "rogue_entry_used")
            return moved

        self._set_sequence_state(
            session.character_id,
            self._ROGUE_GUILD_ID,
            step=new_step,
            room_id=session.current_room.id,
            started_at=started_at,
        )
        await session.send_line(colorize("  The concealed mechanism shifts almost imperceptibly.", TextPresets.SYSTEM))
        return True

    async def _move_special(self, session, target_room_id: int, direction_label: str):
        from server.core.commands.player.movement import _move_player

        room = getattr(session, "current_room", None)
        if not room:
            return True
        target_room = self.server.world.get_room(target_room_id)
        if not target_room:
            await session.send_line("That route leads nowhere right now.")
            return True
        await _move_player(session, room, target_room, direction_label, self.server, sneaking=False)
        return True
