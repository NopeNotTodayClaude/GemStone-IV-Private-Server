"""
esp.py — GemStone IV ESP (Crystal Amulet / Thought) Channel System

Channels
--------
  general   IC  global  — default tuned for all characters
  ooc       OOC global  — out-of-character chat
  help      OOC global  — help requests / new player questions
  trade     OOC global  — buying, selling, services
  guild     IC  global  — profession-specific (Warriors talk to Warriors, etc.)

All channels are global (server-wide).  Guild is filtered to matching professions.

Commands
--------
  ESP                          Show help + current tune status
  ESP TOGGLE                   Toggle all ESP on/off for this session
  ESP TUNE <channel>           Tune to a channel (or set as default if already tuned)
  ESP UNTUNE <channel>         Untune from a channel
  ESP WHO <channel> [FULL]     Show who is tuned to a channel
  ESP IGNORE <player>          Ignore a player on all channels
  ESP UNIGNORE <player>        Remove from ignore list
  THINK <message>              Send to your default channel (general if none set)
  THINK TO <player> <message>  Private thought to one player (global range)
  CHAT <message>               Shortcut — always sends to OOC channel
"""

import logging
from server.core.protocol.colors import colorize, TextPresets
from server.core.commands.player.info import PROFESSIONS

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Channel definitions
# ─────────────────────────────────────────────────────────────────────────────

CHANNELS = {
    'general': {
        'label':    'General',
        'ooc':      False,
        'color':    TextPresets.CHANNEL_GENERAL,
        'tag':      '[General]',
        'desc':     'General in-character discussion (global).',
    },
    'ooc': {
        'label':    'OOC',
        'ooc':      True,
        'color':    TextPresets.CHANNEL_OOC,
        'tag':      '[OOC]',
        'desc':     'Out-of-character chat (global).',
    },
    'help': {
        'label':    'Help',
        'ooc':      True,
        'color':    TextPresets.CHANNEL_HELP,
        'tag':      '[Help]',
        'desc':     'Questions, new-player help (global).',
    },
    'trade': {
        'label':    'Trade',
        'ooc':      True,
        'color':    TextPresets.CHANNEL_TRADE,
        'tag':      '[Trade]',
        'desc':     'Buying, selling, and services (global).',
    },
    'guild': {
        'label':    'Guild',
        'ooc':      False,
        'color':    TextPresets.CHANNEL_GUILD,
        'tag':      '[Guild]',
        'desc':     'Profession channel — only your guild hears you (global).',
        'guild_only': True,
    },
}

DEFAULT_TUNED = {'general', 'ooc', 'help'}


# ─────────────────────────────────────────────────────────────────────────────
# Per-session ESP state helpers
# ─────────────────────────────────────────────────────────────────────────────

def _esp_state(session) -> dict:
    """Return (creating if needed) the ESP state dict on the session."""
    if not hasattr(session, '_esp'):
        session._esp = {
            'enabled':  True,
            'tuned':    set(DEFAULT_TUNED),   # channel keys tuned to
            'default':  'general',            # default channel for THINK
            'ignoring': set(),                # character names being ignored
        }
    return session._esp


def esp_enabled(session) -> bool:
    return _esp_state(session)['enabled']


def is_tuned(session, channel_key: str) -> bool:
    return channel_key in _esp_state(session)['tuned']


def is_ignoring(session, name: str) -> bool:
    return name.lower() in _esp_state(session)['ignoring']


# ─────────────────────────────────────────────────────────────────────────────
# Core broadcast
# ─────────────────────────────────────────────────────────────────────────────

async def _broadcast_channel(server, sender_session, channel_key: str, message: str):
    """
    Send a message to all online players tuned to channel_key.
    Guild channel: only recipients with the same profession_id see it.
    """
    chan = CHANNELS.get(channel_key)
    if not chan:
        return

    sender_name = sender_session.character_name or 'Someone'
    tag         = chan['tag']
    color       = chan['color']
    guild_only  = chan.get('guild_only', False)
    sender_prof = getattr(sender_session, 'profession_id', 0)

    # OOC wrapper for OOC channels
    if chan['ooc']:
        formatted = colorize(f"{tag} {sender_name}'s player says, \"{message}\"", color)
    else:
        formatted = colorize(f"{tag} {sender_name} thinks, \"{message}\"", color)

    for s in server.sessions.playing():
        state = _esp_state(s)
        if not state['enabled']:
            continue
        if channel_key not in state['tuned']:
            continue
        if is_ignoring(s, sender_name):
            continue
        if guild_only:
            if getattr(s, 'profession_id', -1) != sender_prof:
                continue

        if s is sender_session:
            # Sender sees their own message with "You" phrasing
            if chan['ooc']:
                self_msg = colorize(f"{tag} You say, \"{message}\"", color)
            else:
                self_msg = colorize(f"{tag} You think, \"{message}\"", color)
            await s.send_line(self_msg)
        else:
            await s.send_line(formatted)


async def _broadcast_private_think(server, sender_session, target_session, message: str):
    """Send a private THINK TO message between two players."""
    sender = sender_session.character_name or 'Someone'
    target = target_session.character_name or 'Someone'
    color  = TextPresets.CHANNEL_PRIVATE

    await sender_session.send_line(
        colorize(f"You send a thought to {target}, \"{message}\"", color)
    )
    await target_session.send_line(
        colorize(f"{sender} sends you a thought, \"{message}\"", color)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Command: ESP
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_esp(session, cmd, args, server):
    """
    ESP                     Show ESP help and your current channel status.
    ESP TOGGLE              Toggle ESP on or off.
    ESP TUNE <channel>      Tune to a channel (or make it your default).
    ESP UNTUNE <channel>    Stop receiving a channel.
    ESP WHO <channel>       Show how many players are tuned to a channel.
    ESP WHO <channel> FULL  Show names of players tuned to a channel.
    ESP IGNORE <player>     Ignore a player on all ESP channels.
    ESP UNIGNORE <player>   Stop ignoring a player.
    """
    state = _esp_state(session)
    sub   = (args or '').strip()
    sub_l = sub.lower()

    # ── ESP TOGGLE ────────────────────────────────────────────────────────
    if sub_l == 'toggle':
        state['enabled'] = not state['enabled']
        if state['enabled']:
            await session.send_line(colorize(
                'A dull tingle forms in the back of your mind as you become '
                'more aware of the world around you.',
                TextPresets.CHANNEL_GENERAL
            ))
        else:
            await session.send_line(colorize(
                'The dull tingle in the back of your mind fades along with '
                'your heightened awareness of the world around you.',
                TextPresets.SYSTEM
            ))
        return

    # ── ESP TUNE <channel> ────────────────────────────────────────────────
    if sub_l.startswith('tune '):
        chan_name = sub_l[5:].strip()
        chan_key  = _resolve_channel(chan_name, session)
        if not chan_key:
            await session.send_line(
                colorize(f"  Unknown channel '{chan_name}'.  ", TextPresets.WARNING)
                + _channel_list_str()
            )
            return
        if chan_key in state['tuned']:
            # Already tuned → set as default
            state['default'] = chan_key
            label = CHANNELS[chan_key]['label']
            await session.send_line(colorize(
                f"  {label} is now your default THINK channel.", TextPresets.SYSTEM
            ))
        else:
            state['tuned'].add(chan_key)
            label = CHANNELS[chan_key]['label']
            await session.send_line(colorize(
                f"  You are now tuned to the {label} channel.", TextPresets.SYSTEM
            ))
        return

    # ── ESP UNTUNE <channel> ──────────────────────────────────────────────
    if sub_l.startswith('untune '):
        chan_name = sub_l[7:].strip()
        chan_key  = _resolve_channel(chan_name, session)
        if not chan_key:
            await session.send_line(colorize(
                f"  Unknown channel '{chan_name}'.", TextPresets.WARNING
            ))
            return
        if chan_key not in state['tuned']:
            label = CHANNELS[chan_key]['label']
            await session.send_line(colorize(
                f"  You are not tuned to the {label} channel.", TextPresets.SYSTEM
            ))
            return
        state['tuned'].discard(chan_key)
        if state['default'] == chan_key:
            state['default'] = 'general'
        label = CHANNELS[chan_key]['label']
        await session.send_line(colorize(
            f"  You are no longer tuned to the {label} channel.", TextPresets.SYSTEM
        ))
        return

    # ── ESP WHO <channel> [FULL] ──────────────────────────────────────────
    if sub_l.startswith('who '):
        parts    = sub_l[4:].strip().split()
        chan_name = parts[0]
        full      = len(parts) > 1 and parts[1] == 'full'
        chan_key  = _resolve_channel(chan_name, session)
        if not chan_key:
            await session.send_line(colorize(
                f"  Unknown channel '{chan_name}'.", TextPresets.WARNING
            ))
            return
        await _cmd_esp_who(session, server, chan_key, full)
        return

    # ── ESP IGNORE <player> ───────────────────────────────────────────────
    if sub_l.startswith('ignore '):
        target_name = sub[7:].strip()
        target = _find_online(server, target_name)
        if not target:
            await session.send_line(colorize(
                f"  Unable to add '{target_name}' to your ignore list.  "
                "Matching player not found, or player is not online.",
                TextPresets.WARNING
            ))
            return
        tname = target.character_name
        state['ignoring'].add(tname.lower())
        await session.send_line(colorize(
            f"  You are now ignoring {tname}'s thoughts.",
            TextPresets.SYSTEM
        ))
        return

    # ── ESP UNIGNORE <player> ─────────────────────────────────────────────
    if sub_l.startswith('unignore '):
        target_name = sub[9:].strip().lower()
        if target_name in state['ignoring']:
            state['ignoring'].discard(target_name)
            await session.send_line(colorize(
                f"  You are no longer ignoring {target_name}'s thoughts.",
                TextPresets.SYSTEM
            ))
        else:
            await session.send_line(colorize(
                f"  You were not ignoring {target_name}.",
                TextPresets.SYSTEM
            ))
        return

    # ── ESP / ESP HELP — show status ──────────────────────────────────────
    await _show_esp_status(session, state)


async def _show_esp_status(session, state):
    toggle_str = colorize('ON', TextPresets.HEALTH_FULL) if state['enabled'] \
                 else colorize('OFF', TextPresets.HEALTH_CRIT)
    default_label = CHANNELS.get(state['default'], {}).get('label', 'General')

    await session.send_line('')
    await session.send_line(colorize('  ── ESP Channel System ─────────────────────────', TextPresets.SYSTEM))
    await session.send_line(f"  ESP is currently: {toggle_str}")
    await session.send_line(f"  Default THINK channel: {colorize(default_label, TextPresets.CHANNEL_GENERAL)}")
    await session.send_line('')
    await session.send_line(colorize('  Commands:', TextPresets.SYSTEM))
    await session.send_line('    ESP TOGGLE              — Toggle ESP on/off')
    await session.send_line('    ESP TUNE <channel>      — Tune to a channel (or set as default if already tuned)')
    await session.send_line('    ESP UNTUNE <channel>    — Stop receiving a channel')
    await session.send_line('    ESP WHO <channel> [FULL]— Show who is tuned')
    await session.send_line('    ESP IGNORE <player>     — Ignore a player on all channels')
    await session.send_line('    ESP UNIGNORE <player>   — Stop ignoring a player')
    await session.send_line('    THINK <message>         — Broadcast to your default channel')
    await session.send_line('    THINK TO <player> <msg> — Private thought to one player')
    await session.send_line('    CHAT <message>          — Shortcut for the OOC channel')
    await session.send_line('')
    await session.send_line(colorize('  Available Channels:', TextPresets.SYSTEM))
    tuned = state['tuned']
    for key, chan in CHANNELS.items():
        kind    = 'OOC' if chan['ooc'] else 'IC'
        status  = colorize(' [TUNED]', TextPresets.HEALTH_FULL) if key in tuned else ''
        default = colorize(' [DEFAULT]', TextPresets.EXPERIENCE) if key == state['default'] else ''
        guild   = ' (your profession only)' if chan.get('guild_only') else ''
        await session.send_line(
            f"    {colorize(chan['label'], chan['color']):<20}  {kind}  {chan['desc']}{guild}{status}{default}"
        )
    await session.send_line('')
    ignoring = state['ignoring']
    if ignoring:
        await session.send_line(
            colorize('  Ignoring: ', TextPresets.WARNING)
            + ', '.join(sorted(ignoring))
        )
    else:
        await session.send_line('  You are not ignoring anyone.')
    await session.send_line(colorize('  ────────────────────────────────────────────────', TextPresets.SYSTEM))
    await session.send_line('')


async def _cmd_esp_who(session, server, chan_key: str, full: bool):
    chan  = CHANNELS[chan_key]
    label = chan['label']
    guild_only = chan.get('guild_only', False)
    sender_prof = getattr(session, 'profession_id', 0)

    tuned_players = []
    for s in server.sessions.playing():
        st = _esp_state(s)
        if not st['enabled']:
            continue
        if chan_key not in st['tuned']:
            continue
        if guild_only and getattr(s, 'profession_id', -1) != sender_prof:
            continue
        tuned_players.append(s.character_name or '?')

    await session.send_line('')
    await session.send_line(colorize(
        f"  You strain your senses outward searching for others on the {label} channel.",
        chan['color']
    ))
    await session.send_line(f"  Tuned Players: {len(tuned_players)}")
    if full and tuned_players:
        await session.send_line('  ' + ', '.join(sorted(tuned_players)))
    await session.send_line('')


# ─────────────────────────────────────────────────────────────────────────────
# Command: THINK
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_think(session, cmd, args, server):
    """
    THINK <message>              Broadcast to your default ESP channel.
    THINK TO <player> <message>  Private thought to one player (global range).
    THINK ON <channel> <message> Send to a specific channel this one time.
    """
    if not args:
        await session.send_line('What are you thinking?')
        return

    state = _esp_state(session)
    text  = args.strip()
    lower = text.lower()

    # ── THINK TO <player> <message> ───────────────────────────────────────
    if lower.startswith('to ') or lower.startswith('tp ') or lower.startswith('ot '):
        rest  = text[3:].strip()
        parts = rest.split(None, 1)
        if len(parts) < 2:
            await session.send_line('Think to whom, and what?')
            return
        target_name, message = parts[0], parts[1]
        target = _find_online(server, target_name)
        if not target:
            await session.send_line(colorize(
                f"  {target_name} does not appear to be online.",
                TextPresets.WARNING
            ))
            return
        if is_ignoring(target, session.character_name or ''):
            # Silent fail — GS4 behaviour
            await session.send_line(colorize(
                f"  You send a thought to {target.character_name}, \"{message}\"",
                TextPresets.CHANNEL_PRIVATE
            ))
            return
        await _broadcast_private_think(server, session, target, message)
        return

    # ── THINK ON <channel> <message> ──────────────────────────────────────
    if lower.startswith('on '):
        rest  = text[3:].strip()
        parts = rest.split(None, 1)
        if len(parts) < 2:
            await session.send_line('Think on which channel, and what?')
            return
        chan_name, message = parts[0], parts[1]
        chan_key = _resolve_channel(chan_name, session)
        if not chan_key:
            await session.send_line(colorize(
                f"  Unknown channel '{chan_name}'.", TextPresets.WARNING
            ))
            return
        if chan_key not in state['tuned']:
            label = CHANNELS[chan_key]['label']
            await session.send_line(colorize(
                f"  You are not tuned to the {label} channel.  "
                f"Type ESP TUNE {label} to join it.",
                TextPresets.WARNING
            ))
            return
        if not state['enabled']:
            await session.send_line(colorize(
                '  Your ESP is toggled off.  Type ESP TOGGLE to re-enable it.',
                TextPresets.WARNING
            ))
            return
        await _broadcast_channel(server, session, chan_key, message)
        return

    # ── THINK <message> → default channel ─────────────────────────────────
    if not state['enabled']:
        await session.send_line(colorize(
            '  Your ESP is toggled off.  Type ESP TOGGLE to re-enable it.',
            TextPresets.WARNING
        ))
        return

    default_key = state.get('default', 'general')
    if default_key not in state['tuned']:
        default_key = next(iter(state['tuned']), 'general')

    await _broadcast_channel(server, session, default_key, text)


# ─────────────────────────────────────────────────────────────────────────────
# Command: CHAT  (shortcut to OOC)
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_chat(session, cmd, args, server):
    """CHAT <message> — Send a message on the OOC channel."""
    if not args:
        await session.send_line(
            colorize('Usage: CHAT <message>', TextPresets.SYSTEM)
            + '  — sends on the OOC channel.'
        )
        await session.send_line(
            "  Note: CHAT is for the OOC channel.  "
            "To send a private thought use THINK TO <player>."
        )
        return

    # Check if they tried CHAT TO <player>
    lower = args.strip().lower()
    if lower.startswith('to '):
        await session.send_line(colorize(
            "  It looks like you are trying to send a thought to a specific person.  "
            "CHAT is used to speak on the OOC channel.  "
            "To direct thoughts, use THINK TO <player> <message>.",
            TextPresets.WARNING
        ))
        return

    state = _esp_state(session)
    if not state['enabled']:
        await session.send_line(colorize(
            '  Your ESP is toggled off.  Type ESP TOGGLE to re-enable it.',
            TextPresets.WARNING
        ))
        return

    if 'ooc' not in state['tuned']:
        state['tuned'].add('ooc')
        await session.send_line(colorize(
            '  You tune to the OOC channel to speak.',
            TextPresets.SYSTEM
        ))

    await _broadcast_channel(server, session, 'ooc', args.strip())


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_channel(name: str, session=None) -> str | None:
    """Return the canonical channel key for a name/alias, or None."""
    n = name.strip().lower()
    if n in CHANNELS:
        return n
    # Partial match
    for key in CHANNELS:
        if key.startswith(n) or CHANNELS[key]['label'].lower().startswith(n):
            return key
    return None


def _channel_list_str() -> str:
    labels = [CHANNELS[k]['label'] for k in CHANNELS]
    return 'Available channels: ' + ', '.join(labels)


def _find_online(server, name: str):
    """Find an online session by name (case-insensitive, partial ok)."""
    name_l = name.lower()
    exact  = None
    partial = None
    for s in server.sessions.playing():
        cn = (s.character_name or '').lower()
        if cn == name_l:
            exact = s
            break
        if cn.startswith(name_l) and not partial:
            partial = s
    return exact or partial
