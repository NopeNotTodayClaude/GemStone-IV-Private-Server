from __future__ import annotations

import ast
import re
import subprocess
import sys
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ZONES = SCRIPTS / "zones"
AG_FILE = SCRIPTS / "data" / "adventurers_guild.lua"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lupa import LuaRuntime

from server.core.entity.creature import ai_runtime
from server.core.entity.creature.lua_mob_loader import load_all_mob_luas


def _handled_ability_ids() -> set[str]:
    handled: set[str] = set()
    for name in (
        "_STATUS_ABILITY_MAP",
        "_PREDATORY_ABILITIES",
        "_SELF_HEAL_ABILITIES",
        "_SELF_BUFF_ABILITIES",
        "_DIRECT_ATTACK_ABILITIES",
        "_DISARM_ABILITIES",
        "_REGEN_ABILITIES",
        "_SPECIAL_LOOT_BY_ABILITY",
    ):
        obj = getattr(ai_runtime, name, {})
        if isinstance(obj, dict):
            handled.update(str(k) for k in obj.keys())
    handled.update(
        {
            "pack_tactics",
            "pack_hunting",
            "formation_fighting",
            "rapid_decay",
            "cave_sight",
            "tunnel_sight",
            "scouting_awareness",
            "blindness_immunity",
            "burrowing_escape",
            "cold_immune",
            "cold_immunity",
            "fire_immune",
            "gremlin_eat_grub",
            "holding_song_immune",
            "swim",
            "wall_climb",
            "hurl_weapon",
            "stone_throw",
            "pickpocket_attempt",
            "steal_item",
        }
    )
    return handled


def _load_ag_config():
    lua = LuaRuntime(unpack_returned_tuples=True)
    return lua.execute(AG_FILE.read_text(encoding="utf-8", errors="ignore"))


def _authored_low_level_abilities() -> set[str]:
    abilities: set[str] = set()
    for path in ZONES.rglob("*.lua"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Creature\.level\s*=\s*(\d+)", text)
        if not m or int(m.group(1)) > 25:
            continue
        am = re.search(r"Creature\.abilities\s*=\s*\{(.*?)\}", text, re.S)
        if not am:
            continue
        abilities.update(re.findall(r'"([^"]+)"', am.group(1)))
    return abilities


def _validate_lua_compile() -> list[str]:
    luac = None
    override = str(os.environ.get("LUAC_PATH") or "").strip()
    if override:
        candidate = Path(override).expanduser()
        if candidate.exists():
            luac = candidate
    if not luac:
        found = shutil.which("luac")
        if found:
            luac = Path(found)
    if not luac:
        return ["luac.exe not found"]

    errors: list[str] = []
    for path in ZONES.rglob("*.lua"):
        proc = subprocess.run([str(luac), "-p", str(path)], capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append(f"{path}: {proc.stderr.strip() or proc.stdout.strip()}")
    return errors


def main() -> int:
    mobs = load_all_mob_luas(str(SCRIPTS))
    ag = _load_ag_config()

    errors: list[str] = []

    low_level = {k: v for k, v in mobs.items() if int(v.get("level", 999) or 999) <= 25}
    if not low_level:
        errors.append("No level <= 25 creature templates loaded.")

    missing_spawn = sorted(k for k, v in low_level.items() if not v.get("spawn_rooms"))
    if missing_spawn:
        errors.append(f"Low-level creatures missing spawn_rooms: {missing_spawn}")

    handled = _handled_ability_ids()
    authored = _authored_low_level_abilities()
    dead_tags = sorted(authored - handled)
    if dead_tags:
        errors.append(f"Unhandled low-level ability tags: {dead_tags}")

    for town, rows in ag["bounties"].items():
        for _idx, row in rows.items():
            key = str(row["key"])
            for field in ("target_template_id", "encounter_template_id", "escort_enemy_template_id", "rescue_enemy_template_id"):
                value = row[field]
                if value and str(value) not in mobs:
                    errors.append(f"{town}/{key}: missing creature template for {field}={value}")

    lua_errors = _validate_lua_compile()
    errors.extend(lua_errors)

    print(f"Loaded creatures <=25: {len(low_level)}")
    print(f"Low-level creatures with abilities: {sum(1 for row in low_level.values() if row.get('abilities'))}")
    print(f"Low-level creatures with special_loot: {sum(1 for row in low_level.values() if row.get('special_loot'))}")
    print(f"Low-level authored ability tags: {len(authored)}")

    if errors:
        print("\nVALIDATION FAILED")
        for line in errors:
            print(f"- {line}")
        return 1

    print("\nVALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
