"""
Spellcasting command bridge.

Routes player spell verbs into the Lua spell engine while keeping spell data and
effect logic in Lua.
"""

import logging
import re

from server.core.protocol.colors import colorize, roundtime_msg, TextPresets

log = logging.getLogger(__name__)


def _get_spell_engine(server):
    lua = getattr(server, "lua", None)
    if not lua or not lua.engine:
        return None, None
    try:
        return lua.engine, lua.engine.require("globals/magic/spell_engine")
    except Exception as e:
        log.error("spellcasting: failed to load Lua spell engine: %s", e, exc_info=True)
        return lua.engine, None


def _lua_returns(raw):
    if isinstance(raw, tuple):
        return raw
    return (raw,)


def _equipped_armor_asg(session):
    asg = 1
    for item in getattr(session, "inventory", []) or []:
        if item.get("item_type") == "armor" and item.get("slot"):
            try:
                asg = max(asg, int(item.get("armor_asg") or 1))
            except (TypeError, ValueError):
                pass
    return asg


def _session_to_spell_entity(session):
    room_id = session.current_room.id if getattr(session, "current_room", None) else 0
    return {
        "id": int(getattr(session, "character_id", 0) or 0),
        "name": getattr(session, "character_name", "someone") or "someone",
        "level": int(getattr(session, "level", 1) or 1),
        "profession_id": int(getattr(session, "profession_id", 0) or 0),
        "race_id": int(getattr(session, "race_id", 12) or 12),
        "mana_current": int(getattr(session, "mana_current", 0) or 0),
        "mana_max": int(getattr(session, "mana_max", 0) or 0),
        "position": getattr(session, "stance", "neutral") or "neutral",
        "stance": getattr(session, "stance", "neutral") or "neutral",
        "current_room_id": int(room_id or 0),
        "torso_armor_asg": _equipped_armor_asg(session),
        "in_sanctuary": bool(getattr(getattr(session, "current_room", None), "is_sanctuary", False)),
        "stat_strength": int(getattr(session, "stat_strength", 50) or 50),
        "stat_constitution": int(getattr(session, "stat_constitution", 50) or 50),
        "stat_dexterity": int(getattr(session, "stat_dexterity", 50) or 50),
        "stat_agility": int(getattr(session, "stat_agility", 50) or 50),
        "stat_discipline": int(getattr(session, "stat_discipline", 50) or 50),
        "stat_aura": int(getattr(session, "stat_aura", 50) or 50),
        "stat_logic": int(getattr(session, "stat_logic", 50) or 50),
        "stat_intuition": int(getattr(session, "stat_intuition", 50) or 50),
        "stat_wisdom": int(getattr(session, "stat_wisdom", 50) or 50),
        "stat_influence": int(getattr(session, "stat_influence", 50) or 50),
    }


def _player_target_entity(target_session):
    entity = _session_to_spell_entity(target_session)
    entity["ranged_ds"] = 0
    entity["ds_bolt"] = 0
    entity["td"] = 0
    return entity


def _creature_to_spell_entity(creature):
    return {
        "id": int(getattr(creature, "id", 0) or 0),
        "name": getattr(creature, "name", "creature") or "creature",
        "level": int(getattr(creature, "level", 1) or 1),
        "race_id": 12,
        "position": getattr(creature, "stance", "neutral") or "neutral",
        "stance": getattr(creature, "stance", "neutral") or "neutral",
        "current_room_id": int(getattr(creature, "current_room_id", 0) or 0),
        "torso_armor_asg": int(getattr(creature, "armor_asg", 1) or 1),
        "ranged_ds": int(getattr(creature, "ds_ranged", 0) or 0),
        "ds_bolt": int(getattr(creature, "ds_bolt", 0) or 0),
        "td": int(getattr(creature, "td", 0) or 0),
        "stat_strength": 50,
        "stat_constitution": 50,
        "stat_dexterity": 50,
        "stat_agility": 50,
        "stat_discipline": 50,
        "stat_aura": 50,
        "stat_logic": 50,
        "stat_intuition": 50,
        "stat_wisdom": 50,
        "stat_influence": 50,
    }


def _resolve_room_target(session, server, target_name):
    room = getattr(session, "current_room", None)
    if not room or not target_name:
        return None

    target_name = target_name.strip().lower()
    for player in server.world.get_players_in_room(room.id):
        if player is session:
            continue
        pname = (getattr(player, "character_name", "") or "").lower()
        if pname.startswith(target_name):
            return player

    if hasattr(server, "creatures"):
        creature = server.creatures.find_creature_in_room(room.id, target_name)
        if creature and getattr(creature, "alive", True):
            return creature

    return None


def _resolve_default_target(session):
    target = getattr(session, "target", None)
    if not target:
        return None
    room = getattr(session, "current_room", None)
    if not room:
        return None
    if hasattr(target, "current_room") and getattr(target.current_room, "id", None) == room.id:
        return target
    if getattr(target, "current_room_id", None) == room.id:
        return target
    return None


def _target_to_entity(target):
    if target is None:
        return None
    if hasattr(target, "character_id"):
        return _player_target_entity(target)
    return _creature_to_spell_entity(target)


def _split_spell_and_target(session, server, args):
    parts = (args or "").strip().split()
    if len(parts) < 2:
        return (args or "").strip(), None

    max_target_words = min(3, len(parts) - 1)
    for target_words in range(max_target_words, 0, -1):
        target_phrase = " ".join(parts[-target_words:])
        target_obj = _resolve_room_target(session, server, target_phrase)
        if target_obj:
            spell_arg = " ".join(parts[:-target_words]).strip()
            if spell_arg:
                return spell_arg, target_obj

    return (args or "").strip(), None


def _prepared_scroll_state(session):
    state = getattr(session, "prepared_spell", None)
    if state:
        return state
    return getattr(session, "_prepared_spell", None)


def _clear_prepared_scroll_state(session):
    session.prepared_spell = None
    if hasattr(session, "_prepared_spell"):
        session._prepared_spell = None


def _apply_lua_char_updates(engine, lua_char, session):
    try:
        updated = engine.lua_to_python(lua_char)
    except Exception:
        updated = None
    if isinstance(updated, dict) and "mana_current" in updated:
        session.mana_current = int(updated.get("mana_current") or 0)


def _refresh_post_spell_state(session, server):
    if not getattr(server, "db", None) or not getattr(session, "character_id", None):
        return
    try:
        session.fame = int(server.db.get_character_fame(session.character_id) or 0)
    except Exception:
        pass


def _cast_roundtime(prepared_state=None):
    if prepared_state and int(prepared_state.get("number") or 0) == 1700:
        return 5
    return 3


async def cmd_send(session, cmd, args, server):
    """SEND <amount> TO <target> - Share mana using the matching mana control skill."""
    text = (args or "").strip()
    if not text:
        await session.send_line("Send how much mana to whom?")
        return

    match = re.match(r"^(?P<amount>\d+)\s+to\s+(?P<target>.+)$", text, re.IGNORECASE)
    if not match:
        match = re.match(r"^(?P<target>.+?)\s+(?P<amount>\d+)$", text, re.IGNORECASE)
    if not match:
        await session.send_line("Usage: SEND <amount> TO <person>")
        return

    amount = int(match.group("amount") or 0)
    target_name = (match.group("target") or "").strip()
    if amount <= 0:
        await session.send_line("You must send at least 1 mana.")
        return
    if amount > int(getattr(session, "mana_current", 0) or 0):
        await session.send_line("You do not have that much mana to send.")
        return

    target = _resolve_room_target(session, server, target_name)
    if not target or not hasattr(target, "character_id"):
        await session.send_line(f"You do not see any player here matching '{target_name}'.")
        return
    if target is session:
        await session.send_line("You are already carrying your own mana.")
        return

    if int(getattr(target, "mana_current", 0) or 0) >= int(getattr(target, "mana_max", 0) or 0):
        await session.send_line(f"{target.character_name} cannot accept any more mana right now.")
        return

    engine, _spell_engine = _get_spell_engine(server)
    if not engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    try:
        mana_mod = engine.require("globals/magic/mana_system")
        ranks = getattr(session, "skills", {}) or {}
        sender_prof = int(getattr(session, "profession_id", 0) or 0)
        target_prof = int(getattr(target, "profession_id", 0) or 0)

        sphere_by_prof = {
            3: "elemental", 4: "spirit", 5: "spirit", 6: "spirit",
            7: "spirit", 8: "mental", 9: "spirit", 10: "mental",
        }
        preferred = sphere_by_prof.get(sender_prof) or sphere_by_prof.get(target_prof) or "spirit"
        skill_id = {"elemental": 19, "spirit": 20, "mental": 21}[preferred]

        sender_skill = ranks.get(skill_id, {}) if isinstance(ranks, dict) else {}
        receiver_skill = (getattr(target, "skills", {}) or {}).get(skill_id, {})
        sender_bonus = int(sender_skill.get("bonus", 0) or 0) if isinstance(sender_skill, dict) else 0
        receiver_bonus = int(receiver_skill.get("bonus", 0) or 0) if isinstance(receiver_skill, dict) else 0

        actual = int(engine.call_hook(mana_mod, "calc_sharing", amount, sender_bonus, receiver_bonus) or 0)
    except Exception as e:
        log.error("SEND failed to use Lua mana sharing: %s", e, exc_info=True)
        await session.send_line("Mana sharing is unavailable right now.")
        return

    actual = max(0, min(actual, int(getattr(target, "mana_max", 0) or 0) - int(getattr(target, "mana_current", 0) or 0)))
    if actual <= 0:
        await session.send_line("The mana dissipates before your target can benefit from it.")
        return

    session.mana_current = max(0, int(session.mana_current) - amount)
    target.mana_current = min(int(target.mana_max or 0), int(target.mana_current or 0) + actual)

    if getattr(server, "db", None):
        try:
            server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver,
            )
            server.db.save_character_resources(
                target.character_id,
                target.health_current, target.mana_current,
                target.spirit_current, target.stamina_current,
                target.silver,
            )
        except Exception:
            pass

    loss = max(0, amount - actual)
    await session.send_line(colorize(
        f"You send {amount} mana to {target.character_name}, who receives {actual} mana"
        + (f" after {loss} mana bleeds away." if loss else "."),
        TextPresets.SYSTEM,
    ))
    await target.send_line(colorize(
        f"{session.character_name} sends you {actual} mana.",
        TextPresets.SYSTEM,
    ))
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "mana_share_success")
        except Exception:
            pass
    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_prepare(session, cmd, args, server):
    spell_arg = (args or "").strip()
    if not spell_arg:
        await session.send_line("Prepare which spell?")
        return

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session))
    raw = engine.call_hook(spell_engine, "prepare", raw_char, spell_arg)
    ok, message = _lua_returns(raw)[:2]
    if ok:
        _clear_prepared_scroll_state(session)
        await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
    else:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))


async def cmd_release(session, cmd, args, server):
    prepared = _prepared_scroll_state(session)
    if prepared:
        spell_name = prepared.get("name") or f"spell {prepared.get('number', '?')}"
        _clear_prepared_scroll_state(session)
        await session.send_line(colorize(f"  You release the {spell_name} spell.", TextPresets.SYSTEM))
        return

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session))
    raw = engine.call_hook(spell_engine, "release", raw_char)
    ok, message = _lua_returns(raw)[:2]
    preset = TextPresets.SYSTEM if ok else TextPresets.WARNING
    await session.send_line(colorize(f"  {message}", preset))


async def cmd_cast(session, cmd, args, server):
    target = None
    if (args or "").strip():
        target = _resolve_room_target(session, server, args.strip())
        if not target:
            await session.send_line(f"You don't see '{args.strip()}' here.")
            return
    else:
        target = _resolve_default_target(session)

    prepared = _prepared_scroll_state(session)
    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session))
    raw_target = engine.python_to_lua(_target_to_entity(target)) if target else None
    verb = (cmd or "cast").strip().lower()

    if prepared:
        spell_number = int(prepared.get("number") or 0)
        raw = engine.call_hook(
            spell_engine,
            "cast_direct",
            raw_char,
            raw_target,
            spell_number,
            verb,
            None,
            True,
        )
        values = _lua_returns(raw)
        ok = bool(values[0]) if values else False
        message = values[1] if len(values) > 1 else "The spell fizzles."
        if ok:
            _clear_prepared_scroll_state(session)
            await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
            if getattr(server, "guild", None):
                try:
                    await server.guild.record_event(session, "spell_cast_success")
                except Exception:
                    pass
            rt = _cast_roundtime(prepared)
            session.set_roundtime(rt)
            await session.send_line(roundtime_msg(rt))
        else:
            await session.send_line(colorize(f"  {message}", TextPresets.WARNING))
        return

    raw = engine.call_hook(spell_engine, "cast", raw_char, raw_target, verb)
    values = _lua_returns(raw)
    ok = bool(values[0]) if values else False
    message = values[1] if len(values) > 1 else "The spell fizzles."
    _apply_lua_char_updates(engine, raw_char, session)
    _refresh_post_spell_state(session, server)
    if ok:
        await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
        if getattr(server, "guild", None):
            try:
                await server.guild.record_event(session, "spell_cast_success")
            except Exception:
                pass
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
    else:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))


async def cmd_incant(session, cmd, args, server):
    spell_arg, target_obj = _split_spell_and_target(session, server, args)
    if not spell_arg:
        await session.send_line("Incant which spell?")
        return

    if not target_obj:
        target_obj = _resolve_default_target(session)

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session))
    raw_target = engine.python_to_lua(_target_to_entity(target_obj)) if target_obj else None
    raw = engine.call_hook(spell_engine, "incant", raw_char, spell_arg, raw_target, "cast")
    values = _lua_returns(raw)
    ok = bool(values[0]) if values else False
    message = values[1] if len(values) > 1 else "The spell fizzles."
    _apply_lua_char_updates(engine, raw_char, session)
    _refresh_post_spell_state(session, server)
    if ok:
        _clear_prepared_scroll_state(session)
        await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
        if getattr(server, "guild", None):
            try:
                await server.guild.record_event(session, "spell_cast_success")
            except Exception:
                pass
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
    else:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))
