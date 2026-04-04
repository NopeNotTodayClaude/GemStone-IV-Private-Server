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
from server.core.scripting.lua_bindings.combat_maneuver_api import (
    available_maneuver_summaries,
    hotbar_child_maneuver_summaries,
)

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
        prepared_magic_number = self._prepared_magic_number(session)
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
                "prepared": bool(
                    category_key == "magic"
                    and prepared_magic_number > 0
                    and action_key == str(prepared_magic_number)
                ),
                "submenu_label": str((action or {}).get("submenu_label") or ""),
                "submenu_actions": list((action or {}).get("submenu_actions") or []),
                "pulse": bool(ready_state.get("ready")),
                "pulse_until": ready_state.get("ready_until"),
                "pulse_reason": str(ready_state.get("message") or ""),
            })

        return {
            "slots": slots,
            "prepared_magic_number": prepared_magic_number,
            "catalog": {"categories": catalog},
        }

    def _category_label(self, category_key: str) -> str:
        for entry in self._cfg().get("categories", []) or []:
            if str(entry.get("key") or "").strip() == category_key:
                return str(entry.get("label") or category_key.replace("_", " ").title())
        return category_key.replace("_", " ").title()

    def _targeting_summary(self, targeting: str) -> str:
        targeting = str(targeting or "").strip().lower()
        if targeting == "current_target":
            return "Requires a current target."
        if targeting == "current_target_optional":
            return "Uses your current target when available."
        if targeting == "room_player_or_self":
            return "Second click targets a visible player, or yourself when alone."
        if targeting == "room_player_only":
            return "Second click chooses a visible player in the room."
        if targeting == "self_only":
            return "Casts on yourself."
        if targeting == "none":
            return "Does not require a target."
        return ""

    def _build_tooltip_text(self, title: str, description: str = "", *, stats: list[str] | None = None, command_preview: str = "", targeting: str = "") -> str:
        lines = [str(title or "").strip()]
        if description:
            lines.append(str(description).strip())
        for stat in (stats or []):
            stat_text = str(stat or "").strip()
            if stat_text:
                lines.append(stat_text)
        targeting_text = self._targeting_summary(targeting)
        if targeting_text:
            lines.append(targeting_text)
        if command_preview:
            lines.append(f"Use: {str(command_preview).strip()}")
        return "\n".join([line for line in lines if line])

    def _magic_tooltip_text(self, row: dict[str, Any], spell_number: int, name: str) -> str:
        description = str(row.get("description") or "").strip() or "No description available yet."
        mana_cost = int(row.get("mana_cost", 0) or 0)
        cast_rt = int(row.get("cast_roundtime", 0) or 0)
        spell_type = str(row.get("spell_type") or "spell").strip().title()
        activation = str(row.get("activation_verbs") or "cast").strip().upper()
        stats = [f"Mana: {mana_cost}", f"Type: {spell_type}"]
        if cast_rt > 0:
            stats.append(f"Cast RT: {cast_rt}s")
        if activation:
            stats.append(f"Verb: {activation}")
        submenu_actions, _default_subaction_key = self._magic_submenu_actions(row, spell_number, name)
        targeting = str(row.get("targeting_mode") or "").strip().lower()
        command_preview = f"PREPARE {spell_number}, then CAST"
        if submenu_actions:
            stats.append("Second Click: Choose Harm or Heal")
            spell_cfg = self._spell_hotbar_entry(spell_number)
            custom_preview = str((spell_cfg or {}).get("command_preview") or "").strip()
            if custom_preview:
                command_preview = custom_preview
            targeting = "none"
        return self._build_tooltip_text(
            f"{spell_number} {name}",
            description,
            stats=stats,
            command_preview=command_preview,
            targeting=targeting,
        )

    def _spell_hotbar_cfg(self) -> dict:
        lua = getattr(self.server, "lua", None)
        if not lua:
            return {}
        return lua.get_spell_hotbar() or {}

    def _spell_hotbar_entry(self, spell_number: int) -> dict[str, Any]:
        cfg = self._spell_hotbar_cfg()
        by_spell = cfg.get("by_spell") or {}
        if isinstance(by_spell, dict):
            entry = by_spell.get(spell_number) or by_spell.get(str(spell_number)) or {}
            return entry if isinstance(entry, dict) else {}
        if isinstance(by_spell, list):
            for raw in by_spell:
                if not isinstance(raw, dict):
                    continue
                raw_number = raw.get("spell_number")
                try:
                    if int(raw_number or 0) == int(spell_number):
                        return raw
                except Exception:
                    continue
        return {}

    def _magic_submenu_actions(self, row: dict[str, Any], spell_number: int, name: str) -> tuple[list[dict[str, Any]], str]:
        spell_cfg = self._spell_hotbar_entry(spell_number)
        if not isinstance(spell_cfg, dict):
            return [], ""
        raw_actions = spell_cfg.get("actions") or []
        out = []
        default_key = ""
        for raw in raw_actions:
            if not isinstance(raw, dict):
                continue
            key = str(raw.get("key") or "").strip().lower()
            label = str(raw.get("label") or "").strip()
            if not key or not label:
                continue
            targeting = str(raw.get("targeting") or "none").strip().lower()
            command_preview = str(raw.get("command_preview") or "").strip()
            description = str(raw.get("description") or "").strip()
            tooltip = self._build_tooltip_text(
                f"{spell_number} {name} — {label}",
                description,
                command_preview=command_preview,
                targeting=targeting,
            )
            out.append({
                "key": key,
                "label": label,
                "short_label": label,
                "verb": str(raw.get("verb") or "cast").strip().lower() or "cast",
                "targeting": targeting,
                "command_preview": command_preview,
                "description": description,
                "tooltip": tooltip,
            })
            if not default_key:
                default_key = key
        return out, default_key

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
                "tooltip": self._build_tooltip_text(
                    str(tech.get("name") or canonical.title()).strip(),
                    str(tech.get("description") or "").strip(),
                    command_preview=self._weapon_command_preview(tech, canonical),
                    targeting="current_target_optional" if str(tech.get("type") or "").strip().lower() == "aoe" else "current_target",
                ),
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
        summaries = available_maneuver_summaries(session, self.server)
        actions = []
        parents: dict[str, dict[str, Any]] = {}
        parent_defaults: dict[str, str] = {}
        children_by_parent: dict[str, list[dict[str, Any]]] = {}
        for row in summaries:
            key = str(row.get("mnemonic") or "").strip()
            if not key or str(row.get("type") or "").strip().lower() not in {"attack", "setup", "buff", "aoe", "concentration", "martial_stance"}:
                continue
            targeting = str(row.get("targeting") or "none").strip().lower()
            subcommand_prefix = str(row.get("hotbar_subcommand") or "").strip().lower()
            if subcommand_prefix and str(row.get("hotbar_default_child") or "").strip():
                preview = subcommand_prefix.upper()
            else:
                preview = f"{subcommand_prefix.upper() or 'CMAN'} {key}".strip()
            if targeting.startswith("current_target"):
                preview += " <target>"
            action = {
                "key": key,
                "label": str(row.get("name") or key.replace("_", " ").title()).strip(),
                "short_label": str(row.get("name") or key.replace("_", " ").title()).strip(),
                "command_preview": preview,
                "description": str(row.get("description") or "").strip(),
                "rank": int(row.get("rank", 0) or 0),
                "targeting": targeting,
                "ready_rule": row.get("ready_rule") if isinstance(row.get("ready_rule"), dict) else None,
                "submenu_label": "",
                "submenu_actions": [],
                "default_subaction_key": "",
                "subcommand_prefix": subcommand_prefix,
                "tooltip": self._build_tooltip_text(
                    str(row.get("name") or key.replace("_", " ").title()).strip(),
                    str(row.get("description") or "").strip(),
                    stats=[f"Rank: {int(row.get('rank', 0) or 0)}"],
                    command_preview=preview,
                    targeting=targeting,
                ),
            }
            parent_key = str(row.get("hotbar_parent") or "").strip().lower()
            if parent_key:
                children_by_parent.setdefault(parent_key, [])
                continue
            parents[key] = action
            parent_defaults[key] = str(row.get("hotbar_default_child") or "").strip().lower()
            actions.append(action)
        for parent_key in list(children_by_parent.keys()):
            parent = parents.get(parent_key)
            if not parent:
                continue
            children = []
            prefix = str(parent.get("subcommand_prefix") or "").strip().lower()
            for child_row in hotbar_child_maneuver_summaries(session, self.server, parent_key):
                child_targeting = str(child_row.get("targeting") or parent.get("targeting") or "none").strip().lower()
                preview = f"{prefix.upper() or 'CMAN'} {child_row['mnemonic']}".strip()
                if child_targeting.startswith("current_target"):
                    preview += " <target>"
                unlock_skill = str(child_row.get("guild_unlock_skill") or "").strip()
                unlock_rank = int(child_row.get("guild_unlock_rank", 0) or 0)
                lock_label = ""
                if not child_row.get("unlocked") and unlock_skill and unlock_rank > 0:
                    lock_label = f"Requires {unlock_skill} rank {unlock_rank}"
                children.append({
                    "key": str(child_row.get("mnemonic") or "").strip().lower(),
                    "label": str(child_row.get("name") or "").strip(),
                    "short_label": str(child_row.get("name") or "").strip(),
                    "command_preview": preview,
                    "targeting": child_targeting,
                    "enabled": bool(child_row.get("unlocked")),
                    "lock_label": lock_label,
                    "unlock_rank": unlock_rank,
                    "tooltip": self._build_tooltip_text(
                        str(child_row.get("name") or "").strip(),
                        str(child_row.get("description") or parent.get("description") or "").strip(),
                        stats=([lock_label] if lock_label else []) + ([f"Guild Rank: {unlock_rank}"] if unlock_rank > 0 else []),
                        command_preview=preview,
                        targeting=child_targeting,
                    ),
                })
            default_key = str(parent_defaults.get(parent_key) or "").strip().lower()
            if default_key and not any(str(row.get("key") or "").strip().lower() == default_key for row in children):
                default_key = ""
            if not default_key:
                default_key = str(children[0].get("key") if children else "" or "").strip().lower()
            children.sort(
                key=lambda row: (
                    0 if str(row.get("key") or "").strip().lower() == default_key else 1,
                    int(row.get("unlock_rank", 0) or 0),
                    row["label"],
                )
            )
            parent["submenu_label"] = parent["label"]
            parent["submenu_actions"] = children
            parent["default_subaction_key"] = default_key
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
            submenu_actions, default_subaction_key = self._magic_submenu_actions(row, spell_number, name)
            spell_cfg = self._spell_hotbar_entry(spell_number)
            command_preview = f"PREPARE {spell_number} / CAST"
            if submenu_actions:
                custom_preview = str((spell_cfg or {}).get("command_preview") or "").strip()
                if custom_preview:
                    command_preview = custom_preview
            out.append({
                "key": str(spell_number),
                "label": f"{spell_number} {name}",
                "short_label": name,
                "command_preview": command_preview,
                "description": str(row.get("description") or "").strip(),
                "targeting": str(row.get("targeting_mode") or "current_target_optional").strip().lower(),
                "tooltip": self._magic_tooltip_text(row, spell_number, name),
                "submenu_label": str((spell_cfg or {}).get("submenu_label") or "").strip(),
                "submenu_actions": submenu_actions,
                "default_subaction_key": default_subaction_key,
            })
        out.sort(key=lambda row: row["label"])
        return out

    def _prepared_magic_number(self, session) -> int:
        prepared = getattr(session, "prepared_spell", None)
        if isinstance(prepared, dict):
            try:
                return int(prepared.get("number") or 0)
            except Exception:
                return 0
        try:
            return int(getattr(session, "_prepared_lua_spell_number", 0) or 0)
        except Exception:
            return 0

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
                        "command_preview": f"PREPARE {action_key} / CAST",
                        "targeting": str(row.get("targeting_mode") or "current_target_optional").strip().lower(),
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

    async def execute_slot(self, session, slot_index: int, target_name: str = "", subaction_key: str = "") -> tuple[bool, str]:
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

        command = self._command_for_action(session, category_key, action, target_name=target_name, subaction_key=subaction_key)
        if not command:
            return False, f"Hotbar slot {slot_index} cannot be used without a current target."

        await self.server.commands.handle(session, command)
        return True, ""

    def _command_for_action(self, session, category_key: str, action: dict[str, Any], *, target_name: str = "", subaction_key: str = "") -> str:
        action_key = str(action.get("key") or "").strip()
        targeting = str(action.get("targeting") or "").strip().lower()
        resolved_target = self._resolve_target_name(session, target_name, targeting=targeting)
        if category_key == "weapon_techniques":
            if targeting.startswith("current_target"):
                if not resolved_target:
                    return ""
                return f"weapon {action_key} {resolved_target}"
            return f"weapon {action_key}"
        if category_key == "magic":
            prepared_number = self._prepared_magic_number(session)
            if prepared_number == int(action_key or 0):
                child_map = {
                    str(row.get("key") or "").strip().lower(): row
                    for row in (action.get("submenu_actions") or [])
                    if isinstance(row, dict) and str(row.get("key") or "").strip()
                }
                chosen = None
                chosen_targeting = targeting
                chosen_verb = "cast"
                if child_map:
                    chosen_key = str(subaction_key or action.get("default_subaction_key") or "").strip().lower()
                    chosen = child_map.get(chosen_key) or next(iter(child_map.values()), None)
                    if not chosen:
                        return ""
                    chosen_targeting = str(chosen.get("targeting") or targeting).strip().lower()
                    chosen_verb = str(chosen.get("verb") or "cast").strip().lower() or "cast"
                    resolved_target = self._resolve_target_name(session, target_name, targeting=chosen_targeting)
                if chosen_targeting == "room_player_only" and not resolved_target:
                    return ""
                if chosen_targeting in {"room_player_or_self", "self_only"} and resolved_target == "__SELF__":
                    return f"{chosen_verb} self"
                if chosen_targeting.startswith("current_target"):
                    if resolved_target:
                        return f"{chosen_verb} {resolved_target}"
                    if chosen_targeting == "current_target":
                        return ""
                    return chosen_verb
                if chosen_targeting == "room_player_or_self":
                    if resolved_target:
                        return f"{chosen_verb} {resolved_target}"
                    return chosen_verb
                if chosen_targeting == "room_player_only" and not resolved_target:
                    return ""
                if chosen_targeting == "self_only" and resolved_target == "__SELF__":
                    return f"{chosen_verb} self"
                if resolved_target:
                    return f"{chosen_verb} {resolved_target}"
                return chosen_verb
            return f"prepare {action_key}"
        if category_key == "combat_maneuvers":
            submenu_actions = [row for row in (action.get("submenu_actions") or []) if isinstance(row, dict)]
            if submenu_actions:
                child_map = {
                    str(row.get("key") or "").strip().lower(): row
                    for row in submenu_actions
                    if str(row.get("key") or "").strip()
                }
                chosen_key = str(subaction_key or action.get("default_subaction_key") or "").strip().lower()
                chosen = child_map.get(chosen_key) or next(iter(child_map.values()), None)
                if not chosen:
                    return ""
                if not bool(chosen.get("enabled", True)):
                    return ""
                chosen_targeting = str(chosen.get("targeting") or targeting).strip().lower()
                if chosen_targeting.startswith("current_target"):
                    if not resolved_target:
                        return ""
                    prefix = str(action.get("subcommand_prefix") or "").strip().lower()
                    if prefix:
                        return f"{prefix} {chosen['key']} {resolved_target}"
                    return f"cman {chosen['key']} {resolved_target}"
                prefix = str(action.get("subcommand_prefix") or "").strip().lower()
                if prefix:
                    return f"{prefix} {chosen['key']}"
                return f"cman {chosen['key']}"
            if targeting.startswith("current_target"):
                if not resolved_target:
                    return ""
                return f"cman {action_key} {resolved_target}"
            return f"cman {action_key}"
        return ""

    def _resolve_target_name(self, session, preferred_name: str = "", *, targeting: str = "") -> str:
        targeting = str(targeting or "").strip().lower()
        if targeting in {"room_player_or_self", "room_player_only", "self_only"}:
            player_target = self._resolve_player_target(session, preferred_name=preferred_name, allow_self=targeting != "room_player_only")
            if player_target is session:
                return "__SELF__"
            if not player_target:
                return ""
            return str(getattr(player_target, "character_name", "") or "").strip()

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

    def _resolve_player_target(self, session, preferred_name: str = "", *, allow_self: bool) -> Any:
        room = getattr(session, "current_room", None)
        if not room:
            return None
        preferred = str(preferred_name or "").strip().lower()
        self_aliases = {
            "self",
            "me",
            str(getattr(session, "character_name", "") or "").strip().lower(),
        }
        if allow_self and preferred and preferred in self_aliases:
            return session

        world = getattr(self.server, "world", None)
        if not world:
            return session if allow_self and not preferred else None

        visible_players = []
        for other in (world.get_players_in_room(room.id) or []):
            if other is session and not allow_self:
                continue
            visible_players.append(other)

        if preferred:
            for other in visible_players:
                name = str(getattr(other, "character_name", "") or "").strip().lower()
                if name.startswith(preferred):
                    return other
            return None

        if allow_self:
            return session
        return None

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
            if target is None:
                try:
                    session.target = None
                except Exception:
                    pass
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
