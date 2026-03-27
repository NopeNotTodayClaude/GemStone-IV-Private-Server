"""
GemStone IV Social/Action Commands
STAND, SIT, KNEEL, LIE, and all emote/social verbs.
BOW, WAVE, NOD, GRIN, SMILE, FROWN, LAUGH, CRY, SIGH, SHRUG,
WINCE, PONDER, GASP, GROAN, DANCE, CHEER, SALUTE, CURTSY,
GROWL, SNICKER, CACKLE, HUG, KISS
"""

import logging
import random
import time

log = logging.getLogger(__name__)


def _open_d100_roll():
    roll = random.randint(1, 100)
    if roll >= 96:
        roll += random.randint(1, 100)
    elif roll <= 5:
        roll -= random.randint(1, 10)
    return roll


def _pick_skill_bonus(ranks: int) -> int:
    if ranks <= 0:
        return 0
    if ranks <= 10:
        return ranks * 5
    if ranks <= 20:
        return 50 + (ranks - 10) * 4
    if ranks <= 30:
        return 90 + (ranks - 20) * 3
    if ranks <= 40:
        return 120 + (ranks - 30) * 2
    return 140 + (ranks - 40)


def _live_skill_bonus(session, skill_id: int) -> int:
    row = (getattr(session, "skills", {}) or {}).get(skill_id, {})
    if not isinstance(row, dict):
        return 0
    bonus = int(row.get("bonus", 0) or 0)
    if bonus:
        return bonus
    return _pick_skill_bonus(int(row.get("ranks", 0) or 0))


def _resolve_steal_target(session, server, target_name):
    room = getattr(session, "current_room", None)
    if not room or not target_name:
        return None, None

    target_l = target_name.strip().lower()

    for player in server.world.get_players_in_room(room.id):
        if player is session:
            continue
        pname = (getattr(player, "character_name", "") or "").lower()
        if pname.startswith(target_l):
            return "player", player

    if hasattr(server, "npcs"):
        npc = server.npcs.find_npc_in_room(room.id, target_l)
        if npc:
            return "npc", npc

    if hasattr(server, "creatures"):
        creature = server.creatures.find_creature_in_room(room.id, target_l)
        if creature and getattr(creature, "alive", True):
            return "creature", creature

    return None, None


def _target_pickpocket_defense(target_kind, target):
    if target_kind == "player":
        skills = getattr(target, "skills", {}) or {}
        perc = skills.get(27, {}) if isinstance(skills, dict) else {}
        perc_ranks = int(perc.get("ranks", 0)) if isinstance(perc, dict) else 0
        intuition = int(getattr(target, "stat_intuition", 50) or 50)
        dexterity = int(getattr(target, "stat_dexterity", 50) or 50)
        return 60 + _pick_skill_bonus(perc_ranks) + (intuition - 50) // 2 + (dexterity - 50) // 3
    if target_kind == "npc":
        base = int(getattr(target, "level", 1) or 1) * 8
        if getattr(target, "can_shop", False) or getattr(target, "is_guild", False):
            base += 40
        return 80 + base
    level = int(getattr(target, "level", 1) or 1)
    return 55 + level * 7


def _mark_pickpocketed(target, character_id):
    now = time.time()
    picked = getattr(target, "_pickpocketed_by", None)
    if not isinstance(picked, dict):
        picked = {}
        setattr(target, "_pickpocketed_by", picked)
    picked[int(character_id or 0)] = now


def _pickpocket_on_cooldown(target, character_id, cooldown=900):
    picked = getattr(target, "_pickpocketed_by", None)
    if not isinstance(picked, dict):
        return False
    last = picked.get(int(character_id or 0))
    if not last:
        return False
    return (time.time() - last) < cooldown


def _available_pickpocket_silver(target_kind, target, character_id):
    if _pickpocket_on_cooldown(target, character_id):
        return 0

    if target_kind == "player":
        return max(0, int(getattr(target, "silver", 0) or 0))

    if target_kind == "npc":
        if getattr(target, "can_shop", False) or getattr(target, "is_guild", False):
            return 0
        level = int(getattr(target, "level", 1) or 1)
        return random.randint(4, max(6, level * 8))

    level = int(getattr(target, "level", 1) or 1)
    return random.randint(2, max(4, level * 6))


def _parse_use_target(raw_args: str):
    text = (raw_args or "").strip()
    lower = text.lower()
    if " at " in lower:
        idx = lower.index(" at ")
        return text[:idx].strip(), text[idx + 4 :].strip()
    return text, ""


def _magic_item_extra(item):
    keep = (
        "spells", "contents", "charges", "spell_number", "spell_name", "spell_type", "spell_level",
        "custom_name", "material", "color", "enchant_bonus", "attack_bonus", "defense_bonus",
        "flare_type", "living_spell", "crafted_by_spell", "scroll_infusion", "uses",
        "mana_restore", "blessed_food", "familiar_gate", "familiar_room_id",
    )
    data = {}
    if not isinstance(item, dict):
        return data
    for key in keep:
        if key in item and item.get(key) is not None:
            data[key] = item.get(key)
    return data


def _scroll_spells(item):
    if not isinstance(item, dict):
        return []
    spells = item.get("spells") or item.get("contents") or []
    if spells:
        return spells
    if item.get("spell_number"):
        return [{
            "number": int(item.get("spell_number") or 0),
            "name": item.get("spell_name") or f"Spell {item.get('spell_number')}",
            "level": int(item.get("spell_level") or 1),
            "charges": int(item.get("charges", 1) or 1),
        }]
    return []


async def _use_magic_item(session, use_item, hand, target_name, server):
    from server.core.protocol.colors import colorize, roundtime_msg, TextPresets
    from server.core.commands.player.spellcasting import (
        _apply_lua_char_updates,
        _get_spell_engine,
        _lua_returns,
        _refresh_post_spell_state,
        _resolve_default_target,
        _resolve_room_target,
        _session_to_spell_entity,
        _target_to_entity,
    )

    item_name = use_item.get("short_name") or use_item.get("name") or "magic item"
    charges = int(use_item.get("charges", 1) or 0)
    if charges <= 0:
        await session.send_line(colorize(f"The {item_name} is spent and no longer responds.", TextPresets.WARNING))
        return

    spell_number = int(use_item.get("spell_number") or 0)
    spell_name = use_item.get("spell_name") or ""
    spell_type = use_item.get("spell_type") or ""
    spell_level = int(use_item.get("spell_level") or 0)

    if spell_number <= 0 and getattr(server, "db", None):
        conn = None
        cur = None
        try:
            max_cost = max(8, min(25, int(getattr(session, "level", 1) or 1) + 8))
            conn = server.db._get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT spell_number, name, spell_type, mana_cost
                FROM spells
                WHERE spell_type IN ('bolt', 'warding', 'utility', 'buff')
                  AND mana_cost <= %s
                ORDER BY RAND()
                LIMIT 1
                """,
                (max_cost,),
            )
            row = cur.fetchone()
            if row:
                spell_number = int(row.get("spell_number") or 0)
                spell_name = row.get("name") or ""
                spell_type = row.get("spell_type") or ""
                spell_level = int(row.get("mana_cost") or 0)
                use_item.update({
                    "spell_number": spell_number,
                    "spell_name": spell_name,
                    "spell_type": spell_type,
                    "spell_level": spell_level,
                })
        except Exception as e:
            log.error("Failed to bind a spell to %s: %s", item_name, e)
        finally:
            try:
                if cur:
                    cur.close()
            except Exception:
                pass
            try:
                if conn:
                    conn.close()
            except Exception:
                pass

    if spell_number <= 0:
        await session.send_line(colorize(f"The {item_name} hums faintly, but nothing happens.", TextPresets.WARNING))
        return

    engine, spell_engine = _get_spell_engine(server)
    if not engine or not spell_engine:
        await session.send_line("The magic system is unavailable right now.")
        return

    target = _resolve_room_target(session, server, target_name) if target_name else _resolve_default_target(session)
    if spell_type in ("bolt", "warding", "maneuver") and not target:
        await session.send_line(f"Use the {item_name} at whom?")
        return

    skills = getattr(session, "skills", {}) or {}
    miu = skills.get(16, {})
    miu_ranks = int(miu.get("ranks", 0)) if isinstance(miu, dict) else 0
    miu_bonus = _live_skill_bonus(session, 16)
    aura_bonus = (int(getattr(session, "stat_aura", 50) or 50) - 50) // 2
    logic_bonus = (int(getattr(session, "stat_logic", 50) or 50) - 50) // 3
    roll = _open_d100_roll() + miu_bonus + aura_bonus + logic_bonus + int(getattr(session, "level", 1) or 1)
    difficulty = max(20, spell_level * 7)
    if spell_type in ("utility", "buff"):
        difficulty = max(15, difficulty - 8)

    if roll < difficulty:
        await session.send_line(colorize(
            f"You focus on the {item_name}, but the stored magic slips away from your control.",
            TextPresets.WARNING
        ))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    raw_char = engine.python_to_lua(_session_to_spell_entity(session))
    raw_target = engine.python_to_lua(_target_to_entity(target)) if target else None
    raw = engine.call_hook(
        spell_engine,
        "cast_direct",
        raw_char,
        raw_target,
        spell_number,
        "cast",
        None,
        True,
    )
    values = _lua_returns(raw)
    ok = bool(values[0]) if values else False
    message = values[1] if len(values) > 1 else "The magic fizzles."
    _apply_lua_char_updates(engine, raw_char, session)
    _refresh_post_spell_state(session, server)

    if not ok:
        await session.send_line(colorize(f"  {message}", TextPresets.WARNING))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    charges -= 1
    use_item["charges"] = max(0, charges)
    if use_item.get("inv_id") and getattr(server, "db", None):
        state = _magic_item_extra(use_item)
        state.update({
            "charges": use_item["charges"],
            "spell_number": spell_number,
            "spell_name": spell_name,
            "spell_type": spell_type,
            "spell_level": spell_level,
        })
        server.db.save_item_extra_data(use_item["inv_id"], state)

    await session.send_line(colorize(f"  {message}", TextPresets.SYSTEM))
    if charges <= 0:
        await session.send_line(colorize(f"  The {item_name} grows dull and spent.", TextPresets.SYSTEM))
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "magic_item_success")
        except Exception:
            pass
    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


async def cmd_steal(session, cmd, args, server):
    """STEAL <target> - Attempt to pickpocket silver from a visible target."""
    from server.core.protocol.colors import colorize, roundtime_msg, TextPresets

    if not args or not args.strip():
        await session.send_line("Steal from whom?")
        return

    arg = args.strip()
    item_phrase = "silver"
    target_phrase = arg
    lower = arg.lower()
    if " from " in lower:
        idx = lower.index(" from ")
        item_phrase = arg[:idx].strip() or "silver"
        target_phrase = arg[idx + 6 :].strip()

    if item_phrase.lower() not in ("silver", "coins", "coin", "money", "purse", "pocket"):
        await session.send_line("This first pass of STEAL only supports lifting silver and coin purses.")
        return

    target_kind, target = _resolve_steal_target(session, server, target_phrase)
    if not target:
        await session.send_line(f"You don't see any '{target_phrase}' here.")
        return

    skills = getattr(session, "skills", {}) or {}
    pick = skills.get(32, {})
    pick_ranks = int(pick.get("ranks", 0)) if isinstance(pick, dict) else 0
    if pick_ranks <= 0:
        await session.send_line("You lack the Pickpocketing training to try that cleanly.")
        return

    dex_bonus = (int(getattr(session, "stat_dexterity", 50) or 50) - 50) // 2
    agi_bonus = (int(getattr(session, "stat_agility", 50) or 50) - 50) // 3
    hide_bonus = 20 if getattr(session, "hidden", False) else 0
    result = _open_d100_roll() + _pick_skill_bonus(pick_ranks) + dex_bonus + agi_bonus + hide_bonus
    defense = _target_pickpocket_defense(target_kind, target)

    if result < defense:
        session.hidden = False
        session.sneaking = False
        await session.send_line(colorize("You fumble the attempt and get noticed!", TextPresets.WARNING))
        if target_kind == "player":
            await target.send_line(colorize(f"You feel {session.character_name} tugging at your purse!", TextPresets.WARNING))
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    available = _available_pickpocket_silver(target_kind, target, getattr(session, "character_id", 0))
    if available <= 0:
        await session.send_line("You find nothing worth lifting.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    max_take = max(3, int(getattr(session, "level", 1) or 1) * 4 + pick_ranks * 2)
    amount = min(available, random.randint(1, max_take))
    session.silver += amount

    if target_kind == "player":
        target.silver = max(0, int(getattr(target, "silver", 0) or 0) - amount)
        if getattr(server, "db", None) and getattr(target, "character_id", None):
            server.db.save_character_resources(
                target.character_id,
                target.health_current, target.mana_current,
                target.spirit_current, target.stamina_current,
                target.silver
            )

    _mark_pickpocketed(target, getattr(session, "character_id", 0))

    await session.send_line(colorize(
        f"You deftly lift {amount} silver from {getattr(target, 'display_name', getattr(target, 'character_name', getattr(target, 'full_name', 'your target')))}.",
        TextPresets.SYSTEM
    ))

    if getattr(server, "db", None) and getattr(session, "character_id", None):
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver
        )

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


# =========================================================
# Helper for social/emote commands
# =========================================================

async def _do_emote(session, args, server,
                    self_msg, room_msg,
                    self_target_msg=None, target_msg=None, room_target_msg=None,
                    requires_target=False):
    """Generic emote handler.

    self_msg / room_msg: messages when no target (use {name} for actor name)
    self_target_msg / target_msg / room_target_msg: messages when targeting someone
        Use {name} for actor, {target} for target name.
    """
    target = None
    if args and args.strip():
        target_name = args.strip().lower()
        room = session.current_room
        if room:
            for p in server.world.get_players_in_room(room.id):
                if p != session and p.character_name and p.character_name.lower().startswith(target_name):
                    target = p
                    break
        if not target:
            await session.send_line("You don't see them here.")
            return

    if requires_target and not target:
        await session.send_line('Who do you want to do that to?')
        return

    name = session.character_name or 'Someone'

    if target and self_target_msg:
        tname = target.character_name or 'someone'
        await session.send_line(self_target_msg.format(name=name, target=tname))
        if target_msg:
            await target.send_line(target_msg.format(name=name, target=tname))
        if room_target_msg and session.current_room:
            for p in server.world.get_players_in_room(session.current_room.id):
                if p != session and p != target:
                    await p.send_line(room_target_msg.format(name=name, target=tname))
    else:
        await session.send_line(self_msg.format(name=name))
        if session.current_room:
            await server.world.broadcast_to_room(
                session.current_room.id,
                room_msg.format(name=name),
                exclude=session
            )


# =========================================================
# Position commands
# =========================================================

async def cmd_stand(session, cmd, args, server):
    """STAND - Stand up (also wakes from sleep)."""
    _status = getattr(server, 'status', None)

    # Determine current position via status system or raw position flag
    if _status:
        currently_sleeping = _status.has(session, 'sleeping')
        is_standing = (
            not _status.has(session, 'sleeping')
            and not _status.has(session, 'sitting')
            and not _status.has(session, 'kneeling')
            and not _status.has(session, 'resting')
            and not _status.has(session, 'prone')
            and session.position == 'standing'
        )
    else:
        currently_sleeping = session.position == 'sleeping'
        is_standing = session.position == 'standing'

    if is_standing:
        await session.send_line('You are already standing.')
        return

    was_sleeping = currently_sleeping

    # Clear all position status effects
    if _status:
        for st in ('sleeping', 'sitting', 'kneeling', 'resting', 'prone', 'inner_mind'):
            _status.remove(session, st)

    session.position = 'standing'

    if was_sleeping:
        await session.send_line('You wake up and stand.')
        # Brief grogginess after waking (GS4 mechanic)
        if _status:
            _status.apply(session, 'groggy', duration=10)
            await session.send_line('  You feel momentarily groggy.')
    else:
        await session.send_line('You stand back up.')

    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            session.character_name + (' wakes up and stands.' if was_sleeping else ' stands up.'),
            exclude=session
        )


async def cmd_sit(session, cmd, args, server):
    """SIT - Sit down."""
    if session.position == 'sitting':
        await session.send_line('You are already sitting.')
        return
    session.position = 'sitting'
    await session.send_line('You sit down.')
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            session.character_name + ' sits down.',
            exclude=session
        )


async def cmd_kneel(session, cmd, args, server):
    """KNEEL - Kneel down."""
    if session.position == 'kneeling':
        await session.send_line('You are already kneeling.')
        return
    session.position = 'kneeling'
    await session.send_line('You kneel down.')
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            session.character_name + ' kneels down.',
            exclude=session
        )


async def cmd_lie(session, cmd, args, server):
    """LIE - Lie down."""
    if session.position == 'lying':
        await session.send_line('You are already lying down.')
        return
    session.position = 'lying'
    await session.send_line('You lie down.')
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            session.character_name + ' lies down.',
            exclude=session
        )


async def cmd_rest(session, cmd, args, server):
    """REST - Sit or lie down to recover faster. Alias for SIT."""
    _status = getattr(server, 'status', None)
    _in_combat = _status.has(session, 'in_combat') if _status else session.in_combat
    if _in_combat:
        await session.send_line("You can't rest during combat!")
        return
    if session.position in ('sitting', 'lying', 'kneeling'):
        room = session.current_room
        supernode = getattr(room, 'supernode', False) if room else False
        node_str = '  [Supernode - enhanced recovery]' if supernode else ''
        await session.send_line(f'You are already resting.{node_str}')
        return
    session.position = 'sitting'
    room = session.current_room
    supernode = getattr(room, 'supernode', False) if room else False
    if supernode:
        await session.send_line('You sit down to rest.  The mana here flows freely, enhancing your recovery.')
    else:
        await session.send_line('You sit down to rest.')
    if room:
        await server.world.broadcast_to_room(
            room.id,
            session.character_name + ' sits down to rest.',
            exclude=session
        )


async def cmd_sleep(session, cmd, args, server):
    """SLEEP - Fall asleep, greatly accelerating XP absorption.
    Sleep is a formal status effect (sleeping) that:
      - Doubles XP absorption rate (handled in experience_manager)
      - Applies inner_mind buff for enhanced mana recovery on supernodes
      - Blocks actions, movement, speech, hiding, and casting
      - Waking applies a brief 'groggy' debuff (-20 AS/DS, 10 seconds)
    """
    _status = getattr(server, 'status', None)
    _in_combat = _status.has(session, 'in_combat') if _status else session.in_combat
    if _in_combat:
        await session.send_line("You can't sleep during combat!")
        return
    if session.position == 'sleeping' or (_status and _status.has(session, 'sleeping')):
        await session.send_line("You are already asleep.  (STAND to wake up.)")
        return

    # Apply sleeping status (indefinite duration -- cleared by STAND/WAKE)
    if _status:
        _status.apply(session, 'sleeping')
        # Remove sitting/kneeling/resting states
        for st in ('sitting', 'kneeling', 'resting'):
            _status.remove(session, st)
    else:
        session.position = 'sleeping'

    room = session.current_room
    supernode = getattr(room, 'supernode', False) if room else False

    if supernode:
        await session.send_line(
            "You lie down and drift off to sleep.  "
            "The mana flowing through this node fills your dreams."
        )
        # inner_mind: enhanced recovery on supernodes while sleeping
        if _status:
            _status.apply(session, 'inner_mind', duration=3600)
    else:
        await session.send_line(
            "You lie down and drift off to sleep.  "
            "Your mind begins to process your experiences more rapidly."
        )

    if room:
        await server.world.broadcast_to_room(
            room.id,
            session.character_name + ' lies down and falls asleep.',
            exclude=session
        )


async def cmd_use(session, cmd, args, server):
    """USE <item> - Use a consumable item (herb, potion, etc.) from your hands."""
    if not args:
        await session.send_line("Use what?  Hold the item in your hand first.")
        return

    from server.core.protocol.colors import colorize, TextPresets

    item_search, target_search = _parse_use_target(args)
    search = item_search.lower()

    # Find item in hands
    use_item = None
    hand = None
    for hand_name in ('right_hand', 'left_hand'):
        item = getattr(session, hand_name, None)
        if item:
            sn = (item.get('short_name') or '').lower()
            nn = (item.get('noun') or '').lower()
            nm = (item.get('name') or '').lower()
            if search in sn or search in nn or search in nm:
                use_item = item
                hand = hand_name
                break

    if not use_item:
        await session.send_line(f"You aren't holding anything like '{args.strip()}'.")
        return

    item_type = use_item.get('item_type', '')
    if item_type in ('wand', 'rod'):
        await _use_magic_item(session, use_item, hand, target_search, server)
        return

    # ── Herbs ─────────────────────────────────────────────────────────────────
    if item_type == 'herb':
        # Field names: DB schema uses heal_type/heal_amount (canonical).
        # treasure.py drops herbs keyed as herb_heal_type/herb_heal_amount.
        # Support both so herbs work regardless of origin.
        heal_type   = (use_item.get('heal_type') or
                       use_item.get('herb_heal_type') or 'blood')
        heal_amount = int(use_item.get('heal_amount') or
                          use_item.get('herb_heal_amount') or 0)
        heal_rank   = int(use_item.get('heal_rank') or 1)
        item_name   = use_item.get('short_name') or use_item.get('name') or 'herb'

        # ── Bites system ──────────────────────────────────────────────────────
        # GS4: herbs with article "some" have 3 bites; single-article items 1.
        # Per-instance bites_remaining lives in the item dict (loaded from
        # extra_data JSON in inventory, or initialised fresh from template).
        article = (use_item.get('article') or 'a').lower().strip()
        default_bites = 3 if article == 'some' else 1
        bites_left = int(use_item.get('bites_remaining', default_bites))

        if bites_left <= 0:
            await session.send_line(f'The {item_name} is already consumed.')
            return

        bites_left -= 1
        use_item['bites_remaining'] = bites_left
        last_bite = (bites_left == 0)

        if last_bite:
            await session.send_line(f'You eat the last of the {item_name}.')
        elif bites_left == 1:
            await session.send_line(f'You eat some of the {item_name}.  One bite remains.')
        else:
            await session.send_line(
                f'You eat some of the {item_name}.  {bites_left} bites remain.'
            )

        # ── Healing effects — routed through WoundBridge + Lua ───────────────
        # Blood/mana/poison are handled in Python (resource mutation).
        # All wound/scar/regen types delegate to WoundBridge.use_herb so
        # session.wounds stays canonical and treatment.lua drives all logic.

        if heal_type in ('blood', 'health'):
            old_hp = session.health_current
            session.health_current = min(session.health_max,
                                         session.health_current + heal_amount)
            gained = session.health_current - old_hp
            if gained > 0:
                await session.send_line(colorize(
                    f'  You feel the herb working.  You recover {gained} hit points.',
                    TextPresets.SYSTEM
                ))
            else:
                await session.send_line(colorize(
                    '  You feel the herb working, but you are already at full health.',
                    TextPresets.SYSTEM
                ))
            # Blood herbs also calm one bleed stack
            status_mgr = getattr(server, 'status', None)
            effects = getattr(session, 'status_effects', {})
            bleed_key = None
            if status_mgr:
                if status_mgr.has(session, 'major_bleed'):
                    bleed_key = 'major_bleed'
                elif status_mgr.has(session, 'bleeding'):
                    bleed_key = 'bleeding'
                if bleed_key:
                    status_mgr.remove(session, bleed_key)
                    await session.send_line(colorize(
                        '  The herb staunches your bleeding.',
                        TextPresets.SYSTEM
                    ))
            if not bleed_key:
                bleed_key = 'major_bleed' if 'major_bleed' in effects else 'bleeding' if 'bleeding' in effects else None
                if bleed_key:
                    bleed = effects[bleed_key]
                    bleed['stacks'] = max(0, int(bleed.get('stacks', 1)) - 1)
                    if bleed['stacks'] == 0:
                        del effects[bleed_key]
                        await session.send_line(colorize(
                            '  The herb staunches your bleeding.',
                            TextPresets.SYSTEM
                        ))

        elif heal_type == 'mana':
            old_mana = session.mana_current
            session.mana_current = min(session.mana_max,
                                       session.mana_current + heal_amount)
            gained = session.mana_current - old_mana
            await session.send_line(colorize(
                f'  You feel mana flowing back into you.  You recover {gained} mana points.',
                TextPresets.SYSTEM
            ))

        elif heal_type == 'poison':
            effects = getattr(session, 'status_effects', {})
            if 'poison' in effects:
                del effects['poison']
                await session.send_line(colorize(
                    '  The antidote neutralizes the poison in your blood.',
                    TextPresets.SYSTEM
                ))
            else:
                await session.send_line("  You don't feel poisoned, but the herb tastes bitter.")

        else:
            # ── All wound/scar/regen herbs → WoundBridge (Lua treatment.lua) ──
            wb = getattr(server, 'wound_bridge', None)
            if wb and wb.available:
                result = wb.use_herb(session, use_item)
                msg = result.get('message', '')
                if msg:
                    await session.send_line(colorize(f'  {msg}', TextPresets.SYSTEM))
                if not result.get('ok'):
                    # Herb had no valid wound target — refund the bite
                    use_item['bites_remaining'] = bites_left + 1
                    last_bite = False
                # Apply any HP/mana side-effects from Lua
                hp_gain = int(result.get('hp_restore', 0) or 0)
                if hp_gain:
                    session.health_current = min(session.health_max,
                                                 session.health_current + hp_gain)
                mp_gain = int(result.get('mana_restore', 0) or 0)
                if mp_gain:
                    session.mana_current = min(session.mana_max,
                                               session.mana_current + mp_gain)
                if result.get('cure_poison'):
                    getattr(session, 'status_effects', {}).pop('poison', None)
                # Async-persist updated wounds
                if result.get('ok') and server.db and session.character_id:
                    try:
                        import asyncio as _asyncio
                        _asyncio.ensure_future(wb.save_wounds(session))
                    except Exception:
                        pass
            else:
                await session.send_line(colorize(
                    '  You feel the herb working.', TextPresets.SYSTEM
                ))

        # ── Persist bites / remove when fully consumed ────────────────────────
        if last_bite:
            setattr(session, hand, None)
            if use_item.get('inv_id') and server.db:
                server.db.remove_item_from_inventory(use_item['inv_id'])
        else:
            # Still has bites — save updated bites_remaining to extra_data
            if use_item.get('inv_id') and server.db:
                server.db.save_item_extra_data(
                    use_item['inv_id'],
                    {'bites_remaining': bites_left}
                )

        # Save
        if server.db and session.character_id:
            server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current, session.stamina_current,
                session.silver
            )

        if session.current_room:
            await server.world.broadcast_to_room(
                session.current_room.id,
                f'{session.character_name} consumes something.',
                exclude=session
            )

    elif item_type == 'consumable':
        # Food/drink - minor health/stamina recovery
        item_name = use_item.get('short_name') or 'item'
        await session.send_line(f'You consume the {item_name}.')
        heal = 5 + session.level
        session.health_current  = min(session.health_max,  session.health_current  + heal)
        session.stamina_current = min(session.stamina_max, session.stamina_current + heal)
        mana_restore = int(use_item.get("mana_restore", 0) or 0)
        if mana_restore > 0:
            session.mana_current = min(session.mana_max, session.mana_current + mana_restore)
        await session.send_line(colorize(
            f'  You feel slightly refreshed.' + (f'  Mana returns to you ({mana_restore}).' if mana_restore > 0 else ''),
            TextPresets.SYSTEM
        ))
        setattr(session, hand, None)
        if use_item.get('inv_id') and server.db:
            server.db.remove_item_from_inventory(use_item['inv_id'])

    else:
        await session.send_line(f"You can't use that.")


async def cmd_tend(session, cmd, args, server):
    """TEND <location> - Stop bleeding using the canonical Lua wound system."""
    from server.core.protocol.colors import colorize, TextPresets
    wb = getattr(server, 'wound_bridge', None)
    if wb and wb.available:
        result = wb.tend(session, (args or "").strip())
        msg = result.get('message') or "You fail to tend the wound."
        preset = TextPresets.SYSTEM if result.get('ok') else TextPresets.WARNING
        await session.send_line(colorize(f'  {msg}', preset))
        if result.get('ok') and server.db and session.character_id:
            try:
                import asyncio as _asyncio
                _asyncio.ensure_future(wb.save_wounds(session))
            except Exception:
                pass
        return

    await session.send_line(colorize(
        '  The wound system is unavailable right now.',
        TextPresets.WARNING
    ))


# =========================================================
# WOUNDS command — detailed injury report with herb guide
# =========================================================

async def cmd_wounds(session, cmd, args, server):
    """WOUNDS - Display all active wounds/scars with severity and herb recommendations."""
    from server.core.protocol.colors import colorize, TextPresets

    # Herb recommendation table keyed by location slug
    HERB_GUIDE = {
        "head":          {"wound": ["aloeas stem"],              "scar": ["haphip root", "brostheras potion"]},
        "neck":          {"wound": ["aloeas stem"],              "scar": ["haphip root", "brostheras potion"]},
        "chest":         {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "abdomen":       {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "back":          {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "right_eye":     {"wound": ["basal moss", "pothinir grass"], "scar": ["aivren berry"],   "regen": ["bur-clover"]},
        "left_eye":      {"wound": ["basal moss", "pothinir grass"], "scar": ["aivren berry"],   "regen": ["bur-clover"]},
        "right_arm":     {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_arm":      {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "right_hand":    {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_hand":     {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "right_leg":     {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_leg":      {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "nervous_system":{"wound": ["wolifrew lichen", "bolmara potion"], "scar": ["woth flower"]},
    }

    SEVERITY = {
        1: ("minor",      TextPresets.SYSTEM),
        2: ("moderate",   TextPresets.SYSTEM),
        3: ("major",      TextPresets.WARNING),
        4: ("severe",     TextPresets.WARNING),
        5: ("crippling",  TextPresets.HEALTH_CRIT),
    }

    wb = getattr(server, 'wound_bridge', None)
    wounds = {}
    if wb:
        wounds = wb.get_wounds(session)

    await session.send_line(colorize(
        "=" * 55, TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        "  INJURIES — Current Wounds & Scars",
        TextPresets.SYSTEM
    ))
    await session.send_line(colorize(
        "=" * 55, TextPresets.SYSTEM
    ))

    if not wounds:
        await session.send_line("  You have no active wounds or scars.")
        await session.send_line(colorize("=" * 55, TextPresets.SYSTEM))
        return

    has_any = False
    for loc_key in [
        "head", "neck", "chest", "abdomen", "back",
        "right_eye", "left_eye",
        "right_arm", "left_arm", "right_hand", "left_hand",
        "right_leg", "left_leg", "nervous_system"
    ]:
        entry = wounds.get(loc_key)
        if not entry:
            continue
        wr = int(entry.get('wound_rank', 0))
        sr = int(entry.get('scar_rank',  0))
        bl = bool(entry.get('is_bleeding', False))
        ba = bool(entry.get('bandaged', False))
        if not wr and not sr:
            continue

        has_any = True
        loc_display = loc_key.replace('_', ' ').title()
        guide = HERB_GUIDE.get(loc_key, {})

        # Wound line
        if wr:
            sev_name, sev_color = SEVERITY.get(wr, (f"rank {wr}", TextPresets.WARNING))
            bleed_tag = ""
            if bl and not ba:
                bleed_tag = "  \033[31m[BLEEDING]\033[0m"
            elif ba:
                bleed_tag = "  [bandaged]"
            await session.send_line(colorize(
                f"  {loc_display:<18} WOUND rank {wr} ({sev_name}){bleed_tag}",
                sev_color
            ))
            # Herb recommendation — rank 5 = severed/regen herb needed
            if wr >= 5 and 'regen' in guide:
                herbs = ', '.join(guide['regen'])
                await session.send_line(
                    f"    \033[91m↳ SEVERED — use: {herbs}\033[0m"
                )
            elif wr >= 4 and 'regen' in guide:
                herbs_w = ', '.join(guide.get('wound', ['unknown']))
                herbs_r = ', '.join(guide['regen'])
                await session.send_line(
                    f"    \033[93m↳ Treat with: {herbs_w}  (or {herbs_r} to restore)\033[0m"
                )
            else:
                herbs = ', '.join(guide.get('wound', ['unknown']))
                await session.send_line(
                    f"    \033[36m↳ Treat with: {herbs}\033[0m"
                )

        # Scar line
        if sr:
            sev_name, sev_color = SEVERITY.get(sr, (f"rank {sr}", TextPresets.WARNING))
            await session.send_line(colorize(
                f"  {loc_display:<18} SCAR  rank {sr} ({sev_name})",
                sev_color
            ))
            herbs = ', '.join(guide.get('scar', ['unknown']))
            await session.send_line(
                f"    \033[33m↳ Reduce with: {herbs}\033[0m"
            )

    if not has_any:
        await session.send_line("  You have no active wounds or scars.")

    # Bleeding summary
    bleeding_locs = [
        k.replace('_', ' ') for k, v in wounds.items()
        if v.get('is_bleeding') and not v.get('bandaged')
    ]
    if bleeding_locs:
        await session.send_line("")
        await session.send_line(colorize(
            f"  \033[31mActive bleeding:\033[0m {', '.join(bleeding_locs)}",
            TextPresets.WARNING
        ))
        await session.send_line(
            "  Use TEND MY <area> to bandage bleeding wounds."
        )

    await session.send_line(colorize("=" * 55, TextPresets.SYSTEM))
    await session.send_line(
        "  EAT <herb> or DRINK <herb> from your hand to treat wounds."
    )
    await session.send_line(
        "  Herbs auto-target the worst eligible wound they can treat."
    )
    await session.send_line(colorize("=" * 55, TextPresets.SYSTEM))


# =========================================================
# Social emote commands
# =========================================================

async def cmd_bow(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You bow.', '{name} bows.',
                    'You bow to {target}.', '{name} bows to you.', '{name} bows to {target}.')

async def cmd_wave(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You wave.', '{name} waves.',
                    'You wave to {target}.', '{name} waves to you.', '{name} waves to {target}.')

async def cmd_nod(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You nod.', '{name} nods.',
                    'You nod to {target}.', '{name} nods to you.', '{name} nods to {target}.')

async def cmd_grin(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You grin.', '{name} grins.',
                    'You grin at {target}.', '{name} grins at you.', '{name} grins at {target}.')

async def cmd_smile(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You smile.', '{name} smiles.',
                    'You smile at {target}.', '{name} smiles at you.', '{name} smiles at {target}.')

async def cmd_frown(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You frown.', '{name} frowns.',
                    'You frown at {target}.', '{name} frowns at you.', '{name} frowns at {target}.')

async def cmd_laugh(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You laugh!', '{name} laughs!',
                    'You laugh at {target}!', '{name} laughs at you!', '{name} laughs at {target}!')

async def cmd_cry(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You cry.', '{name} cries.',
                    'You cry on {target}.', '{name} cries on you.', '{name} cries on {target}.')

async def cmd_sigh(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You sigh.', '{name} sighs.',
                    'You sigh at {target}.', '{name} sighs at you.', '{name} sighs at {target}.')

async def cmd_shrug(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You shrug.', '{name} shrugs.',
                    'You shrug at {target}.', '{name} shrugs at you.', '{name} shrugs at {target}.')

async def cmd_wince(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You wince.', '{name} winces.',
                    'You wince at {target}.', '{name} winces at you.', '{name} winces at {target}.')

async def cmd_ponder(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You ponder.', '{name} appears to be lost in thought.',
                    'You ponder {target}.', '{name} ponders you.', '{name} ponders {target}.')

async def cmd_gasp(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You gasp!', '{name} gasps!',
                    'You gasp at {target}!', '{name} gasps at you!', '{name} gasps at {target}!')

async def cmd_groan(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You groan.', '{name} groans.',
                    'You groan at {target}.', '{name} groans at you.', '{name} groans at {target}.')

async def cmd_dance(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You dance around!', '{name} dances around!',
                    'You dance with {target}!', '{name} dances with you!', '{name} dances with {target}!')

async def cmd_cheer(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You cheer!', '{name} cheers!',
                    'You cheer for {target}!', '{name} cheers for you!', '{name} cheers for {target}!')

async def cmd_salute(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You salute.', '{name} salutes.',
                    'You salute {target}.', '{name} salutes you.', '{name} salutes {target}.')

async def cmd_curtsy(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You curtsy.', '{name} curtsies.',
                    'You curtsy to {target}.', '{name} curtsies to you.', '{name} curtsies to {target}.')

async def cmd_growl(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You growl.', '{name} growls.',
                    'You growl at {target}.', '{name} growls at you.', '{name} growls at {target}.')

async def cmd_snicker(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You snicker.', '{name} snickers.',
                    'You snicker at {target}.', '{name} snickers at you.', '{name} snickers at {target}.')

async def cmd_cackle(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You cackle!', '{name} cackles!',
                    'You cackle at {target}!', '{name} cackles at you!', '{name} cackles at {target}!')

async def cmd_hug(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You hug yourself.', '{name} hugs themselves.',
                    'You hug {target}.', '{name} hugs you.', '{name} hugs {target}.',
                    requires_target=False)

async def cmd_kiss(session, cmd, args, server):
    await _do_emote(session, args, server,
                    'You blow a kiss.', '{name} blows a kiss.',
                    'You kiss {target} on the cheek.', '{name} kisses you on the cheek.', '{name} kisses {target} on the cheek.',
                    requires_target=False)


# =========================================================
# READ - Read a scroll to see its spells
# =========================================================

async def cmd_read(session, cmd, args, server):
    """READ <scroll> - Read a scroll to see what spells are written on it.
    The item must be in your hand.
    Subject to Arcane Symbols skill check at very low skill.
    """
    if not args:
        await session.send_line("Read what?  Hold a scroll in your hand first.")
        return

    search = args.strip().lower()

    # Find scroll in hands
    scroll = None
    hand = None
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("item_type") == "scroll":
            if (search in (item.get("name") or "").lower() or
                    search in (item.get("short_name") or "").lower() or
                    search in (item.get("noun") or "").lower()):
                scroll = item
                hand = slot
                break

    if not scroll:
        await session.send_line(
            f"You aren't holding anything like '{args.strip()}' that can be read.  "
            "You must have the scroll in your hand."
        )
        return

    # Arcane Symbols check — very low bar, just prevents total failure at 0 skill
    from server.core.commands.player.training import resolve_skill
    SKILL_ARCANE_SYMBOLS = (resolve_skill("arcane symbols")[0] or 15)
    skills = getattr(session, 'skills', {}) or {}
    arc_data = skills.get(SKILL_ARCANE_SYMBOLS, {})
    arc_ranks = int(arc_data.get('ranks', 0)) if isinstance(arc_data, dict) else 0
    arc_bonus = _live_skill_bonus(session, SKILL_ARCANE_SYMBOLS)

    import random as _rand
    scroll_spells = _scroll_spells(scroll)
    highest_level = max([int(sp.get("level", 1) or 1) for sp in scroll_spells], default=1)
    aura_bonus = (int(getattr(session, "stat_aura", 50) or 50) - 50) // 2
    logic_bonus = (int(getattr(session, "stat_logic", 50) or 50) - 50) // 3
    roll = _rand.randint(1, 100) + arc_bonus + aura_bonus + logic_bonus + session.level
    if roll < max(20, highest_level * 6):  # Very low threshold — near-impossible to fail with any training
        await session.send_line(
            colorize(
                "You squint at the scroll but the mystical writing is completely indecipherable to you.",
                TextPresets.WARNING
            )
        )
        session.set_roundtime(2)
        await session.send_line(roundtime_msg(2))
        return

    scroll_name = scroll.get("short_name") or scroll.get("name") or "the scroll"
    await session.send_line(f"You carefully examine {colorize(scroll_name, TextPresets.ITEM_NAME)}.")

    spells = _scroll_spells(scroll)
    if not spells:
        # Generic scroll with no specific spell list — show description
        desc = scroll.get("description") or "Elaborate magical script covers the surface, but you cannot identify the specific spell."
        await session.send_line(f"  {desc}")
        await session.send_line("  Use INVOKE <#> to attempt to activate a spell from this scroll.")
    else:
        await session.send_line("  The following spells are written on this scroll:")
        for idx, spell in enumerate(spells, 1):
            spell_name   = spell.get("name") or f"Spell #{spell.get('number', '?')}"
            spell_number = spell.get("number", "")
            charges      = spell.get("charges", 1)
            charge_str   = f" ({charges} charge{'s' if charges != 1 else ''})" if charges else ""
            num_str      = f" [{spell_number}]" if spell_number else ""
            await session.send_line(
                f"  {idx}. {colorize(spell_name, TextPresets.ITEM_NAME)}{num_str}{charge_str}"
            )
        await session.send_line("  Use INVOKE <#> to prepare a spell from this scroll.")

    session.set_roundtime(2)
    await session.send_line(roundtime_msg(2))
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "scroll_read_success")
        except Exception:
            pass


# =========================================================
# INVOKE - Prepare a spell from a scroll
# =========================================================

async def cmd_invoke(session, cmd, args, server):
    """INVOKE <#|spell name> - Prepare a spell from a scroll held in hand.
    Once invoked the spell is prepared and ready to CAST or INCANT.
    Costs one charge from that spell on the scroll.
    Subject to Arcane Symbols skill check.
    """
    if not args:
        await session.send_line("Invoke which spell?  Hold a scroll and use INVOKE <spell number>.")
        return

    # Find scroll in hands
    scroll = None
    hand = None
    for slot in ("right_hand", "left_hand"):
        item = getattr(session, slot, None)
        if item and item.get("item_type") == "scroll":
            scroll = item
            hand = slot
            break

    if not scroll:
        await session.send_line("You need to be holding a scroll to invoke a spell from it.")
        return

    spells = _scroll_spells(scroll)
    if not spells:
        await session.send_line(
            "This scroll doesn't appear to have any invokable spells.  "
            "Try READ to examine it first."
        )
        return

    # Match by index or name
    target_spell = None
    arg = args.strip()
    try:
        idx = int(arg) - 1
        if 0 <= idx < len(spells):
            target_spell = spells[idx]
    except ValueError:
        arg_lower = arg.lower()
        for spell in spells:
            if (arg_lower in (spell.get("name") or "").lower() or
                    arg_lower == str(spell.get("number", ""))):
                target_spell = spell
                break

    if not target_spell:
        await session.send_line(
            f"You don't find '{arg}' on this scroll.  Use READ to see available spells."
        )
        return

    # Check charges
    charges = target_spell.get("charges", 1)
    if charges <= 0:
        spell_name = target_spell.get("name") or f"spell #{target_spell.get('number', '?')}"
        await session.send_line(
            colorize(
                f"  The {spell_name} on this scroll has been exhausted.",
                TextPresets.WARNING
            )
        )
        return

    # Arcane Symbols skill check
    from server.core.commands.player.training import resolve_skill
    SKILL_ARCANE_SYMBOLS = (resolve_skill("arcane symbols")[0] or 15)
    skills = getattr(session, 'skills', {}) or {}
    arc_data = skills.get(SKILL_ARCANE_SYMBOLS, {})
    arc_ranks = int(arc_data.get('ranks', 0)) if isinstance(arc_data, dict) else 0
    arc_bonus = _live_skill_bonus(session, SKILL_ARCANE_SYMBOLS)

    import random as _rand
    aura_bonus = (int(getattr(session, "stat_aura", 50) or 50) - 50) // 2
    logic_bonus = (int(getattr(session, "stat_logic", 50) or 50) - 50) // 2
    roll = _rand.randint(1, 100) + arc_bonus + aura_bonus + logic_bonus + session.level * 2
    spell_level = target_spell.get("level", 1) or 1
    difficulty = max(15, spell_level * 8)

    spell_name = target_spell.get("name") or f"spell {target_spell.get('number', '')}"
    scroll_name = scroll.get("short_name") or scroll.get("name") or "the scroll"

    if roll < difficulty:
        await session.send_line(
            f"You attempt to invoke {colorize(spell_name, TextPresets.ITEM_NAME)} "
            f"from {colorize(scroll_name, TextPresets.ITEM_NAME)}..."
        )
        await session.send_line(
            colorize(
                "  The magical script blurs and shifts — you cannot activate this spell yet.  "
                "Train more Arcane Symbols.",
                TextPresets.WARNING
            )
        )
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    # Success — prepare spell on session, consume charge
    target_spell["charges"] = charges - 1
    spell_number = target_spell.get("number")

    if scroll.get("inv_id") and getattr(server, "db", None):
        state = _magic_item_extra(scroll)
        if scroll.get("spell_number"):
            state.update({
                "charges": target_spell["charges"],
                "spell_number": spell_number,
                "spell_name": target_spell.get("name"),
                "spell_type": scroll.get("spell_type") or "utility",
                "spell_level": target_spell.get("level", 1),
            })
        else:
            state["spells"] = spells
        server.db.save_item_extra_data(scroll["inv_id"], state)

    # Set prepared spell on session
    session.prepared_spell = {
        "name":    spell_name,
        "number":  spell_number,
        "source":  "scroll",
        "scroll":  scroll,
        "spell":   target_spell,
    }
    session._prepared_spell = session.prepared_spell

    await session.send_line(
        f"You invoke {colorize(spell_name, TextPresets.ITEM_NAME)} "
        f"from {colorize(scroll_name, TextPresets.ITEM_NAME)}."
    )

    if target_spell["charges"] <= 0:
        await session.send_line(
            colorize(
                f"  As your voice fades, so too does the ink — that spell is now exhausted from the scroll.",
                TextPresets.SYSTEM
            )
        )
        # Remove exhausted spell entry (keep scroll until all spells depleted)
        spells_remaining = [s for s in spells if s.get("charges", 1) > 0]
        if not spells_remaining:
            await session.send_line(
                colorize(
                    f"  The scroll crumbles to dust as its last spell is spent.",
                    TextPresets.SYSTEM
                )
            )
            # Remove scroll from hand
            setattr(session, hand, None)
            inv_id = scroll.get("inv_id")
            if inv_id and getattr(server, "db", None):
                server.db.remove_item_from_inventory(inv_id)

    await session.send_line(
        colorize(f"  {spell_name} is prepared.  Use CAST to release it.", TextPresets.SYSTEM)
    )
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "scroll_invoke_success")
        except Exception:
            pass

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))


# =========================================================
# LUA-DRIVEN EMOTE ENGINE
# =========================================================
# load_emotes_from_lua(server) -> dict[verb, async_fn]
#
# Called once at startup by command_router.register_commands().
# Reads scripts/data/emotes.lua via LuaManager and builds a
# {verb: async handler} dict.  The router registers every entry.
#
# To add a new emote: edit scripts/data/emotes.lua only.
# No Python changes needed.
# =========================================================

def _make_lua_emote_cmd(emote_def: dict):
    """
    Factory: returns an async command handler for one emote definition.
    Closes over the emote_def dict so each verb has its own messages.
    """
    async def _handler(session, cmd, args, server):
        await _do_emote(
            session, args, server,
            emote_def["self"],
            emote_def["room"],
            emote_def["self_t"],
            emote_def["target_t"],
            emote_def["room_t"],
        )
    _handler.__name__ = f"cmd_{emote_def['verb']}_lua"
    return _handler


def load_emotes_from_lua(server) -> dict:
    """
    Load emotes from Lua and return {verb: async_handler}.
    Falls back to empty dict if Lua is unavailable.
    Called by command_router at startup.
    """
    lua_mgr = getattr(server, "lua", None)
    if not lua_mgr:
        log.warning("load_emotes_from_lua: no lua manager on server")
        return {}
    try:
        emote_list = lua_mgr.get_emotes()
    except Exception as e:
        log.warning("load_emotes_from_lua: get_emotes failed: %s", e)
        return {}

    if not emote_list:
        log.warning("load_emotes_from_lua: no emotes returned from Lua")
        return {}

    handlers = {}
    for emote_def in emote_list:
        verb = emote_def.get("verb", "").strip().lower()
        if verb:
            handlers[verb] = _make_lua_emote_cmd(emote_def)

    log.info("load_emotes_from_lua: registered %d emote verbs from Lua", len(handlers))
    return handlers


# =========================================================
# EMOTE — Custom free-form emote
# =========================================================
# Usage:
#   EMOTE waves their arms in wild circles
#   -> You wave your arms in wild circles.      (to self)
#   -> Laernu waves their arms in wild circles. (to room)
#
# Rules:
#   - Must supply text after EMOTE
#   - Auto-adds trailing period if no sentence-ending punctuation
#   - The raw text is broadcast as-is (no target system)
# =========================================================

async def cmd_emote(session, cmd, args, server):
    """EMOTE <action text> - Perform a custom free-form emote."""
    text = (args or "").strip()
    if not text:
        await session.send_line("Emote what?  Usage:  EMOTE <action text>")
        await session.send_line("Example:  EMOTE waves their arms wildly.")
        return

    # Auto-punctuate
    if text[-1] not in ".!?,;:":
        text += "."

    name = session.character_name or "Someone"

    # Self message: capitalise first letter and replace leading third-person
    # subject with "You" only if the text starts with a recognisable verb/pronoun.
    # Since free-form emotes are inherently third-person ("waves", "sighs deeply")
    # we show the player a prefixed confirmation.
    self_msg  = f"You {text}"
    room_msg  = f"{name} {text}"

    await session.send_line(self_msg)
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id, room_msg, exclude=session
        )
