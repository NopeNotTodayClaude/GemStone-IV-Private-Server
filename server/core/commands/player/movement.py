"""
Movement commands - LOOK, directional movement, GO
Now with ANSI colors, real-time DB saves, LOOK AT support, ground items, and NPC display.
"""

import logging
import random
from server.core.world.room import DIRECTION_ALIASES, normalize_exit_key, Room
from server.core.engine.magic_effects import get_active_buff_totals, is_visible_to
from server.core.protocol.colors import (
    room_title, room_desc, room_exits, colorize, TextPresets,
    creature_name as fmt_creature_name, player_name as fmt_player_name,
    item_name as fmt_item_name, npc_name as fmt_npc_name
)

log = logging.getLogger(__name__)

HEARTHSTONE_MIN_FAME = 200000
HEARTHSTONE_MIN_LEVEL = 21


# =============================================================================
# PERCEPTION HELPER — sneak detection
# Mirrors _run_hide_perception_checks in combat.py but for movement.
# Values are driven by server.perception_cfg (globals/perception.lua).
# =============================================================================

async def _check_sneak_detection(session, room, sneak_total: int, server):
    """
    After a successful sneak move into `room`, every non-hidden player already
    present gets a Perception counter-roll against the sneaker's total.
    If they beat it they receive a notice — the sneaker stays hidden either way
    (GS4 doesn't auto-reveal on detection, just informs the observer).
    """
    cfg          = getattr(server, "perception_cfg", {})
    hider_bonus  = cfg.get("sneak_hider_bonus", 15)
    obs_mod      = cfg.get("sneak_observer_mod", 0)
    hider_side   = sneak_total + hider_bonus

    # Room environment works against the observer (more cover = harder to spot)
    dark    = getattr(room, "dark", False)
    indoor  = getattr(room, "indoor", False)
    if dark:
        room_mod = cfg.get("dark_penalty", -20)
    elif not indoor:
        room_mod = cfg.get("outdoor_penalty", -10)
    else:
        room_mod = 0

    sneaker_name = session.character_name or "Someone"

    for obs in server.world.get_players_in_room(room.id):
        if obs is session:
            continue
        if getattr(obs, "hidden", False):
            continue  # hidden observers can't spot sneakers either

        # Perception roll for this observer
        pcfg      = cfg
        sid       = pcfg.get("skill_id", 27)
        rmult     = pcfg.get("rank_multiplier", 3)
        stat_name = pcfg.get("stat", "stat_intuition")
        sdiv      = pcfg.get("stat_divisor", 2)

        skills    = getattr(obs, "skills", {}) or {}
        sk_data   = skills.get(sid, {})
        ranks     = sk_data.get("ranks", 0) if isinstance(sk_data, dict) else 0
        sk_bonus  = ranks * rmult

        stat_val   = getattr(obs, stat_name, 50)
        stat_bonus = (stat_val - 50) // sdiv

        base = random.randint(1, 100)
        if base >= 96:
            base += random.randint(1, 100)
        elif base <= 5:
            base -= random.randint(1, 10)

        obs_roll = base + sk_bonus + stat_bonus + obs_mod + room_mod

        if obs_roll >= hider_side:
            await obs.send_line(
                colorize(
                    f"  Your keen senses detect {sneaker_name} slipping into the area.",
                    TextPresets.SYSTEM
                )
            )


async def cmd_look(session, cmd, args, server):
    """LOOK [AT target] - Display room or examine something."""
    room = session.current_room
    if not room:
        await session.send_line("You are nowhere... this shouldn't happen.")
        return

    # Handle LOOK AT / LOOK IN / LOOK ON
    if args:
        target = args.strip().lower()

        # LOOK IN <container> â€” route directly to cmd_look_in
        if target.startswith('in ') or target.startswith('inside '):
            from server.core.commands.player.inventory import cmd_look_in
            container_arg = target.split(' ', 1)[1].strip()
            await cmd_look_in(session, cmd, container_arg, server)
            return

        # Strip remaining prepositions for LOOK AT / LOOK ON
        for prefix in ('at ', 'on ', 'under ', 'behind '):
            if target.startswith(prefix):
                target = target[len(prefix):]
                break
        # Strip "my " prefix
        if target.startswith('my '):
            target = target[3:]

        await _look_at(session, target, server)
        return

    # Standard room look
    others = server.world.get_players_in_room(room.id)
    others = [s for s in others if s != session and is_visible_to(server, session, s)]

    lines = []

    # Build GS4-style title: [Zone Name, Location Name]
    # Lua rooms store full title already (e.g. "Fearling Pass, Rocky Trail")
    # DB rooms store title=location_name and zone comes from the zone object
    zone_name  = getattr(room, "zone_name", "") or getattr(getattr(room, "zone", None), "name", "") or ""
    room_label = getattr(room, "location_name", "") or room.title
    if zone_name and not room_label.startswith(zone_name):
        full_title = f"{zone_name}, {room_label}"
    else:
        full_title = room_label

    lines.append(room_title(full_title) + colorize(f'  #{room.id}', TextPresets.SYSTEM))
    lines.append(room_desc(room.description))

    # Show NPCs
    if hasattr(server, 'npcs'):
        npcs = server.npcs.get_npcs_in_room(room.id)
        for npc in npcs:
            lines.append('You also see ' + fmt_npc_name(npc.display_name) + '.')

    if hasattr(server, 'pets'):
        for entity in server.pets.get_visible_entities_in_room(room.id, viewer=session):
            lines.append(server.pets.format_room_line(entity))

    if hasattr(server, 'ferries'):
        lines.extend(server.ferries.get_room_lines(room.id, session))

    # Show creatures
    if hasattr(server, 'creatures'):
        living = server.creatures.get_creatures_in_room(room.id)
        dead = server.creatures.get_dead_creatures_in_room(room.id)

        for creature in living:
            lines.append('You also see ' + fmt_creature_name(creature.full_name) + ' [Level ' + str(creature.level) + '].')

        for creature in dead:
            lines.append('You also see the body of ' + fmt_creature_name(creature.full_name) + ' [Level ' + str(creature.level) + '].')

    # Show other players â€” dead players appear as lifeless bodies
    if others:
        for other in others:
            if getattr(other, 'is_dead', False):
                lines.append(colorize(
                    f'You also see the lifeless body of {other.character_name} lying here.',
                    TextPresets.COMBAT_DEATH
                ))
            else:
                status = ''
                if other.position == 'sitting':
                    status = ' who is sitting down'
                elif other.position == 'kneeling':
                    status = ' who is kneeling'
                elif other.position == 'lying':
                    status = ' who is lying down'
                lines.append('You also see ' + fmt_player_name(other.character_name) + status + '.')

    # Show items on ground
    ground_items = server.world.get_ground_items(room.id) if hasattr(server, "world") else getattr(room, '_ground_items', [])
    if ground_items:
        for item in ground_items:
            name = item.get('short_name') or item.get('name') or 'something'
            lines.append('You also see ' + fmt_item_name(name) + '.')

    # Show exits â€” hidden while dead (can't move anyway)
    if not getattr(session, 'is_dead', False):
        exit_type = 'Obvious exits' if room.indoor else 'Obvious paths'
        display_exits = room.get_display_exit_names(session)
        if display_exits:
            exit_names = ', '.join(display_exits)
            lines.append(room_exits(exit_type, exit_names))
        else:
            lines.append(room_exits(exit_type, 'none'))
    else:
        lines.append(colorize(
            "  [You are a spirit.  Sergeant Beefy is on his way.]",
            TextPresets.SYSTEM
        ))

    await session.send_line('\r\n'.join(lines))

    # Trigger NPC greetings on look (first visit)
    if hasattr(server, 'npcs'):
        await server.npcs.on_player_enter_room(session, room.id)


async def cmd_glance(session, cmd, args, server):
    """GLANCE <target> - Quick visual check for a named target."""
    target = (args or "").strip()
    if not target:
        await session.send_line("Glance at what?")
        return
    lowered = target.lower()
    for prefix in ('at ', 'my '):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):].strip()
            break
    await _look_at(session, lowered, server)


async def _look_at(session, target, server):
    """Handle LOOK AT <target> -- examine a creature, player, NPC, item, or self."""
    room = session.current_room
    if not room:
        return

    # Look at self
    if target in ('self', 'myself', 'me'):
        await session.send_line('You see yourself.')
        await session.send_line('You are ' + (session.position or 'standing') + '.')
        if hasattr(session, 'right_hand') and session.right_hand:
            rn = session.right_hand.get('short_name') or 'something'
            await session.send_line('  Right hand: ' + fmt_item_name(rn))
        if hasattr(session, 'left_hand') and session.left_hand:
            ln = session.left_hand.get('short_name') or 'something'
            await session.send_line('  Left hand: ' + fmt_item_name(ln))
        worn = [i for i in session.inventory if i.get('slot')]
        if worn:
            await session.send_line('  You are wearing:')
            for item in worn:
                await session.send_line('    ' + fmt_item_name(item.get('short_name') or item.get('name') or '???'))
        return

    # Look at an NPC
    if hasattr(server, 'npcs'):
        npc = server.npcs.find_npc_in_room(room.id, target)
        if npc:
            await session.send_line('You see ' + fmt_npc_name(npc.display_name) + '.')
            if npc.description:
                await session.send_line('  ' + npc.description)
            if npc.title:
                await session.send_line('  ' + npc.title)
            return

    if hasattr(server, 'pets'):
        entity = server.pets.find_visible_entity(room.id, target, viewer=session)
        if entity:
            for line in server.pets.look_lines_for_entity(entity):
                await session.send_line(line)
            return

    if hasattr(server, 'ferries'):
        ferry_lines = server.ferries.describe_target(room.id, target)
        if ferry_lines:
            for line in ferry_lines:
                await session.send_line(line)
            return

    # Look at another player
    for p in server.world.get_players_in_room(room.id):
        if p != session and p.character_name and target in p.character_name.lower() and is_visible_to(server, session, p):
            from server.core.commands.player.info import RACES, PROFESSIONS
            from server.core.engine.encumbrance import encumbrance_name
            from server.core.engine.combat.status_effects import EFFECT_DEFS

            race = RACES.get(p.race_id, 'Unknown')
            prof = PROFESSIONS.get(p.profession_id, 'Unknown')

            # ── Header ───────────────────────────────────────────────────
            await session.send_line('')
            await session.send_line(
                colorize('  ' + p.character_name, TextPresets.SYSTEM)
                + colorize(f'  (Level {p.level} {race} {prof})', TextPresets.SYSTEM)
            )
            await session.send_line('')

            # ── Title / guild ─────────────────────────────────────────────
            title = getattr(p, 'title', None)
            if title:
                await session.send_line(f'  Title  : {title}')

            # ── Position & stance ─────────────────────────────────────────
            pos = (p.position or 'standing').capitalize()
            stance = getattr(p, 'stance', 'neutral').capitalize()
            await session.send_line(f'  Posture: {pos}   Stance: {stance}')

            # ── Stealth state ─────────────────────────────────────────────
            if getattr(p, 'hidden', False):
                await session.send_line(
                    colorize('  (They appear to be hiding.)', TextPresets.STEALTH)
                )
            if getattr(p, 'sneaking', False):
                await session.send_line(
                    colorize('  (They are moving stealthily.)', TextPresets.STEALTH)
                )

            # ── Health state (visible wound description, not numbers) ─────
            h_cur = getattr(p, 'health_current', 0)
            h_max = getattr(p, 'health_max', 1) or 1
            hp_pct = h_cur / h_max
            if hp_pct >= 0.9:
                health_desc = 'in perfect health'
            elif hp_pct >= 0.75:
                health_desc = 'slightly wounded'
            elif hp_pct >= 0.5:
                health_desc = 'moderately wounded'
            elif hp_pct >= 0.25:
                health_desc = 'heavily wounded'
            elif hp_pct > 0:
                health_desc = 'critically wounded'
            else:
                health_desc = 'dead'
            health_color = (TextPresets.HEALTH_FULL if hp_pct >= 0.75
                            else TextPresets.WARNING if hp_pct >= 0.25
                            else TextPresets.HEALTH_CRIT)
            await session.send_line(
                '  Health : ' + colorize(health_desc, health_color)
            )

            # ── Encumbrance ───────────────────────────────────────────────
            try:
                enc = encumbrance_name(p)
                if enc and enc.lower() != 'unencumbered':
                    await session.send_line(f'  Burden : {enc}')
            except Exception:
                pass

            # ── Active status effects (visible ones) ──────────────────────
            effects = getattr(p, 'status_effects', {}) or {}
            visible_effects = []
            for ename, edata in effects.items():
                desc = EFFECT_DEFS.get(ename, {}).get('description', ename.capitalize())
                visible_effects.append(desc)
            # Also check StatusManager if present
            try:
                mgr = getattr(server, 'status', None)
                if mgr:
                    for eid in ('stunned', 'staggered', 'prone', 'bleeding',
                                'poisoned', 'webbed', 'fear'):
                        if mgr.has(p, eid) and eid.capitalize() not in visible_effects:
                            visible_effects.append(eid.capitalize())
            except Exception:
                pass
            if visible_effects:
                await session.send_line(
                    '  Status : ' + colorize(', '.join(visible_effects), TextPresets.WARNING)
                )

            # ── Injuries (location + severity label) ──────────────────────
            injuries = getattr(p, 'injuries', {}) or {}
            if injuries:
                SEV = {1: 'minor', 2: 'moderate', 3: 'serious', 4: 'severe', 5: 'critical'}
                await session.send_line('  Wounds :')
                for loc, sev in sorted(injuries.items()):
                    await session.send_line(
                        f'    {loc.capitalize()}: '
                        + colorize(SEV.get(sev, 'injured'), TextPresets.WARNING)
                    )

            await session.send_line('')

            # ── Hands ─────────────────────────────────────────────────────
            rh = getattr(p, 'right_hand', None)
            lh = getattr(p, 'left_hand',  None)
            if rh:
                await session.send_line(
                    '  Right hand: ' + fmt_item_name(rh.get('short_name') or rh.get('name') or 'something')
                )
            else:
                await session.send_line('  Right hand: empty')
            if lh:
                await session.send_line(
                    '  Left hand : ' + fmt_item_name(lh.get('short_name') or lh.get('name') or 'something')
                )
            else:
                await session.send_line('  Left hand : empty')

            # ── Worn items ────────────────────────────────────────────────
            worn = [i for i in getattr(p, 'inventory', [])
                    if i and i.get('slot') and i.get('slot') not in ('right_hand', 'left_hand')]
            if worn:
                await session.send_line('')
                await session.send_line(f'  {p.character_name} is wearing:')
                for item in worn:
                    dye_color = item.get('color', '')
                    name_str  = fmt_item_name(item.get('short_name') or item.get('name') or '???')
                    color_str = f' [{dye_color}]' if dye_color else ''
                    await session.send_line(f'    {name_str}{color_str}')
            else:
                await session.send_line('')
                await session.send_line(f'  {p.character_name} appears to be wearing nothing.')

            await session.send_line('')

            # ── Broadcast that you looked ──────────────────────────────────
            await server.world.broadcast_to_room(
                room.id,
                f"{session.character_name} glances at {p.character_name}.",
                exclude=session
            )
            return

    try:
        from server.core.commands.player.shop import maybe_handle_pawn_backroom_look
        if await maybe_handle_pawn_backroom_look(session, target, server):
            return
    except Exception:
        pass

    # Look at a creature
    if hasattr(server, 'creatures'):
        creature = server.creatures.find_creature_in_room(room.id, target)
        if creature:
            await session.send_line('You see ' + fmt_creature_name(creature.full_name) + '.')
            if hasattr(creature, 'description') and creature.description:
                await session.send_line('  ' + creature.description)
            await session.send_line('  It appears to be level ' + str(creature.level) + '.')
            return
        # Check dead creatures
        dead = server.creatures.get_dead_creatures_in_room(room.id)
        for c in dead:
            if target in c.name.lower():
                await session.send_line('You see the body of ' + fmt_creature_name(c.full_name) + '.')
                return

    # Look at item on ground
    ground_items = server.world.get_ground_items(room.id) if hasattr(server, "world") else getattr(room, '_ground_items', [])
    for item in ground_items:
        sn = (item.get('short_name') or '').lower()
        nn = (item.get('noun') or '').lower()
        if target in sn or target in nn:
            await session.send_line('You see ' + fmt_item_name(item.get('short_name') or 'something') + '.')
            desc = item.get('description')
            if desc:
                await session.send_line('  ' + desc)
            return

    # Look at item in inventory/hands
    if hasattr(session, 'right_hand') and session.right_hand:
        sn = (session.right_hand.get('short_name') or '').lower()
        nn = (session.right_hand.get('noun') or '').lower()
        if target in sn or target in nn:
            await session.send_line('You see ' + fmt_item_name(session.right_hand.get('short_name') or 'something') + ' in your right hand.')
            travel_mgr = getattr(server, "travel_offices", None)
            if travel_mgr:
                lines = travel_mgr.look_travel_item(session.right_hand, session=session)
                if lines:
                    for line in lines[1:]:
                        await session.send_line('  ' + line)
                    return
            desc = session.right_hand.get('description')
            if desc:
                await session.send_line('  ' + desc)
            return

    if hasattr(session, 'left_hand') and session.left_hand:
        sn = (session.left_hand.get('short_name') or '').lower()
        nn = (session.left_hand.get('noun') or '').lower()
        if target in sn or target in nn:
            await session.send_line('You see ' + fmt_item_name(session.left_hand.get('short_name') or 'something') + ' in your left hand.')
            travel_mgr = getattr(server, "travel_offices", None)
            if travel_mgr:
                lines = travel_mgr.look_travel_item(session.left_hand, session=session)
                if lines:
                    for line in lines[1:]:
                        await session.send_line('  ' + line)
                    return
            desc = session.left_hand.get('description')
            if desc:
                await session.send_line('  ' + desc)
            return

    for item in session.inventory:
        sn = (item.get('short_name') or '').lower()
        nn = (item.get('noun') or '').lower()
        if target in sn or target in nn:
            await session.send_line('You see ' + fmt_item_name(item.get('short_name') or 'something') + '.')
            desc = item.get('description')
            if desc:
                await session.send_line('  ' + desc)
            return

    await session.send_line("I could not find what you were referring to.")


async def cmd_move(session, cmd, args, server):
    """Handle directional movement (north, south, etc.)."""
    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    try:
        from server.core.commands.player.bank import maybe_handle_locker_leave
        if await maybe_handle_locker_leave(session, server):
            return
    except Exception as e:
        log.error("Locker departure hook failed: %s", e)

    if session.position != 'standing':
        await session.send_line('You need to stand up first.')
        return

    direction = DIRECTION_ALIASES.get(cmd.lower(), cmd.lower())
    target_room_id = room.get_exit_for_session(direction, session)

    if target_room_id is None:
        await session.send_line("You can't go that way.")
        return

    target_room = server.world.get_room(target_room_id)
    if not target_room:
        await session.send_line("That exit leads nowhere... (room not loaded)")
        return
    if not await _check_special_access(session, room, target_room):
        return
    if hasattr(server, "ferries"):
        ok = await server.ferries.before_move(session, room, target_room_id, direction)
        if not ok:
            return
    if hasattr(server, "justice"):
        ok = await server.justice.before_move(session, room, target_room_id, direction)
        if not ok:
            return

    # Break combat on movement -- only send flee message if truly mid-combat.
    # exited_combat grace period (set after kill) suppresses the message so
    # normal post-kill movement does not yell "You flee from combat!".
    status_mgr = getattr(server, 'status', None)
    if status_mgr:
        truly_in_combat = (
            status_mgr.has(session, 'in_combat')
            and not status_mgr.has(session, 'exited_combat')
            and session.target is not None
            and getattr(session.target, 'alive', False)
        )
        if truly_in_combat:
            await session.send_line(colorize('You flee from combat!', TextPresets.WARNING))
        if status_mgr.has(session, 'in_combat'):
            status_mgr.exit_combat(session)
    else:
        if session.in_combat:
            session.in_combat = False
            if session.target:
                if hasattr(session.target, 'in_combat'):
                    session.target.in_combat = False
                    session.target.target = None
                session.target = None
            await session.send_line(colorize('You flee from combat!', TextPresets.WARNING))

    await _move_player(session, room, target_room, direction, server, sneaking=session.hidden or getattr(session, 'sneaking', False))


async def cmd_go(session, cmd, args, server):
    """GO <target> - Move through a non-compass exit."""
    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    try:
        from server.core.commands.player.bank import maybe_handle_locker_leave
        if await maybe_handle_locker_leave(session, server):
            return
    except Exception as e:
        log.error("Locker departure hook failed: %s", e)

    if session.position != 'standing':
        await session.send_line('You need to stand up first.')
        return

    if not args:
        await session.send_line('Go where?')
        return

    raw_target = args.strip().lower()
    target = normalize_exit_key(raw_target)
    if not target:
        await session.send_line('Go where?')
        return

    # climb_ exits require the CLIMB verb, not GO â€” redirect the player
    if room.exits.get('climb_' + target) is not None:
        await session.send_line(f"You must CLIMB the {raw_target} to go that way.  Try: CLIMB {raw_target.upper()}")
        return
    if room.exits.get('swim_' + target) is not None:
        await session.send_line(f"You must SWIM {raw_target.upper()} to go that way.")
        return

    # go resolves: go_ prefixed exits, bare names, AND revealed hidden exits
    target_room_id = (
        room.exits.get('go_' + target)
        or room.exits.get(target)
        or room.get_exit_for_session(target, session)
        or room.get_exit_for_session('go_' + target, session)
    )

    if target_room_id is None:
        matches = room.find_exit_matches(target, session)
        unique_targets = list(dict.fromkeys(matches.values()))
        if len(unique_targets) == 1:
            target_room_id = unique_targets[0]
        elif len(unique_targets) > 1:
            options = ", ".join(Room.display_exit_name(key) for key in matches.keys())
            await session.send_line(f"Which '{raw_target}' do you mean?  Options here: {options}")
            return
        else:
            await session.send_line("You don't see any '" + raw_target + "' to go to.")
            return

    target_room = server.world.get_room(target_room_id)
    if not target_room:
        await session.send_line("That exit leads nowhere... (room not loaded)")
        return
    if not await _check_special_access(session, room, target_room):
        return
    if hasattr(server, "ferries"):
        ok = await server.ferries.before_move(session, room, target_room_id, 'go_' + target)
        if not ok:
            return
    if hasattr(server, "justice"):
        ok = await server.justice.before_move(session, room, target_room_id, 'go_' + target)
        if not ok:
            return

    # Same logic as cmd_move -- suppress flee message during post-combat grace period
    status_mgr = getattr(server, 'status', None)
    if status_mgr:
        truly_in_combat = (
            status_mgr.has(session, 'in_combat')
            and not status_mgr.has(session, 'exited_combat')
            and session.target is not None
            and getattr(session.target, 'alive', False)
        )
        if truly_in_combat:
            await session.send_line(colorize('You flee from combat!', TextPresets.WARNING))
        if status_mgr.has(session, 'in_combat'):
            status_mgr.exit_combat(session)
    else:
        if session.in_combat:
            session.in_combat = False
            if session.target:
                if hasattr(session.target, 'in_combat'):
                    session.target.in_combat = False
                    session.target.target = None
                session.target = None
            await session.send_line(colorize('You flee from combat!', TextPresets.WARNING))

    await _move_player(session, room, target_room, 'through the ' + raw_target, server, sneaking=session.hidden or getattr(session, 'sneaking', False))


async def _move_player(session, from_room, to_room, direction, server, sneaking=False):
    """Move a player between rooms, notifying others and saving to DB."""

    # â”€â”€ Sneak roll when moving hidden â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if sneaking:
        SKILL_STALKING = 26
        skills  = getattr(session, 'skills', {}) or {}
        sh_data = skills.get(SKILL_STALKING, {})
        sh_ranks  = sh_data.get('ranks', 0) if isinstance(sh_data, dict) else 0

        # GS4 sneak formula: d100 open-ended + skill bonuses vs threshold.
        # ranks * 3 means 200 ranks = +600 — near-impossible to fail without
        # creatures actively watching.  Low-skill players fail frequently.
        sh_bonus   = sh_ranks * 3
        buffs      = get_active_buff_totals(server, session)
        sh_bonus  += int(buffs.get("stalking_hiding_bonus", 0) or 0)
        if buffs.get("movement_bonus"):
            sh_bonus += 10

        disc_val   = getattr(session, 'stat_discipline', 50)
        disc_bonus = (disc_val - 50) // 2

        agil_val   = getattr(session, 'stat_agility', 50)
        agil_bonus = (agil_val - 50) // 2

        prof_id = getattr(session, 'profession_id', 0)
        level   = getattr(session, 'level', 1)
        if prof_id == 2:    # Rogue
            prof_bonus = (level + 3) if level >= 20 else level
        elif prof_id in (7, 8):
            prof_bonus = min(20, level)
        else:
            prof_bonus = 0

        # Terrain modifier — dark/outdoor rooms are easier to sneak in
        terrain_mod = 0
        if getattr(to_room, 'dark', False):
            terrain_mod += 20
        elif not getattr(to_room, 'indoor', False):
            terrain_mod += 10
        elif getattr(to_room, 'safe', False):
            terrain_mod -= 15

        # Creature difficulty — only destination room creatures can spot you
        creature_difficulty = 0
        if hasattr(server, 'creatures'):
            for c in server.creatures.get_creatures_in_room(to_room.id):
                if c.alive and c.aggressive:
                    creature_difficulty += max(0, (c.level - level) * 3 + 5)

        # d100 open-ended roll (low fumble is mild — not a -100 death spiral)
        base_roll = random.randint(1, 100)
        if base_roll >= 96:
            base_roll += random.randint(1, 100)
        elif base_roll <= 5:
            base_roll -= random.randint(1, 10)

        total = base_roll + sh_bonus + disc_bonus + agil_bonus + prof_bonus + terrain_mod

        # Success threshold: 101 + creature difficulty.
        # High-skill player (200 ranks): bonus ~+600 — succeeds on any positive roll.
        # Low-skill player (10 ranks): bonus ~+30 — needs a roll of ~70+ to succeed.
        threshold = 101 + creature_difficulty

        if total >= threshold:
            dir_display = direction.replace('_', ' ')
            await session.send_line(colorize(f'You sneak {dir_display}.', TextPresets.STEALTH))
            depart_msg = f'{session.character_name} slips away silently.'
            arrive_msg = f'Something shifts in the shadows.'
        else:
            session.hidden  = False
            session.sneaking = False
            dir_display = direction.replace('_', ' ')
            await session.send_line(colorize(
                f'You stumble while trying to sneak and are revealed!',
                TextPresets.WARNING
            ))

            depart_msg = f'{fmt_player_name(session.character_name)} just went {direction}.'
            arrive_msg = f'{fmt_player_name(session.character_name)} just arrived.'

    else:
        depart_msg = f'{fmt_player_name(session.character_name)} just went {direction}.'
        arrive_msg = f'{fmt_player_name(session.character_name)} just arrived.'

    pets = getattr(server, "pets", None)
    if pets:
        pet_depart, pet_arrive = pets.move_messages(session, direction, sneaking and getattr(session, "hidden", False))
        if pet_depart:
            depart_msg = pet_depart
        if pet_arrive:
            arrive_msg = pet_arrive

    await server.world.broadcast_to_room(from_room.id, depart_msg, exclude=session)

    tracker = getattr(server, "tracking", None)
    if tracker:
        try:
            tracker.record_departure(
                actor_kind="player",
                actor_id=int(getattr(session, "character_id", 0) or 0),
                actor_name=getattr(session, "character_name", "") or "someone",
                from_room_id=int(from_room.id),
                to_room_id=int(to_room.id),
                direction=str(direction or "out"),
                hidden=bool(getattr(session, "hidden", False)),
                sneaking=bool(getattr(session, "sneaking", False)),
                actor_level=int(getattr(session, "level", 1) or 1),
            )
        except Exception as e:
            log.debug("Failed to record player trail: %s", e)

    server.world.remove_player_from_room(session, from_room.id)
    session.previous_room = from_room
    session.current_room = to_room
    server.world.add_player_to_room(session, to_room.id)

    await server.world.broadcast_to_room(to_room.id, arrive_msg, exclude=session)

    # Sneak perception counter-roll
    if sneaking and session.hidden:
        await _check_sneak_detection(session, to_room, total, server)

    # Save room change to DB in real-time
    if server.db and session.character_id:
        server.db.save_character_room(session.character_id, to_room.id)

    # Party follow: silently drag living party members in same room
    try:
        from server.core.commands.player.party import party_follow_move
        await party_follow_move(session, from_room, to_room, direction, server)
    except Exception as _pfe:
        import logging as _log
        _log.getLogger(__name__).error("party_follow_move error: %s", _pfe)

    # Show the new room
    await cmd_look(session, 'look', '', server)

    # Context-sensitive command hints
    from server.core.world.room_hints import show_room_hints
    await show_room_hints(session, to_room, server)

    justice_mgr = getattr(server, "justice", None)
    if justice_mgr:
        try:
            await justice_mgr.after_move(session, to_room)
        except Exception as e:
            log.error("Justice after_move failed: %s", e, exc_info=True)

    try:
        guild_engine = getattr(server, "guild", None)
        if guild_engine:
            if hasattr(guild_engine, "on_character_enter_room"):
                await guild_engine.on_character_enter_room(session, from_room=from_room, to_room=to_room)
            elif hasattr(guild_engine, "maybe_complete_travel_bounty"):
                await guild_engine.maybe_complete_travel_bounty(session)
    except Exception as e:
        log.error("Adventurer travel bounty hook failed: %s", e)

    # Tutorial hook
    if hasattr(session, 'tutorial_complete') and not session.tutorial_complete:
        if hasattr(server, 'tutorial'):
            await server.tutorial.on_room_enter(session, to_room.id)

    if hasattr(server, "pets"):
        await server.pets.on_room_enter(session, from_room, to_room)


def _is_hearthstone_room(room) -> bool:
    if not room:
        return False
    title = str(getattr(room, "title", "") or "")
    label = str(getattr(room, "location_name", "") or "")
    return title.startswith("Hearthstone") or label.startswith("Hearthstone")


async def _check_special_access(session, from_room, to_room):
    """Retail-style access checks for special locations."""
    entering_hearthstone = _is_hearthstone_room(to_room) and not _is_hearthstone_room(from_room)
    if entering_hearthstone:
        fame_total = int(getattr(session, "fame", 0) or 0)
        level = int(getattr(session, "level", 0) or 0)
        if fame_total < HEARTHSTONE_MIN_FAME and level < HEARTHSTONE_MIN_LEVEL:
            await session.send_line(
                colorize(
                    "A discreet servant bars the way.  Only adventurers with at least 200,000 fame or those above level 20 may enter Hearthstone Manor.",
                    TextPresets.WARNING,
                )
            )
            return False
    return True
