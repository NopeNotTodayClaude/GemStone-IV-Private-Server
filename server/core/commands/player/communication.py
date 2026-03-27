"""
GemStone IV Communication Commands
SAY, WHISPER (IC/OOC/VISIBLE), YELL, SHOUT, SING, ASK, TELL

THINK, CHAT, and ESP are in esp.py.
YELL propagates:
  - Same room:      full message + speaker name  (bold yellow)
  - 1 room away:    "[Name] yells from the [direction], ..."  (yellow)
  - 2 rooms away:   "You hear a distant yell..."  (dim yellow)
"""

import logging
from server.core.protocol.colors import (
    speech, whisper as fmt_whisper, colorize, TextPresets
)

log = logging.getLogger(__name__)

_OPPOSITES = {
    'north':     'south',     'south':     'north',
    'east':      'west',      'west':      'east',
    'northeast': 'southwest', 'southwest': 'northeast',
    'northwest': 'southeast', 'southeast': 'northwest',
    'up':        'below',     'down':      'above',
    'out':       'inside',
}


# ─────────────────────────────────────────────────────────────────────────────
# SAY
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_say(session, cmd, args, server):
    """SAY <message> - Speak aloud to everyone in the room."""
    if not args:
        await session.send_line('What do you want to say?')
        return

    message = args.strip()
    if message.endswith('!'):
        verb_self, verb_other = 'exclaim', 'exclaims'
    elif message.endswith('?'):
        verb_self, verb_other = 'ask', 'asks'
    else:
        verb_self, verb_other = 'say', 'says'

    await session.send_line(speech('You', verb_self, message, is_self=True))
    room = session.current_room
    if room:
        for other in server.world.get_players_in_room(room.id):
            if other != session:
                await other.send_line(
                    speech(session.character_name, verb_other, message)
                )


# ─────────────────────────────────────────────────────────────────────────────
# WHISPER  (IC / OOC / VISIBLE / GROUP)
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_whisper(session, cmd, args, server):
    """
    WHISPER <player> <message>          IC whisper (default)
    WHISPER IC <player> <message>       Explicit IC whisper
    WHISPER OOC <player> <message>      OOC player-to-player whisper
    WHISPER VISIBLE <player> <message>  IC; room sees the act but not content
    WHISPER GROUP <message>             Whisper to all party members (IC)
    WHISPER OOC GROUP <message>         OOC whisper to all party members
    """
    if not args:
        await session.send_line(
            'Usage: WHISPER <player> <message>  |  '
            'WHISPER IC/OOC/VISIBLE <player> <message>  |  '
            'WHISPER GROUP <message>'
        )
        return

    parts = args.split(None, 1)
    first = parts[0].lower()
    wtype = 'ic'
    rest  = args

    if first in ('ic', 'ooc', 'visible'):
        wtype = first
        rest  = parts[1].strip() if len(parts) > 1 else ''
        if not rest:
            await session.send_line('Whisper to whom, and what?')
            return

    rest_parts = rest.split(None, 1)

    if rest_parts[0].lower() == 'group':
        message = rest_parts[1] if len(rest_parts) > 1 else ''
        if not message:
            await session.send_line('What do you want to whisper to the group?')
            return
        await _whisper_group(session, message, wtype, server)
        return

    if len(rest_parts) < 2:
        await session.send_line('Whisper to whom? And what?')
        return

    target_name = rest_parts[0]
    message     = rest_parts[1]
    room        = session.current_room
    if not room:
        return

    players_in_room = server.world.get_players_in_room(room.id)
    target = None
    for p in players_in_room:
        if p.character_name and p.character_name.lower().startswith(target_name.lower()):
            target = p
            break

    if not target:
        await session.send_line(f"You don't see {target_name} here.")
        return

    if target is session:
        await session.send_line('You whisper to yourself.')
        for p in players_in_room:
            if p is not session:
                await p.send_line(
                    colorize(f"{session.character_name} whispers something to themselves.", TextPresets.WHISPER)
                )
        return

    await _send_whisper(session, target, message, wtype, players_in_room)


async def _send_whisper(sender, target, message, wtype, room_players):
    sname = sender.character_name
    tname = target.character_name
    if wtype == 'ooc':
        to_sender  = colorize(f"(OOC) You whisper to {tname}'s player, \"{message}\"", TextPresets.CHANNEL_OOC)
        to_target  = colorize(f"(OOC) {sname}'s player whispers to you, \"{message}\"", TextPresets.CHANNEL_OOC)
        to_room    = colorize(f"(OOC) {sname}'s player whispers something to {tname}'s player.", TextPresets.CHANNEL_OOC)
    elif wtype == 'visible':
        to_sender  = fmt_whisper(sname, tname, message, 'sender')
        to_target  = fmt_whisper(sname, tname, message, 'receiver')
        to_room    = colorize(f"{sname} leans toward {tname} and whispers something.", TextPresets.WHISPER)
    else:
        to_sender  = fmt_whisper(sname, tname, message, 'sender')
        to_target  = fmt_whisper(sname, tname, message, 'receiver')
        to_room    = fmt_whisper(sname, tname, message, 'observer')

    await sender.send_line(to_sender)
    await target.send_line(to_target)
    for p in room_players:
        if p is not sender and p is not target:
            await p.send_line(to_room)


async def _whisper_group(session, message, wtype, server):
    mgr = getattr(server, 'party_manager', None)
    if not mgr:
        await session.send_line(colorize('  You are not in a party.', TextPresets.WARNING))
        return
    party = mgr.get_party(session)
    if not party:
        await session.send_line(colorize('  You are not in a party.', TextPresets.WARNING))
        return
    sname = session.character_name
    if wtype == 'ooc':
        to_self   = colorize(f"(OOC) [Group] You whisper, \"{message}\"", TextPresets.CHANNEL_OOC)
        to_others = colorize(f"(OOC) [Group] {sname}'s player whispers, \"{message}\"", TextPresets.CHANNEL_OOC)
    else:
        to_self   = colorize(f"[Group] You whisper, \"{message}\"", TextPresets.WHISPER)
        to_others = colorize(f"[Group] {sname} whispers, \"{message}\"", TextPresets.WHISPER)
    await session.send_line(to_self)
    for m in party.living_members():
        if m is not session:
            await m.send_line(to_others)


# ─────────────────────────────────────────────────────────────────────────────
# YELL  — 3-tier distance propagation
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_yell(session, cmd, args, server):
    """YELL <message> — Heard in this room, adjacent rooms, and 2 rooms away."""
    room = session.current_room
    if not room:
        return

    name = session.character_name

    if not args:
        self_msg  = colorize('You let out a loud yell!', TextPresets.YELL_LOCAL)
        room_msg  = colorize(f'{name} lets out a loud yell!', TextPresets.YELL_LOCAL)
        near_fn   = lambda rev: colorize(f'You hear someone yell from the {rev}!', TextPresets.YELL_NEAR)
        far_msg   = colorize('You hear a distant yell from somewhere nearby.', TextPresets.YELL_FAR)
    else:
        msg       = args.strip()
        self_msg  = colorize(f'You yell, "{msg}"', TextPresets.YELL_LOCAL)
        room_msg  = colorize(f'{name} yells, "{msg}"', TextPresets.YELL_LOCAL)
        near_fn   = lambda rev: colorize(f'{name} yells from the {rev}, "{msg}"', TextPresets.YELL_NEAR)
        far_msg   = colorize(f'You hear a distant yell, "{msg}"', TextPresets.YELL_FAR)

    await session.send_line(self_msg)
    await server.world.broadcast_to_room(room.id, room_msg, exclude=session)

    one_hop_ids = set()
    for direction, adj_id in room.exits.items():
        if direction.startswith('go_'):
            rev = 'nearby'
        else:
            rev = _OPPOSITES.get(direction, 'nearby')
        one_hop_ids.add(adj_id)
        await server.world.broadcast_to_room(adj_id, near_fn(rev))

    for adj_id in one_hop_ids:
        adj_room = server.world.get_room(adj_id)
        if not adj_room:
            continue
        for _, far_id in adj_room.exits.items():
            if far_id != room.id and far_id not in one_hop_ids:
                await server.world.broadcast_to_room(far_id, far_msg)


# ─────────────────────────────────────────────────────────────────────────────
# SHOUT  — entire zone
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_shout(session, cmd, args, server):
    """SHOUT <message> - Shout to everyone in the zone."""
    name = session.character_name
    if not args:
        await session.send_line(colorize('You let out a loud shout!', TextPresets.YELL_LOCAL))
        text_room = colorize(f'{name} lets out a loud shout!', TextPresets.YELL_LOCAL)
        text_zone = colorize('You hear someone shout from nearby.', TextPresets.YELL_NEAR)
    else:
        msg = args.strip()
        await session.send_line(colorize(f'You shout, "{msg}"', TextPresets.YELL_LOCAL))
        text_room = colorize(f'{name} shouts, "{msg}"', TextPresets.YELL_LOCAL)
        text_zone = colorize(f'You hear someone shout, "{msg}"', TextPresets.YELL_NEAR)

    room = session.current_room
    if not room:
        return
    await server.world.broadcast_to_room(room.id, text_room, exclude=session)
    if hasattr(room, 'zone') and room.zone and hasattr(room.zone, 'rooms'):
        for other_room_id in room.zone.rooms:
            if other_room_id != room.id:
                await server.world.broadcast_to_room(other_room_id, text_zone)


# ─────────────────────────────────────────────────────────────────────────────
# SING
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_sing(session, cmd, args, server):
    """SING <lyrics> - Sing something aloud."""
    if not args:
        await session.send_line('You hum a soft melody.')
        if session.current_room:
            await server.world.broadcast_to_room(
                session.current_room.id,
                f'{session.character_name} hums a soft melody.',
                exclude=session
            )
        return
    msg = args.strip()
    await session.send_line(f'You sing, "{msg}"')
    if session.current_room:
        await server.world.broadcast_to_room(
            session.current_room.id,
            colorize(f'{session.character_name} sings, "{msg}"', TextPresets.SPEECH),
            exclude=session
        )


# ─────────────────────────────────────────────────────────────────────────────
# ASK
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_ask(session, cmd, args, server):
    """ASK <player> ABOUT <topic>"""
    if not args:
        await session.send_line('Ask whom about what?')
        return
    lower = args.lower()
    if ' about ' in lower:
        idx         = lower.index(' about ')
        target_name = args[:idx].strip()
        topic       = args[idx + 7:].strip()
    else:
        parts       = args.split(None, 1)
        target_name = parts[0]
        topic       = parts[1] if len(parts) > 1 else ''
    if not topic:
        await session.send_line('Ask them about what?')
        return
    room = session.current_room
    if not room:
        return
    target = None
    for p in server.world.get_players_in_room(room.id):
        if p.character_name and p.character_name.lower().startswith(target_name.lower()):
            target = p
            break
    if not target:
        await session.send_line(f"You don't see {target_name} here.")
        return
    await session.send_line(f'You ask {target.character_name} about {topic}.')
    await target.send_line(f'{session.character_name} asks you about {topic}.')
    for p in server.world.get_players_in_room(room.id):
        if p is not session and p is not target:
            await p.send_line(f'{session.character_name} asks {target.character_name} about {topic}.')


# ─────────────────────────────────────────────────────────────────────────────
# TELL
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_tell(session, cmd, args, server):
    """TELL <player> <message> - Private message to any online player."""
    if not args:
        await session.send_line('Tell whom what?')
        return
    parts       = args.split(None, 1)
    target_name = parts[0]
    message     = parts[1] if len(parts) > 1 else ''
    if not message:
        await session.send_line('What do you want to tell them?')
        return
    target  = None
    name_l  = target_name.lower()
    for s in server.sessions.playing():
        if s.character_name and s.character_name.lower() == name_l:
            target = s
            break
    if not target:
        for s in server.sessions.playing():
            if s.character_name and s.character_name.lower().startswith(name_l):
                target = s
                break
    if not target:
        await session.send_line('That person is not online.')
        return
    await session.send_line(
        colorize(f'You tell {target.character_name}, "{message}"', TextPresets.WHISPER)
    )
    await target.send_line(
        colorize(f'{session.character_name} tells you, "{message}"', TextPresets.WHISPER)
    )
