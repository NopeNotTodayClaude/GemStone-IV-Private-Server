"""
hotbar_manager.py
-----------------
Server-owned hotbar catalog, persistence, and silent execution.
"""

from __future__ import annotations

import logging
from typing import Any

from server.core.engine.action_ready import evaluate_ready_rule
from server.core.scripting.lua_bindings.weapon_api import (
    _get_skill_ranks,
    _resolve_profession_name,
    _validate_technique_loadout,
)
from server.core.scripting.lua_bindings.combat_maneuver_api import available_maneuver_summaries

log = logging.getLogger(__name__)


class HotbarManager:
    def __init__(self, server):
        self.server = server

    def _cfg(self) -> dict:
        return self.server.lua.get_hotbar_actions() or {}

    def load_for_session(self, session):
        db = getattr(self.server, "db", None)
        if not db or not getattr(session, "character_id", None):
            session.hotbar_slots = {}
            session.spell_ranks = {}
            session.spellbook = []
            return
        session.hotbar_slots = db.load_character_hotbar_slots(session.character_id) or {}
        session.spell_ranks = db.load_character_spell_ranks(session.character_id) or {}
        session.spellbook = db.load_character_spellbook(session.character_id) or []

    def build_sync_state(self, session) -> dict:
        catalog = self._available_catalog(session)
        action_index = {
            (category["key"], action["key"]): action
            for category in catalog
            for action in category.get("actions", [])
        }
        slots = []
        assignments = getattr(session, "hotbar_slots", {}) or {}
        category_labels = {row["key"]: row["label"] for row in catalog}

        for slot in range(1, 10):
            assigned = assignments.get(slot) or {}
            category_key = str(assigned.get("category_key") or "").strip()
            action_key = str(assigned.get("action_key") or "").strip()
            action = action_index.get((category_key, action_key))
            enabled = action is not None
            if not action and category_key and action_key:
                action = self._resolve_saved_action(session, category_key, action_key)
            ready_state = self._slot_ready_state(session, action) if enabled else {
                "ready": False,
                "ready_until": None,
                "message": "",
            }

            slots.append({
                "slot": slot,
                "assigned": bool(category_key and action_key),
                "enabled": bool(enabled),
                "category_key": category_key,
                "category_label": category_labels.get(category_key) or self._category_label(category_key),
                "action_key": action_key,
                "label": str((action or {}).get("label") or ""),
                "short_label": str((action or {}).get("short_label") or (action or {}).get("label") or ""),
                "command_preview": str((action or {}).get("command_preview") or ""),
                "targeting": str((action or {}).get("targeting") or "").strip().lower(),
                "pulse": bool(ready_state.get("ready")),
                "pulse_until": ready_state.get("ready_until"),
                "pulse_reason": str(ready_state.get("message") or ""),
            })

        return {
            "slots": slots,
            "catalog": {"categories": catalog},
        }

    def _category_label(self, category_key: str) -> str:
        for entry in self._cfg().get("categories", []) or []:
            if str(entry.get("key") or "").strip() == category_key:
                return str(entry.get("label") or category_key.replace("_", " ").title())
        return category_key.replace("_", " ").title()

    def _available_catalog(self, session) -> list[dict]:
        cfg = self._cfg()
        categories = sorted(
            [row for row in (cfg.get("categories", []) or []) if isinstance(row, dict)],
            key=lambda row: int(row.get("sort_order", 999) or 999),
        )
        out = []
        for category in categories:
            key = str(category.get("key") or "").strip()
            label = str(category.get("label") or key.replace("_", " ").title()).strip()
            if key == "weapon_techniques":
                actions = self._weapon_actions(session)
            elif key == "combat_maneuvers":
                actions = self._combat_maneuver_actions(session)
            elif key == "magic":
                actions = self._magic_actions(session)
            else:
                actions = []
            if actions:
                out.append({
                    "key": key,
                    "label": label,
                    "actions": actions,
                })
        return out

    def _weapon_actions(self, session) -> list[dict]:
        defs = self.server.lua.get_weapon_techniques() or {}
        profession_key = _resolve_profession_name(session, self.server)
        learned = dict(getattr(session, "weapon_techniques", {}) or {})
        current_categories = self._current_weapon_categories(session)
        out = []
        for mnemonic, tech in (defs or {}).items():
            if not isinstance(tech, dict):
                continue
            canonical = str(tech.get("mnemonic") or mnemonic).strip().lower()
            if canonical != str(mnemonic).strip().lower():
                continue
            if int(learned.get(canonical, 0) or 0) <= 0:
                continue
            category_key = self._normalize_category(tech.get("category"))
            if category_key not in current_categories:
                continue
            available_to = [str(v).strip().lower() for v in (tech.get("available_to") or [])]
            if available_to and profession_key not in available_to:
                continue
            loadout_ok, _loadout_msg = _validate_technique_loadout(session, tech)
            if not loadout_ok:
                continue
            out.append({
                "key": canonical,
                "label": str(tech.get("name") or canonical.title()).strip(),
                "short_label": str(tech.get("name") or canonical.title()).strip(),
                "command_preview": self._weapon_command_preview(tech, canonical),
                "description": str(tech.get("description") or "").strip(),
                "targeting": "current_target_optional" if str(tech.get("type") or "").strip().lower() == "aoe" else "current_target",
                "ready_rule": self._weapon_ready_rule(tech),
            })
        out.sort(key=lambda row: row["label"])
        return out

    def _weapon_command_preview(self, tech: dict[str, Any], mnemonic: str) -> str:
        if tech.get("valid_limbs"):
            return f"WEAPON {mnemonic} <target> <limb>"
        if str(tech.get("type") or "").strip().lower() == "aoe":
            return f"WEAPON {mnemonic}"
        return f"WEAPON {mnemonic} <target>"

    def _combat_maneuver_actions(self, session) -> list[dict]:
        actions = []
        for row in available_maneuver_summaries(session, self.server):
            key = str(row.get("mnemonic") or "").strip()
            if not key or str(row.get("type") or "").strip().lower() not in {"attack", "setup", "buff", "aoe", "concentration", "martial_stance"}:
                continue
            targeting = str(row.get("targeting") or "none").strip().lower()
            preview = f"CMAN {key}"
            if targeting.startswith("current_target"):
                preview += " <target>"
            actions.append(
                {
                    "key": key,
                    "label": str(row.get("name") or key.replace("_", " ").title()).strip(),
                    "short_label": str(row.get("name") or key.replace("_", " ").title()).strip(),
                    "command_preview": preview,
                    "description": str(row.get("description") or "").strip(),
                    "rank": int(row.get("rank", 0) or 0),
                    "targeting": targeting,
                    "ready_rule": row.get("ready_rule") if isinstance(row.get("ready_rule"), dict) else None,
                }
            )
        return actions

    def _combat_action_allowed(self, session, action_key: str) -> bool:
        guild_membership = getattr(session, "guild_membership", None) or {}
        guild_skills = getattr(session, "guild_skills", {}) or {}
        cm_ranks = int((getattr(session, "skills", {}) or {}).get(4, {}).get("ranks", 0) or 0)

        if action_key == "feint":
            return cm_ranks >= 1
        if guild_membership.get("guild_id") != "rogue":
            return False
        if action_key == "sweep":
            return int((guild_skills.get("Sweep") or {}).get("ranks", 0) or 0) > 0
        if action_key == "subdue":
            return (
                int((guild_skills.get("Subdue") or {}).get("ranks", 0) or 0) > 0
                and bool(getattr(session, "right_hand", None))
            )
        if action_key == "cheapshot":
            return int((guild_skills.get("Cheapshots") or {}).get("ranks", 0) or 0) > 0
        if action_key == "rgambit_divert":
            return int((guild_skills.get("Rogue Gambits") or {}).get("ranks", 0) or 0) > 0
        return False

    def _magic_actions(self, session) -> list[dict]:
        spellbook = [row for row in (getattr(session, "spellbook", []) or []) if isinstance(row, dict)]
        out = []
        for row in spellbook:
            spell_number = int(row.get("spell_number", 0) or 0)
            if spell_number <= 0:
                continue
            name = str(row.get("name") or row.get("mnemonic") or spell_number).strip()
            out.append({
                "key": str(spell_number),
                "label": f"{spell_number} {name}",
                "short_label": name,
                "command_preview": f"INCANT {spell_number}",
                "description": str(row.get("spell_type") or "spell").strip().title(),
                "targeting": "current_target_optional",
            })
        out.sort(key=lambda row: row["label"])
        return out

    def _normalize_category(self, raw: Any) -> str:
        key = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
        if key in ("two_handed", "twohanded_weapons", "two_handed_weapons"):
            return "twohanded"
        if key in ("blunt_weapons",):
            return "blunt"
        if key in ("edged_weapons",):
            return "edged"
        if key in ("polearm_weapons",):
            return "polearm"
        if key in ("ranged_weapons",):
            return "ranged"
        return key

    def _current_weapon_categories(self, session) -> set[str]:
        categories: set[str] = set()
        hands = [getattr(session, "right_hand", None), getattr(session, "left_hand", None)]
        has_non_brawling = False
        for item in hands:
            if not item or item.get("item_type") != "weapon":
                continue
            category = self._normalize_category(item.get("weapon_category") or item.get("weapon_type") or "")
            if not category:
                continue
            categories.add(category)
            if category != "brawling":
                has_non_brawling = True
        if not has_non_brawling:
            categories.add("brawling")
        return categories

    def _weapon_ready_rule(self, tech: dict[str, Any]) -> dict | None:
        rule = tech.get("hotbar_ready")
        if isinstance(rule, dict):
            return rule
        trigger = str(tech.get("reaction_trigger") or "").strip().lower()
        if not trigger:
            return None
        return {
            "kind": "reaction_trigger",
            "trigger": trigger,
            "message": self._reaction_message(trigger),
        }

    def _reaction_message(self, trigger: str) -> str:
        labels = {
            "recent_parry": "That technique requires a recent parry window.",
            "recent_block": "That technique requires a recent block window.",
            "recent_evade": "That technique requires a recent evade window.",
            "recent_evade_block_parry": "That technique requires a recent evade, block, or parry window.",
        }
        return labels.get(str(trigger or "").strip().lower(), "That technique is not ready yet.")

    def _slot_ready_state(self, session, action: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(action, dict):
            return {"ready": False, "ready_until": None, "message": ""}

        rule = action.get("ready_rule")
        if not isinstance(rule, dict):
            return {"ready": False, "ready_until": None, "message": ""}

        targeting = str(action.get("targeting") or "").strip().lower()
        target = self._resolve_target_entity(session, allow_first_room_target=False) if targeting.startswith("current_target") else None
        eval_rule = rule
        if targeting.startswith("current_target"):
            eval_rule = {
                "all_of": [{"kind": "target_required"}, rule],
                "message": str(rule.get("message") or ""),
            }
        return evaluate_ready_rule(
            eval_rule,
            session=session,
            server=self.server,
            target=target,
            rank=int(action.get("rank", 0) or 0),
        )

    def _resolve_saved_action(self, session, category_key: str, action_key: str) -> dict | None:
        if category_key == "weapon_techniques":
            defs = self.server.lua.get_weapon_techniques() or {}
            tech = defs.get(action_key)
            if isinstance(tech, dict):
                return {
                    "key": action_key,
                    "label": str(tech.get("name") or action_key.title()).strip(),
                    "short_label": str(tech.get("name") or action_key.title()).strip(),
                    "command_preview": self._weapon_command_preview(tech, action_key),
                }
        elif category_key == "combat_maneuvers":
            for row in available_maneuver_summaries(session, self.server):
                if str(row.get("mnemonic") or "").strip() == action_key:
                    targeting = str(row.get("targeting") or "none").strip().lower()
                    preview = f"CMAN {action_key}"
                    if targeting.startswith("current_target"):
                        preview += " <target>"
                    return {
                        "key": action_key,
                        "label": str(row.get("name") or action_key.replace("_", " ").title()).strip(),
                        "short_label": str(row.get("name") or action_key.replace("_", " ").title()).strip(),
                        "command_preview": preview,
                    }
        elif category_key == "magic":
            for row in (getattr(session, "spellbook", []) or []):
                if str(int(row.get("spell_number", 0) or 0)) == str(action_key):
                    name = str(row.get("name") or row.get("mnemonic") or action_key).strip()
                    return {
                        "key": action_key,
                        "label": f"{action_key} {name}",
                        "short_label": name,
                        "command_preview": f"INCANT {action_key}",
                    }
        return None

    async def assign_slot(self, session, slot_index: int, category_key: str, action_key: str) -> tuple[bool, str]:
        if not getattr(session, "character_id", None):
            return False, "Hotbar assignments require a character."
        if slot_index < 1 or slot_index > 9:
            return False, "Hotbar slot must be between 1 and 9."
        catalog = self._available_catalog(session)
        allowed = {
            (category["key"], action["key"])
            for category in catalog
            for action in category.get("actions", [])
        }
        if (category_key, action_key) not in allowed:
            return False, "That action is not currently valid for this character."
        db = getattr(self.server, "db", None)
        if not db or not db.save_character_hotbar_slot(session.character_id, slot_index, category_key, action_key):
            return False, "Could not save that hotbar assignment."
        slots = dict(getattr(session, "hotbar_slots", {}) or {})
        slots[int(slot_index)] = {
            "category_key": str(category_key),
            "action_key": str(action_key),
        }
        session.hotbar_slots = slots
        return True, "Hotbar slot updated."

    async def clear_slot(self, session, slot_index: int) -> tuple[bool, str]:
        if slot_index < 1 or slot_index > 9:
            return False, "Hotbar slot must be between 1 and 9."
        db = getattr(self.server, "db", None)
        if db and getattr(session, "character_id", None):
            db.clear_character_hotbar_slot(session.character_id, slot_index)
        slots = dict(getattr(session, "hotbar_slots", {}) or {})
        slots.pop(int(slot_index), None)
        session.hotbar_slots = slots
        return True, "Hotbar slot cleared."

    async def execute_slot(self, session, slot_index: int, target_name: str = "") -> tuple[bool, str]:
        slot_index = int(slot_index)
        assignment = (getattr(session, "hotbar_slots", {}) or {}).get(slot_index)
        if not assignment:
            return False, f"Hotbar slot {slot_index} is empty."

        category_key = str(assignment.get("category_key") or "").strip()
        action_key = str(assignment.get("action_key") or "").strip()
        catalog = self._available_catalog(session)
        action = None
        for category in catalog:
            if category.get("key") != category_key:
                continue
            for row in category.get("actions", []):
                if row.get("key") == action_key:
                    action = row
                    break
            if action:
                break

        if not action:
            return False, f"Hotbar slot {slot_index} is not available with your current loadout."

        command = self._command_for_action(session, category_key, action, target_name=target_name)
        if not command:
            return False, f"Hotbar slot {slot_index} cannot be used without a current target."

        await self.server.commands.handle(session, command)
        return True, ""

    def _command_for_action(self, session, category_key: str, action: dict[str, Any], *, target_name: str = "") -> str:
        action_key = str(action.get("key") or "").strip()
        targeting = str(action.get("targeting") or "").strip().lower()
        resolved_target = self._resolve_target_name(session, target_name)
        if category_key == "weapon_techniques":
            if targeting.startswith("current_target"):
                if not resolved_target:
                    return ""
                return f"weapon {action_key} {resolved_target}"
            return f"weapon {action_key}"
        if category_key == "magic":
            return f"incant {action_key}"
        if category_key == "combat_maneuvers":
            if targeting.startswith("current_target"):
                if not resolved_target:
                    return ""
                return f"cman {action_key} {resolved_target}"
            return f"cman {action_key}"
        return ""

    def _resolve_target_name(self, session, preferred_name: str = "") -> str:
        creature = self._resolve_target_entity(session, preferred_name=preferred_name, allow_first_room_target=True)
        if not creature:
            return ""

        try:
            session.target = creature
        except Exception:
            pass

        return str(
            getattr(creature, "name", None)
            or getattr(creature, "character_name", None)
            or getattr(creature, "full_name", None)
            or ""
        ).strip()

    def _resolve_target_entity(self, session, preferred_name: str = "", *, allow_first_room_target: bool) -> Any:
        creatures = getattr(self.server, "creatures", None)
        room = getattr(session, "current_room", None)
        room_id = getattr(room, "id", None)
        creature = None

        preferred = str(preferred_name or "").strip()
        if preferred and creatures and room_id:
            creature = creatures.find_creature_in_room(room_id, preferred)

        target = getattr(session, "target", None)
        if not creature and target and not getattr(target, "is_dead", False):
            if room:
                if hasattr(target, "current_room_id") and getattr(target, "current_room_id", None) not in (None, room.id):
                    target = None
                elif hasattr(target, "current_room") and getattr(getattr(target, "current_room", None), "id", room.id) != room.id:
                    target = None
            creature = target

        if not creature and allow_first_room_target and creatures and room_id:
            for candidate in (creatures.get_creatures_in_room(room_id) or []):
                if getattr(candidate, "is_dead", False):
                    continue
                if hasattr(candidate, "alive") and not getattr(candidate, "alive", True):
                    continue
                creature = candidate
                break

        return creature
