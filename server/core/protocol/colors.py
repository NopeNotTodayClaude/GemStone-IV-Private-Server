"""
ANSI Color System for GemStone IV
Based on the Wrayth protocol preset IDs.
Maps game text types to ANSI escape codes for telnet clients.

Color assignments (based on classic StormFront/Lich conventions):
  Room title:     Bold Cyan
  Room desc:      White (default)
  Speech:         Green
  Whisper:        Magenta/Purple
  Thought:        Light Blue (bright cyan)
  Creature:       Bold Red
  Item/Loot:      Yellow
  Exits:          Bold White
  Combat hit:     Bold Yellow
  Combat miss:    Gray
  Damage taken:   Bold Red
  System/Status:  Bold Blue
  Experience:     Bright Green
  Death:          Bold Red on Black
  Prompt:         Gray
  Roundtime:      Yellow
"""

# ANSI escape code constants
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"

# Foreground colors
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright foreground
BRIGHT_BLACK = "\033[90m"   # Gray
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"


class TextPresets:
    """Maps GS4 text categories to ANSI color codes."""

    # Room display
    ROOM_TITLE = BOLD + CYAN
    ROOM_DESC = WHITE
    ROOM_EXITS = BOLD + WHITE
    ROOM_EXIT_LABEL = BRIGHT_BLACK  # "Obvious paths:" in gray

    # Communication
    SPEECH = GREEN
    SPEECH_QUOTE = BRIGHT_GREEN
    WHISPER = MAGENTA
    WHISPER_QUOTE = BRIGHT_MAGENTA
    THOUGHT = BRIGHT_CYAN

    # Entities
    CREATURE_NAME = BOLD + RED
    CREATURE_DESC = RED
    NPC_NAME = BOLD + YELLOW
    NPC_EMOTE = BRIGHT_CYAN       # light blue — ambient emotes
    NPC_SPEECH = BOLD + GREEN     # bold green — NPC spoken dialogue
    PLAYER_NAME = BOLD + WHITE
    ITEM_NAME = YELLOW
    ITEM_DESC = BRIGHT_YELLOW

    # Combat
    COMBAT_HIT = BOLD + YELLOW
    COMBAT_MISS = BRIGHT_BLACK
    COMBAT_CRIT = BOLD + RED
    COMBAT_DAMAGE_DEALT = BRIGHT_GREEN
    COMBAT_DAMAGE_TAKEN = BRIGHT_RED
    COMBAT_DEATH = BOLD + RED

    # Status & System
    SYSTEM = BOLD + BLUE
    EXPERIENCE = BRIGHT_GREEN
    LEVEL_UP = BOLD + BRIGHT_GREEN
    ROUNDTIME = YELLOW
    PROMPT = BRIGHT_BLACK
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW

    # Health status colors
    HEALTH_FULL = BRIGHT_GREEN
    HEALTH_MID = YELLOW
    HEALTH_LOW = BRIGHT_RED
    HEALTH_CRIT = BOLD + RED

    # Mind state (experience)
    MIND_CLEAR = BRIGHT_GREEN
    MIND_FRESH = GREEN
    MIND_MUDDLED = YELLOW
    MIND_SATURATED = RED

    # Stealth
    STEALTH = DIM + WHITE

    # ESP / Chat channels
    CHANNEL_GENERAL = BRIGHT_CYAN          # General  — IC global
    CHANNEL_OOC     = BRIGHT_MAGENTA       # OOC      — OOC global
    CHANNEL_HELP    = BRIGHT_YELLOW        # Help     — OOC global
    CHANNEL_TRADE   = YELLOW               # Trade    — OOC global
    CHANNEL_GUILD   = BRIGHT_BLUE          # Guild    — IC profession-only
    CHANNEL_PRIVATE = MAGENTA              # THINK TO <player> private
    YELL_LOCAL      = BOLD + YELLOW        # Yell in same room
    YELL_NEAR       = YELLOW               # Yell heard 1 room away
    YELL_FAR        = DIM + YELLOW         # Yell heard 2 rooms away


def colorize(text, color_code):
    """Wrap text in ANSI color codes with reset."""
    if not text:
        return text
    return f"{color_code}{text}{RESET}"


def room_title(title):
    """Format a room title: [Title] in bold cyan."""
    return colorize(f"[{title}]", TextPresets.ROOM_TITLE)


def room_desc(text):
    """Format room description in white."""
    return colorize(text, TextPresets.ROOM_DESC)


def room_exits(exit_type, exit_names):
    """Format exit line: 'Obvious paths: north, south'."""
    label = colorize(f"{exit_type}:", TextPresets.ROOM_EXIT_LABEL)
    names = colorize(f" {exit_names}", TextPresets.ROOM_EXITS)
    return f"{label}{names}"


def speech(speaker, verb, message, is_self=False):
    """Format speech: 'Gandalf says, "Hello!"'"""
    if is_self:
        speaker_text = "You"
        return f"{colorize(speaker_text, TextPresets.PLAYER_NAME)} {verb}, {colorize(chr(34) + message + chr(34), TextPresets.SPEECH_QUOTE)}"
    else:
        return f"{colorize(speaker, TextPresets.PLAYER_NAME)} {verb}, {colorize(chr(34) + message + chr(34), TextPresets.SPEECH_QUOTE)}"


def whisper(speaker, target, message, perspective="sender"):
    """Format whisper text based on perspective."""
    if perspective == "sender":
        return f"You whisper to {colorize(target, TextPresets.PLAYER_NAME)}, {colorize(chr(34) + message + chr(34), TextPresets.WHISPER_QUOTE)}"
    elif perspective == "receiver":
        return f"{colorize(speaker, TextPresets.PLAYER_NAME)} whispers to you, {colorize(chr(34) + message + chr(34), TextPresets.WHISPER_QUOTE)}"
    else:
        return f"{colorize(speaker, TextPresets.PLAYER_NAME)} whispers something to {colorize(target, TextPresets.PLAYER_NAME)}."


def thought(thinker, message, is_self=False):
    """Format thought text."""
    if is_self:
        return f"You think, {colorize(chr(34) + message + chr(34), TextPresets.THOUGHT)}"
    else:
        return f"{colorize(thinker, TextPresets.PLAYER_NAME)} appears lost in thought."


def creature_name(name):
    """Format a creature name in bold red."""
    return colorize(name, TextPresets.CREATURE_NAME)


def creature_arrival(name, action="lumbers in"):
    """Format creature arrival message."""
    return f"{colorize(name, TextPresets.CREATURE_NAME)} {action}."


def creature_departure(name, direction):
    """Format creature departure."""
    return f"{colorize(name, TextPresets.CREATURE_NAME)} just went {direction}."


def npc_name(name):
    """Format an NPC name in bold yellow."""
    return colorize(name, TextPresets.NPC_NAME)


def item_name(name):
    """Format an item name in yellow, with color/material order corrected."""
    from server.core.world.material_data import pretty_item_name
    return colorize(pretty_item_name(str(name)) if name else name, TextPresets.ITEM_NAME)


def player_name(name):
    """Format a player name in bold white."""
    return colorize(name, TextPresets.PLAYER_NAME)


def combat_attack(attacker, target, verb, endroll, hit=True):
    """Format a combat attack line."""
    if hit:
        return colorize(
            f"{attacker} {verb} at {target}! (d100+AS-DS = {endroll})",
            TextPresets.COMBAT_HIT
        )
    else:
        return colorize(
            f"{attacker} {verb} at {target} but misses. ({endroll})",
            TextPresets.COMBAT_MISS
        )


def combat_damage(amount, location=None):
    """Format damage dealt."""
    loc = f" to the {location}" if location else ""
    return colorize(f"  ... {amount} hit points of damage{loc}!", TextPresets.COMBAT_DAMAGE_DEALT)


def combat_crit(rank, message):
    """Format a critical hit message."""
    return colorize(f"  ... {rank} rank critical! {message}", TextPresets.COMBAT_CRIT)


def combat_death(name):
    """Format a death message."""
    return colorize(f"  {name} falls to the ground dead!", TextPresets.COMBAT_DEATH)


def roundtime_msg(seconds):
    """Format roundtime notification."""
    return colorize(f"Roundtime: {seconds} sec.", TextPresets.ROUNDTIME)


def experience_msg(amount, mind_state=None):
    """Format experience gain."""
    text = f"You gained {amount} experience!"
    if mind_state:
        text += f"  Your mind is {mind_state}."
    return colorize(text, TextPresets.EXPERIENCE)


def level_up_msg(new_level):
    """Format level up notification."""
    return colorize(
        f"*** CONGRATULATIONS! You have reached level {new_level}! ***",
        TextPresets.LEVEL_UP
    )


def system_msg(text):
    """Format a system message."""
    return colorize(text, TextPresets.SYSTEM)


def error_msg(text):
    """Format an error message."""
    return colorize(text, TextPresets.ERROR)


def prompt_text(text):
    """Format the command prompt."""
    return colorize(text, TextPresets.PROMPT)


def health_color(current, maximum):
    """Return color code based on health percentage."""
    if maximum <= 0:
        return TextPresets.HEALTH_CRIT
    pct = current / maximum
    if pct > 0.75:
        return TextPresets.HEALTH_FULL
    elif pct > 0.40:
        return TextPresets.HEALTH_MID
    elif pct > 0.15:
        return TextPresets.HEALTH_LOW
    else:
        return TextPresets.HEALTH_CRIT


def health_bar(label, current, maximum):
    """Format a health/mana/stamina bar with appropriate color."""
    color = health_color(current, maximum)
    return f"  {label}: {colorize(f'{current}/{maximum}', color)}"


def npc_emote(text):
    """Format an NPC ambient emote in light blue (bright cyan)."""
    return colorize(text, TextPresets.NPC_EMOTE)


def npc_speech(name, text):
    """Format a full NPC speech line: bold-yellow name + bold-green dialogue."""
    return f"{colorize(name, TextPresets.NPC_NAME)} {colorize(text, TextPresets.NPC_SPEECH)}"
