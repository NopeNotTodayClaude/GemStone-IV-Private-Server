import sys as _sys
import traceback as _tb
import os as _os

def _crash_handler(exc_type, exc_value, exc_tb):
    log_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "crash.log")
    with open(log_path, "w") as _f:
        _f.write("CRASH:\n")
        _tb.print_exception(exc_type, exc_value, exc_tb, file=_f)
    _tb.print_exception(exc_type, exc_value, exc_tb)

_sys.excepthook = _crash_handler

#!/usr/bin/env python3
"""
gsiv_hud.py — GemStone IV Private Server Client HUD
A full desktop client with:
  • ANSI-colored game text output
  • HP / MP / Spirit / Stamina status bars (auto-updated from server tags)
  • Clickable compass map showing current room + neighbors
  • BFS pathfinding — click any room to auto-walk there (:go2 style)
  • Command history (up/down arrow)

Requires: Python 3.10+, tkinter (included in standard Python on Windows)

Usage:
    python client/gsiv_hud.py
    python client/gsiv_hud.py --host 192.168.1.10 --port 4901
"""

import tkinter as tk
from tkinter import ttk
import socket
import threading
import queue
import json
import os
import re
import time
import argparse
import heapq
from collections import deque
from typing import Optional, Dict, List, Tuple

# Sync client (same directory)
import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
try:
    from sync_client import SyncClient
    _SYNC_AVAILABLE = True
except ImportError:
    _SYNC_AVAILABLE = False

try:
    from audio_engine import AudioManager
    _AUDIO_AVAILABLE = True
except ImportError:
    _AUDIO_AVAILABLE = False

# PIL (Pillow) for map image rendering — install with: pip install Pillow
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ─────────────────────────────────────────────
# Default server address
# ─────────────────────────────────────────────
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4901
GRAPH_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "room_graph.json")
REGIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "map_regions.json")
CONFIG_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "hud_config.json")
LICH_MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map-1773601222.json")
AUDIO_RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "audio_regions.json")
SHOP_ROOM_IDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "shop_room_ids.json")
CLIENTMEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clientmedia")
LICH_MAP_DIR_CANDIDATES = [
    r"N:\Ruby4Lich5\R4LInstall\Lich5.15.1\maps",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "maps"),
]

# Temporary pathfinder denylist for incomplete areas we do not want AUTO/map pathing to use.
PATHFIND_BLOCKED_EXIT_KEYS = {
    "go_burghal",
}

# ── FORCED PANEL LAYOUT ──────────────────────────────────────────────────────
# Left zone:  status (top, small) + room (mid) + experience (bottom)
# Right zone: map only — takes the entire right column top to bottom
# Sash positions hammered on startup so nothing drifts.
FORCED_LEFT_PANELS  = ["status", "exp", "timeweather"]  # room panel removed
FORCED_RIGHT_PANELS = ["map"]                     # map alone fills entire right column
FORCED_LEFT_SASHES  = [150, 380]                  # y px: status/exp split, exp/timeweather split
FORCED_RIGHT_SASHES = []                          # no sashes — map fills full height
FORCED_MAIN_SASHES  = [210, 2200]                 # x px: wider left col, map starts further right
FORCED_APPLY_COUNT  = 20                          # hammer attempts
FORCED_APPLY_MS     = 500                         # ms between each hammer
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────
# Dark theme palette
# ─────────────────────────────────────────────
BG_APP      = "#0d1117"
BG_PANEL    = "#161b22"
BG_INPUT    = "#1c2128"
BORDER_CLR  = "#30363d"
TEXT_MAIN   = "#e6edf3"
TEXT_DIM    = "#8b949e"
ACCENT_BLUE = "#58a6ff"
ACCENT_GRN  = "#3fb950"
ACCENT_RED  = "#f85149"
ACCENT_YEL  = "#e3b341"
ACCENT_PRP  = "#bc8cff"
ACCENT_CYN  = "#39c5cf"

BAR_BG      = "#21262d"
BAR_HP      = "#da3633"
BAR_MP      = "#1f6feb"
BAR_SP      = "#8957e5"
BAR_ST      = "#2ea043"

MAP_BG        = "#0d1117"
MAP_ROOM_STD  = "#1c2128"
MAP_ROOM_CUR  = "#0d2340"
MAP_ROOM_HOV  = "#2d3748"
MAP_EDGE_STD  = "#30363d"
MAP_EDGE_CUR  = "#58a6ff"
MAP_CONN      = "#21262d"
MAP_CONN_DASH = "#2a3441"
MAP_CONN_UPD  = "#3fb950"   # up/down connectors

INPUT_MODES = [
    {"id": "command", "label": "CMD", "prompt": "cmd>",   "color": ACCENT_BLUE, "verb": ""},
    {"id": "say",     "label": "SAY", "prompt": "say>",   "color": ACCENT_GRN,  "verb": "say"},
    {"id": "think",   "label": "THK", "prompt": "think>", "color": ACCENT_PRP,  "verb": "think"},
    {"id": "chat",    "label": "OOC", "prompt": "chat>",  "color": ACCENT_YEL,  "verb": "chat"},
    {"id": "yell",    "label": "YEL", "prompt": "yell>",  "color": ACCENT_RED,  "verb": "yell"},
]
COMM_INPUT_MODES = [mode for mode in INPUT_MODES if mode["id"] != "command"]

# ─────────────────────────────────────────────
# ANSI escape handling
# ─────────────────────────────────────────────
ANSI_RE  = re.compile(r'\x1b\[([0-9;]*)m')
OSC_RE   = re.compile(r'\x1b\][^\x07]*\x07')
BARE_ESC = re.compile(r'\x1b[^[]]')

# 8/16 color ANSI → hex
ANSI_COLORS: Dict[int, str] = {
    30: "#555555", 31: "#cc3333", 32: "#339933", 33: "#aaaa33",
    34: "#3355cc", 35: "#aa33aa", 36: "#33aaaa", 37: "#bbbbbb",
    90: "#666666", 91: "#ff5555", 92: "#55cc55", 93: "#ffff55",
    94: "#5577ff", 95: "#ff55ff", 96: "#55ffff", 97: "#ffffff",
}

# Bold upgrades (richer color when bold=True)
BOLD_UPGRADES: Dict[str, str] = {
    "#cc3333": "#ff5555",
    "#339933": "#55cc55",
    "#aaaa33": "#ffff55",
    "#3355cc": "#5577ff",
    "#aa33aa": "#ff55ff",
    "#33aaaa": "#55ffff",
    "#bbbbbb": "#ffffff",
}


def parse_ansi(text: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse ANSI-colored text into (chunk, color_hex|None) pairs.
    None means default terminal color.
    """
    text = OSC_RE.sub("", text)
    text = BARE_ESC.sub("", text)

    segments: List[Tuple[str, Optional[str]]] = []
    cur_fg: Optional[str] = None
    cur_bold: bool = False
    pos = 0

    for m in ANSI_RE.finditer(text):
        if m.start() > pos:
            chunk = text[pos:m.start()]
            if chunk:
                color = BOLD_UPGRADES.get(cur_fg, cur_fg) if cur_bold and cur_fg else cur_fg
                segments.append((chunk, color))
        pos = m.end()

        codes_str = m.group(1)
        if not codes_str:
            codes = [0]
        else:
            codes = [int(c) for c in codes_str.split(";") if c]

        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                cur_fg = None
                cur_bold = False
            elif c == 1:
                cur_bold = True
            elif c == 2:
                cur_bold = False
            elif c in ANSI_COLORS:
                cur_fg = ANSI_COLORS[c]
            elif c == 38 and i + 2 < len(codes) and codes[i+1] == 5:
                # 256-color — skip the index byte
                i += 2
            i += 1

    if pos < len(text):
        chunk = text[pos:]
        if chunk:
            color = BOLD_UPGRADES.get(cur_fg, cur_fg) if cur_bold and cur_fg else cur_fg
            segments.append((chunk, color))

    return segments


def _resolve_map_image_path(image_ref: str) -> str:
    image_ref = str(image_ref or "").strip()
    if not image_ref:
        return ""

    if os.path.isabs(image_ref) and os.path.exists(image_ref):
        return image_ref

    candidates = []
    if image_ref:
        candidates.append(os.path.join(os.path.dirname(REGIONS_PATH), image_ref))
        candidates.append(os.path.join(os.path.dirname(REGIONS_PATH), "maps", os.path.basename(image_ref)))

    for maps_dir in LICH_MAP_DIR_CANDIDATES:
        candidates.append(os.path.join(maps_dir, os.path.basename(image_ref)))

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return ""


# ─────────────────────────────────────────────
# Server tags (emitted by patched session.py)
# ─────────────────────────────────────────────
GSIV_STATUS_RE = re.compile(
    r"<GSIV HP=(\d+)/(\d+) MP=(\d+)/(\d+) SP=(\d+)/(\d+) ST=(\d+)/(\d+) RT=(\d+)"
    r"(?:\s+ROOM=(\d+))?>",
    re.IGNORECASE
)

# Parsed from room LOOK output
# NOTE: the server often prefixes the room title line with ">" (the prompt),
# so we allow an optional leading ">".
ROOM_TITLE_RE = re.compile(r"^>?\s*\[(.+?)\]\s+#(\d+)")
EXITS_RE      = re.compile(r"^Obvious (?:exits|paths):\s+(.+)", re.IGNORECASE)
PROMPT_RE     = re.compile(r"^(?:\[RT:\s*\d+s\])?>\s*$")
RT_START_RE   = re.compile(r"Roundtime:\s*(\d+)\s*sec", re.I)     # "Roundtime: 3 sec."
RT_REMAIN_RE  = re.compile(r"Roundtime:\s*(\d+)\s*second", re.I)  # "Roundtime: 2 seconds remaining."
RT_PROMPT_RE  = re.compile(r"^\[RT:\s*(\d+)s\]>")                 # "[RT: 2s]>"

# Parse stats from health / exp command output
HEALTH_HP_RE  = re.compile(r"Maximum Health Points:\s*(\d+)\s+Remaining:\s*(\d+)", re.I)
HEALTH_MP_RE  = re.compile(r"Maximum Mana Points:\s*(\d+)\s+Remaining:\s*(\d+)", re.I)
HEALTH_SP_RE  = re.compile(r"Maximum Spirit Points:\s*(\d+)\s+Remaining:\s*(\d+)", re.I)
HEALTH_ST_RE  = re.compile(r"Maximum Stamina Points:\s*(\d+)\s+Remaining:\s*(\d+)", re.I)
# Combat inline health update: "  Health: 128/132"
COMBAT_HP_RE  = re.compile(r"^\s*Health:\s*(\d+)/(\d+)", re.I)
# "Health Recovery: 13 points per round" — parsed from health command output
HP_RECOVERY_RE = re.compile(r"Health Recovery:\s*(\d+)\s*points?\s*per\s*round", re.I)
# Server signals that combat has fully ended
COMBAT_CLEAR_RE = re.compile(
    r"(?:The combat area is clear"          # explicit clear message
    r"|You gained \d+ experience"           # kill XP = enemy dead
    r"|flees from combat"                   # flee
    r"|breaks away and flees"               # flee variant
    r")",
    re.I)
# Flee / retreat lines — clears current target
FLEE_RE       = re.compile(
    r"(?:flees?|fled|breaks? away|retreats?|runs? away|escapes?|darts? away)"
    r"(?:\s+(?:from combat|north|south|east|west|northeast|northwest|southeast|southwest|up|down|out))?",
    re.I)
EXP_PTP_RE    = re.compile(r"PTPs?:\s*(\d+)", re.I)
EXP_MTP_RE    = re.compile(r"MTPs?:\s*(\d+)", re.I)
STANCE_CUR_RE = re.compile(r"Current stance:\s*(\w+)", re.I)
STANCE_VAL_RE = re.compile(r"Valid stances:\s*(.+)", re.I)

# AIM command server response parsing
AIM_SET_RE   = re.compile(r"You're now aiming at the (.+?) of your target", re.I)
AIM_CLEAR_RE = re.compile(r"You're now no longer aiming at anything in particular", re.I)

# EXP command output parsing
EXP_TOTAL_RE  = re.compile(r"Total experience:\s*([\d,]+)", re.I)
EXP_TNL_RE    = re.compile(r"(?:Exp(?:erience)?\s+(?:needed|to next level)|TNL)\s*:?\s*([\d,]+)", re.I)
EXP_MIND_RE   = re.compile(r"Mind\s+State\s*:\s*(.+)", re.I)
EXP_LEVEL_RE  = re.compile(r"(?:Current\s+)?[Ll]evel\s*:\s*(\d+)", re.I)
# Inline mind state from combat kill line: "You gained 240 experience [kill].  Mind: becoming saturated"
EXP_MIND_INLINE_RE = re.compile(r"\bMind:\s+(.+)", re.I)
LEVEL_UP_SFX_RE = re.compile(r"CONGRATULATIONS!\s+You have reached level\s+\d+!", re.I)
HIDE_SFX_RE = re.compile(
    r"(?:You slip into the darkness and vanish from sight\.|You attempt to blend into the shadows\.\.\.\s*success!)",
    re.I,
)
AMBUSH_SFX_RE = re.compile(r"\b(?:You emerge from hiding and ambush|emerges from hiding and ambushes)\b", re.I)
SLEEP_SFX_RE = re.compile(r"(?:You lie down and drift off to sleep\b|lies down and falls asleep\.)", re.I)
LOOT_SFX_RE = re.compile(
    r"(?:\bYou find\b|\bfinds\b).*(?:silver coins|and puts it in their|and leaves it on the ground)",
    re.I,
)

# Enemy detection — "You also see X" and "X just arrived" patterns
# Matches: "You also see a fanged rodent [Level 1]." and similar
YOU_ALSO_SEE_RE = re.compile(
    r"You also see (?:a |an |the )?([\w\s\-]+?)(?:\s*\[Level \d+\])?[,.]",
    re.IGNORECASE)
# "A fanged rodent just arrived from the north." / "A large orc appears."
ARRIVED_RE = re.compile(
    r"^(?:A|An|The)\s+([\w\s\-]+?)\s+(?:just arrived|just entered|appears?|emerges?|rushes? in|charges? in|runs? in)",
    re.IGNORECASE)

# GS4 mind states in order of absorption % (0=clear → 12=mind lock)
MIND_STATES = [
    "clear", "dabbling", "processing", "learning", "contemplating",
    "muddled", "becoming", "concentrating", "discerning", "deliberating",
    "ruminating", "focusing", "mind lock",
]


# Sync control line injected by server on login (null-byte delimited, never displayed)
SYNC_INIT_RE = re.compile(r"\x00SYNC:([0-9a-f]{64}):(\d+)\x00")
# Server sends the training/character-creator URL as a plain text line.
# Detect it client-side and open the browser here — not on the server.
AUTOOPEN_URL_RE = re.compile(r"https?://\S+(?:8765|8766)/\S+token=\S+")
# HUD strips it from display and pre-loads shop items into _known_items.
SHOP_CATALOG_RE = re.compile(r"\x00SHOP_CATALOG:(.+?)\x00")
# Server injects \x00CUSTOMIZE_MENU:{json}\x00 when showing material options
CUSTOMIZE_MENU_RE = re.compile(r"\x00CUSTOMIZE_MENU:(.+?)\x00")
# Server injects \x00CUSTOMIZE_COLORS:{json}\x00 for color-only customization
CUSTOMIZE_COLORS_RE = re.compile(r"\x00CUSTOMIZE_COLORS:(.+?)\x00")

SFX_SHOP_ENTER = "universfield-bell-2-123742.mp3"
SFX_SHOP_EXIT = "universfield-creaking-door-03-487855.mp3"
SFX_LEVEL_UP = "universfield-game-level-complete-143022.mp3"
SFX_LOOT = "yodguard-drop-or-pickup-item-1-387916.mp3"
SFX_HIDE = "gargamel10-rustling-leaves-378798.mp3"
SFX_AMBUSH = "dragon-studio-sword-slice-2-393845.mp3"
SFX_SLEEP = "scottishperson-sound-effect-cat-snoring-262650.mp3"


def _load_room_id_set(path: str) -> set[int]:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            payload = json.load(f)
        room_ids = payload.get("room_ids", []) if isinstance(payload, dict) else payload
        return {int(room_id) for room_id in room_ids}
    except Exception:
        return set()

# ─────────────────────────────────────────────────────────────────────────────
# DockManager — flexible panel docking system
#
# Three dock zones: "left", "right", "top"
# Each zone is a PanedWindow.  Each panel is wrapped in a DockPanel that has
# a drag-handle header bar.  Dragging near a zone snaps the panel in.
# Layout (zone membership + order + sash positions) persists to hud_config.json
#
# Public API:
#   dm = DockManager(root, center_frame, config_dict)
#   dm.add_zone("left",  orient="vertical",   minsize=150, width=170)
#   dm.add_zone("right", orient="vertical",   minsize=280, width=400)
#   dm.add_zone("top",   orient="horizontal", minsize=0,   height=0)
#   dm.register("exp",    build_fn, zone="left",  title="Experience")
#   dm.register("status", build_fn, zone="right", title="Status")
#   dm.register("map",    build_fn, zone="right", title="Map")
#   dm.register("room",   build_fn, zone="right", title="Room")
#   dm.finalize()          # build all zones and panels
#   dm.get_layout()        # → dict for saving
#   dm.apply_layout(dict)  # restore saved layout
# ─────────────────────────────────────────────────────────────────────────────

class DockZone:
    """One docking column/row (a PanedWindow plus bookkeeping)."""

    SNAP_PX = 60   # pixels from zone edge to trigger snap

    def __init__(self, root, outer, zone_id, orient, minsize, fixed_size, app):
        self.zone_id   = zone_id
        self.orient    = orient   # "vertical" | "horizontal"
        self.minsize   = minsize
        self.fixed_size = fixed_size  # width for vert zones, height for horiz
        self.app       = app

        self.frame = tk.Frame(outer, bg=BG_APP)

        self.paned = tk.PanedWindow(
            self.frame, orient=orient,
            bg=BG_APP, sashwidth=5, sashrelief="flat",
            sashpad=2, handlepad=40, handlesize=8,
        )
        self.paned.pack(fill="both", expand=True)
        # <Configure> fires whenever ANY pane inside this PanedWindow changes
        # size — including when the user drags a sash.  Debounce 800ms so we
        # don't hammer the disk on every pixel of the drag.
        self._save_after_id = None
        def _on_paned_configure(_e):
            if self._save_after_id:
                self.app.root.after_cancel(self._save_after_id)
            self._save_after_id = self.app.root.after(800, self.app._save_config)
        self.paned.bind("<Configure>", _on_paned_configure)

        self.panels: list = []    # DockPanel objects in order

    def add_panel(self, panel, index=None):
        if panel in self.panels:
            return
        if index is None or index >= len(self.panels):
            self.panels.append(panel)
        else:
            self.panels.insert(index, panel)
        ms = max(panel.minsize, 60)
        spacer = getattr(self, '_spacer', None)
        if spacer and spacer.winfo_exists():
            # Insert before the spacer so spacer stays at bottom
            self.paned.add(panel.outer_frame, minsize=ms, stretch="never",
                           before=spacer)
        else:
            self.paned.add(panel.outer_frame, minsize=ms, stretch="never")
        panel.current_zone = self.zone_id

    def remove_panel(self, panel):
        if panel not in self.panels:
            return
        try:
            self.paned.remove(panel.outer_frame)
        except Exception:
            pass
        self.panels.remove(panel)
        panel.current_zone = None

    def is_visible(self):
        return bool(self.panels)

    def get_sash_positions(self):
        positions = []
        # There is one sash between each pair of adjacent panes.
        # The zone paned contains: panel0, panel1, …, panelN, spacer
        # That gives N sashes total (N panels means N sashes including the
        # spacer boundary).  We must capture ALL of them — the last sash
        # (between the bottom-most panel and the spacer) is the one the user
        # drags to resize the bottom panel, and it was previously missed.
        n_panes = len(self.panels) + 1  # +1 for the spacer frame
        for i in range(n_panes - 1):
            try:
                coord = self.paned.sash_coord(i)
                positions.append(coord[1] if self.orient == "vertical" else coord[0])
            except Exception:
                positions.append(None)
        return positions

    def restore_sash_positions(self, positions):
        """Place all sashes including the panel→spacer boundary sash."""
        for i, pos in enumerate(positions or []):
            if pos is not None:
                try:
                    if self.orient == "vertical":
                        self.paned.sash_place(i, 0, int(pos))
                    else:
                        self.paned.sash_place(i, int(pos), 0)
                except Exception:
                    pass


class DockPanel:
    """One draggable panel with a header handle."""

    HANDLE_H = 14   # height of the drag handle bar

    def __init__(self, panel_id, title, build_fn, zone_id, minsize, app):
        self.panel_id     = panel_id
        self.title        = title
        self.build_fn     = build_fn
        self.default_zone = zone_id
        self.current_zone = zone_id
        self.minsize      = minsize
        self.app          = app

        self.outer_frame  = None   # set in build()
        self.content_frame = None  # set in build()
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._ghost        = None

    def build(self, parent):
        """Create outer_frame with handle + content_frame inside."""
        self.outer_frame = tk.Frame(parent, bg=BG_PANEL, bd=0)

        # ── Drag handle ───────────────────────────────────────────────────────
        handle = tk.Frame(self.outer_frame, bg="#1c2128",
                          height=self.HANDLE_H, cursor="fleur")
        handle.pack(fill="x", side="top")
        handle.pack_propagate(False)

        # Title left, grip dots right
        tk.Label(handle, text=self.title,
                 fg="#58a6ff", bg="#1c2128",
                 font=("Courier New", 7, "bold"),
                 anchor="w").pack(side="left", padx=4)
        tk.Label(handle, text="⠿",
                 fg="#30363d", bg="#1c2128",
                 font=("Courier New", 9)).pack(side="right", padx=3)

        # Separator line
        tk.Frame(self.outer_frame, bg="#30363d", height=1).pack(fill="x")

        # ── Content area ──────────────────────────────────────────────────────
        self.content_frame = tk.Frame(self.outer_frame, bg=BG_PANEL)
        self.content_frame.pack(fill="both", expand=True)

        # Bind drag events to handle and its children
        for w in (handle,) + tuple(handle.winfo_children()):
            w.bind("<ButtonPress-1>",   self._on_drag_start)
            w.bind("<B1-Motion>",       self._on_drag_motion)
            w.bind("<ButtonRelease-1>", self._on_drag_release)

        # Build content
        self.build_fn(self.content_frame)
        return self.outer_frame

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _on_drag_start(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._ghost = None

    def _on_drag_motion(self, event):
        dx = abs(event.x_root - self._drag_start_x)
        dy = abs(event.y_root - self._drag_start_y)
        if dx < 8 and dy < 8:
            return  # not a real drag yet

        dm = self.app._dock
        if dm is None:
            return

        # Create ghost window on first motion
        if self._ghost is None:
            self._ghost = tk.Toplevel(self.app.root)
            self._ghost.overrideredirect(True)
            self._ghost.attributes("-alpha", 0.45)
            self._ghost.attributes("-topmost", True)
            self._ghost.configure(bg="#58a6ff")
            gw = max(120, self.outer_frame.winfo_width())
            gh = max(60,  self.outer_frame.winfo_height())
            self._ghost.geometry(f"{gw}x{gh}")
            tk.Label(self._ghost, text=self.title, fg="white", bg="#58a6ff",
                     font=("Courier New", 9, "bold")).pack(expand=True)

        self._ghost.geometry(
            f"+{event.x_root - 40}+{event.y_root - 8}"
        )

        # Highlight the zone we're hovering over
        zone = dm.zone_at(event.x_root, event.y_root)
        dm.highlight_zone(zone)

    def _on_drag_release(self, event):
        if self._ghost:
            self._ghost.destroy()
            self._ghost = None

        dm = self.app._dock
        if dm is None:
            return

        dm.clear_highlight()
        zone = dm.zone_at(event.x_root, event.y_root)
        if zone and zone != self.current_zone:
            dm.move_panel(self, zone)
        elif zone == self.current_zone:
            pass  # dropped back in same zone — reorder by Y position
        # else: dropped outside all zones — snap back (do nothing, stays put)


class DockManager:
    """Owns all zones and panels, manages the outer layout frame."""

    def __init__(self, root, outer, app):
        self.root   = root
        self.outer  = outer
        self.app    = app
        self._zones: dict  = {}    # zone_id -> DockZone
        self._panels: dict = {}    # panel_id -> DockPanel
        self._zone_order   = []    # insertion order for layout

        # Top zone container (sits above the main horizontal row)
        self._top_container  = None
        self._main_row       = None   # Frame holding left + center + right
        self._center_frame   = None   # game text — never moves

        self._highlight_zone_id = None

    # ── Setup ─────────────────────────────────────────────────────────────────

    def set_center(self, frame):
        self._center_frame = frame

    def add_zone(self, zone_id, orient, minsize=0, width=0, height=0):
        zone = DockZone(self.root, self._get_zone_parent(orient),
                        zone_id, orient, minsize,
                        width if orient == "vertical" else height,
                        self.app)
        self._zones[zone_id] = zone
        self._zone_order.append(zone_id)
        return zone

    def _get_zone_parent(self, orient):
        # top zones go in top_container; left/right go in main_row
        return self._top_container if orient == "horizontal" else self._main_row

    def register(self, panel_id, build_fn, zone, title, minsize=80):
        p = DockPanel(panel_id, title, build_fn, zone, minsize, self.app)
        self._panels[panel_id] = p
        return p

    def finalize(self):
        """Build all panels into their zones, then add a spacer to each zone."""
        # Group panels by their zone
        by_zone: dict = {}
        for panel_id, panel in self._panels.items():
            by_zone.setdefault(panel.default_zone, []).append(panel)

        for zone_id, panels in by_zone.items():
            zone = self._zones.get(zone_id)
            if zone is None:
                continue
            for panel in panels:
                panel.build(zone.paned)
                zone.add_panel(panel)
            # Spacer at bottom of each zone absorbs leftover space.
            # Exception: if a zone has exactly ONE panel (e.g. the map zone),
            # give that panel stretch="always" so it fills the full height,
            # and add only a zero-height spacer that never grows.
            if len(panels) == 1:
                try:
                    zone.paned.paneconfig(panels[0].outer_frame, stretch="always")
                except Exception:
                    pass
            spacer = tk.Frame(zone.paned, bg=BG_APP, height=1)
            zone.paned.add(spacer, minsize=0, stretch="never" if len(panels) == 1 else "always")
            zone._spacer = spacer

        self._update_zone_visibility()

    # ── Zone frame access ─────────────────────────────────────────────────────

    def get_zone_frame(self, zone_id):
        z = self._zones.get(zone_id)
        return z.frame if z else None

    # ── Move panel between zones ──────────────────────────────────────────────

    def move_panel(self, panel, target_zone_id):
        src_zone = self._zones.get(panel.current_zone)
        dst_zone = self._zones.get(target_zone_id)
        if dst_zone is None or src_zone is dst_zone:
            return

        # Remove from current zone
        if src_zone:
            src_zone.remove_panel(panel)

        # Destroy the old outer_frame completely and rebuild fresh in new paned
        if panel.outer_frame:
            try:
                panel.outer_frame.destroy()
            except Exception:
                pass
            panel.outer_frame = None

        panel.build(dst_zone.paned)
        dst_zone.add_panel(panel)

        self._update_zone_visibility()
        self._save_layout()

    # ── Zone hit testing ──────────────────────────────────────────────────────

    def zone_at(self, x_root, y_root):
        """Return zone_id of the zone the cursor is in, or None."""
        for zid, zone in self._zones.items():
            if not zone.is_visible():
                continue
            try:
                f = zone.frame
                fx = f.winfo_rootx()
                fy = f.winfo_rooty()
                fw = f.winfo_width()
                fh = f.winfo_height()
                # Extend snap zone by SNAP_PX on all edges
                sp = DockZone.SNAP_PX
                if (fx - sp <= x_root <= fx + fw + sp and
                        fy - sp <= y_root <= fy + fh + sp):
                    return zid
            except Exception:
                pass
        return None

    # ── Zone highlight ────────────────────────────────────────────────────────

    def highlight_zone(self, zone_id):
        if zone_id == self._highlight_zone_id:
            return
        self.clear_highlight()
        self._highlight_zone_id = zone_id
        z = self._zones.get(zone_id)
        if z:
            z.frame.configure(bg="#1f4068")

    def clear_highlight(self):
        z = self._zones.get(self._highlight_zone_id)
        if z:
            z.frame.configure(bg=BG_APP)
        self._highlight_zone_id = None

    # ── Visibility (hide empty zones) ────────────────────────────────────────

    def _update_zone_visibility(self):
        # Left/right zones are permanent paned children — no show/hide needed.
        # Only the top zone container toggles visibility.
        top_zone = self._zones.get("top")
        tc = getattr(self, '_top_container', None)
        if top_zone and tc:
            try:
                if top_zone.panels:
                    tc.pack(fill="x", side="top", pady=(0, 2))
                else:
                    tc.pack_forget()
            except Exception:
                pass

    # ── Layout persistence ────────────────────────────────────────────────────

    def get_layout(self) -> dict:
        layout = {}
        for zid, zone in self._zones.items():
            layout[zid] = {
                "panels": [p.panel_id for p in zone.panels],
                "sashes": zone.get_sash_positions(),
            }
        # Save main paned sash positions (left/right zone widths)
        main_sashes = []
        try:
            mp = self.app._paned
            for i in range(3):   # left | center | right = 2 sashes
                try:
                    main_sashes.append(mp.sash_coord(i)[0])
                except Exception:
                    break
        except Exception:
            pass
        layout["_main_sashes"] = main_sashes
        return layout

    def apply_layout(self, layout: dict):
        if not layout:
            return
        # Re-order panels per saved layout
        for zid, data in layout.items():
            if zid.startswith("_"):
                continue
            zone = self._zones.get(zid)
            if not zone:
                continue
            for pid in data.get("panels", []):
                panel = self._panels.get(pid)
                if panel and panel.current_zone != zid:
                    self.move_panel(panel, zid)
        # Restore per-zone sash positions
        for zid, data in layout.items():
            if zid.startswith("_"):
                continue
            zone = self._zones.get(zid)
            if zone:
                zone.restore_sash_positions(data.get("sashes", []))
        # Restore main paned sash positions — called directly, caller handles timing
        main_sashes = layout.get("_main_sashes", [])
        if main_sashes:
            mp = self.app._paned
            for i, x in enumerate(main_sashes):
                try:
                    mp.sash_place(i, int(x), 1)
                except Exception:
                    pass

    def _save_layout(self):
        try:
            self.app._save_config()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Status Effect Icon Definitions
# Each entry: effect_id -> dict with visual and tooltip info.
# Icons are drawn procedurally on 32x32 Canvas cells (no image files needed).
# Style inspiration: FFXI status effect icons — solid coloured square with
# a symbol/letter, category-coloured border.
#
# shape:   "square"|"circle"|"diamond"|"skull"|"arrow_up"|"arrow_down"|"zzz"|"dot"
# color:   fill color of the icon body
# border:  border/accent color
# symbol:  1-3 char text drawn on the icon
# label:   short name shown under icon
# tip:     full tooltip description
# ─────────────────────────────────────────────────────────────────────────────
STATUS_ICON_DEFS = {
    # ── DEBUFF_COMBAT ─────────────────────────────────────────────────────────
    "stunned":     {"shape":"diamond","color":"#ffd700","border":"#fff176","symbol":"S","label":"Stun",    "tip":"Stunned\n-20 DS, 50% evade/parry/block penalty.\nCannot act, move, or speak."},
    "webbed":      {"shape":"square", "color":"#7c4dab","border":"#b39ddb","symbol":"W","label":"Web",     "tip":"Webbed\nEntangled in thick webbing.\nCannot act or move. -20 DS."},
    "rooted":      {"shape":"circle", "color":"#558b2f","border":"#aed581","symbol":"R","label":"Root",    "tip":"Rooted\nCannot move between rooms. -10 DS."},
    "immobile":    {"shape":"square", "color":"#37474f","border":"#90a4ae","symbol":"I","label":"Immob",   "tip":"Immobile\nCannot move. -15 DS, -25%% evade."},
    "silenced":    {"shape":"circle", "color":"#880e4f","border":"#f48fb1","symbol":"X","label":"Silence", "tip":"Silenced\nCannot speak or cast spells."},
    "unconscious": {"shape":"skull",  "color":"#212121","border":"#757575","symbol":"U","label":"Unconscious","tip":"Unconscious\nCompletely helpless. -50 DS."},
    "possessed":   {"shape":"square", "color":"#4a148c","border":"#ce93d8","symbol":"P","label":"Possess", "tip":"Possessed\nActions may be hijacked by a spirit."},
    "calmed":      {"shape":"circle", "color":"#1565c0","border":"#90caf9","symbol":"C","label":"Calm",    "tip":"Calmed\nCannot initiate attacks."},
    # ── DEBUFF_DOT ────────────────────────────────────────────────────────────
    "bleeding":    {"shape":"blood_drop", "color":"#c62828","border":"#ef9a9a","symbol":"","label":"Bleed",   "tip":"Bleeding\nLosing health each tick.\nTend wounds or use herbs to stop."},
    "major_bleed": {"shape":"blood_drop", "color":"#b71c1c","border":"#ff5252","symbol":"","label":"MajBleed","tip":"Major Bleed\nSevere bleeding — % health lost per tick."},
    "poisoned":    {"shape":"circle", "color":"#1b5e20","border":"#69f0ae","symbol":"P","label":"Poison",  "tip":"Poisoned\nToxic damage per round.\nDissipates 5 dmg/tick. Cure: Unpoison (114)."},
    "major_poison":{"shape":"circle", "color":"#004d00","border":"#00e676","symbol":"PP","label":"MajPoison","tip":"Major Poison\n%% health damage per tick."},
    "disease":     {"shape":"square", "color":"#827717","border":"#fff176","symbol":"D","label":"Disease", "tip":"Diseased\nPeriodic damage, reduced recovery."},
    "wounded":     {"shape":"square", "color":"#6d4c41","border":"#bcaaa4","symbol":"W","label":"Wound",   "tip":"Wounded\nPrevents natural regeneration."},
    "mind_rot":    {"shape":"skull",  "color":"#311b92","border":"#b39ddb","symbol":"M","label":"MindRot", "tip":"Mind Rot\nSpirit drains each tick. Death at 0."},
    # ── DEBUFF_STAT ───────────────────────────────────────────────────────────
    "staggered":   {"shape":"diamond","color":"#e65100","border":"#ffab91","symbol":"~","label":"Stagger", "tip":"Staggered\n-15 AS and DS."},
    "prone":       {"shape":"arrow_down","color":"#5d4037","border":"#a1887f","symbol":"p","label":"Prone","tip":"Prone\nLying on ground. -50 AS/DS, 50%% defense penalty."},
    "blinded":     {"shape":"circle", "color":"#212121","border":"#bdbdbd","symbol":"B","label":"Blind",   "tip":"Blinded\nCannot see. -20 AS/DS, -25%% evade."},
    "slowed":      {"shape":"diamond","color":"#0d47a1","border":"#82b1ff","symbol":"S","label":"Slow",    "tip":"Slowed\n-10 AS, -5 DS. +2 RT on all actions."},
    "crippled":    {"shape":"square", "color":"#4e342e","border":"#d7ccc8","symbol":"C","label":"Cripple", "tip":"Crippled\nLeg injury. Movement halved. -20 AS, -10 DS."},
    "demoralized": {"shape":"arrow_down","color":"#263238","border":"#90a4ae","symbol":"D","label":"Demoralized","tip":"Demoralized\n-20 AS and DS."},
    "feeble":      {"shape":"circle", "color":"#546e7a","border":"#b0bec5","symbol":"F","label":"Feeble",  "tip":"Feeble\nStrength reduced. -15 AS."},
    "clumsy":      {"shape":"diamond","color":"#ff6f00","border":"#ffcc02","symbol":"?","label":"Clumsy",  "tip":"Clumsy\nChance to fumble attacks. -10 AS, -5 DS."},
    "dazed":       {"shape":"circle", "color":"#795548","border":"#d7ccc8","symbol":"~","label":"Dazed",   "tip":"Dazed\n-15 AS/DS, 25%% defense penalty."},
    "disoriented": {"shape":"circle", "color":"#37474f","border":"#90a4ae","symbol":"?","label":"Disoriented","tip":"Disoriented\n-10 AS and DS."},
    "overexerted": {"shape":"square", "color":"#bf360c","border":"#ff8a65","symbol":"O","label":"Overexerted","tip":"Overexerted\nStamina depleted. -20 AS, -10 DS."},
    "vulnerable":  {"shape":"diamond","color":"#880e4f","border":"#f48fb1","symbol":"V","label":"Vuln",    "tip":"Vulnerable\n-30 DS, increased damage taken."},
    "groggy":      {"shape":"circle", "color":"#455a64","border":"#b0bec5","symbol":"z","label":"Groggy",  "tip":"Groggy\nPost-sleep grogginess. -20 AS/DS for 10s."},
    "weakened_armament":{"shape":"square","color":"#3e2723","border":"#a1887f","symbol":"W","label":"WeakArm","tip":"Weakened Armament\nWeapon enchantment suppressed. -20 AS."},
    # ── DEBUFF_CONTROL ────────────────────────────────────────────────────────
    "confused":    {"shape":"circle", "color":"#6a1b9a","border":"#ce93d8","symbol":"?","label":"Confused","tip":"Confused\nMay attack random targets. -10 AS/DS."},
    "frenzied":    {"shape":"square", "color":"#b71c1c","border":"#ff1744","symbol":"F","label":"Frenzy",  "tip":"Frenzied\n+20 AS, -20 DS. Cannot disengage."},
    "sheer_fear":  {"shape":"skull",  "color":"#1a237e","border":"#7986cb","symbol":"!","label":"ShrFear", "tip":"Sheer Fear\nParalyzed with fear. Cannot act."},
    "terrified":   {"shape":"diamond","color":"#283593","border":"#7986cb","symbol":"T","label":"Terrified","tip":"Terrified\nMay flee combat each tick. -10 AS/DS."},
    "horrified":   {"shape":"diamond","color":"#212121","border":"#9e9e9e","symbol":"H","label":"Horror",  "tip":"Horrified\nMay flee. -15 AS/DS."},
    "fear":        {"shape":"diamond","color":"#1a237e","border":"#5c6bc0","symbol":"F","label":"Fear",    "tip":"Frightened\nMay flee combat. -10 AS/DS."},
    "disengaged":  {"shape":"arrow_down","color":"#37474f","border":"#78909c","symbol":"<","label":"Disengaged","tip":"Disengaged\nStepped back from engagement. -10 AS."},
    "pressed":     {"shape":"arrow_down","color":"#4a148c","border":"#ab47bc","symbol":">","label":"Pressed","tip":"Pressed\nForced into defensive position. -15 DS."},
    # ── BUFF_COMBAT ───────────────────────────────────────────────────────────
    "empowered":   {"shape":"square", "color":"#f57f17","border":"#fff176","symbol":"E","label":"Empowered","tip":"Empowered\n+20 AS, +10 DS."},
    "quickness":   {"shape":"circle", "color":"#00bcd4","border":"#80deea","symbol":"Q","label":"Quick",   "tip":"Quickness\nReduced roundtime on all actions."},
    "evasiveness": {"shape":"circle", "color":"#00897b","border":"#80cbc4","symbol":"E","label":"Evade",   "tip":"Evasiveness\n+15 evade DS. Better dodge chance."},
    "defensive_posture":{"shape":"square","color":"#1565c0","border":"#90caf9","symbol":"D","label":"DefPost","tip":"Defensive Posture\n+30 DS, improved defenses. -20 AS."},
    "forceful_blows":{"shape":"square","color":"#e65100","border":"#ffab91","symbol":"F","label":"Force",  "tip":"Forceful Blows\n+15 AS."},
    "slashing_strikes":{"shape":"diamond","color":"#c62828","border":"#ef9a9a","symbol":"S","label":"Slash","tip":"Slashing Strikes\n+10 AS. Increased bleed chance."},
    "concussive_blows":{"shape":"square","color":"#4e342e","border":"#d7ccc8","symbol":"K","label":"Concuss","tip":"Concussive Blows\n+10 AS blunt. Increased stun chance."},
    # ── BUFF_REACTIVE ─────────────────────────────────────────────────────────
    "recent_block":{"shape":"circle", "color":"#1b5e20","border":"#69f0ae","symbol":"B","label":"Block",   "tip":"Recent Block\nJust blocked an attack. +5 AS/DS window."},
    "recent_parry":{"shape":"circle", "color":"#004d40","border":"#64ffda","symbol":"P","label":"Parry",   "tip":"Recent Parry\nJust parried an attack. +5 AS/DS window."},
    "recent_evade":{"shape":"circle", "color":"#1a237e","border":"#82b1ff","symbol":"E","label":"Evade",   "tip":"Recent Evade\nJust evaded an attack. Brief bonus."},
    "counter":     {"shape":"diamond","color":"#e65100","border":"#ff6d00","symbol":"C","label":"Counter", "tip":"Counter\nCounter-attack window open. +20 AS next strike."},
    # ── BUFF_SPECIAL ──────────────────────────────────────────────────────────
    "inner_mind":  {"shape":"circle", "color":"#4a148c","border":"#e040fb","symbol":"IM","label":"InnerMind","tip":"Inner Mind\nEnhanced XP absorption rate."},
    "enhance":     {"shape":"square", "color":"#006064","border":"#80deea","symbol":"+","label":"Enhance", "tip":"Enhanced\nGeneric enhancement from spell or item."},
    "shrouded":    {"shape":"circle", "color":"#212121","border":"#757575","symbol":"SH","label":"Shrouded","tip":"Shrouded\nAura of concealment. Harder to detect."},
    # ── STATE ─────────────────────────────────────────────────────────────────
    "sleeping":    {"shape":"zzz",    "color":"#0d47a1","border":"#90caf9","symbol":"Z","label":"Sleep",   "tip":"Sleeping\nAsleep. XP absorption doubled.\nCompletely defenseless. STAND to wake."},
    "resting":     {"shape":"circle", "color":"#1b5e20","border":"#69f0ae","symbol":"R","label":"Rest",    "tip":"Resting\nResting. Improved recovery. -15 AS, -20 DS."},
    "sitting":     {"shape":"circle", "color":"#33691e","border":"#b9f6ca","symbol":"s","label":"Sit",     "tip":"Sitting\nSeated. -15 AS, -20 DS."},
    "kneeling":    {"shape":"circle", "color":"#558b2f","border":"#ccff90","symbol":"K","label":"Kneel",   "tip":"Kneeling\n-10 AS, -15 DS."},
    "hidden":      {"shape":"square", "color":"#1a1a2e","border":"#4a4a8a","symbol":"H","label":"Hidden",  "tip":"Hidden\nConcealed from sight.\nRevealed by movement or combat."},
    "invisible":   {"shape":"circle", "color":"#e0e0e0","border":"#ffffff","symbol":"i","label":"Invis",   "tip":"Invisible\nCannot be directly targeted."},
    "death_sting": {"shape":"skull",  "color":"#000000","border":"#424242","symbol":"DS","label":"DeathSting","tip":"Death\'s Sting\nXP absorption reduced to 25%%.\nDecays as experience is absorbed."},
    "in_combat":   {"shape":"diamond","color":"#b71c1c","border":"#ff5252","symbol":"⚔","label":"Combat",  "tip":"In Combat\nEngaged in active combat."},
}

# Effects to never show in the status bar (internal state, not player-facing)
STATUS_BAR_HIDDEN = {"exited_combat", "roundtime", "recent_block", "recent_parry", "recent_evade"}
# ── Inventory line patterns (for clickable item tracking) ────────────────────
# "You are holding a steel falchion in your right hand."
INV_HOLD_RE = re.compile(
    r"You are holding (.+?) in your (right|left) hand"
    r"(?:\s+and\s+(.+?) in your (right|left) hand)?",
    re.I)
# "You are wearing a leather backpack, a belt pouch, and a steel falchion."
INV_WEAR_RE = re.compile(r"^You are wearing (.+)\.$", re.I)
# "  In a leather backpack:"  or  "In a leather backpack:"
INV_CONT_RE = re.compile(r"^\s*In (.*?):\s*$", re.I)
# Item line inside container: "    light leather armor"  (indented, no colon)
INV_ITEM_RE = re.compile(r"^  {2,}(\S.+)$")
# "Total items: N"
INV_TOTAL_RE    = re.compile(r"^Total items:", re.I)
INV_UNPLACED_RE = re.compile(r"^Unplaced items", re.I)
# Lines the server uses to ask for input (login, menus, etc.)
SERVER_ASK_RE = re.compile(
    r"^(?:"
    r"Choice\s*\([\d\-]+\)"               # Choice (1-2):
    r"|(?:Enter\s+your\s+)?(?:account\s+)?(?:username|password)\s*:"  # Username: / Password:
    r"|(?:account\s+)?name\s*:"           # Name:
    r")\s*$",
    re.IGNORECASE
)
# Bracketed command menus: [Bank: CHECK BALANCE, DEPOSIT ...] or [STORE: BUY, SELL]
MENU_CMD_RE = re.compile(r"^\[([A-Za-z0-9 ']+):\s*(.+)\]$")

# ─────────────────────────────────────────────
# Room graph + BFS pathfinder
# ─────────────────────────────────────────────

class RoomGraph:
    def __init__(self, path: str = GRAPH_PATH):
        self.rooms: Dict[int, dict] = {}
        self.uid_to_room: Dict[int, int] = {}
        self._path = path
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            print(f"[RoomGraph] No file at {self._path}. Run map_builder.py first.")
            return
        try:
            with open(self._path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            for rid_str, room in data.get("rooms", {}).items():
                rid = int(rid_str)
                room["exits"] = {d: int(v) for d, v in room.get("exits", {}).items()}
                edges = []
                for edge in room.get("edges", []) or []:
                    try:
                        target_id = int(edge.get("to"))
                    except (TypeError, ValueError):
                        continue
                    command = str(edge.get("command") or "").strip()
                    if not command:
                        continue
                    key = str(edge.get("key") or "").strip().lower() or command.replace(" ", "_").lower()
                    try:
                        cost = float(edge.get("cost", 1.0))
                    except (TypeError, ValueError):
                        cost = 1.0
                    edges.append({
                        "to": target_id,
                        "command": command,
                        "key": key,
                        "cost": max(0.05, cost),
                    })
                if not edges:
                    for direction, nxt_id in room["exits"].items():
                        edges.append({
                            "to": int(nxt_id),
                            "command": direction.replace("_", " "),
                            "key": str(direction).strip().lower(),
                            "cost": 1.0,
                        })
                room["edges"] = edges
                self.rooms[rid] = room
                lich_uid = room.get("lich_uid")
                try:
                    if lich_uid is not None:
                        self.uid_to_room[int(lich_uid)] = rid
                except (TypeError, ValueError):
                    pass
                for uid in room.get("uid", []) or []:
                    try:
                        self.uid_to_room[int(uid)] = rid
                    except (TypeError, ValueError):
                        pass
            self._merge_lich_tags()
            print(f"[RoomGraph] {len(self.rooms)} rooms loaded.")
        except Exception as e:
            print(f"[RoomGraph] Load error: {e}")

    def _merge_lich_tags(self, path: str = LICH_MAP_PATH):
        """Merge service tags from the authoritative LICH map file."""
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return
            merged_count = 0
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                rid = entry.get("id")
                tags = entry.get("tags") or []
                tags = [
                    str(t).strip().lower()
                    for t in tags
                    if str(t).strip().lower() in {"bank", "herbalist"}
                ]
                try:
                    rid = int(rid)
                except (TypeError, ValueError):
                    continue
                room = self.rooms.get(rid)
                if not room or not tags:
                    continue
                merged = {str(t).strip().lower() for t in room.get("tags", []) if str(t).strip()}
                before = len(merged)
                merged.update(str(t).strip().lower() for t in tags if str(t).strip())
                if len(merged) != before:
                    room["tags"] = sorted(merged)
                    merged_count += 1
            if merged_count:
                print(f"[RoomGraph] Merged LICH tags for {merged_count} rooms.")
        except Exception as e:
            print(f"[RoomGraph] LICH tag merge error: {e}")

    def get(self, room_id: int) -> Optional[dict]:
        return self.rooms.get(int(room_id))

    def _is_blocked_path_edge(self, current_room_id: int, exit_key: str, next_room_id: int) -> bool:
        return str(exit_key or "").strip().lower() in PATHFIND_BLOCKED_EXIT_KEYS

    def _iter_edges(self, room: dict):
        for edge in room.get("edges", []) or []:
            try:
                yield {
                    "to": int(edge.get("to")),
                    "command": str(edge.get("command") or "").strip(),
                    "key": str(edge.get("key") or "").strip().lower(),
                    "cost": max(0.05, float(edge.get("cost", 1.0))),
                }
            except (TypeError, ValueError):
                continue

    def resolve_go2_target(self, query: str, from_id: Optional[int] = None) -> Tuple[Optional[int], str]:
        target = str(query or "").strip()
        if not target:
            return None, "Usage: go2 <room id|lich id|u####|tag>"

        lowered = target.lower()
        if lowered == "help":
            return None, "go2 supports room ids, LICH ids, u####, and exact service tags like bank/herbalist."

        uid_match = re.fullmatch(r"u(\d+)", lowered)
        if uid_match:
            uid = int(uid_match.group(1))
            rid = self.uid_to_room.get(uid)
            return (rid, "") if rid is not None else (None, f"No room found for LICH id u{uid}.")

        if lowered.isdigit():
            value = int(lowered)
            if value in self.rooms:
                return value, ""
            if value in self.uid_to_room:
                return self.uid_to_room[value], ""
            return None, f"No room found for id {value}."

        tagged = self.find_tagged_rooms(lowered, from_id=from_id, limit=1)
        if tagged:
            return tagged[0], ""

        return None, f"No go2 target found for '{target}'."

    def find_path(self, from_id: int, to_id: int) -> Optional[List[str]]:
        """BFS. Returns list of direction strings, or None if unreachable."""
        from_id, to_id = int(from_id), int(to_id)
        if from_id == to_id:
            return []
        if from_id not in self.rooms or to_id not in self.rooms:
            return None

        visited = {from_id}
        q: deque = deque([(from_id, [])])

        while q:
            cur_id, path = q.popleft()
            for direction, nxt_id in self.rooms.get(cur_id, {}).get("exits", {}).items():
                nxt_id = int(nxt_id)
                # Convert stored key (go_gate, climb_bank) → game command (go gate, climb bank)
                cmd = direction.replace("_", " ")
                new_path = path + [cmd]
                if nxt_id == to_id:
                    return new_path
                if nxt_id not in visited and nxt_id in self.rooms:
                    visited.add(nxt_id)
                    q.append((nxt_id, new_path))
        return None

    def find_tagged_rooms(self, tag: str, from_id: Optional[int] = None,
                          limit: Optional[int] = None) -> List[int]:
        """Return room ids with the given tag, nearest-first when from_id is known."""
        needle = str(tag or "").strip().lower()
        if not needle:
            return []

        if from_id is None:
            matches = [
                rid for rid, room in self.rooms.items()
                if needle in (room.get("tags") or [])
            ]
            return matches[:limit] if limit else matches

        try:
            from_id = int(from_id)
        except (TypeError, ValueError):
            return []
        if from_id not in self.rooms:
            return []

        found: List[int] = []
        visited = {from_id}
        q: deque = deque([from_id])
        while q:
            cur_id = q.popleft()
            room = self.rooms.get(cur_id, {})
            if needle in (room.get("tags") or []):
                found.append(cur_id)
                if limit and len(found) >= limit:
                    break
            for nxt_id in room.get("exits", {}).values():
                nxt_id = int(nxt_id)
                if nxt_id not in visited and nxt_id in self.rooms:
                    visited.add(nxt_id)
                    q.append(nxt_id)
        return found

    def find_path(self, from_id: int, to_id: int) -> Optional[List[str]]:
        """Weighted pathfinding using Lich timeto when available."""
        from_id, to_id = int(from_id), int(to_id)
        if from_id == to_id:
            return []
        if from_id not in self.rooms or to_id not in self.rooms:
            return None

        best_cost = {from_id: 0.0}
        queue = [(0.0, from_id, [])]

        while queue:
            cost_so_far, cur_id, path = heapq.heappop(queue)
            if cur_id == to_id:
                return path
            if cost_so_far > best_cost.get(cur_id, float("inf")):
                continue

            room = self.rooms.get(cur_id, {})
            for edge in self._iter_edges(room):
                nxt_id = edge["to"]
                if nxt_id not in self.rooms:
                    continue
                if self._is_blocked_path_edge(cur_id, edge["key"], nxt_id):
                    continue
                new_cost = cost_so_far + edge["cost"]
                if new_cost >= best_cost.get(nxt_id, float("inf")):
                    continue
                best_cost[nxt_id] = new_cost
                heapq.heappush(queue, (new_cost, nxt_id, path + [edge["command"]]))

        return None

    def find_tagged_rooms(self, tag: str, from_id: Optional[int] = None,
                          limit: Optional[int] = None) -> List[int]:
        """Return room ids with the given tag, nearest-first when from_id is known."""
        needle = str(tag or "").strip().lower()
        if not needle:
            return []

        if from_id is None:
            matches = [
                rid for rid, room in self.rooms.items()
                if needle in (room.get("tags") or [])
            ]
            return matches[:limit] if limit else matches

        try:
            from_id = int(from_id)
        except (TypeError, ValueError):
            return []
        if from_id not in self.rooms:
            return []

        found: List[int] = []
        visited = {from_id}
        q: deque = deque([from_id])
        while q:
            cur_id = q.popleft()
            room = self.rooms.get(cur_id, {})
            if needle in (room.get("tags") or []):
                found.append(cur_id)
                if limit and len(found) >= limit:
                    break
            for edge in self._iter_edges(room):
                nxt_id = edge["to"]
                if self._is_blocked_path_edge(cur_id, edge["key"], nxt_id):
                    continue
                if nxt_id not in visited and nxt_id in self.rooms:
                    visited.add(nxt_id)
                    q.append(nxt_id)
        return found


# ─────────────────────────────────────────────
# Map regions loader
# ─────────────────────────────────────────────

def load_map_regions(path: str = REGIONS_PATH) -> dict:
    """Load map_regions.json → {zone_name: {image, rooms:{id:(x,y,w,h)}}}"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        result = {}
        for zone, info in data.get("maps", {}).items():
            rooms = {}
            for rid_str, coords in info.get("rooms", {}).items():
                rooms[int(rid_str)] = tuple(coords)   # (x, y, w, h)
            result[zone] = {"image": info.get("image", ""), "rooms": rooms}
        return result
    except Exception as e:
        print(f"[MapRegions] Load error: {e}")
        return {}


# ─────────────────────────────────────────────
# Image-based Map Canvas
# ─────────────────────────────────────────────

class MapImageCanvas(tk.Canvas):
    """
    Displays a full zone-map PNG image.
    • Scroll wheel  → zoom in / out (centered on mouse)
    • Left drag     → pan
    • Click a room  → pathfind there (rooms must be annotated in map_regions.json)

    Run map_annotator.py to annotate room positions on each map image.
    """
    ZOOM_MIN = 0.08
    ZOOM_MAX = 5.0

    def __init__(self, parent, graph: RoomGraph, regions: dict, on_click, **kw):
        kw.setdefault("bg", MAP_BG)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, **kw)

        self.graph    = graph
        self.regions  = regions          # {zone_name: {image:str, rooms:{id:(x,y,w,h)}}}
        self.on_click = on_click

        self.current_room_id: Optional[int] = None
        self._current_zone:   str  = ""
        self._pil_img               = None   # PIL.Image (full res)
        self._tk_img                = None   # ImageTk.PhotoImage (scaled)
        self._img_id                = None   # canvas item id for the image
        self._zoom:           float = 1.0
        self._pan_x:          float = 0.0
        self._pan_y:          float = 0.0
        self._drag_start            = None
        self._drag_moved:    bool   = False
        self._hover_room: Optional[int] = None
        self._overlay_items: Dict[int, List[int]] = {}   # room_id → [canvas ids]

        self.bind("<Configure>",       lambda _: self._render())
        self.bind("<MouseWheel>",      self._on_wheel)
        self.bind("<Button-4>",        self._on_wheel)
        self.bind("<Button-5>",        self._on_wheel)
        self.bind("<ButtonPress-1>",   self._on_drag_start)
        self.bind("<B1-Motion>",       self._on_drag_move)
        self.bind("<ButtonRelease-1>", self._on_drag_end)
        self.bind("<Motion>",          self._on_motion)
        self.bind("<Leave>",           self._on_leave)

    # ── public API ──────────────────────────────

    def set_room(self, room_id: int):
        same_room = room_id == self.current_room_id
        self.current_room_id = room_id
        room = self.graph.get(room_id)
        zone = room.get("zone_name", "") if room else ""
        if zone != self._current_zone:
            self._load_zone(zone)   # also calls _render
        elif not same_room:
            self._update_overlays()
        self._center_on_room(room_id)

    # ── map loading ──────────────────────────────

    def _load_zone(self, zone_name: str):
        self._current_zone = zone_name
        self._pil_img = None
        self._tk_img  = None

        zone_data = self.regions.get(zone_name)
        if zone_data and PIL_AVAILABLE:
            img_rel = zone_data.get("image", "")
            img_path = img_rel if os.path.isabs(img_rel) else \
                       os.path.join(os.path.dirname(REGIONS_PATH), img_rel)
            if os.path.exists(img_path):
                try:
                    self._pil_img = Image.open(img_path).convert("RGBA")
                except Exception as e:
                    print(f"[Map] Image load error: {e}")

        # Reset view: fit image to canvas
        self.update_idletasks()
        if self._pil_img:
            cw = self.winfo_width() or 280
            ch = self.winfo_height() or 400
            iw, ih = self._pil_img.size
            self._zoom = 1.0
        else:
            self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._render()

    def _render(self):
        self.delete("all")
        self._overlay_items.clear()
        self._img_id = None

        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400

        if not PIL_AVAILABLE:
            self.create_text(cw // 2, ch // 2,
                text="Install Pillow to use image maps:\npip install Pillow",
                fill=ACCENT_YEL, font=("Courier New", 9), justify="center")
            return

        if self._pil_img is None:
            msg = (f"No map image for:\n'{self._current_zone}'\n\n"
                   "Run  map_annotator.py\nto link a PNG to this zone.")
            self.create_text(cw // 2, ch // 2, text=msg,
                fill=TEXT_DIM, font=("Courier New", 9), justify="center")
            return

        # Scale and draw the image
        iw, ih = self._pil_img.size
        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        scaled = self._pil_img.resize((nw, nh), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(scaled)

        ox = cw // 2 + int(self._pan_x)
        oy = ch // 2 + int(self._pan_y)
        self._img_id = self.create_image(ox, oy, image=self._tk_img, anchor="center")

        self._update_overlays()

    def _update_overlays(self):
        for items in self._overlay_items.values():
            for item in items:
                self.delete(item)
        self._overlay_items.clear()

        zone_data = self.regions.get(self._current_zone, {})
        rooms = zone_data.get("rooms", {})

        for rid, (rx, ry, rw, rh) in rooms.items():
            cx1, cy1 = self._img_to_canvas(rx, ry)
            cx2, cy2 = self._img_to_canvas(rx + rw, ry + rh)
            is_cur = rid == self.current_room_id
            is_hov = rid == self._hover_room

            if is_cur:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill="#1a4a8a", outline=ACCENT_BLUE, width=2, stipple="gray50")
            elif is_hov:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill=MAP_ROOM_HOV, outline=ACCENT_YEL, width=2, stipple="gray50")
            else:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill="", outline=ACCENT_GRN, width=1)
            self._overlay_items[rid] = [rect]

        # Current room always on top
        if self.current_room_id in self._overlay_items:
            for item in self._overlay_items[self.current_room_id]:
                self.tag_raise(item)

    def _center_on_room(self, room_id: int):
        """Pan map so the current room is centered."""
        zone_data = self.regions.get(self._current_zone, {})
        rooms = zone_data.get("rooms", {})
        if room_id not in rooms or not self._pil_img:
            return
        rx, ry, rw, rh = rooms[room_id]
        # Room center in image coords
        irx = rx + rw / 2
        iry = ry + rh / 2
        iw, ih = self._pil_img.size
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        # pan so that image point (irx,iry) lands at canvas center
        self._pan_x = -(irx - iw / 2) * self._zoom
        self._pan_y = -(iry - ih / 2) * self._zoom
        self._render()

    # ── coordinate transforms ────────────────────

    def _img_to_canvas(self, ix: float, iy: float) -> Tuple[float, float]:
        if not self._pil_img:
            return 0.0, 0.0
        iw, ih = self._pil_img.size
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return ox + (ix - iw / 2) * self._zoom, oy + (iy - ih / 2) * self._zoom

    def _canvas_to_img(self, cx: float, cy: float) -> Tuple[float, float]:
        if not self._pil_img:
            return 0.0, 0.0
        iw, ih = self._pil_img.size
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return (cx - ox) / self._zoom + iw / 2, (cy - oy) / self._zoom + ih / 2

    # ── events ──────────────────────────────────

    def _on_wheel(self, ev):
        zoom_in = ev.num == 4 or (hasattr(ev, "delta") and ev.delta > 0)
        factor  = 1.15 if zoom_in else (1 / 1.15)
        old     = self._zoom
        self._zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self._zoom * factor))
        # zoom toward mouse cursor position
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        self._pan_x = ev.x - (ev.x - cw / 2 - self._pan_x) * (self._zoom / old) - cw / 2
        self._pan_y = ev.y - (ev.y - ch / 2 - self._pan_y) * (self._zoom / old) - ch / 2
        self._render()

    def _on_drag_start(self, ev):
        self._drag_start = (ev.x, ev.y)
        self._drag_moved = False
        self.config(cursor="fleur")

    def _on_drag_move(self, ev):
        if self._drag_start:
            dx = ev.x - self._drag_start[0]
            dy = ev.y - self._drag_start[1]
            if abs(dx) > 3 or abs(dy) > 3:
                self._drag_moved = True
            self._pan_x += dx
            self._pan_y += dy
            self._drag_start = (ev.x, ev.y)
            self._render()

    def _on_drag_end(self, ev):
        self.config(cursor="")
        if not self._drag_moved:
            self._handle_click(ev.x, ev.y)
        self._drag_start = None

    def _on_motion(self, ev):
        rid = self._room_at(ev.x, ev.y)
        if rid != self._hover_room:
            self._hover_room = rid
            self.config(cursor="hand2" if rid and rid != self.current_room_id else "")
            self._update_overlays()

    def _on_leave(self, ev):
        if self._hover_room:
            self._hover_room = None
            self.config(cursor="")
            self._update_overlays()

    def _handle_click(self, cx: int, cy: int):
        rid = self._room_at(cx, cy)
        if rid is not None and rid != self.current_room_id:
            self.on_click(rid)

    def _room_at(self, cx: int, cy: int) -> Optional[int]:
        zone_data = self.regions.get(self._current_zone, {})
        rooms = zone_data.get("rooms", {})
        for rid, (rx, ry, rw, rh) in rooms.items():
            x1, y1 = self._img_to_canvas(rx, ry)
            x2, y2 = self._img_to_canvas(rx + rw, ry + rh)
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return rid
        return None


# ─────────────────────────────────────────────
# Telnet client (runs in background thread)
# ─────────────────────────────────────────────

class TelnetThread(threading.Thread):
    def __init__(self, host: str, port: int, rx_q: queue.Queue):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.rx_q = rx_q          # (type, payload) tuples
        self._tx_q: queue.Queue = queue.Queue()
        self._sock: Optional[socket.socket] = None
        self._running = False

    def send(self, text: str):
        self._tx_q.put(text + "\r\n")

    def stop(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def run(self):
        self._running = True
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=10)
            self._sock.settimeout(0.05)   # short timeout so we can flush bare prompts
            self.rx_q.put(("connected", None))
        except Exception as e:
            self.rx_q.put(("error", f"Cannot connect to {self.host}:{self.port} — {e}"))
            return

        # Sender thread
        def _sender():
            while self._running:
                try:
                    data = self._tx_q.get(timeout=0.5)
                    if self._sock:
                        self._sock.sendall(data.encode("utf-8"))
                except queue.Empty:
                    continue
                except Exception:
                    break

        threading.Thread(target=_sender, daemon=True).start()

        # Receiver loop — line-by-line, with bare-prompt detection
        # The server sends ">" and also "Choice (1-2):" with NO trailing newline.
        # We detect these via a 50ms timeout and flush them immediately.
        PROMPT_BARE     = re.compile(rb'^(?:\[RT:\s*\d+s\])?>[ \t]*$')
        INPUT_PROMPT    = re.compile(rb'.+:\s*$')   # anything ending in ": "
        buf = b""
        try:
            while self._running:
                try:
                    chunk = self._sock.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                except socket.timeout:
                    pass   # expected — fall through to prompt check

                # Emit all complete lines
                while b"\n" in buf:
                    raw_line, buf = buf.split(b"\n", 1)
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
                    self.rx_q.put(("line", line))

                # Flush a bare prompt or an input-request line sitting without a newline
                # SAFETY: Never flush partial lines containing \x00 (null bytes).
                # These are hidden control tags (SHOP_CATALOG, CUSTOMIZE_MENU, etc.)
                # that must arrive as complete lines for proper HUD interception.
                stripped = buf.rstrip(b"\r")
                if stripped and b"\x00" not in stripped and (PROMPT_BARE.match(stripped) or INPUT_PROMPT.match(stripped)):
                    line = buf.decode("utf-8", errors="replace").rstrip("\r")
                    self.rx_q.put(("line", line))
                    buf = b""

        except Exception:
            pass
        finally:
            self._running = False
            self.rx_q.put(("disconnected", None))


# ─────────────────────────────────────────────
# Map regions loader
# ─────────────────────────────────────────────

def load_map_regions(path: str = REGIONS_PATH) -> dict:
    """Load map_regions.json → {zone_name: {image, rooms:{id:(x,y,w,h)}}}"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = {}
        for zone, info in data.get("maps", {}).items():
            rooms = {}
            for rid_str, coords in info.get("rooms", {}).items():
                rooms[int(rid_str)] = tuple(coords)   # (x, y, w, h)
            result[zone] = {"image": info.get("image", ""), "rooms": rooms}
        return result
    except Exception as e:
        print(f"[MapRegions] Load error: {e}")
        return {}


# ─────────────────────────────────────────────
# Image-based Map Canvas
# ─────────────────────────────────────────────

class MapImageCanvas(tk.Canvas):
    """
    Displays a full zone-map PNG image.
    • Scroll wheel  → zoom in / out (centered on mouse)
    • Left drag     → pan
    • Click a room  → pathfind there (annotate rooms via map_annotator.py)
    """
    ZOOM_MIN = 0.08
    ZOOM_MAX = 5.0

    def __init__(self, parent, graph: RoomGraph, regions: dict, on_click, **kw):
        kw.setdefault("bg", MAP_BG)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, **kw)

        self.graph    = graph
        self.regions  = regions
        self.on_click = on_click

        self.current_room_id: Optional[int] = None
        self._current_zone:   str  = ""
        self._pil_img               = None
        self._tk_img                = None
        self._img_id                = None
        self._zoom:           float = 1.0
        self._pan_x:          float = 0.0
        self._pan_y:          float = 0.0
        self._drag_start            = None
        self._drag_moved:    bool   = False
        self._hover_room: Optional[int] = None
        self._overlay_items: Dict[int, List[int]] = {}

        self.bind("<Configure>",       lambda _: self._render())
        self.bind("<MouseWheel>",      self._on_wheel)
        self.bind("<Button-4>",        self._on_wheel)
        self.bind("<Button-5>",        self._on_wheel)
        self.bind("<ButtonPress-1>",   self._on_drag_start)
        self.bind("<B1-Motion>",       self._on_drag_move)
        self.bind("<ButtonRelease-1>", self._on_drag_end)
        self.bind("<Motion>",          self._on_motion)
        self.bind("<Leave>",           self._on_leave)

    # ── public API ──────────────────────────────

    def _region_name_for_room(self, room_id: Optional[int]) -> str:
        if room_id is None:
            return ""
        room = self.graph.get(room_id)
        region_name = room.get("region_name", "") if room else ""
        if region_name and room_id in ((self.regions.get(region_name) or {}).get("rooms", {}) or {}):
            return region_name
        zone = room.get("zone_name", "") if room else ""
        zone_data = self.regions.get(zone)
        if zone_data and room_id in zone_data.get("rooms", {}):
            return zone
        for region_name, region_data in self.regions.items():
            if room_id in (region_data.get("rooms", {}) or {}):
                return region_name
        return zone

    def set_room(self, room_id: int):
        same_room = room_id == self.current_room_id
        self.current_room_id = room_id
        zone = self._region_name_for_room(room_id)
        if zone != self._current_zone:
            self._load_zone(zone)
        elif not same_room:
            self._update_overlays()
        self._center_on_room(room_id)

    def reload_regions(self):
        self.regions = load_map_regions()
        self._load_zone(self._current_zone)

    # ── map loading ──────────────────────────────

    def _load_zone(self, zone_name: str):
        self._current_zone = zone_name
        self._pil_img = None
        self._tk_img  = None

        zone_data = self.regions.get(zone_name)
        if zone_data and PIL_AVAILABLE:
            img_rel  = zone_data.get("image", "")
            img_path = _resolve_map_image_path(img_rel)
            if os.path.exists(img_path):
                try:
                    self._pil_img = Image.open(img_path).convert("RGBA")
                except Exception as e:
                    print(f"[Map] Image load error: {e}")

        self.update_idletasks()
        if self._pil_img:
            cw = self.winfo_width() or 280
            ch = self.winfo_height() or 400
            iw, ih = self._pil_img.size
            self._zoom = 1.0
        else:
            self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._render()
        if self.current_room_id:
            self._center_on_room(self.current_room_id)

    def _render(self):
        self.delete("all")
        self._overlay_items.clear()
        self._img_id = None

        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400

        if not PIL_AVAILABLE:
            self.create_text(cw // 2, ch // 2,
                text="Install Pillow for image maps:\npip install Pillow",
                fill=ACCENT_YEL, font=("Courier New", 9), justify="center")
            return

        if self._pil_img is None:
            msg = (f"No map image for zone:\n'{self._current_zone}'\n\n"
                   "Run  map_annotator.py  to\nlink a PNG to this zone.")
            self.create_text(cw // 2, ch // 2, text=msg,
                fill=TEXT_DIM, font=("Courier New", 9), justify="center")
            return

        iw, ih = self._pil_img.size
        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        scaled    = self._pil_img.resize((nw, nh), Image.LANCZOS)
        self._tk_img  = ImageTk.PhotoImage(scaled)

        ox = cw // 2 + int(self._pan_x)
        oy = ch // 2 + int(self._pan_y)
        self._img_id = self.create_image(ox, oy, image=self._tk_img, anchor="center")

        self._update_overlays()

    def _update_overlays(self):
        for items in self._overlay_items.values():
            for item in items:
                self.delete(item)
        self._overlay_items.clear()

        zone_data = self.regions.get(self._current_zone, {})
        rooms     = zone_data.get("rooms", {})

        for rid, (rx, ry, rw, rh) in rooms.items():
            cx1, cy1 = self._img_to_canvas(rx, ry)
            cx2, cy2 = self._img_to_canvas(rx + rw, ry + rh)
            is_cur = rid == self.current_room_id
            is_hov = rid == self._hover_room

            if is_cur:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill="#1a4a8a", outline=ACCENT_BLUE, width=2, stipple="gray50")
            elif is_hov:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill=MAP_ROOM_HOV, outline=ACCENT_YEL, width=2, stipple="gray50")
            else:
                rect = self.create_rectangle(cx1, cy1, cx2, cy2,
                    fill="", outline=ACCENT_GRN, width=1)
            self._overlay_items[rid] = [rect]

        if self.current_room_id in self._overlay_items:
            for item in self._overlay_items[self.current_room_id]:
                self.tag_raise(item)

    def _center_on_room(self, room_id: int):
        zone_data = self.regions.get(self._current_zone, {})
        rooms = zone_data.get("rooms", {})
        if room_id not in rooms or not self._pil_img:
            return
        rx, ry, rw, rh = rooms[room_id]
        iw, ih = self._pil_img.size
        self._pan_x = -(rx + rw / 2 - iw / 2) * self._zoom
        self._pan_y = -(ry + rh / 2 - ih / 2) * self._zoom
        self._render()

    # ── coordinate transforms ────────────────────

    def _img_to_canvas(self, ix: float, iy: float) -> Tuple[float, float]:
        if not self._pil_img:
            return 0.0, 0.0
        iw, ih = self._pil_img.size
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return ox + (ix - iw / 2) * self._zoom, oy + (iy - ih / 2) * self._zoom

    def _canvas_to_img(self, cx: float, cy: float) -> Tuple[float, float]:
        if not self._pil_img:
            return 0.0, 0.0
        iw, ih = self._pil_img.size
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return (cx - ox) / self._zoom + iw / 2, (cy - oy) / self._zoom + ih / 2

    # ── events ──────────────────────────────────

    def _on_wheel(self, ev):
        zoom_in = ev.num == 4 or (hasattr(ev, "delta") and ev.delta > 0)
        factor  = 1.15 if zoom_in else (1 / 1.15)
        old     = self._zoom
        self._zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self._zoom * factor))
        cw = self.winfo_width() or 280
        ch = self.winfo_height() or 400
        # zoom toward mouse cursor
        self._pan_x = ev.x - (ev.x - cw / 2 - self._pan_x) * (self._zoom / old) - cw / 2
        self._pan_y = ev.y - (ev.y - ch / 2 - self._pan_y) * (self._zoom / old) - ch / 2
        self._render()

    def _on_drag_start(self, ev):
        self._drag_start = (ev.x, ev.y)
        self._drag_moved = False
        self.config(cursor="fleur")

    def _on_drag_move(self, ev):
        if self._drag_start:
            dx = ev.x - self._drag_start[0]
            dy = ev.y - self._drag_start[1]
            if abs(dx) > 3 or abs(dy) > 3:
                self._drag_moved = True
            self._pan_x += dx
            self._pan_y += dy
            self._drag_start = (ev.x, ev.y)
            self._render()

    def _on_drag_end(self, ev):
        self.config(cursor="")
        if not self._drag_moved:
            self._handle_click(ev.x, ev.y)
        self._drag_start = None

    def _on_motion(self, ev):
        rid = self._room_at(ev.x, ev.y)
        if rid != self._hover_room:
            self._hover_room = rid
            self.config(cursor="hand2" if rid and rid != self.current_room_id else "")
            self._update_overlays()

    def _on_leave(self, ev):
        if self._hover_room:
            self._hover_room = None
            self.config(cursor="")
            self._update_overlays()

    def _handle_click(self, cx: int, cy: int):
        rid = self._room_at(cx, cy)
        if rid is not None and rid != self.current_room_id:
            self.on_click(rid)

    def _room_at(self, cx: int, cy: int) -> Optional[int]:
        zone_data = self.regions.get(self._current_zone, {})
        rooms     = zone_data.get("rooms", {})
        for rid, (rx, ry, rw, rh) in rooms.items():
            pad = 3
            x1, y1 = self._img_to_canvas(rx, ry)
            x2, y2 = self._img_to_canvas(rx + rw, ry + rh)
            if (x1 - pad) <= cx <= (x2 + pad) and (y1 - pad) <= cy <= (y2 + pad):
                return rid
        return None


# ─────────────────────────────────────────────
# Status bar widget — ttk.Progressbar based
# ─────────────────────────────────────────────

class StatBar(tk.Frame):
    """Stat bar using ttk.Progressbar (guaranteed to render) + value label."""

    _BASE_COLORS = {"HP": BAR_HP, "MP": BAR_MP, "SP": BAR_SP, "ST": BAR_ST}

    def __init__(self, parent, label: str, color: str, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)
        self._label    = label
        self._base_col = color
        self._cur      = 0
        self._max      = 0

        # Configure a unique ttk style per label so colors are independent
        self._style_name = f"{label}.Horizontal.TProgressbar"
        style = ttk.Style()
        style.theme_use("default")
        style.configure(self._style_name,
                        troughcolor=BAR_BG,
                        background=color,
                        borderwidth=0,
                        thickness=18)

        row = tk.Frame(self, bg=BG_PANEL)
        row.pack(fill="x", padx=4, pady=2)

        tk.Label(row, text=label, fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 10, "bold"), width=3, anchor="w").pack(side="left")

        self._bar = ttk.Progressbar(row, style=self._style_name,
                                    orient="horizontal", mode="determinate",
                                    maximum=100, value=0)
        self._bar.pack(side="left", fill="x", expand=True, padx=(2, 4))

        self._val_lbl = tk.Label(row, text="—/—", fg=TEXT_DIM, bg=BG_PANEL,
                                  font=("Courier New", 10), width=9, anchor="e")
        self._val_lbl.pack(side="left")

    def update(self, cur: int, max_val: int):
        self._cur = cur
        self._max = max_val
        pct = (cur / max_val * 100) if max_val > 0 else 0
        self._bar["maximum"] = 100
        self._bar["value"]   = pct
        self._val_lbl.config(text=f"{cur}/{max_val}")
        # Danger colour via style update
        style = ttk.Style()
        if pct <= 25:
            col = ACCENT_RED
        elif pct <= 50:
            col = ACCENT_YEL
        else:
            col = self._base_col
        style.configure(self._style_name, background=col)


# ─────────────────────────────────────────────
# Main HUD Window
# ─────────────────────────────────────────────

class HUDApp:
    def __init__(self, root: tk.Tk, host: str, port: int):
        self.root = root
        self.host = host
        self.port = port

        self.rx_q: queue.Queue = queue.Queue()
        self._telnet: Optional[TelnetThread] = None
        self.graph   = RoomGraph(GRAPH_PATH)
        self.regions = load_map_regions(REGIONS_PATH)
        self._shop_room_ids: set[int] = _load_room_id_set(SHOP_ROOM_IDS_PATH)

        # State
        self._current_room_id: Optional[int] = None
        self._current_room_title: str = ""
        self._current_room_zone: str = ""
        self._last_room_was_shop: bool = False
        self._live_exits: Dict[str, int] = {}      # exits seen from LOOK output
        self._pathfind_steps: List[str] = []       # queued directions
        self._pathfind_timer: Optional[str] = None
        self._pathfind_waiting: bool = False        # True while waiting for server RT clearance
        self._hist: List[str] = []                 # command history
        self._hist_idx: int = -1
        self._input_mode: str = "command"
        self._comm_input_mode: str = "say"
        self._roundtime: int = 0
        self._hp_regen_rate: float = 0.0   # HP regen per 10-second server pulse
        self._in_combat:    bool = False
        self._saved_servers: list = []
        self._font_size: int = 14      # game text font — larger default for 4K
        self._panel_font_size: int = 11  # panel labels (exp/status/room/map)
        self._music_enabled: bool = True
        self._sfx_enabled: bool = True
        self._music_volume: int = 65
        self._sfx_volume: int = 75

        # Auto-login
        self._auto_login_enabled:  bool = False
        self._auto_login_username: str  = ""
        self._auto_login_password: str  = ""
        self._auto_login_char_slot: int = 1    # which character number to pick
        self._auto_login_fired:    bool = False  # prevents double-fire per session

        # Real-time sync channel
        self.sync_q: queue.Queue = queue.Queue()
        self._sync: "Optional[SyncClient]" = None
        self._sync_connected: bool = False
        # Last full snapshot from sync — used by panels for live rendering
        self._last_sync: dict = {}
        self._room_npcs: List[dict] = []
        self._npc_link_seq: int = 0
        self._room_start_index: str = "1.0"

        # Embedded status effect bar (toolbar strip)
        self._fx_icon_frame: "Optional[tk.Frame]" = None
        self._fx_bar_icons: dict = {}
        self._fx_tooltip_win: "Optional[tk.Toplevel]" = None

        # Dock manager
        self._dock: "Optional[DockManager]" = None

        # EXP panel state
        self._exp_total:   int = 0
        self._exp_tnl:     int = 0
        self._exp_level:   int = 0
        self._mind_state:  str = "clear"

        # Time & Weather panel state (populated via sync)
        self._tw_day_name:    str = "—"
        self._tw_month_name:  str = "—"
        self._tw_day:         int = 0
        self._tw_year:        int = 0
        self._tw_period:      str = "—"
        self._tw_hour_name:   str = "—"
        self._tw_time_24:     str = "—:—"
        self._tw_holiday:     str = ""
        self._tw_weather:     str = "—"
        self._tw_forced:      bool = False
        self._tw_precip:      bool = False
        self._tw_indoor:      bool = False

        # Wound panel state (populated via sync)
        # {loc: {wound_rank:0-5, scar_rank:0-5, is_bleeding:bool, bandaged:bool}}
        self._wounds: dict = {}
        # AUTO mode state
        self._auto_healing:     bool = False
        self._auto_saved_hands: list = []  # [(slot, item_name), ...]
        self._auto_ctx:         dict = {}

        # Last lockbox/coffer noun seen in hand — for Pick/Detect/Disarm
        self._last_lockbox_noun: str = ""

        # ── Inventory model ──────────────────────────────────────────────
        # Tracks items seen in inv/inv full output so we can make them clickable
        # key = lowercase short name,  val = dict with state info
        self._known_items: Dict[str, dict] = {}
        self._inventory_counts: Dict[str, int] = {}
        # Shop catalog items injected by ORDER output — keyed by item index "1","2"…
        self._shop_catalog: Dict[str, dict] = {}
        # Currently worn containers (name→full_name), for "put X in ?" menus
        self._worn_containers: List[str] = []
        # inv-parse state machine
        self._inv_parsing:      bool = False
        self._inv_parse_started: bool = False
        self._inv_unplaced_section: bool = False  # suppress "Unplaced items" block from display   # True once first hold/wear line seen this parse
        self._inv_cur_cont:     str  = ""       # container we're currently listing items under

        self._game_font: str = "Georgia"  # Readable serif — less DOS, more RPG

        self._load_config()   # restore saved geometry / sash / font before building UI

        self._audio = AudioManager(CLIENTMEDIA_ROOT, AUDIO_RULES_PATH) if _AUDIO_AVAILABLE else None
        self._build_ui()
        if self._audio:
            self._audio.log_cb = self._sys
            self._audio.apply_settings(
                music_enabled=self._music_enabled,
                music_volume=self._music_volume,
                sfx_enabled=self._sfx_enabled,
                sfx_volume=self._sfx_volume,
            )
        self._setup_tags()
        self._poll()
        root.after(100, self._connect)       # auto-connect to last-used server
        root.after(0, self._restore_layout)  # restore saved window/panel state after first draw
        root.after(5000, self._passive_hp_regen)
        root.after(200, self._audio_tick)

    # ════════════════════════════════════════════
    # UI construction
    # ════════════════════════════════════════════

    def _build_ui(self):
        self.root.title("GemStone IV — Private Server HUD")
        self.root.configure(bg=BG_APP)
        self.root.minsize(960, 600)

        # ── Outer vertical stack ──────────────────────────────────────────────
        outer = tk.Frame(self.root, bg=BG_APP)
        outer.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        # ── Dock layout root ─────────────────────────────────────────────────
        # Top zone: sits above the main horizontal paned window.
        # It's a PanedWindow (horizontal) inside a collapsible frame.
        top_container = tk.Frame(outer, bg=BG_APP)
        # Not packed yet — shown only when panels are dropped there

        # Main horizontal PanedWindow: left | center | right
        # This gives proper sash handles so left/right zones are draggable.
        main_paned = tk.PanedWindow(outer, orient="horizontal",
                                    bg=BG_APP, sashwidth=6,
                                    sashrelief="flat", sashpad=2,
                                    handlepad=60, handlesize=8)
        main_paned.pack(fill="both", expand=True)
        self._main_paned = main_paned
        # <Configure> fires on every sash move in the main splitter.
        # Debounce 800ms so initial layout doesn't thrash the file.
        self._main_sash_after_id = None
        def _on_main_configure(_e):
            if self._main_sash_after_id:
                self.root.after_cancel(self._main_sash_after_id)
            self._main_sash_after_id = self.root.after(800, self._save_config)
        main_paned.bind("<Configure>", _on_main_configure)
        self._window_save_after_id = None
        def _on_root_configure(_e):
            if self._window_save_after_id:
                self.root.after_cancel(self._window_save_after_id)
            self._window_save_after_id = self.root.after(800, self._save_config)
        self.root.bind("<Configure>", _on_root_configure)

        # ── DockManager ───────────────────────────────────────────────────────
        dm = DockManager(self.root, outer, self)
        dm._top_container = top_container
        dm._main_row      = main_paned   # left/right zones add into this paned
        self._dock = dm

        left_zone  = dm.add_zone("left",  orient="vertical",   minsize=150, width=210)
        right_zone = dm.add_zone("right", orient="vertical",   minsize=280, width=380)
        top_zone   = dm.add_zone("top",   orient="horizontal", minsize=0,   height=80)

        # Add left zone into main horizontal paned (leftmost)
        main_paned.add(left_zone.frame, minsize=150, width=210, stretch="never")

        # ── Center: game text (fixed anchor in main paned) ───────────────────
        text_frame = tk.Frame(main_paned, bg=BG_PANEL)
        main_paned.add(text_frame, minsize=400, stretch="always")

        # Add right zone — stretch="always" so it fills remaining width and
        # the map panel inside it stretches top-to-bottom automatically
        main_paned.add(right_zone.frame, minsize=280, width=380, stretch="always")

        # top_zone.frame is already a child of top_container (DockZone creates it there)
        # Just pack the frame — paned is already packed inside frame by DockZone.__init__
        top_zone.frame.pack(fill="both", expand=True)

        # ── Register all panels ───────────────────────────────────────────────
        dm.register("status",      self._build_status_panel,      zone="left",  title="Status",         minsize=100)
        dm.register("exp",         self._build_exp_panel,         zone="left",  title="Experience",     minsize=100)
        dm.register("timeweather", self._build_timeweather_panel, zone="left",  title="Time & Weather", minsize=120)
        dm.register("wounds",      self._build_wounds_panel,      zone="left",  title="Wounds",         minsize=220)
        dm.register("map",         self._build_map_panel,         zone="right", title="Map",            minsize=200)

        # Set _paned BEFORE finalize so DockManager can reference it during build
        self._paned = main_paned

        # Build all panels into their zones
        dm.finalize()

        # Slim toolbar: just server status + gear icon (font controls moved to gear dialog)
        toolbar = tk.Frame(text_frame, bg=BG_PANEL)
        toolbar.pack(fill="x", side="top")

        # ── Status effect icon strip (left side of toolbar) ──────────────────
        # Icons are 26x26, packed left to right. Empty = dim label.
        self._fx_icon_frame = tk.Frame(toolbar, bg=BG_PANEL)
        self._fx_icon_frame.pack(side="left", fill="y", padx=(2, 4))
        # Start with the empty placeholder
        self._fx_empty_lbl = tk.Label(
            self._fx_icon_frame,
            text="no effects",
            fg="#2a3040", bg=BG_PANEL,
            font=("Courier New", 8),
        )
        self._fx_empty_lbl.pack(side="left", padx=6, pady=4)

        # ── ⚙ Settings gear button (top-right) ──
        self._gear_btn = tk.Button(
            toolbar, text="⚙",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=("Georgia", 11), relief="flat", bd=0, padx=6,
            activebackground=BORDER_CLR, cursor="hand2",
            command=self._show_settings_dialog,
        )
        self._gear_btn.pack(side="right", padx=(0, 4))

        # ── Connect / Disconnect button ──
        self._conn_btn = tk.Button(
            toolbar, text="⚡ Connect",
            bg="#0d2a0d", fg=ACCENT_GRN,
            font=("Georgia", 9, "bold"), relief="flat", bd=0, padx=8,
            activebackground="#1a4a1a", cursor="hand2",
            command=self._show_connect_dialog,
        )
        self._conn_btn.pack(side="right", padx=(0, 2))
        self._conn_status = tk.Label(
            toolbar, text=f"{self.host}:{self.port}",
            fg=TEXT_DIM, bg=BG_PANEL, font=("Georgia", 8),
        )
        self._conn_status.pack(side="right", padx=(0, 2))

        self._text = tk.Text(
            text_frame,
            bg="#0a0c10", fg=TEXT_MAIN,
            font=(self._game_font, self._font_size),
            wrap="word",
            state="disabled",
            bd=0,
            padx=8, pady=6,
            spacing1=2, spacing2=1, spacing3=3,
            insertbackground=ACCENT_BLUE,
            selectbackground="#2a3f5f",
        )
        sb = ttk.Scrollbar(text_frame, command=self._text.yview)
        self._text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)

        self._text.bind("<Control-MouseWheel>",
                        lambda e: self._resize_text(1 if e.delta > 0 else -1))
        self._text.bind("<Control-Button-4>", lambda e: self._resize_text(+1))
        self._text.bind("<Control-Button-5>", lambda e: self._resize_text(-1))

        # ── Stance bar (bottom of left text pane) ──
        stance_frame = tk.Frame(text_frame, bg="#0d1117")
        stance_frame.pack(fill="x", side="bottom", pady=(2, 0))
        tk.Label(stance_frame, text="Stance:", fg=TEXT_DIM, bg="#0d1117",
                 font=("Georgia", 9)).pack(side="left", padx=(6, 4))
        self._stance_lbl = tk.Label(stance_frame, text="—", fg=ACCENT_YEL,
                                     bg="#0d1117", font=("Georgia", 9, "bold"))
        self._stance_lbl.pack(side="left", padx=(0, 8))
        STANCES = ["Offensive", "Advance", "Forward", "Neutral", "Guarded", "Defensive"]
        for stance in STANCES:
            abbrev = stance[:3].upper()
            btn = tk.Button(stance_frame, text=abbrev, fg="#aaccaa", bg="#131a13",
                            activebackground="#1e2e1e", relief="flat", bd=0,
                            padx=6, pady=2, font=("Georgia", 9),
                            command=lambda st=stance: self._set_stance(st))
            btn.pack(side="left", padx=1)

        # Panels registered via DockManager above — no separate right_vpaned needed

        # ── Combat action buttons (row 1) ─────────────────────────────────────
        combat_bar = tk.Frame(self.root, bg="#0d1117", pady=3)
        combat_bar.pack(fill="x", padx=4, pady=(3, 0))

        btn_style = dict(relief="flat", bd=0, padx=14, pady=5,
                         font=("Georgia", 10, "bold"), cursor="hand2")

        # RT countdown bar
        rt_box = tk.Frame(combat_bar, bg="#0d1117")
        rt_box.pack(side="left", padx=(2, 6))
        self._rt_canvas = tk.Canvas(rt_box, width=60, height=28,
                                    bg="#111318", highlightthickness=1,
                                    highlightbackground="#333a44")
        self._rt_canvas.pack()
        self._rt_bar_id = None
        self._rt_end_time: float = 0.0
        self._rt_total:    float = 0.0

        self._attack_btn = tk.Button(
            combat_bar, text="⚔  Attack",
            bg="#3a1a0a", fg="#ff9966",
            activebackground="#5a2a10",
            command=self._cmd_attack, **btn_style)
        self._attack_btn.pack(side="left", padx=(0, 3))

        self._target_btn = tk.Button(
            combat_bar, text="◎  Target",
            bg="#1a2a3a", fg="#66aaff",
            activebackground="#2a3a5a",
            command=self._cmd_target_monster, **btn_style)
        self._target_btn.pack(side="left", padx=(3, 0))

        self._bodypart_btn = tk.Button(
            combat_bar, text="🎯  Body Part",
            bg="#1a2a3a", fg="#88bbff",
            activebackground="#2a3a5a",
            command=self._cmd_aim_bodypart, **btn_style)
        self._bodypart_btn.pack(side="left", padx=(3, 0))

        self._target_lbl = tk.Label(
            combat_bar, text="No target", fg=TEXT_DIM, bg="#0d1117",
            font=("Georgia", 9, "italic"), width=14)
        self._target_lbl.pack(side="left", padx=(6, 6))

        self._loot_btn = tk.Button(
            combat_bar, text="💰  Loot",
            bg="#1a2a1a", fg="#88dd88",
            activebackground="#2a4a2a",
            command=self._cmd_loot, **btn_style)
        self._loot_btn.pack(side="left", padx=(0, 3))

        self._look_btn = tk.Button(
            combat_bar, text="👁  Look",
            bg="#1a1a2a", fg="#aaaadd",
            activebackground="#2a2a4a",
            command=self._cmd_look, **btn_style)
        self._look_btn.pack(side="left", padx=3)

        tk.Button(combat_bar, text="🔓  Pick",
                  bg="#1a2a1a", fg="#88cc88",
                  activebackground="#2a4a2a",
                  command=self._cmd_pick,
                  **btn_style).pack(side="right", padx=3)
        tk.Button(combat_bar, text="🔍  Detect",
                  bg="#1a2a1a", fg="#88bbcc",
                  activebackground="#2a4a2a",
                  command=self._cmd_detect,
                  **btn_style).pack(side="right", padx=3)
        tk.Button(combat_bar, text="💣  Disarm",
                  bg="#2a1a0a", fg="#ccaa66",
                  activebackground="#4a2a10",
                  command=self._cmd_disarm,
                  **btn_style).pack(side="right", padx=3)

        tk.Frame(combat_bar, bg="#0d1117").pack(side="left", fill="x", expand=True)

        tk.Button(combat_bar, text="🌑  Hide",
                  bg="#1a1a1a", fg="#999999",
                  activebackground="#2a2a2a",
                  command=lambda: self._quick_cmd("hide"),
                  **btn_style).pack(side="left", padx=3)
        tk.Button(combat_bar, text="🗡  Ambush",
                  bg="#2a1a1a", fg="#cc8888",
                  activebackground="#4a2a2a",
                  command=self._cmd_ambush,
                  **btn_style).pack(side="left", padx=(3, 8))
        tk.Button(combat_bar, text="⚡  Feint",
                  bg="#1a1a2a", fg="#aaaaff",
                  activebackground="#2a2a4a",
                  command=lambda: self._quick_cmd("feint"),
                  **btn_style).pack(side="left", padx=(0, 8))

        # ── Input bar (between combat row and utility row) ─────────────────────
        bottom = tk.Frame(self.root, bg=BG_APP)
        bottom.pack(fill="x", padx=4, pady=(3, 0))

        self._rt_label = tk.Label(bottom, text="", fg=ACCENT_YEL, bg=BG_APP,
                                   font=("Georgia", 9))
        self._rt_label.pack(side="left", padx=(0, 6))

        self._input_mode_btn = tk.Button(
            bottom, text="◉", width=2,
            bg="#182030", fg=ACCENT_BLUE,
            activebackground="#24314a",
            font=("Georgia", 9, "bold"),
            relief="flat", bd=0, padx=2, pady=2,
            cursor="hand2",
            command=self._toggle_input_mode,
        )
        self._input_mode_btn.pack(side="left", padx=(0, 4))
        self._input_mode_btn.bind("<Button-3>", self._show_comm_mode_menu)

        self._prompt_lbl = tk.Label(bottom, text=">", fg=TEXT_DIM, bg=BG_APP,
                                     font=("Georgia", 11, "bold"), width=6, anchor="w")
        self._prompt_lbl.pack(side="left", padx=(0, 4))

        self._entry_var = tk.StringVar()
        self._entry = tk.Entry(
            bottom,
            textvariable=self._entry_var,
            bg=BG_INPUT, fg=TEXT_MAIN,
            font=("Georgia", 11),
            insertbackground=ACCENT_BLUE,
            bd=0, highlightthickness=1,
            highlightcolor=ACCENT_BLUE,
            highlightbackground=BORDER_CLR,
        )
        self._entry.pack(side="left", fill="x", expand=True, ipady=5)
        self._entry.bind("<Return>",   self._on_enter)
        self._entry.bind("<Up>",       self._hist_prev)
        self._entry.bind("<Down>",     self._hist_next)
        self._entry.bind("<Escape>",   lambda _: self._entry_var.set(""))
        self._entry.focus_set()
        self._apply_input_mode()

        self._cancel_btn = tk.Button(
            bottom, text="✕ Cancel Path",
            bg="#3a1010", fg=ACCENT_RED,
            font=("Georgia", 9),
            relief="flat", bd=0, padx=6,
            activebackground="#5a2020",
            command=self._cancel_pathfind,
        )

        # ── Utility buttons row (below input bar) ─────────────────────────────
        util_bar = tk.Frame(self.root, bg="#0a0c10", pady=2)
        util_bar.pack(fill="x", padx=4, pady=(2, 3))

        util_style = dict(relief="flat", bd=0, padx=10, pady=3,
                          font=("Georgia", 9), cursor="hand2")

        tk.Button(util_bar, text="📦 Full Inventory",
                  bg="#1a1a2a", fg="#ccccff",
                  activebackground="#2a2a4a",
                  command=lambda: self._quick_cmd("inv full"),
                  **util_style).pack(side="left", padx=(2, 3))
        tk.Button(util_bar, text="🎒 Inventory",
                  bg="#1a1a2a", fg="#ccccff",
                  activebackground="#2a2a4a",
                  command=lambda: self._quick_cmd("inv"),
                  **util_style).pack(side="left", padx=3)
        tk.Button(util_bar, text="📈 Train",
                  bg="#1a2a1a", fg="#aaddaa",
                  activebackground="#2a4a2a",
                  command=lambda: self._quick_cmd("train"),
                  **util_style).pack(side="left", padx=3)
        tk.Button(util_bar, text="🧙 Character",
                  bg="#2a1a2a", fg="#ddaadd",
                  activebackground="#4a2a4a",
                  command=lambda: self._quick_cmd("info"),
                  **util_style).pack(side="left", padx=3)
        tk.Button(util_bar, text="📊 EXP",
                  bg="#1a2a1a", fg="#88ddaa",
                  activebackground="#2a4a2a",
                  command=lambda: self._quick_cmd("exp"),
                  **util_style).pack(side="left", padx=3)
        tk.Button(util_bar, text="❤ Health",
                  bg="#2a1a1a", fg="#dd8888",
                  activebackground="#4a2a2a",
                  command=lambda: self._quick_cmd("health"),
                  **util_style).pack(side="left", padx=3)

        # Enemies seen in current room
        self._room_enemies: List[dict] = []
        self._target_index: int = 0
        self._current_target: str = ""
        self._current_target_match: str = ""
        # Persistent AIM preference (mirrors server session.aimed_location)
        # "" = not set (random), otherwise e.g. "head", "right arm"
        self._current_aim: str = ""

    def _build_status_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Status ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=(6, 2))

        self._hp_bar = StatBar(frame, "HP", BAR_HP)
        self._mp_bar = StatBar(frame, "MP", BAR_MP)
        self._sp_bar = StatBar(frame, "SP", BAR_SP)
        self._st_bar = StatBar(frame, "ST", BAR_ST)

        for bar in (self._hp_bar, self._mp_bar, self._sp_bar, self._st_bar):
            bar.pack(fill="x", pady=0)

        tp_row = tk.Frame(frame, bg=BG_PANEL)
        tp_row.pack(fill="x", padx=4, pady=(2, 3))
        tk.Label(tp_row, text="PTP:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 10, "bold")).pack(side="left")
        self._ptp_lbl = tk.Label(tp_row, text="—", fg=ACCENT_GRN, bg=BG_PANEL,
                                  font=("Courier New", 10))
        self._ptp_lbl.pack(side="left", padx=(2, 10))
        tk.Label(tp_row, text="MTP:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 10, "bold")).pack(side="left")
        self._mtp_lbl = tk.Label(tp_row, text="—", fg=ACCENT_BLUE, bg=BG_PANEL,
                                  font=("Courier New", 10))
        self._mtp_lbl.pack(side="left", padx=(2, 0))

    def _build_map_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Map — drag/scroll/click ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=2)

        btn_bar = tk.Frame(frame, bg=BG_PANEL)
        btn_bar.pack(fill="x", side="bottom")
        tk.Button(btn_bar, text="⟳ Reload annotations", fg=TEXT_DIM, bg=BG_INPUT,
                  font=("Courier New", 8), relief="flat", bd=0, padx=4,
                  activebackground=BORDER_CLR,
                  command=self._reload_map_annotations).pack(side="right", padx=2, pady=1)

        self._map = MapImageCanvas(frame, self.graph, self.regions, self._on_map_click)
        self._map.pack(fill="both", expand=True)

    def _build_fx_panel(self, parent):
        """Status effects panel — buffs/debuffs with live countdown timers."""
        frame = tk.LabelFrame(parent, text=" Effects ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=(2, 4))

        # Scrollable inner area for many effects
        canvas = tk.Canvas(frame, bg=BG_PANEL, highlightthickness=0)
        sb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_PANEL)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(inner_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _resize)

        # Placeholder shown when no effects are active
        self._fx_empty_lbl = tk.Label(inner, text="No active effects",
                                       fg="#333a44", bg=BG_PANEL,
                                       font=("Courier New", 8))
        self._fx_empty_lbl.pack(pady=6)

        self._fx_inner  = inner
        self._fx_canvas = canvas
        # Row widgets: effect_id -> tk.Frame  (rebuilt on each sync update)
        self._fx_rows: dict = {}

    def _update_fx_panel(self, effects: list):
        """
        Rebuild the effects panel from a live effects list.
        effects: list of dicts from sync snapshot status_effects field.
        """
        inner = self._fx_inner

        # Destroy all existing rows
        for w in list(self._fx_rows.values()):
            w.destroy()
        self._fx_rows.clear()

        # Category colour map
        CAT_COLORS = {
            "DEBUFF_COMBAT":  "#da3633",   # red
            "DEBUFF_DOT":     "#ff6b35",   # orange-red
            "DEBUFF_STAT":    "#e3a835",   # amber
            "DEBUFF_CONTROL": "#b06000",   # dark orange
            "BUFF_COMBAT":    "#238636",   # green
            "BUFF_REACTIVE":  "#1a7f37",   # dark green
            "BUFF_SPECIAL":   "#1f6feb",   # blue
            "STATE":          "#444c56",   # grey
        }

        # Filter out pure STATE effects that aren't interesting to display
        HIDE_STATES = {"in_combat", "exited_combat", "roundtime"}
        visible = [e for e in effects if e.get("id") not in HIDE_STATES]

        if not visible:
            self._fx_empty_lbl.pack(pady=6)
            return

        self._fx_empty_lbl.pack_forget()

        for ef in visible:
            eid      = ef.get("id", "")
            name     = ef.get("name", eid)
            cat      = ef.get("category", "")
            stacks   = ef.get("stacks", 1)
            rem      = ef.get("remaining", -1)
            pchar    = ef.get("prompt_char") or ""
            color    = CAT_COLORS.get(cat, TEXT_DIM)

            row = tk.Frame(inner, bg=BG_PANEL)
            row.pack(fill="x", padx=3, pady=1)

            # Coloured indicator pip
            pip = tk.Frame(row, bg=color, width=4)
            pip.pack(side="left", fill="y", padx=(0, 3))

            # Name + stacks
            disp = name if stacks <= 1 else f"{name} x{stacks}"
            tk.Label(row, text=disp, fg=color, bg=BG_PANEL,
                     font=("Courier New", 8, "bold"),
                     anchor="w").pack(side="left", fill="x", expand=True)

            # Timer
            if rem < 0:
                rem_str = "∞"
                rem_col = TEXT_DIM
            elif rem <= 5:
                rem_str = f"{rem:.0f}s"
                rem_col = ACCENT_RED
            elif rem <= 15:
                rem_str = f"{rem:.0f}s"
                rem_col = ACCENT_YEL
            else:
                rem_str = f"{int(rem)}s" if rem < 60 else f"{int(rem)//60}m{int(rem)%60:02d}s"
                rem_col = TEXT_DIM

            tk.Label(row, text=rem_str, fg=rem_col, bg=BG_PANEL,
                     font=("Courier New", 8), width=6, anchor="e").pack(side="right")

            self._fx_rows[eid] = row

        self._fx_canvas.configure(scrollregion=self._fx_canvas.bbox("all"))

    # ── Real-time sync dispatch ───────────────────────────────────────────────

    def _dispatch_sync(self, stype: str, payload):
        """Handle messages from the sync queue (called from _poll)."""
        try:
            if stype == "sync_state":
                self._apply_sync_state(payload)
            elif stype == "sync_closed":
                self._sync_connected = False
            elif stype == "sync_error":
                pass  # connection noise, ignore
        except Exception:
            pass  # never propagate sync errors to the poll loop

    def _apply_sync_state(self, snap: dict):
        """
        Apply a full state snapshot from the sync server.
        Updates all HUD panels silently — nothing goes to the chat window.
        """
        self._last_sync = snap
        self._sync_connected = True
        self._refresh_sync_hand_cache()

        room_info = snap.get("room")
        if isinstance(room_info, dict):
            try:
                room_id = int(room_info.get("id"))
            except (TypeError, ValueError):
                room_id = None
            if room_id is not None:
                self._update_room(room_id)

        # ── Vitals ──────────────────────────────────────────────────────────
        v = snap.get("vitals", {})
        if v:
            self._hp_bar.update(v.get("hp", 0),      v.get("hp_max",      100))
            self._mp_bar.update(v.get("mp", 0),      v.get("mp_max",      0))
            self._sp_bar.update(v.get("sp", 0),      v.get("sp_max",      10))
            self._st_bar.update(v.get("stamina", 0), v.get("stamina_max", 100))

        # ── XP / mind ───────────────────────────────────────────────────────
        xp = snap.get("xp", {})
        if xp:
            self._exp_level = xp.get("level",      self._exp_level)
            self._exp_total = xp.get("total",      self._exp_total)
            self._exp_tnl   = xp.get("tnl",        self._exp_tnl)
            mind = xp.get("mind_state", "")
            if mind:
                self._mind_state = mind
            self._update_exp_panel()

        # ── Status effects — update both the left panel and the floating bar ──
        effects = snap.get("status_effects", [])
        self._render_fx_bar(effects)     # toolbar icon bar

        # ── Combat flag ──────────────────────────────────────────────────────
        combat = snap.get("combat", {})
        self._in_combat = combat.get("in_combat", False)

        # ── Stance ───────────────────────────────────────────────────────────
        stance = snap.get("stance", "")
        if stance:
            self._stance_lbl.config(text=stance.capitalize())

        # ── PTP / MTP ────────────────────────────────────────────────────────
        ptp = snap.get("ptp")
        mtp = snap.get("mtp")
        if ptp is not None:
            self._ptp_lbl.config(text=str(ptp))
        if mtp is not None:
            self._mtp_lbl.config(text=str(mtp))

        # ── TNL ──────────────────────────────────────────────────────────────
        tnl = snap.get("xp", {}).get("tnl")
        if tnl is not None:
            self._exp_tnl = tnl
            self._exp_tnl_lbl.config(text=f"{tnl:,}" if tnl else "—")

        # ── Time & Weather ────────────────────────────────────────────────────
        tw = snap.get("time_weather", {})
        if tw:
            self._tw_day_name   = tw.get("day_name",       self._tw_day_name)
            self._tw_month_name = tw.get("month_name",     self._tw_month_name)
            self._tw_day        = tw.get("day",            self._tw_day)
            self._tw_year       = tw.get("elanthian_year", self._tw_year)
            self._tw_period     = tw.get("period",         self._tw_period)
            self._tw_hour_name  = tw.get("hour_name",      self._tw_hour_name)
            self._tw_time_24    = tw.get("time_24",        self._tw_time_24)
            self._tw_holiday    = tw.get("holiday") or ""
            self._tw_weather    = tw.get("weather_label",  self._tw_weather)
            self._tw_forced     = bool(tw.get("weather_forced",  False))
            self._tw_precip     = bool(tw.get("precipitation",   False))
            self._tw_indoor     = bool(tw.get("indoor",          False))
            # Map weather_label back to state key for icon lookup
            state_raw = tw.get("weather_state", "clear")
            self._tw_weather    = state_raw   # store raw state for icon lookup
            self._update_timeweather_panel()

        # ── Position / encumbrance (future panel use) ────────────────────────
        # Stored in _last_sync for any panel that wants to read it.

        # ── Wounds ────────────────────────────────────────────────────────────
        room_enemies = snap.get("room_enemies")
        if isinstance(room_enemies, list):
            normalized = []
            for entry in room_enemies:
                if not isinstance(entry, dict):
                    continue
                token = str(entry.get("token") or "").strip()
                if not token:
                    continue
                normalized.append({
                    "token": token,
                    "display": str(entry.get("display") or token).strip(),
                    "match": str(entry.get("match") or token).strip().lower(),
                })
            self._room_enemies = normalized
            if self._current_target and not any(e.get("token") == self._current_target for e in self._room_enemies):
                self._clear_target()

        room_npcs = snap.get("room_npcs")
        if isinstance(room_npcs, list):
            normalized_npcs = []
            for entry in room_npcs:
                if not isinstance(entry, dict):
                    continue
                actions = []
                for action in entry.get("actions", []):
                    if not isinstance(action, dict):
                        continue
                    cmd = str(action.get("command") or "").strip()
                    label = str(action.get("label") or cmd).strip()
                    if not cmd or not label:
                        continue
                    actions.append({
                        "label": label,
                        "command": cmd,
                        "prefill": bool(action.get("prefill", False)),
                    })
                if not actions:
                    continue
                aliases = []
                for alias in entry.get("aliases", []):
                    alias_text = str(alias or "").strip()
                    if alias_text and alias_text not in aliases:
                        aliases.append(alias_text)
                if not aliases:
                    continue
                patterns = []
                for alias in aliases:
                    escaped = re.escape(alias)
                    patterns.append(re.compile(rf"(?<![A-Za-z0-9_])({escaped})(?![A-Za-z0-9_])", re.IGNORECASE))
                normalized_npcs.append({
                    "template_id": str(entry.get("template_id") or "").strip(),
                    "name": str(entry.get("name") or "").strip(),
                    "display": str(entry.get("display") or aliases[0]).strip(),
                    "aliases": aliases,
                    "patterns": patterns,
                    "marker": str(entry.get("marker") or " ·"),
                    "actions": actions,
                })
            self._room_npcs = normalized_npcs
            self._decorate_visible_npc_links()

        wounds_snap = snap.get("wounds", {})
        if wounds_snap is not None:
            self._wounds = wounds_snap
            self._update_wounds_panel()


    # ══════════════════════════════════════════════════════════════════════════
    # Status Effect Icon Bar  (embedded in toolbar, no floating window)
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_sync_hand_cache(self):
        """Keep lockbox button state aligned with the live sync snapshot."""
        box_nouns = {"box", "coffer", "chest", "crate", "strongbox", "lockbox", "safe"}
        for hand_key in ("right_hand", "left_hand"):
            noun = str(self._last_sync.get(hand_key) or "").strip().lower()
            if noun and any(box in noun for box in box_nouns):
                self._last_lockbox_noun = noun
                return
        self._last_lockbox_noun = ""

    def _build_fx_bar(self):
        """No-op — bar is built inline in _build_ui toolbar."""
        pass

    def _draw_fx_icon(self, parent, effect_id: str, se: dict) -> tk.Frame:
        """
        Draw a 26x26 icon cell inside the toolbar frame.
        Returns the cell Frame so caller can track it.
        """
        defn = STATUS_ICON_DEFS.get(effect_id, {
            "shape": "square", "color": "#444c56", "border": "#8b949e",
            "symbol": effect_id[:2].upper(), "label": effect_id[:5],
            "tip": effect_id.replace("_", " ").title(),
        })

        SZ = 26  # icon canvas size — fits in toolbar row height

        cell = tk.Frame(parent, bg=BG_PANEL)
        cell.pack(side="left", padx=1, pady=2)

        c = tk.Canvas(cell, width=SZ, height=SZ,
                      bg=BG_PANEL, highlightthickness=0)
        c.pack()

        color  = defn["color"]
        border = defn["border"]
        shape  = defn["shape"]
        symbol = defn["symbol"]
        stacks = se.get("stacks", 1)
        rem    = se.get("remaining", -1)
        p = 1   # padding inside icon

        # ── Shape ────────────────────────────────────────────────────────────
        if shape == "square":
            c.create_rectangle(p, p, SZ-p, SZ-p, fill=color, outline=border, width=2)
        elif shape == "circle":
            c.create_oval(p, p, SZ-p, SZ-p, fill=color, outline=border, width=2)
        elif shape == "diamond":
            m = SZ // 2
            c.create_polygon([m, p+1, SZ-p-1, m, m, SZ-p-1, p+1, m],
                             fill=color, outline=border, width=2)
        elif shape == "skull":
            c.create_oval(p+2, p+1, SZ-p-2, SZ-p-4, fill=color, outline=border, width=2)
            c.create_rectangle(SZ//2-3, SZ-p-5, SZ//2+3, SZ-p-1,
                               fill=color, outline=border, width=1)
            c.create_oval(p+5, SZ//2-4, p+9,  SZ//2,   fill="#000", outline="")
            c.create_oval(SZ-p-9, SZ//2-4, SZ-p-5, SZ//2, fill="#000", outline="")
        elif shape == "arrow_down":
            m = SZ // 2
            c.create_polygon([m, SZ-p-1, p+1, p+2, SZ-p-1, p+2],
                             fill=color, outline=border, width=2)
        elif shape == "arrow_up":
            m = SZ // 2
            c.create_polygon([m, p+1, p+1, SZ-p-1, SZ-p-1, SZ-p-1],
                             fill=color, outline=border, width=2)
        elif shape == "zzz":
            c.create_rectangle(p, p, SZ-p, SZ-p, fill=color, outline=border, width=2)
            c.create_text(SZ-6, 6,    text="z", fill="#90caf9", font=("Courier New", 5, "bold"))
            c.create_text(SZ//2+2, SZ//2-2, text="Z", fill="#bbdefb", font=("Courier New", 7, "bold"))
            c.create_text(7, SZ-7,  text="Z", fill="#e3f2fd", font=("Courier New", 9, "bold"))
        elif shape == "blood_drop":
            # FFXI-style blood drop: teardrop — round bottom, pointed top
            cx = SZ // 2
            # Circular body (bottom 60% of icon)
            br = (SZ - 2*p) // 2 - 2
            by = SZ - p - br - 1
            c.create_oval(cx-br, by, cx+br, by+br*2, fill=color, outline=border, width=2)
            # Pointed tip (top)
            tip_x, tip_y = cx, p + 2
            c.create_polygon(
                tip_x, tip_y,
                cx - br//2, by + br//2,
                cx + br//2, by + br//2,
                fill=color, outline=border, width=1, smooth=True
            )
            # Highlight glint (top-left of drop body — FFXI style)
            c.create_oval(cx-br//2, by+2, cx-2, by+br//2,
                          fill="#ff8a80", outline="", stipple="")
        elif shape == "dot":
            r = (SZ-2*p)//3
            cx, cy = SZ//2, SZ//2
            c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline=border, width=2)
        else:
            c.create_rectangle(p, p, SZ-p, SZ-p, fill=color, outline=border, width=2)

        # ── Symbol (skip shapes that already drew their own content) ──────────
        if shape not in ("skull", "zzz", "blood_drop"):
            fs = 7 if len(symbol) > 1 else 10
            c.create_text(SZ//2+1, SZ//2+1, text=symbol,
                          fill="#00000099", font=("Courier New", fs, "bold"))
            c.create_text(SZ//2,   SZ//2,   text=symbol,
                          fill="#ffffff",  font=("Courier New", fs, "bold"))

        # ── Stacks badge ──────────────────────────────────────────────────────
        if stacks > 1:
            bx, by = SZ-3, 3
            c.create_oval(bx-5, by-5, bx+5, by+5, fill="#e65100", outline="")
            c.create_text(bx, by, text=str(stacks), fill="white",
                          font=("Courier New", 5, "bold"))

        # ── Timer overlay ─────────────────────────────────────────────────────
        if 0 <= rem < 60:
            col = "#ff5252" if rem < 5 else ("#e3b341" if rem < 15 else "#8b949e")
            c.create_text(SZ-2, SZ-2, text=f"{int(rem)}s",
                          fill=col, font=("Courier New", 5), anchor="se")
            if rem < 5:
                c.create_rectangle(p, p, SZ-p, SZ-p,
                                   fill="#00000044", outline="")

        # ── Tooltip ───────────────────────────────────────────────────────────
        tip_lines = [defn.get("tip", effect_id.replace("_"," ").title())]
        if 0 <= rem:
            tip_lines.append(f"Remaining: {int(rem)}s" if rem < 60
                             else f"Remaining: {int(rem)//60}m{int(rem)%60:02d}s")
        if stacks > 1:
            tip_lines.append(f"Stacks: {stacks}")
        tip_text = "\n".join(tip_lines)

        for w in (c, cell):
            w.bind("<Enter>",  lambda e, t=tip_text: self._show_fx_tooltip(e, t))
            w.bind("<Leave>",  lambda e:              self._hide_fx_tooltip())

        return cell

    def _render_fx_bar(self, effects: list):
        """
        Rebuild the embedded status icon strip from a live effects list.
        Called by _apply_sync_state every second.
        """
        if self._fx_icon_frame is None:
            return

        # Destroy all current icon cells
        for w in self._fx_icon_frame.winfo_children():
            w.destroy()
        self._fx_bar_icons.clear()

        # Filter: remove internal states AND effects that have expired (remaining == 0)
        # remaining == -1 means indefinite (keep), > 0 means active (keep), == 0 means done (drop)
        visible = [
            e for e in effects
            if e.get("id") not in STATUS_BAR_HIDDEN
            and e.get("remaining", -1) != 0
        ]

        if not visible:
            # Show the dim placeholder
            self._fx_empty_lbl = tk.Label(
                self._fx_icon_frame,
                text="no effects",
                fg="#2a3040", bg=BG_PANEL,
                font=("Courier New", 8),
            )
            self._fx_empty_lbl.pack(side="left", padx=6, pady=4)
            return

        # Draw icons left to right
        for ef in visible:
            eid  = ef.get("id", "")
            cell = self._draw_fx_icon(self._fx_icon_frame, eid, ef)
            self._fx_bar_icons[eid] = cell

    def _show_fx_tooltip(self, event, text: str):
        """Tooltip Toplevel near cursor — these are fine as Toplevels."""
        self._hide_fx_tooltip()
        if not text:
            return
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.configure(bg="#1c2128")

        tk.Frame(tip, bg="#58a6ff", height=1).pack(fill="x")
        inner = tk.Frame(tip, bg="#1c2128", padx=8, pady=5)
        inner.pack()
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if not line:
                continue
            tk.Label(inner, text=line,
                     fg="#ffffff" if i == 0 else "#8b949e",
                     bg="#1c2128",
                     font=("Georgia", 9, "bold" if i == 0 else "normal"),
                     justify="left", anchor="w").pack(fill="x")
        tk.Frame(tip, bg="#30363d", height=1).pack(fill="x")

        tip.update_idletasks()
        x = min(event.x_root + 12, tip.winfo_screenwidth()  - tip.winfo_reqwidth()  - 4)
        y = min(event.y_root + 12, tip.winfo_screenheight() - tip.winfo_reqheight() - 4)
        tip.geometry(f"+{x}+{y}")
        self._fx_tooltip_win = tip

    def _hide_fx_tooltip(self):
        if self._fx_tooltip_win:
            try:
                self._fx_tooltip_win.destroy()
            except Exception:
                pass
            self._fx_tooltip_win = None

    def _build_exp_panel(self, parent):
        """Left-side EXP / mind-state panel."""
        frame = tk.LabelFrame(parent, text=" Experience ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=(6, 4))

        def _row(lbl_text):
            r = tk.Frame(frame, bg=BG_PANEL)
            r.pack(fill="x", padx=6, pady=(3, 0))
            tk.Label(r, text=lbl_text, fg=TEXT_DIM, bg=BG_PANEL,
                     font=("Courier New", 10, "bold"), anchor="w", width=5).pack(side="left")
            val = tk.Label(r, text="—", fg=TEXT_MAIN, bg=BG_PANEL,
                           font=("Courier New", 10), anchor="e")
            val.pack(side="right")
            return val

        self._exp_lvl_lbl   = _row("LV")
        self._exp_total_lbl = _row("XP")
        self._exp_tnl_lbl   = _row("TNL")

        ms_row = tk.Frame(frame, bg=BG_PANEL)
        ms_row.pack(fill="x", padx=6, pady=(8, 2))
        tk.Label(ms_row, text="Mind:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 10, "bold")).pack(side="left")
        self._mind_lbl = tk.Label(ms_row, text="clear", fg=ACCENT_GRN, bg=BG_PANEL,
                                   font=("Courier New", 10, "bold"))
        self._mind_lbl.pack(side="right")

        bar_frame = tk.Frame(frame, bg=BG_PANEL)
        bar_frame.pack(fill="x", padx=6, pady=(2, 6))
        self._mind_canvas = tk.Canvas(bar_frame, height=12, bg="#111318",
                                      highlightthickness=1,
                                      highlightbackground="#333a44")
        self._mind_canvas.pack(fill="x")
        self._mind_canvas.bind("<Configure>", lambda _: self._update_mind_bar())

    def _update_mind_bar(self):
        """Redraw the mind state bar."""
        try:
            state  = self._mind_state.lower().strip()
            idx    = next((i for i, s in enumerate(MIND_STATES) if s in state), 0)
            total  = len(MIND_STATES) - 1   # 12
            pct    = idx / total

            w = self._mind_canvas.winfo_width() or 140
            h = self._mind_canvas.winfo_height() or 10
            self._mind_canvas.delete("all")
            fill_w = max(1, int(w * pct))

            # Color: green → yellow → orange → red as mind fills
            if pct < 0.35:
                color = ACCENT_GRN
            elif pct < 0.60:
                color = ACCENT_YEL
            elif pct < 0.80:
                color = "#ff8c00"
            else:
                color = ACCENT_RED
            self._mind_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")
        except Exception:
            pass

    def _update_exp_panel(self):
        """Push latest exp values to the panel labels."""
        self._exp_lvl_lbl.config(text=str(self._exp_level) if self._exp_level else "—")
        xp_str = f"{self._exp_total:,}" if self._exp_total else "—"
        tnl_str = f"{self._exp_tnl:,}" if self._exp_tnl else "—"
        self._exp_total_lbl.config(text=xp_str)
        self._exp_tnl_lbl.config(text=tnl_str)

        state = self._mind_state.lower().strip()
        idx   = next((i for i, s in enumerate(MIND_STATES) if s in state), 0)
        total = len(MIND_STATES) - 1
        pct   = idx / total
        if pct < 0.35:
            color = ACCENT_GRN
        elif pct < 0.60:
            color = ACCENT_YEL
        elif pct < 0.80:
            color = "#ff8c00"
        else:
            color = ACCENT_RED
        self._mind_lbl.config(text=self._mind_state, fg=color)
        self._update_mind_bar()

    def _build_room_info_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Room ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=(2, 6))

        self._room_name_lbl = tk.Label(
            frame, text="—", fg=ACCENT_BLUE, bg=BG_PANEL,
            font=("Courier New", 11, "bold"), wraplength=260, justify="left", anchor="w"
        )
        self._room_name_lbl.pack(fill="x", padx=4, pady=(2, 0))

        self._room_id_lbl = tk.Label(
            frame, text="", fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 9), anchor="w"
        )
        self._room_id_lbl.pack(fill="x", padx=4)

        self._room_zone_lbl = tk.Label(
            frame, text="", fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 9), anchor="w"
        )
        self._room_zone_lbl.pack(fill="x", padx=4, pady=(0, 2))

    # ════════════════════════════════════════════
    # Time & Weather panel
    # ════════════════════════════════════════════

    # Weather state → icon character + color
    _WEATHER_ICONS = {
        "clear":         ("☀",  "#ffd700"),
        "partly_cloudy": ("⛅", "#aaccff"),
        "overcast":      ("☁",  "#8b949e"),
        "fog":           ("🌫", "#8b949e"),
        "drizzle":       ("🌦", "#5599cc"),
        "light_rain":    ("🌧", "#5599cc"),
        "rain":          ("🌧", "#3377aa"),
        "heavy_rain":    ("🌧", "#2255aa"),
        "storm":         ("⛈", "#cc44cc"),
        "snow":          ("❄",  "#aaddff"),
        "heavy_snow":    ("❄",  "#88bbff"),
        "blizzard":      ("❄",  "#6699ff"),
        "sleet":         ("🌨", "#99bbdd"),
        "blood_rain":    ("🩸", "#cc2222"),
        "thunderstorm":  ("⛈", "#ff44ff"),
        "still":         ("〰", "#444c56"),
    }

    def _build_timeweather_panel(self, parent):
        """Time & Weather panel — populated entirely from sync, no chat parsing."""
        frame = tk.LabelFrame(parent, text=" Time & Weather ", fg=TEXT_DIM, bg=BG_PANEL,
                               font=("Courier New", 9), bd=1, relief="groove")
        frame.pack(fill="both", expand=True, padx=4, pady=(2, 4))

        # ── Date row ──────────────────────────────────────────────────────────
        date_row = tk.Frame(frame, bg=BG_PANEL)
        date_row.pack(fill="x", padx=6, pady=(6, 0))

        self._tw_date_lbl = tk.Label(
            date_row, text="—",
            fg=ACCENT_BLUE, bg=BG_PANEL,
            font=("Courier New", 9, "bold"),
            anchor="w", wraplength=155, justify="left"
        )
        self._tw_date_lbl.pack(fill="x")

        # ── Year row ──────────────────────────────────────────────────────────
        year_row = tk.Frame(frame, bg=BG_PANEL)
        year_row.pack(fill="x", padx=6, pady=(1, 0))

        self._tw_year_lbl = tk.Label(
            year_row, text="Year —",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 9), anchor="w"
        )
        self._tw_year_lbl.pack(side="left")

        # ── Time row ──────────────────────────────────────────────────────────
        time_row = tk.Frame(frame, bg=BG_PANEL)
        time_row.pack(fill="x", padx=6, pady=(4, 0))

        tk.Label(time_row, text="⏱", fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 10)).pack(side="left", padx=(0, 3))

        self._tw_time_lbl = tk.Label(
            time_row, text="—:—",
            fg=ACCENT_YEL, bg=BG_PANEL,
            font=("Courier New", 10, "bold"), anchor="w"
        )
        self._tw_time_lbl.pack(side="left")

        self._tw_period_lbl = tk.Label(
            time_row, text="",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 9, "italic"), anchor="e"
        )
        self._tw_period_lbl.pack(side="right")

        # ── Hour name row ─────────────────────────────────────────────────────
        hour_row = tk.Frame(frame, bg=BG_PANEL)
        hour_row.pack(fill="x", padx=6, pady=(1, 0))

        self._tw_hour_lbl = tk.Label(
            hour_row, text="—",
            fg=ACCENT_PRP, bg=BG_PANEL,
            font=("Courier New", 9), anchor="w"
        )
        self._tw_hour_lbl.pack(fill="x")

        # ── Divider ───────────────────────────────────────────────────────────
        tk.Frame(frame, bg=BORDER_CLR, height=1).pack(fill="x", padx=6, pady=(6, 4))

        # ── Weather row ───────────────────────────────────────────────────────
        wx_row = tk.Frame(frame, bg=BG_PANEL)
        wx_row.pack(fill="x", padx=6, pady=(0, 2))

        self._tw_wx_icon_lbl = tk.Label(
            wx_row, text="—",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 14)
        )
        self._tw_wx_icon_lbl.pack(side="left", padx=(0, 4))

        wx_text_col = tk.Frame(wx_row, bg=BG_PANEL)
        wx_text_col.pack(side="left", fill="x", expand=True)

        self._tw_wx_state_lbl = tk.Label(
            wx_text_col, text="—",
            fg=TEXT_MAIN, bg=BG_PANEL,
            font=("Courier New", 9, "bold"), anchor="w"
        )
        self._tw_wx_state_lbl.pack(fill="x")

        self._tw_wx_sub_lbl = tk.Label(
            wx_text_col, text="",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 8, "italic"), anchor="w"
        )
        self._tw_wx_sub_lbl.pack(fill="x")

        # ── Holiday row (hidden when no holiday) ──────────────────────────────
        self._tw_holiday_lbl = tk.Label(
            frame, text="",
            fg=ACCENT_GRN, bg=BG_PANEL,
            font=("Courier New", 8, "italic"),
            wraplength=155, justify="left", anchor="w"
        )
        # Not packed yet — only shown when a holiday is active

    def _update_timeweather_panel(self):
        """Push current _tw_* state vars into the panel labels."""
        try:
            # ── Date ──────────────────────────────────────────────────────────
            if self._tw_day and self._tw_month_name and self._tw_day_name:
                # e.g. "Feastday, 21 Charlatos"
                date_str = f"{self._tw_day_name}, {self._tw_day} {self._tw_month_name}"
                self._tw_date_lbl.config(text=date_str)
            else:
                self._tw_date_lbl.config(text="—")

            # ── Year ──────────────────────────────────────────────────────────
            self._tw_year_lbl.config(
                text=f"Year {self._tw_year} ME" if self._tw_year else "Year —"
            )

            # ── Time ──────────────────────────────────────────────────────────
            self._tw_time_lbl.config(text=self._tw_time_24 or "—:—")
            self._tw_period_lbl.config(text=self._tw_period or "")
            self._tw_hour_lbl.config(text=self._tw_hour_name or "—")

            # ── Weather icon + label ───────────────────────────────────────────
            state       = self._tw_weather or "clear"
            icon, color = self._WEATHER_ICONS.get(state, ("?", TEXT_DIM))
            wx_label    = state.replace("_", " ").title()
            if self._tw_weather in ("still", "—", "", None):
                wx_label = "Indoors"
                icon     = "🏠"
                color    = TEXT_DIM

            self._tw_wx_icon_lbl.config(text=icon, fg=color)
            self._tw_wx_state_lbl.config(text=wx_label, fg=color)

            # Sub-line: forced note or precipitation indicator
            sub = ""
            if self._tw_forced and state not in ("still", "clear"):
                sub = "✦ unnaturally altered"
            elif self._tw_precip:
                sub = "☂ precipitation active"
            self._tw_wx_sub_lbl.config(text=sub)

            # ── Holiday ───────────────────────────────────────────────────────
            if self._tw_holiday:
                self._tw_holiday_lbl.config(text=f"✦ {self._tw_holiday}")
                self._tw_holiday_lbl.pack(fill="x", padx=6, pady=(0, 4))
            else:
                self._tw_holiday_lbl.pack_forget()

        except Exception:
            pass  # panel may not be built yet on first sync tick

    # ════════════════════════════════════════════
    # Wounds Panel
    # ════════════════════════════════════════════

    # ── Herb → location mapping (wounds and scars, up to rank 5) ─────────────
    # Keyed by body-location slug.  Each entry lists herbs that treat wounds
    # then herbs that treat scars at that location, in priority order.
    # Rank 5 = limb loss — use limb_regen herb where available.
    _WOUND_HERBS = {
        "head":       {"wound": ["aloeas stem"],             "scar": ["haphip root", "brostheras potion"]},
        "neck":       {"wound": ["aloeas stem"],             "scar": ["haphip root", "brostheras potion"]},
        "chest":      {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "abdomen":    {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "back":       {"wound": ["basal moss", "pothinir grass"], "scar": ["blue argent tincture"]},
        "right_eye":  {"wound": ["basal moss", "pothinir grass"], "scar": ["aivren berry"],  "regen": ["bur-clover"]},
        "left_eye":   {"wound": ["basal moss", "pothinir grass"], "scar": ["aivren berry"],  "regen": ["bur-clover"]},
        "right_arm":  {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_arm":   {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "right_hand": {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_hand":  {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "right_leg":  {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
        "left_leg":   {"wound": ["ambrominas leaf", "ephlox moss"], "scar": ["cactacae spine"], "regen": ["sovyn clove"]},
    }

    # Tags for shop / bank rooms in the map graph
    _HERBALIST_TAG = "herbalist"
    _BANK_TAG      = "bank"

    def _build_wounds_panel(self, parent):
        """Human body silhouette with clickable wound/scar indicators per location."""
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)

        # ── Title ─────────────────────────────────────────────────────────────
        tk.Label(outer, text=" Wounds & Scars ", fg=TEXT_DIM, bg=BG_PANEL,
                 font=("Courier New", 9), anchor="w").pack(fill="x", padx=4, pady=(4, 0))

        # ── Canvas body figure ────────────────────────────────────────────────
        # We draw a simple stick-figure silhouette in SVG-style using tk.Canvas.
        # Each clickable hotspot is a canvas oval/rect tagged with the location.
        # Size: 170 wide × 220 tall (fits the left column at 210px width)
        W, H = 170, 220
        self._wound_canvas = tk.Canvas(outer, width=W, height=H,
                                       bg=BG_PANEL, highlightthickness=0)
        self._wound_canvas.pack(padx=4, pady=(2, 0))

        # Body part geometry: (tag, x-center, y-center, width, height, label)
        # Coordinates tuned for a ~170×260 canvas
        self._wound_parts = [
            ("head",       85,  22, 28, 24,  "Head"),
            ("neck",       85,  46, 14, 12,  "Neck"),
            ("chest",      85,  78, 44, 28,  "Chest"),
            ("abdomen",    85, 110, 38, 20,  "Abdomen"),
            ("back",       85,  94, 44, 44,  "Back"),   # overlaps chest/abdomen — drawn last, transparent
            ("right_eye",  74,  17,  7,  7,  "R.Eye"),
            ("left_eye",   96,  17,  7,  7,  "L.Eye"),
            ("right_arm",  54,  88, 14, 44,  "R.Arm"),
            ("left_arm",  116,  88, 14, 44,  "L.Arm"),
            ("right_hand", 54, 120, 12, 14,  "R.Hand"),
            ("left_hand", 116, 120, 12, 14,  "L.Hand"),
            ("right_leg",  70, 168, 16, 52,  "R.Leg"),
            ("left_leg",  100, 168, 16, 52,  "L.Leg"),
        ]

        # Draw body outline (static — just a silhouette)
        c = self._wound_canvas
        body_col = "#1e2a1e"
        outline   = "#2d4a2d"
        # torso
        c.create_rectangle(63, 56, 107, 136, fill=body_col, outline=outline, width=1)
        # head
        c.create_oval(71, 8, 99, 38, fill=body_col, outline=outline, width=1)
        # neck
        c.create_rectangle(80, 38, 90, 56, fill=body_col, outline=outline, width=1)
        # right arm
        c.create_rectangle(47, 58, 62, 132, fill=body_col, outline=outline, width=1)
        # left arm
        c.create_rectangle(108, 58, 123, 132, fill=body_col, outline=outline, width=1)
        # right leg
        c.create_rectangle(63, 136, 82, 204, fill=body_col, outline=outline, width=1)
        # left leg
        c.create_rectangle(88, 136, 107, 204, fill=body_col, outline=outline, width=1)

        # Draw hotspot overlays (transparent by default, colored when wounded)
        self._wound_hotspots = {}   # tag -> canvas item ids (rect + text)
        _part_boxes = {
            "head":       (71,   8,  99,  38),
            "neck":       (80,  38,  90,  56),
            "chest":      (63,  56, 107,  96),
            "abdomen":    (63,  96, 107, 136),
            # "back" uses a distinct strip — upper-torso only so it doesn't
            # overlap abdomen's hotspot zone. Its click area is drawn FIRST
            # (lower z-order) so abdomen receives mouse events over its zone.
            "back":       (63,  56, 107,  72),
            "right_eye":  (71,  10,  80,  22),
            "left_eye":   (90,  10,  99,  22),
            "right_arm":  (47,  58,  62, 132),
            "left_arm":   (108, 58, 123, 132),
            "right_hand": (47, 118,  62, 132),
            "left_hand":  (108,118, 123, 132),
            "right_leg":  (63, 136,  82, 204),
            "left_leg":   (88, 136, 107, 204),
        }
        _part_labels = {
            "head": "HD", "neck": "NK", "chest": "CH", "abdomen": "AB",
            "back": "BK", "right_eye": "RE", "left_eye": "LE",
            "right_arm": "RA", "left_arm": "LA",
            "right_hand": "RH", "left_hand": "LH",
            "right_leg": "RL", "left_leg": "LL",
        }
        # Draw back FIRST so abdomen and chest rects sit on top in z-order.
        # This prevents "back" stealing click events from abdomen's region.
        _DRAW_ORDER = [
            "back",
            "head", "neck", "chest", "abdomen",
            "right_eye", "left_eye",
            "right_arm", "left_arm", "right_hand", "left_hand",
            "right_leg", "left_leg",
        ]
        for tag in _DRAW_ORDER:
            if tag not in _part_boxes:
                continue
            x1, y1, x2, y2 = _part_boxes[tag]
            rect = c.create_rectangle(x1, y1, x2, y2,
                                      fill="", outline="", width=1,
                                      tags=(tag, "hotspot"))
            lbl  = c.create_text((x1+x2)//2, (y1+y2)//2,
                                  text="", fill="#ffffff",
                                  font=("Courier New", 7, "bold"),
                                  tags=(tag, "hotspot_text"))
            self._wound_hotspots[tag] = (rect, lbl)
            c.tag_bind(tag, "<Button-1>", lambda e, t=tag: self._wound_click(t))
            c.tag_bind(tag, "<Enter>",
                       lambda e, t=tag: self._wound_hover(t, True))
            c.tag_bind(tag, "<Leave>",
                       lambda e, t=tag: self._wound_hover(t, False))

        # ── Legend ────────────────────────────────────────────────────────────
        leg = tk.Frame(outer, bg=BG_PANEL)
        leg.pack(fill="x", padx=6, pady=(2, 0))
        legend_items = [
            ("#8b0000", "W1-2"), ("#cc0000", "W3-4"), ("#ff2020", "W5"),
            ("#4a3500", "S1-2"), ("#8b6914", "S3-4"), ("#d4a017", "S5"),
            ("#1a6a1a", "OK"),
        ]
        for col, lbl in legend_items:
            tk.Label(leg, text="█", fg=col, bg=BG_PANEL,
                     font=("Courier New", 8)).pack(side="left")
            tk.Label(leg, text=lbl+" ", fg=TEXT_DIM, bg=BG_PANEL,
                     font=("Courier New", 7)).pack(side="left")

        # ── Wound detail list ─────────────────────────────────────────────────
        detail_frame = tk.Frame(outer, bg=BG_PANEL)
        detail_frame.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        self._wound_detail_text = tk.Text(
            detail_frame, height=4, bg=BG_INPUT, fg=TEXT_DIM,
            font=("Courier New", 8), bd=0, relief="flat",
            state="disabled", wrap="word",
            highlightthickness=1, highlightbackground=BORDER_CLR,
            highlightcolor=ACCENT_BLUE,
        )
        self._wound_detail_text.pack(fill="both", expand=True)
        self._wound_detail_text.tag_config("wound",  foreground="#cc4444")
        self._wound_detail_text.tag_config("scar",   foreground="#d4a017")
        self._wound_detail_text.tag_config("bleed",  foreground="#ff4444")
        self._wound_detail_text.tag_config("ok",     foreground="#3fb950")
        self._wound_detail_text.tag_config("header", foreground=ACCENT_BLUE)

        # ── AUTO button ───────────────────────────────────────────────────────
        btn_row = tk.Frame(outer, bg=BG_PANEL)
        btn_row.pack(fill="x", padx=4, pady=(4, 6))

        self._auto_heal_btn = tk.Button(
            btn_row, text="⚕ AUTO Heal",
            fg="#ffffff", bg="#0d2a2a",
            font=("Courier New", 9, "bold"),
            relief="flat", bd=0, padx=8, pady=4,
            activebackground="#1a4a4a",
            command=self._wounds_auto_heal,
        )
        self._auto_heal_btn.pack(fill="x")

        self._wound_status_lbl = tk.Label(
            outer, text="", fg=TEXT_DIM, bg=BG_PANEL,
            font=("Courier New", 8), wraplength=155, justify="left",
        )
        self._wound_status_lbl.pack(fill="x", padx=4, pady=(0, 4))

    # ── Color helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _wound_color(wound_rank: int, scar_rank: int, is_bleeding: bool):
        """Return (fill_color, outline_color, label_text) for a body part."""
        wr, sr = wound_rank, scar_rank
        if wr == 5:
            return "#ff2020", "#ff6060", "†5"   # rank 5 = limb loss
        if wr >= 3:
            return "#cc0000", "#ff4444", f"W{wr}"
        if wr >= 1:
            return "#8b0000", "#cc2222", f"W{wr}"
        if sr == 5:
            return "#d4a017", "#ffe066", "†5"
        if sr >= 3:
            return "#8b6914", "#d4a017", f"S{sr}"
        if sr >= 1:
            return "#4a3500", "#8b6914", f"S{sr}"
        return "", "", ""   # clean

    def _update_wounds_panel(self):
        """Redraw all hotspots and refresh the detail list from self._wounds."""
        if not hasattr(self, "_wound_canvas"):
            return
        c = self._wound_canvas

        any_wound = False
        detail_lines = []   # list of (text, tag)

        for tag, (rect_id, lbl_id) in self._wound_hotspots.items():
            entry   = self._wounds.get(tag, {})
            wr      = int(entry.get("wound_rank",  0))
            sr      = int(entry.get("scar_rank",   0))
            bl      = bool(entry.get("is_bleeding", False))
            ba      = bool(entry.get("bandaged",    False))

            fill, outline, label_txt = self._wound_color(wr, sr, bl)

            if fill:
                any_wound = True
                c.itemconfig(rect_id, fill=fill, outline=outline, width=1)
                # Blinking outline for bleeding
                if bl:
                    c.itemconfig(rect_id, outline="#ff4444", width=2)
                label_txt += "♥" if bl else ""
                c.itemconfig(lbl_id, text=label_txt)
                # Detail line
                loc_display = tag.replace("_", " ").title()
                if wr:
                    detail_lines.append((f"{loc_display}: Wound {wr}", "wound"))
                    if bl:
                        detail_lines.append(("  ↳ bleeding" + (" (bandaged)" if ba else ""), "bleed"))
                if sr:
                    detail_lines.append((f"{loc_display}: Scar  {sr}", "scar"))
            else:
                c.itemconfig(rect_id, fill="", outline="", width=0)
                c.itemconfig(lbl_id, text="")

        # Update detail text widget
        tw = self._wound_detail_text
        tw.config(state="normal")
        tw.delete("1.0", "end")
        if detail_lines:
            tw.insert("end", "Active injuries:\n", "header")
            for txt, tag in detail_lines:
                tw.insert("end", txt + "\n", tag)
        else:
            tw.insert("end", "No wounds or scars.", "ok")
        tw.config(state="disabled")

    # ── Click-to-heal a single location ──────────────────────────────────────

    def _wound_click(self, loc: str):
        """Player clicked a body part — try to heal it from inventory."""
        entry = self._wounds.get(loc, {})
        wr    = int(entry.get("wound_rank", 0))
        sr    = int(entry.get("scar_rank",  0))

        if not wr and not sr:
            self._wound_status("No injury at " + loc.replace("_", " ") + ".")
            return

        # Determine which herb type we need
        herbs_map = self._WOUND_HERBS.get(loc, {})
        if wr == 5:
            # Limb loss — need regen herb
            need_type = "regen"
        elif wr:
            need_type = "wound"
        else:
            need_type = "scar"

        herb_candidates = herbs_map.get(need_type, [])
        if not herb_candidates:
            herb_candidates = herbs_map.get("wound", [])

        if not herb_candidates:
            self._wound_status(f"No herb known for {loc.replace('_',' ')}.")
            return

        # Send: inv full — then parse response via the existing chat parser
        # We queue a callback to check after "inv full" output arrives
        self._wound_status("Preparing treatment...")
        self._wound_pending_heal = (loc, herb_candidates, need_type)
        self.root.after(50, self._wound_heal_exec)

    def _wound_heal_exec(self):
        """Called after inv full has been sent — stow hands, get herb, eat herb."""
        if not hasattr(self, "_wound_pending_heal"):
            return
        loc, herb_candidates, need_type = self._wound_pending_heal
        del self._wound_pending_heal

        herb        = herb_candidates[0]
        loc_display = loc.replace("_", " ")
        self._wound_status(f"Healing {loc_display} with {herb}…")

        # Determine which hands are occupied from the last sync snapshot so we
        # know exactly which stow commands are needed before fetching the herb.
        snap       = self._last_sync
        right_item = snap.get("right_hand") if snap else None
        left_item  = snap.get("left_hand")  if snap else None

        # Build the command sequence with per-step delays:
        #   stow right  (if held)  → 700 ms
        #   stow left   (if held)  → 700 ms
        #   get <herb>             → 900 ms   (allow server round-trip)
        #   eat <herb>             → 900 ms
        steps   = []
        delays  = []

        elapsed = 0
        if right_item:
            steps.append("stow right")
            elapsed += 700
            delays.append(elapsed)
        if left_item:
            steps.append("stow left")
            elapsed += 700
            delays.append(elapsed)

        # Always try to stow both hands even if sync has no data,
        # to handle the case where sync hasn't caught up yet.
        if not right_item and not left_item:
            steps.append("stow right")
            elapsed += 700
            delays.append(elapsed)
            steps.append("stow left")
            elapsed += 400
            delays.append(elapsed)

        steps.append(f"get {herb}")
        elapsed += 900
        delays.append(elapsed)

        steps.append(f"use {herb}")
        elapsed += 900
        delays.append(elapsed)

        for cmd, ms in zip(steps, delays):
            self.root.after(ms, lambda c=cmd: self._send(c))

        self.root.after(elapsed + 500,
            lambda: self._send("wounds"))
        self.root.after(elapsed + 850,
            lambda: self._wound_status(f"Applied {herb} to {loc_display}."))

    def _wound_status(self, msg: str):
        """Update the status label under the AUTO button."""
        if hasattr(self, "_wound_status_lbl"):
            self._wound_status_lbl.config(text=msg)

    def _wound_hover(self, loc: str, entering: bool):
        """Show tooltip-style info on hover."""
        if not entering:
            return
        entry = self._wounds.get(loc, {})
        wr = int(entry.get("wound_rank", 0))
        sr = int(entry.get("scar_rank",  0))
        bl = bool(entry.get("is_bleeding", False))
        loc_disp = loc.replace("_", " ").title()
        if wr or sr:
            tip = f"{loc_disp}: W{wr} S{sr}" + (" ♥" if bl else "")
        else:
            tip = f"{loc_disp}: clean"
        self._wound_status(tip)

    # ── AUTO heal ─────────────────────────────────────────────────────────────

    def _auto_abort(self, message: str):
        self._wound_status(message)
        self._auto_done()

    def _auto_worn_container_keys(self) -> List[str]:
        keys: List[str] = []
        for cont in self._worn_containers:
            key = self._item_key(cont)
            if key and key not in keys:
                keys.append(key)
        return keys

    def _auto_pick_hand_container(self, item_type: str) -> Optional[str]:
        containers = self._auto_worn_container_keys()
        if not containers:
            return None

        def first_match(words: Tuple[str, ...]) -> Optional[str]:
            for cont in containers:
                if any(word in cont for word in words):
                    return cont
            return None

        if item_type == "weapon":
            return (
                first_match(("sheath", "scabbard"))
                or first_match(("cloak", "cape"))
                or first_match(("backpack", "rucksack", "haversack", "pack"))
                or containers[0]
            )

        return (
            first_match(("cloak", "cape"))
            or first_match(("backpack", "rucksack", "haversack", "pack"))
            or containers[0]
        )

    def _auto_pick_herb_container(self) -> Optional[str]:
        containers = self._auto_worn_container_keys()
        if not containers:
            return None

        for cont in containers:
            if "herb" in cont and "pouch" in cont:
                return cont
        for cont in containers:
            if any(word in cont for word in ("pouch", "satchel", "sack", "bag")):
                return cont
        for cont in containers:
            if any(word in cont for word in ("backpack", "rucksack", "haversack", "pack")):
                return cont
        return containers[0]

    def _auto_snapshot_hands(self) -> List[dict]:
        hand_items: List[dict] = []
        for hand in ("right", "left"):
            state = f"{hand}_hand"
            info = None
            for item in self._known_items.values():
                if item.get("state") == state:
                    info = item
                    break
            sync_name = str(self._last_sync.get(state) or "").strip()
            target = ""
            display = ""
            item_type = ""
            if info:
                display = str(info.get("full_name") or "").strip()
                target = self._item_key(display)
                item_type = str(info.get("item_type") or "").strip().lower()
            if not target and sync_name:
                display = sync_name
                target = self._item_key(sync_name)
            if not target:
                continue
            if not item_type:
                item_type = self._guess_type(target)
            hand_items.append({
                "hand": hand,
                "display": display or target,
                "target": target,
                "item_type": item_type or "misc",
            })
        return hand_items

    def _auto_build_requirements(self) -> Tuple[dict, dict, List[str], List[str]]:
        to_heal = {}
        herb_counts: Dict[str, int] = {}
        herb_sequence: List[str] = []
        missing: List[str] = []

        for loc, entry in self._wounds.items():
            wr = int(entry.get("wound_rank", 0))
            sr = int(entry.get("scar_rank", 0))
            if not (wr or sr):
                continue
            to_heal[loc] = {"wr": wr, "sr": sr}
            herbs_map = self._WOUND_HERBS.get(loc, {})

            if wr == 5:
                regen_herbs = herbs_map.get("regen", herbs_map.get("wound", []))
                herb = regen_herbs[0] if regen_herbs else None
                if herb:
                    herb_counts[herb] = herb_counts.get(herb, 0) + 1
                    herb_sequence.append(herb)
                else:
                    missing.append(f"{loc.replace('_', ' ')} wound")
            elif wr > 0:
                wound_herbs = herbs_map.get("wound", [])
                herb = wound_herbs[0] if wound_herbs else None
                if herb:
                    herb_counts[herb] = herb_counts.get(herb, 0) + wr
                    herb_sequence.extend([herb] * wr)
                else:
                    missing.append(f"{loc.replace('_', ' ')} wound")

            if sr > 0:
                scar_herbs = herbs_map.get("scar", [])
                herb = scar_herbs[0] if scar_herbs else None
                if herb:
                    herb_counts[herb] = herb_counts.get(herb, 0) + sr
                    herb_sequence.extend([herb] * sr)
                else:
                    missing.append(f"{loc.replace('_', ' ')} scar")

        hp_cur = int(self._last_sync.get("vitals", {}).get("hp", 0))
        hp_max = int(self._last_sync.get("vitals", {}).get("hp_max", 0))
        hp_missing = max(0, hp_max - hp_cur)
        acantha_needed = (hp_missing + 29) // 30 if hp_missing else 0
        if acantha_needed:
            herb_counts["acantha leaf"] = herb_counts.get("acantha leaf", 0) + acantha_needed
            herb_sequence.extend(["acantha leaf"] * acantha_needed)

        return to_heal, herb_counts, herb_sequence, missing

    def _auto_build_restore_steps(self, ctx: dict) -> List[Tuple[str, object]]:
        steps: List[Tuple[str, object]] = []
        steps.append(("send", "stow right"))
        steps.append(("send", "stow left"))
        steps.append(("delay", 500))
        for item in ctx.get("saved_hands", []):
            container = item.get("restore_container")
            target = item.get("target")
            if not target:
                continue
            if container:
                steps.append(("send", f"get {target} from {container}"))
            else:
                steps.append(("send", f"get {target}"))
            steps.append(("delay", 700))
        return steps

    def _auto_build_treatment_steps(self, ctx: dict) -> List[Tuple[str, object]]:
        herb_container = ctx.get("herb_container")
        herb_sequence = ctx.get("herb_sequence", [])
        steps: List[Tuple[str, object]] = []
        for herb in herb_sequence:
            if herb_container:
                steps.append(("send", f"get {herb} from {herb_container}"))
            else:
                steps.append(("send", f"get {herb}"))
            steps.append(("delay", 700))
            steps.append(("send", f"use {herb}"))
            steps.append(("delay", 1200))
        steps.extend(self._auto_build_restore_steps(ctx))
        steps.append(("send", "inv full"))
        steps.append(("delay", 1000))
        steps.append(("done", None))
        return steps

    def _auto_queue_herbalist_visit(self):
        ctx = self._auto_ctx
        candidates = ctx.get("herbalist_candidates", [])
        idx = int(ctx.get("herbalist_index", 0))
        if idx >= len(candidates):
            self._auto_abort("AUTO: I could not find a mapped herbalist carrying the required herbs.")
            return

        dest = int(candidates[idx])
        ctx["current_herbalist"] = dest
        self._shop_catalog = {}
        self._wound_status(f"AUTO: heading to herbalist room #{dest}.")

        steps: List[Tuple[str, object]] = []
        if self._current_room_id != dest:
            steps.append(("nav", dest))
            steps.append(("delay", 350))
        steps.append(("send", "order"))
        steps.append(("delay", 1100))
        steps.append(("catalog", None))
        self._auto_cmd_queue = steps + getattr(self, "_auto_cmd_queue", [])
        self.root.after(10, self._auto_run_next)

    def _auto_match_catalog(self) -> Tuple[dict, List[str], int]:
        ctx = self._auto_ctx
        herb_counts = ctx.get("herb_counts", {})
        matched = {}
        missing = []
        total_cost = 0

        by_key = {}
        for entry in self._shop_catalog.values():
            if not isinstance(entry, dict):
                continue
            keys = {
                self._item_key(entry.get("name", "")),
                self._item_key(entry.get("short_name", "")),
                self._item_key(entry.get("noun", "")),
            }
            for key in [k for k in keys if k]:
                by_key.setdefault(key, entry)

        for herb, qty in herb_counts.items():
            entry = by_key.get(self._item_key(herb))
            if not entry:
                missing.append(herb)
                continue
            matched[herb] = entry
            total_cost += int(entry.get("price", 0)) * int(qty)

        return matched, missing, total_cost

    def _auto_process_catalog(self):
        ctx = self._auto_ctx
        matched, missing, total_cost = self._auto_match_catalog()
        current_shop = ctx.get("current_herbalist")

        if missing:
            ctx["herbalist_index"] = int(ctx.get("herbalist_index", 0)) + 1
            if ctx["herbalist_index"] >= len(ctx.get("herbalist_candidates", [])):
                self._auto_abort(
                    "AUTO: no mapped herbalist had all required herbs: "
                    + ", ".join(sorted(missing))
                )
                return
            self._wound_status(
                "AUTO: this herbalist is missing "
                + ", ".join(sorted(missing))
                + ". Trying the next one."
            )
            self._auto_cmd_queue = [("herbalist", None)] + getattr(self, "_auto_cmd_queue", [])
            self.root.after(10, self._auto_run_next)
            return

        silver = int(self._last_sync.get("silver", 0))
        shortfall = max(0, total_cost - silver)
        if shortfall > 0:
            bank_id = ctx.get("bank_id")
            if ctx.get("bank_attempted"):
                self._auto_abort(
                    f"AUTO: still short {shortfall} silver after the bank trip."
                )
                return
            if bank_id is None:
                self._auto_abort(
                    f"AUTO: need {shortfall} more silver, but no mapped bank was found."
                )
                return
            ctx["bank_attempted"] = True
            self._wound_status(f"AUTO: short {shortfall} silver. Heading to the bank.")
            steps = [
                ("nav", int(bank_id)),
                ("delay", 350),
                ("send", f"bank withdraw {shortfall}"),
                ("delay", 1600),
            ]
            if current_shop is not None:
                steps.append(("herbalist", None))
            self._auto_cmd_queue = steps + getattr(self, "_auto_cmd_queue", [])
            self.root.after(10, self._auto_run_next)
            return

        herb_container = ctx.get("herb_container")
        if not herb_container:
            self._auto_abort("AUTO: I need a pouch, backpack, or other worn container for herbs.")
            return

        buy_steps: List[Tuple[str, object]] = []
        for herb, qty in ctx.get("herb_counts", {}).items():
            entry = matched.get(herb)
            if not entry:
                continue
            idx = entry.get("idx")
            buy_target = str(idx) if idx else herb
            for _ in range(int(qty)):
                buy_steps.append(("send", f"buy {buy_target}"))
                buy_steps.append(("delay", 800))
                buy_steps.append(("send", f"put {herb} in {herb_container}"))
                buy_steps.append(("delay", 550))

        self._wound_status("AUTO: herbs secured. Treating wounds now.")
        self._auto_cmd_queue = self._auto_build_treatment_steps(ctx) + getattr(self, "_auto_cmd_queue", [])
        self._auto_cmd_queue = buy_steps + self._auto_cmd_queue
        self.root.after(10, self._auto_run_next)

    def _wounds_auto_heal(self):
        """
        Full AUTO heal sequence:
        1. Snapshot hands / worn containers from INV FULL
        2. Stow current hand items into appropriate containers
        3. Navigate to the nearest mapped herbalist and ORDER its catalog
        4. If silver is short, navigate to the nearest mapped bank and withdraw
        5. Buy the required herbs, stash them, treat wounds/scars, then restore hands
        """
        if self._auto_healing:
            self._wound_status("AUTO heal already running.")
            return

        to_heal, herb_counts, herb_sequence, missing = self._auto_build_requirements()
        if not to_heal and not herb_sequence:
            self._wound_status("Nothing to heal.")
            return
        if missing:
            self._wound_status(
                "AUTO: no herb mapping for " + ", ".join(sorted(missing)) + "."
            )
            return
        if self._current_room_id is None:
            self._wound_status("AUTO: unknown current room. Try LOOK first.")
            return

        self._auto_healing = True
        self._auto_heal_btn.config(text="⏳ Healing…", state="disabled")
        self._wound_status("AUTO: taking inventory snapshot…")
        self._auto_ctx = {
            "to_heal": to_heal,
            "herb_counts": herb_counts,
            "herb_sequence": herb_sequence,
            "bank_id": self._find_tagged_room(self._BANK_TAG),
            "herbalist_candidates": self.graph.find_tagged_rooms(
                self._HERBALIST_TAG,
                from_id=self._current_room_id,
                limit=8,
            ) if self.graph else [],
            "herbalist_index": 0,
            "bank_attempted": False,
        }

        self._send("inv full")
        self._append("> inv full\n", "prompt")
        self.root.after(900, self._auto_prepare_inventory)

    def _find_tagged_room(self, tag: str) -> int | None:
        if not self.graph:
            return None
        rooms = self.graph.find_tagged_rooms(tag, from_id=self._current_room_id, limit=1)
        return rooms[0] if rooms else None

    def _auto_prepare_inventory(self):
        if not self._auto_healing:
            return

        ctx = self._auto_ctx
        herb_container = self._auto_pick_herb_container()
        if not herb_container:
            self._auto_abort("AUTO: I need a pouch, backpack, or other worn container first.")
            return

        saved_hands = self._auto_snapshot_hands()
        stow_steps: List[Tuple[str, object]] = []
        for item in saved_hands:
            container = self._auto_pick_hand_container(item.get("item_type", "misc"))
            item["restore_container"] = container
            if container:
                stow_steps.append(("send", f"put {item['target']} in {container}"))
            else:
                stow_steps.append(("send", f"stow {item['hand']}"))
            stow_steps.append(("delay", 550))

        ctx["saved_hands"] = saved_hands
        ctx["herb_container"] = herb_container

        if ctx.get("herb_counts"):
            if not ctx.get("herbalist_candidates"):
                self._auto_abort("AUTO: no mapped herbalist was found from this location.")
                return
            self._auto_cmd_queue = stow_steps + [("herbalist", None)]
            self._wound_status("AUTO: inventory ready. Heading for herbs.")
        else:
            self._auto_cmd_queue = stow_steps + self._auto_build_treatment_steps(ctx)
            self._wound_status("AUTO: herbs already on hand. Treating now.")

        self._auto_run_next()

    def _auto_run_next(self):
        """Pop and execute the next command in _auto_cmd_queue."""
        if not hasattr(self, "_auto_cmd_queue") or not self._auto_cmd_queue:
            self._auto_done()
            return

        action, value = self._auto_cmd_queue.pop(0)

        if action == "send":
            self._send(value)
            self.root.after(50, self._auto_run_next)

        elif action == "delay":
            self.root.after(int(value), self._auto_run_next)

        elif action == "herbalist":
            self._auto_queue_herbalist_visit()

        elif action == "catalog":
            self._auto_process_catalog()

        elif action == "nav":
            # Use existing pathfind system; resume AUTO queue when arrived
            dest = int(value)
            if self._current_room_id == dest:
                self.root.after(50, self._auto_run_next)
                return
            path = self.graph.find_path(self._current_room_id, dest)
            if not path:
                self._wound_status(f"AUTO: can't path to room {dest}.")
                self._auto_done()
                return
            # Inject path steps directly into _pathfind_steps and hook completion
            self._pathfind_steps = path
            self._auto_waiting_nav = True
            self._do_next_step()
            # _auto_nav_arrived() called from _do_next_step's completion handler
            self._auto_nav_resume_fn = self._auto_run_next

        elif action == "done":
            self._send("wounds")
            self._wound_status("AUTO: all done! Wounds and scars treated.")
            self._auto_done()

    def _auto_nav_arrived(self):
        """Called when pathfinding completes during AUTO mode."""
        if getattr(self, "_auto_waiting_nav", False):
            self._auto_waiting_nav = False
            fn = getattr(self, "_auto_nav_resume_fn", None)
            if fn:
                self.root.after(400, fn)

    def _auto_done(self):
        self._auto_healing = False
        if hasattr(self, "_auto_cmd_queue"):
            del self._auto_cmd_queue
        self._auto_ctx = {}
        self._auto_waiting_nav = False
        self._auto_nav_resume_fn = None
        if hasattr(self, "_auto_heal_btn"):
            self._auto_heal_btn.config(text="⚕ AUTO Heal", state="normal")

    # ════════════════════════════════════════════
    # Text widget color tags
    # ════════════════════════════════════════════

    def _setup_tags(self):
        self._apply_font_tags()

    def _apply_font_tags(self):
        """(Re-)configure all text widget tags using current _font_size / _game_font."""
        fn = (self._game_font, self._font_size)
        for code, hexcol in ANSI_COLORS.items():
            self._text.tag_configure(f"c_{hexcol.lstrip('#')}", foreground=hexcol, font=fn)
        for _, hexcol in BOLD_UPGRADES.items():
            self._text.tag_configure(f"c_{hexcol.lstrip('#')}", foreground=hexcol, font=fn)
        self._text.tag_configure("dim",     foreground=TEXT_DIM,    font=fn)
        self._text.tag_configure("sys",     foreground=ACCENT_BLUE, font=fn)
        self._text.tag_configure("prompt",  foreground=TEXT_DIM,    font=fn)
        self._text.tag_configure("err",     foreground=ACCENT_RED,  font=fn)
        self._text.tag_configure("path",    foreground=ACCENT_GRN,  font=fn)
        self._text.tag_configure("default", foreground=TEXT_MAIN,   font=fn)
        self._text.tag_configure("exit_link", foreground=ACCENT_CYN,
                                 font=(self._game_font, self._font_size, "underline"),
                                 underline=True)
        self._text.tag_configure("ask",     foreground=ACCENT_YEL,
                                 font=(self._game_font, self._font_size, "bold"))
        self._text.config(font=fn)

    def _show_settings_dialog(self):
        """⚙ Settings — font, size, panel font size."""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=BG_APP)
        win.resizable(False, False)
        win.grab_set()

        fg   = TEXT_MAIN
        dim  = TEXT_DIM
        sf   = ("Georgia", 10)
        sbf  = ("Georgia", 10, "bold")

        tk.Label(win, text="⚙  Display Settings", fg=ACCENT_BLUE, bg=BG_APP,
                 font=("Georgia", 13, "bold")).pack(padx=24, pady=(16, 8))

        # ── Game text font ───────────────────────────────────────────────────
        tk.Label(win, text="Game text font:", fg=dim, bg=BG_APP, font=sf)\
            .pack(anchor="w", padx=24)
        font_var = tk.StringVar(value=self._game_font)
        font_choices = ["Georgia", "Palatino Linotype", "Book Antiqua",
                        "Garamond", "Cambria", "Courier New", "Consolas",
                        "Lucida Console", "Times New Roman"]
        font_cb = ttk.Combobox(win, textvariable=font_var, values=font_choices,
                               state="readonly", width=24, font=sf)
        font_cb.pack(padx=24, pady=(2, 10), fill="x")

        # ── Game text size ───────────────────────────────────────────────────
        tk.Label(win, text="Game text size:", fg=dim, bg=BG_APP, font=sf)\
            .pack(anchor="w", padx=24)
        size_frame = tk.Frame(win, bg=BG_APP)
        size_frame.pack(padx=24, pady=(2, 10), fill="x")
        size_var = tk.IntVar(value=self._font_size)
        size_lbl = tk.Label(size_frame, textvariable=size_var,
                            fg=TEXT_MAIN, bg=BG_APP, font=sbf, width=3)
        size_lbl.pack(side="right")
        tk.Button(size_frame, text="A−", fg=dim, bg=BG_INPUT, font=sf,
                  relief="flat", bd=0, padx=6,
                  command=lambda: size_var.set(max(6, size_var.get()-1))
                  ).pack(side="left", padx=(0, 2))
        tk.Scale(size_frame, from_=8, to=28, orient="horizontal",
                 variable=size_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True)
        tk.Button(size_frame, text="A+", fg=fg, bg=BG_INPUT, font=sf,
                  relief="flat", bd=0, padx=6,
                  command=lambda: size_var.set(min(28, size_var.get()+1))
                  ).pack(side="left", padx=(2, 4))

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=8)

        # ── Panel font size ──────────────────────────────────────────────────
        tk.Label(win, text="Panel font size (EXP / Status / Room / Map labels):",
                 fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        psz_frame = tk.Frame(win, bg=BG_APP)
        psz_frame.pack(padx=24, pady=(2, 12), fill="x")
        psz_var = tk.IntVar(value=self._panel_font_size)
        psz_lbl = tk.Label(psz_frame, textvariable=psz_var,
                           fg=TEXT_MAIN, bg=BG_APP, font=sbf, width=3)
        psz_lbl.pack(side="right")
        tk.Scale(psz_frame, from_=8, to=18, orient="horizontal",
                 variable=psz_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True, padx=(0, 4))

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=8)

        # ── Auto-Login ───────────────────────────────────────────────────────
        tk.Label(win, text="Auto-Login", fg=ACCENT_BLUE, bg=BG_APP,
                 font=(self._game_font, 10, "bold")).pack(anchor="w", padx=24, pady=(0, 4))

        al_enabled_var = tk.BooleanVar(value=self._auto_login_enabled)
        tk.Checkbutton(win, text="Enable auto-login on connect",
                       variable=al_enabled_var,
                       fg=TEXT_MAIN, bg=BG_APP, selectcolor=BG_INPUT,
                       activebackground=BG_APP, activeforeground=TEXT_MAIN,
                       font=sf).pack(anchor="w", padx=24, pady=(0, 6))

        tk.Label(win, text="Username:", fg=dim, bg=BG_APP, font=sf)\
            .pack(anchor="w", padx=24)
        al_user_var = tk.StringVar(value=self._auto_login_username)
        tk.Entry(win, textvariable=al_user_var, bg=BG_INPUT, fg=TEXT_MAIN,
                 font=sf, insertbackground=ACCENT_BLUE, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT_BLUE,
                 highlightbackground=BORDER_CLR, width=28)\
            .pack(padx=24, pady=(2, 6), ipady=3, fill="x")

        tk.Label(win, text="Password:", fg=dim, bg=BG_APP, font=sf)\
            .pack(anchor="w", padx=24)
        al_pass_var = tk.StringVar(value=self._auto_login_password)
        tk.Entry(win, textvariable=al_pass_var, show="*", bg=BG_INPUT, fg=TEXT_MAIN,
                 font=sf, insertbackground=ACCENT_BLUE, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT_BLUE,
                 highlightbackground=BORDER_CLR, width=28)\
            .pack(padx=24, pady=(2, 6), ipady=3, fill="x")

        tk.Label(win, text="Character slot (1, 2, 3…):", fg=dim, bg=BG_APP, font=sf)\
            .pack(anchor="w", padx=24)
        al_slot_var = tk.IntVar(value=self._auto_login_char_slot)
        tk.Spinbox(win, from_=1, to=9, textvariable=al_slot_var,
                   bg=BG_INPUT, fg=TEXT_MAIN, buttonbackground=BG_INPUT,
                   font=sf, bd=0, highlightthickness=1,
                   highlightcolor=ACCENT_BLUE, highlightbackground=BORDER_CLR,
                   width=4).pack(anchor="w", padx=24, pady=(2, 8), ipady=3)

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_row = tk.Frame(win, bg=BG_APP)
        btn_row.pack(fill="x", padx=24, pady=(4, 16))

        def _apply():
            self._game_font      = font_var.get()
            self._font_size      = size_var.get()
            self._panel_font_size = psz_var.get()
            self._auto_login_enabled   = al_enabled_var.get()
            self._auto_login_username  = al_user_var.get().strip()
            self._auto_login_password  = al_pass_var.get()
            self._auto_login_char_slot = max(1, al_slot_var.get())
            self._apply_font_tags()
            self._apply_panel_fonts()
            self._save_config()
            win.destroy()

        def _reset():
            font_var.set("Georgia")
            size_var.set(14)
            psz_var.set(11)

        tk.Button(btn_row, text="Apply", fg=fg, bg="#0d2a0d",
                  font=("Georgia", 10, "bold"), relief="flat", bd=0,
                  padx=14, pady=6, activebackground="#1a4a1a",
                  command=_apply).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Reset Defaults", fg=dim, bg=BG_INPUT,
                  font=sf, relief="flat", bd=0, padx=10, pady=5,
                  activebackground=BORDER_CLR,
                  command=_reset).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Cancel", fg=dim, bg=BG_INPUT,
                  font=sf, relief="flat", bd=0, padx=10, pady=5,
                  activebackground=BORDER_CLR,
                  command=win.destroy).pack(side="left")

        win.bind("<Return>", lambda _: _apply())

    def _show_settings_dialog(self):
        """Settings dialog for display, auto-login, and audio."""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=BG_APP)
        win.resizable(False, False)
        win.grab_set()

        fg = TEXT_MAIN
        dim = TEXT_DIM
        sf = ("Georgia", 10)
        sbf = ("Georgia", 10, "bold")

        tk.Label(win, text="Settings", fg=ACCENT_BLUE, bg=BG_APP,
                 font=("Georgia", 13, "bold")).pack(padx=24, pady=(16, 8))

        tk.Label(win, text="Game text font:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        font_var = tk.StringVar(value=self._game_font)
        font_choices = ["Georgia", "Palatino Linotype", "Book Antiqua",
                        "Garamond", "Cambria", "Courier New", "Consolas",
                        "Lucida Console", "Times New Roman"]
        ttk.Combobox(win, textvariable=font_var, values=font_choices,
                     state="readonly", width=24, font=sf).pack(padx=24, pady=(2, 10), fill="x")

        tk.Label(win, text="Game text size:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        size_frame = tk.Frame(win, bg=BG_APP)
        size_frame.pack(padx=24, pady=(2, 10), fill="x")
        size_var = tk.IntVar(value=self._font_size)
        tk.Label(size_frame, textvariable=size_var, fg=TEXT_MAIN, bg=BG_APP, font=sbf, width=3).pack(side="right")
        tk.Button(size_frame, text="A-", fg=dim, bg=BG_INPUT, font=sf,
                  relief="flat", bd=0, padx=6,
                  command=lambda: size_var.set(max(6, size_var.get()-1))
                  ).pack(side="left", padx=(0, 2))
        tk.Scale(size_frame, from_=8, to=28, orient="horizontal",
                 variable=size_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True)
        tk.Button(size_frame, text="A+", fg=fg, bg=BG_INPUT, font=sf,
                  relief="flat", bd=0, padx=6,
                  command=lambda: size_var.set(min(28, size_var.get()+1))
                  ).pack(side="left", padx=(2, 4))

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=8)

        tk.Label(win, text="Panel font size (EXP / Status / Room / Map labels):",
                 fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        psz_frame = tk.Frame(win, bg=BG_APP)
        psz_frame.pack(padx=24, pady=(2, 12), fill="x")
        psz_var = tk.IntVar(value=self._panel_font_size)
        tk.Label(psz_frame, textvariable=psz_var, fg=TEXT_MAIN, bg=BG_APP, font=sbf, width=3).pack(side="right")
        tk.Scale(psz_frame, from_=8, to=18, orient="horizontal",
                 variable=psz_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True, padx=(0, 4))

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=8)

        tk.Label(win, text="Auto-Login", fg=ACCENT_BLUE, bg=BG_APP,
                 font=(self._game_font, 10, "bold")).pack(anchor="w", padx=24, pady=(0, 4))
        al_enabled_var = tk.BooleanVar(value=self._auto_login_enabled)
        tk.Checkbutton(win, text="Enable auto-login on connect",
                       variable=al_enabled_var,
                       fg=TEXT_MAIN, bg=BG_APP, selectcolor=BG_INPUT,
                       activebackground=BG_APP, activeforeground=TEXT_MAIN,
                       font=sf).pack(anchor="w", padx=24, pady=(0, 6))

        tk.Label(win, text="Username:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        al_user_var = tk.StringVar(value=self._auto_login_username)
        tk.Entry(win, textvariable=al_user_var, bg=BG_INPUT, fg=TEXT_MAIN,
                 font=sf, insertbackground=ACCENT_BLUE, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT_BLUE,
                 highlightbackground=BORDER_CLR, width=28).pack(padx=24, pady=(2, 6), ipady=3, fill="x")

        tk.Label(win, text="Password:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        al_pass_var = tk.StringVar(value=self._auto_login_password)
        tk.Entry(win, textvariable=al_pass_var, show="*", bg=BG_INPUT, fg=TEXT_MAIN,
                 font=sf, insertbackground=ACCENT_BLUE, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT_BLUE,
                 highlightbackground=BORDER_CLR, width=28).pack(padx=24, pady=(2, 6), ipady=3, fill="x")

        tk.Label(win, text="Character slot (1, 2, 3...):", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        al_slot_var = tk.IntVar(value=self._auto_login_char_slot)
        tk.Spinbox(win, from_=1, to=9, textvariable=al_slot_var,
                   bg=BG_INPUT, fg=TEXT_MAIN, buttonbackground=BG_INPUT,
                   font=sf, bd=0, highlightthickness=1,
                   highlightcolor=ACCENT_BLUE, highlightbackground=BORDER_CLR,
                   width=4).pack(anchor="w", padx=24, pady=(2, 8), ipady=3)

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=8)

        tk.Label(win, text="Audio Settings", fg=ACCENT_BLUE, bg=BG_APP,
                 font=(self._game_font, 10, "bold")).pack(anchor="w", padx=24, pady=(0, 4))
        music_enabled_var = tk.BooleanVar(value=self._music_enabled)
        sfx_enabled_var = tk.BooleanVar(value=self._sfx_enabled)
        tk.Checkbutton(win, text="Enable music",
                       variable=music_enabled_var,
                       fg=TEXT_MAIN, bg=BG_APP, selectcolor=BG_INPUT,
                       activebackground=BG_APP, activeforeground=TEXT_MAIN,
                       font=sf).pack(anchor="w", padx=24, pady=(0, 4))
        tk.Checkbutton(win, text="Enable sound effects",
                       variable=sfx_enabled_var,
                       fg=TEXT_MAIN, bg=BG_APP, selectcolor=BG_INPUT,
                       activebackground=BG_APP, activeforeground=TEXT_MAIN,
                       font=sf).pack(anchor="w", padx=24, pady=(0, 8))

        tk.Label(win, text="Music volume:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        music_vol_var = tk.IntVar(value=self._music_volume)
        music_frame = tk.Frame(win, bg=BG_APP)
        music_frame.pack(padx=24, pady=(2, 8), fill="x")
        tk.Scale(music_frame, from_=0, to=100, orient="horizontal",
                 variable=music_vol_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True)
        tk.Label(music_frame, textvariable=music_vol_var, fg=TEXT_MAIN,
                 bg=BG_APP, font=sbf, width=4).pack(side="right", padx=(8, 0))

        tk.Label(win, text="SFX volume:", fg=dim, bg=BG_APP, font=sf).pack(anchor="w", padx=24)
        sfx_vol_var = tk.IntVar(value=self._sfx_volume)
        sfx_frame = tk.Frame(win, bg=BG_APP)
        sfx_frame.pack(padx=24, pady=(2, 8), fill="x")
        tk.Scale(sfx_frame, from_=0, to=100, orient="horizontal",
                 variable=sfx_vol_var, bg=BG_APP, fg=fg,
                 troughcolor=BG_INPUT, highlightthickness=0,
                 showvalue=False).pack(side="left", fill="x", expand=True)
        tk.Label(sfx_frame, textvariable=sfx_vol_var, fg=TEXT_MAIN,
                 bg=BG_APP, font=sbf, width=4).pack(side="right", padx=(8, 0))

        btn_row = tk.Frame(win, bg=BG_APP)
        btn_row.pack(fill="x", padx=24, pady=(4, 16))

        def _apply():
            self._game_font = font_var.get()
            self._font_size = size_var.get()
            self._panel_font_size = psz_var.get()
            self._auto_login_enabled = al_enabled_var.get()
            self._auto_login_username = al_user_var.get().strip()
            self._auto_login_password = al_pass_var.get()
            self._auto_login_char_slot = max(1, al_slot_var.get())
            self._music_enabled = music_enabled_var.get()
            self._sfx_enabled = sfx_enabled_var.get()
            self._music_volume = max(0, min(100, music_vol_var.get()))
            self._sfx_volume = max(0, min(100, sfx_vol_var.get()))
            self._apply_font_tags()
            self._apply_panel_fonts()
            if self._audio:
                self._audio.apply_settings(
                    music_enabled=self._music_enabled,
                    music_volume=self._music_volume,
                    sfx_enabled=self._sfx_enabled,
                    sfx_volume=self._sfx_volume,
                )
            self._save_config()
            win.destroy()

        def _reset():
            font_var.set("Georgia")
            size_var.set(14)
            psz_var.set(11)
            music_enabled_var.set(True)
            sfx_enabled_var.set(True)
            music_vol_var.set(65)
            sfx_vol_var.set(75)

        tk.Button(btn_row, text="Apply", fg=fg, bg="#0d2a0d",
                  font=("Georgia", 10, "bold"), relief="flat", bd=0,
                  padx=14, pady=6, activebackground="#1a4a1a",
                  command=_apply).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Reset Defaults", fg=dim, bg=BG_INPUT,
                  font=sf, relief="flat", bd=0, padx=10, pady=5,
                  activebackground=BORDER_CLR,
                  command=_reset).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Cancel", fg=dim, bg=BG_INPUT,
                  font=sf, relief="flat", bd=0, padx=10, pady=5,
                  activebackground=BORDER_CLR,
                  command=win.destroy).pack(side="left")

        win.bind("<Return>", lambda _: _apply())

    def _apply_panel_fonts(self):
        """Update all panel label fonts to current _panel_font_size."""
        psz = self._panel_font_size
        pf  = ("Courier New", psz)
        pbf = ("Courier New", psz, "bold")
        try:
            self._exp_lvl_lbl.config(font=pf)
            self._exp_total_lbl.config(font=pf)
            self._exp_tnl_lbl.config(font=pf)
            self._mind_lbl.config(font=pbf)
            if hasattr(self, "_room_name_lbl"):
                self._room_name_lbl.config(font=pbf)
            if hasattr(self, "_room_id_lbl"):
                self._room_id_lbl.config(font=pf)
            if hasattr(self, "_room_zone_lbl"):
                self._room_zone_lbl.config(font=pf)
            self._ptp_lbl.config(font=pf)
            self._mtp_lbl.config(font=pf)
        except Exception:
            pass

    def _resize_text(self, delta: int, reset: bool = False):
        if reset:
            self._font_size = 14
        else:
            self._font_size = max(6, min(28, self._font_size + delta))
        self._apply_font_tags()

    def _change_font(self, family: str):
        self._game_font = family
        self._apply_font_tags()

    def _color_tag(self, hexcol: Optional[str]) -> str:
        if hexcol is None:
            return "default"
        return f"c_{hexcol.lstrip('#')}"

    # ════════════════════════════════════════════
    # Text output
    # ════════════════════════════════════════════

    def _text_should_follow(self) -> bool:
        """Auto-follow only when the player is already near the bottom."""
        try:
            _top, bottom = self._text.yview()
            return bottom >= 0.98
        except Exception:
            return True

    def _text_follow_if_needed(self, should_follow: bool):
        if should_follow:
            self._text.see("end")

    def _append_exits_line(self, raw: str, live_exits: Dict[str, int]):
        """
        Render the 'Obvious paths/exits: …' line so every direction that
        has a known room-id is a clickable hyperlink that sends that direction.
        """
        # Strip ANSI to get the plain text, then re-render with links.
        clean = re.sub(r'\x1b\[[0-9;]*m', '', raw)

        should_follow = self._text_should_follow()
        self._text.config(state="normal")
        # Render the label part ("Obvious paths: ") in cyan
        m = EXITS_RE.match(clean)
        if m:
            label_end = m.start(1)   # index where the exit list starts
            self._text.insert("end", clean[:label_end], "c_" + ACCENT_CYN.lstrip("#"))
            # Now insert each exit, making known ones clickable
            parts = clean[label_end:].rstrip(".")
            tokens = [p.strip() for p in parts.split(",") if p.strip()]
            for i, token in enumerate(tokens):
                key = token.lower()
                if key in live_exits or key in {"north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down", "out"}:
                    # Unique tag for this exit occurrence
                    safe_key = re.sub(r"[^a-z0-9_]+", "_", key)
                    tag_name = f"{self._new_inline_tag('exit')}_{safe_key}_{i}"
                    self._text.tag_configure(tag_name,
                                             foreground=ACCENT_CYN,
                                             font=("Courier New", self._font_size, "underline"),
                                             underline=True)
                    # live_exits[key] = (target_room_id, cmd_to_send) or legacy int
                    val = live_exits.get(key)
                    cmd_to_send = val[1] if isinstance(val, tuple) else key
                    def _make_cmd(cmd=cmd_to_send):
                        return lambda _e: (self._send(cmd),
                                           self._append(f"> {cmd}\n", "prompt"))
                    self._text.tag_bind(tag_name, "<Button-1>", _make_cmd())
                    self._text.tag_bind(tag_name, "<Enter>",
                                        lambda _e, t=tag_name: self._text.config(cursor="hand2"))
                    self._text.tag_bind(tag_name, "<Leave>",
                                        lambda _e: self._text.config(cursor=""))
                    self._text.insert("end", token, tag_name)
                else:
                    self._text.insert("end", token, "c_" + ACCENT_CYN.lstrip("#"))
                if i < len(tokens) - 1:
                    self._text.insert("end", ", ", "c_" + ACCENT_CYN.lstrip("#"))
        else:
            # Fallback: render as normal colored line
            for chunk, color in parse_ansi(raw):
                self._text.insert("end", chunk, self._color_tag(color))

        self._text.insert("end", "\n", "default")
        self._text.config(state="disabled")
        self._text_follow_if_needed(should_follow)

    def _append_menu_line(self, raw: str, context: str, cmds_str: str):
        """
        Render a bracketed command menu like:
          [Bank: CHECK BALANCE, DEPOSIT {#|ALL|NOTE}, WITHDRAW {#} [NOTE]]

        Each base command is a clickable link.
        Each option inside {a|b|c} or [opt] is also individually clickable:
          - '#' prefills the input box with "base_cmd " so the user just types the number
          - any word option sends "base_cmd option" immediately
        """
        # ── split top-level tokens by comma ──────────────────────────────
        tokens = []
        depth = 0
        cur = ""
        for ch in cmds_str:
            if ch in "{[":
                depth += 1
                cur += ch
            elif ch in "}]":
                depth -= 1
                cur += ch
            elif ch == "," and depth == 0:
                tokens.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            tokens.append(cur.strip())

        should_follow = self._text_should_follow()
        self._text.config(state="normal")
        self._text.insert("end", f"[{context}: ", "dim")

        # ── helper: make a unique tag name ────────────────────────────────
        _seq = [0]
        def _newtag():
            _seq[0] += 1
            return f"_menu_{_seq[0]}"

        # ── helper: bind a clickable link ─────────────────────────────────
        def _link(display: str, cmd: str, prefill: bool = False):
            """Insert `display` as a clickable span.
            If prefill=True, put `cmd` in the entry box (ready to type more).
            Otherwise send `cmd` immediately.
            """
            tn = _newtag()
            self._text.tag_configure(tn, foreground=ACCENT_CYN,
                font=(self._game_font, self._font_size, "underline"), underline=True)
            if prefill:
                def _act(_e, c=cmd):
                    self._entry_var.set(c)
                    self._entry.icursor("end")
                    self._entry.focus_set()
            else:
                def _act(_e, c=cmd):
                    self._send(c)
                    self._append(f"> {c}\n", "prompt")
            self._text.tag_bind(tn, "<Button-1>", _act)
            self._text.tag_bind(tn, "<Enter>",
                lambda _e: self._text.config(cursor="hand2"))
            self._text.tag_bind(tn, "<Leave>",
                lambda _e: self._text.config(cursor=""))
            self._text.insert("end", display, tn)

        # ── process each token ────────────────────────────────────────────
        # Token grammar (rough):
        #   BASE_WORDS  ( '{' OPT '|' OPT ... '}' | '[' OPT ']' )*
        import re as _re
        OPTION_GROUP = _re.compile(r'\{([^}]+)\}|\[([^\]]+)\]')

        for ti, token in enumerate(tokens):
            # Base command = text before first { or [
            base_cmd = _re.split(r'[{\[]', token)[0].strip().lower()

            # Render base command as a link
            _link(base_cmd.upper(), base_cmd)

            # Find all option groups  {a|b|c}  or  [opt]
            for gm in OPTION_GROUP.finditer(token):
                inner = gm.group(1) or gm.group(2)   # group(1)=curly, group(2)=square
                opts  = [o.strip() for o in inner.split("|")]
                optional = gm.group(2) is not None    # square bracket = optional

                self._text.insert("end", " (", "dim")
                for oi, opt in enumerate(opts):
                    if opt == "#":
                        # Prefill entry with "base_cmd "
                        _link("#", base_cmd + " ", prefill=True)
                    else:
                        full_cmd = f"{base_cmd} {opt.lower()}"
                        _link(opt, full_cmd)
                    if oi < len(opts) - 1:
                        self._text.insert("end", "|", "dim")
                close = ")" if not optional else "?)"
                self._text.insert("end", close, "dim")

            if ti < len(tokens) - 1:
                self._text.insert("end", ",  ", "dim")

        self._text.insert("end", "]\n", "dim")
        self._text.config(state="disabled")
        self._text_follow_if_needed(should_follow)

    def _append_line(self, line: str):
        """Append a parsed ANSI line, making item names and actionable NPC names clickable."""
        segments = parse_ansi(line)
        should_follow = self._text_should_follow()
        self._text.config(state="normal")

        # ITEM_NAME color = YELLOW (ANSI 33) → hex #aaaa33
        ITEM_HEX = "aaaa33"

        for chunk, color in segments:
            tag = self._color_tag(color)
            col_key = (color or "").lstrip("#").lower()

            if col_key == ITEM_HEX and chunk.strip():
                # Yellow item name — derive key from chunk and look up directly.
                # Server now sends clean names (no leading articles), so
                # _item_key(chunk) matches the stored key reliably.
                chunk_key = self._item_key(chunk)

                matched_key = None
                matched_score = -1
                matched_len = -1
                for key, info in self._known_items.items():
                    candidate_key = info.get("match_key") or key
                    if not candidate_key:
                        continue
                    score = -1
                    if candidate_key == chunk_key:
                        score = 300
                    elif candidate_key in chunk_key:
                        score = 200
                    elif chunk_key in candidate_key:
                        score = 100
                    if score < 0:
                        continue
                    if info.get("state") == "shop":
                        score += 50
                    if score > matched_score or (score == matched_score and len(candidate_key) > matched_len):
                        matched_key = key
                        matched_score = score
                        matched_len = len(candidate_key)

                if matched_key:
                    tn = f"_item_{matched_key.replace(' ','_')}_{id(chunk)}"
                    self._text.tag_configure(tn, foreground="#" + ITEM_HEX,
                                             font=(self._game_font, self._font_size),
                                             underline=True)
                    self._text.tag_bind(tn, "<Button-1>",
                        lambda e, k=matched_key: self._show_item_menu(e, k))
                    self._text.tag_bind(tn, "<Enter>",
                        lambda _e: self._text.config(cursor="hand2"))
                    self._text.tag_bind(tn, "<Leave>",
                        lambda _e: self._text.config(cursor=""))
                    self._text.insert("end", chunk, tn)
                    continue
            self._insert_chunk_with_npc_links(chunk, tag)

        self._text.insert("end", "\n", "default")
        self._text.config(state="disabled")
        self._text_follow_if_needed(should_follow)

    def _insert_chunk_with_npc_links(self, chunk: str, base_tag: str):
        if not chunk or not self._room_npcs:
            self._text.insert("end", chunk, base_tag)
            return

        idx = 0
        while idx < len(chunk):
            best = None
            best_npc = None
            for npc in self._room_npcs:
                for pat in npc.get("patterns", []):
                    m = pat.search(chunk, idx)
                    if not m:
                        continue
                    if best is None or m.start() < best.start() or (m.start() == best.start() and len(m.group(1)) > len(best.group(1))):
                        best = m
                        best_npc = npc
            if best is None or best_npc is None:
                self._text.insert("end", chunk[idx:], base_tag)
                return

            if best.start() > idx:
                self._text.insert("end", chunk[idx:best.start()], base_tag)

            self._insert_npc_link(best.group(1), base_tag, best_npc)
            idx = best.end()

    def _new_inline_tag(self, prefix: str) -> str:
        self._npc_link_seq += 1
        return f"_{prefix}_{self._npc_link_seq}"

    def _bind_npc_tags(self, tag_name: str, marker_tag: str, npc_info: dict):
        def _open_menu(event, info=npc_info):
            self._show_npc_menu(event, info)

        for tn in (tag_name, marker_tag):
            self._text.tag_bind(tn, "<Button-1>", _open_menu)
            self._text.tag_bind(tn, "<Enter>", lambda _e: self._text.config(cursor="hand2"))
            self._text.tag_bind(tn, "<Leave>", lambda _e: self._text.config(cursor=""))

    def _insert_npc_link(self, display_text: str, base_tag: str, npc_info: dict):
        tag_name = self._new_inline_tag("npc")
        marker_tag = self._new_inline_tag("npcm")

        self._text.tag_configure(
            tag_name,
            foreground=self._text.tag_cget(base_tag, "foreground") or TEXT_MAIN,
            font=self._text.tag_cget(base_tag, "font") or (self._game_font, self._font_size),
        )
        self._text.tag_configure(
            marker_tag,
            foreground=ACCENT_CYN,
            font=(self._game_font, self._font_size),
        )
        self._bind_npc_tags(tag_name, marker_tag, npc_info)

        self._text.insert("end", display_text, (base_tag, tag_name))
        marker = str(npc_info.get("marker") or "")
        if marker:
            self._text.insert("end", marker, marker_tag)

    def _decorate_visible_npc_links(self):
        if not self._room_npcs:
            return

        start = getattr(self, "_room_start_index", "1.0") or "1.0"
        end = self._text.index("end-1c")
        if self._text.compare(start, ">=", end):
            return

        should_follow = self._text_should_follow()
        self._text.config(state="normal")
        try:
            for npc_info in self._room_npcs:
                aliases = sorted(
                    [str(a or "") for a in npc_info.get("aliases", []) if str(a or "").strip()],
                    key=len,
                    reverse=True,
                )
                for alias in aliases:
                    search_at = start
                    while True:
                        match_at = self._text.search(alias, search_at, stopindex=end, nocase=True)
                        if not match_at:
                            break

                        match_end = self._text.index(f"{match_at}+{len(alias)}c")
                        before = self._text.get(f"{match_at}-1c", match_at) if self._text.compare(match_at, ">", "1.0") else ""
                        after = self._text.get(match_end, f"{match_end}+1c")
                        if ((before and (before[-1].isalnum() or before[-1] == "_")) or
                                (after and (after[0].isalnum() or after[0] == "_"))):
                            search_at = self._text.index(f"{match_at}+1c")
                            continue

                        existing_tags = self._text.tag_names(match_at)
                        if any(tag.startswith("_npc_") for tag in existing_tags):
                            search_at = match_end
                            continue

                        tag_name = self._new_inline_tag("npc")
                        marker_tag = self._new_inline_tag("npcm")
                        self._text.tag_configure(tag_name, underline=False)
                        self._text.tag_configure(
                            marker_tag,
                            foreground=ACCENT_CYN,
                            font=(self._game_font, self._font_size),
                        )
                        self._bind_npc_tags(tag_name, marker_tag, npc_info)
                        self._text.tag_add(tag_name, match_at, match_end)

                        marker = str(npc_info.get("marker") or "")
                        if marker:
                            following = self._text.get(match_end, f"{match_end}+{len(marker)}c")
                            if following != marker:
                                self._text.insert(match_end, marker, marker_tag)
                                end = self._text.index("end-1c")

                        search_at = self._text.index(f"{match_end}+1c")
        finally:
            self._text.config(state="disabled")
            self._text_follow_if_needed(should_follow)

    def _apply_npc_action(self, action: dict):
        cmd = str(action.get("command") or "").strip()
        if not cmd:
            return
        if action.get("prefill"):
            self._entry_var.set(cmd)
            self._entry.icursor("end")
            self._entry.focus_set()
            return
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    def _show_npc_menu(self, event, npc_info: dict):
        actions = npc_info.get("actions") or []
        if not actions:
            return

        menu = tk.Menu(self.root, tearoff=0, bg="#1a1e26", fg=TEXT_MAIN,
                       font=(self._game_font, 10),
                       activebackground="#2a3a5a",
                       activeforeground=TEXT_MAIN,
                       relief="flat", bd=1)

        title = str(npc_info.get("display") or npc_info.get("name") or "NPC").strip()
        menu.add_command(label=title, state="disabled")
        menu.add_separator()

        for action in actions:
            label = str(action.get("label") or action.get("command") or "").strip()
            if not label:
                continue
            menu.add_command(label=label, command=lambda a=action: self._apply_npc_action(a))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    def _append(self, text: str, tag: str = "default"):
        should_follow = self._text_should_follow()
        self._text.config(state="normal")
        self._text.insert("end", text, tag)
        self._text.config(state="disabled")
        self._text_follow_if_needed(should_follow)

    def _sys(self, msg: str):
        self._append(f"[{msg}]\n", "sys")

    # ════════════════════════════════════════════
    # Connection
    # ════════════════════════════════════════════


    def _start_sync(self, token: str, port: int):
        """Called when the server sends the SYNC control line on login."""
        if not _SYNC_AVAILABLE:
            return
        # Stop any existing sync connection first
        self._stop_sync()
        self._sync = SyncClient(self.host, port, self.sync_q)
        self._sync.connect(token)

    def _stop_sync(self):
        """Tear down the sync connection (called on HUD disconnect)."""
        if self._sync:
            self._sync.stop()
            self._sync = None
        self._sync_connected = False

    def _connect(self):
        self._sys(f"Connecting to {self.host}:{self.port}…")
        self._conn_btn.config(text="● Connecting…", bg="#2a2a0a", fg=ACCENT_YEL,
                              state="disabled")
        self._conn_status.config(text=f"{self.host}:{self.port}")
        self._telnet = TelnetThread(self.host, self.port, self.rx_q)
        self._telnet.start()

    def _disconnect(self):
        if self._telnet:
            self._telnet.stop()
            self._telnet = None
        self._conn_btn.config(text="⚡ Connect", bg="#0d2a0d", fg=ACCENT_GRN,
                              state="normal", activebackground="#1a4a1a")
        self._conn_status.config(text="Disconnected", fg=ACCENT_RED)
        self._sys("Disconnected.")

    def _show_connect_dialog(self):
        """Pop up the Connect / server-picker dialog."""
        # If connected, offer to disconnect instead
        if self._telnet and self._telnet._running:
            self._disconnect()
            return

        win = tk.Toplevel(self.root)
        win.title("Connect to Server")
        win.configure(bg=BG_APP)
        win.resizable(False, False)
        win.grab_set()

        fg    = TEXT_MAIN
        dim   = TEXT_DIM
        gfont = (self._game_font, 10)
        sfont = (self._game_font, 9)

        tk.Label(win, text="GemStone IV — Connect", fg=ACCENT_BLUE, bg=BG_APP,
                 font=(self._game_font, 13, "bold")).pack(padx=24, pady=(16, 4))

        # ── Saved servers dropdown ──────────────────────────────────────────
        saved = self._saved_servers  # list of {"label","host","port"}
        if saved:
            tk.Label(win, text="Saved servers:", fg=dim, bg=BG_APP, font=sfont)\
                .pack(anchor="w", padx=24, pady=(8, 0))
            srv_var = tk.StringVar()
            labels  = [s["label"] for s in saved]
            srv_cb  = ttk.Combobox(win, textvariable=srv_var, values=labels,
                                   state="readonly", width=30, font=sfont)
            srv_cb.pack(padx=24, pady=(2, 0), fill="x")

            def _on_saved_select(_e=None):
                label = srv_var.get()
                for s in saved:
                    if s["label"] == label:
                        host_var.set(s["host"])
                        port_var.set(str(s["port"]))
                        break
            srv_cb.bind("<<ComboboxSelected>>", _on_saved_select)

            # Pre-select current server if it matches
            cur_label = f"{self.host}:{self.port}"
            for s in saved:
                if s["host"] == self.host and s["port"] == self.port:
                    srv_var.set(s["label"])
                    break
            else:
                srv_var.set(labels[0])
                _on_saved_select()

        sep = tk.Frame(win, bg=BORDER_CLR, height=1)
        sep.pack(fill="x", padx=16, pady=10)

        # ── Manual entry ───────────────────────────────────────────────────
        tk.Label(win, text="Host / IP address:", fg=dim, bg=BG_APP, font=sfont)\
            .pack(anchor="w", padx=24)
        host_var = tk.StringVar(value=self.host)
        host_entry = tk.Entry(win, textvariable=host_var, bg=BG_INPUT, fg=fg,
                              font=gfont, insertbackground=ACCENT_BLUE,
                              bd=0, highlightthickness=1,
                              highlightcolor=ACCENT_BLUE,
                              highlightbackground=BORDER_CLR, width=30)
        host_entry.pack(padx=24, pady=(2, 8), ipady=4, fill="x")

        tk.Label(win, text="Port:", fg=dim, bg=BG_APP, font=sfont)\
            .pack(anchor="w", padx=24)
        port_var = tk.StringVar(value=str(self.port))
        port_entry = tk.Entry(win, textvariable=port_var, bg=BG_INPUT, fg=fg,
                              font=gfont, insertbackground=ACCENT_BLUE,
                              bd=0, highlightthickness=1,
                              highlightcolor=ACCENT_BLUE,
                              highlightbackground=BORDER_CLR, width=10)
        port_entry.pack(padx=24, pady=(2, 0), ipady=4)

        # ── Save-as-label option ───────────────────────────────────────────
        tk.Label(win, text="Save as (leave blank to not save):", fg=dim, bg=BG_APP,
                 font=sfont).pack(anchor="w", padx=24, pady=(12, 0))
        save_var = tk.StringVar()
        tk.Entry(win, textvariable=save_var, bg=BG_INPUT, fg=fg,
                 font=sfont, insertbackground=ACCENT_BLUE,
                 bd=0, highlightthickness=1, highlightcolor=ACCENT_BLUE,
                 highlightbackground=BORDER_CLR, width=30)\
            .pack(padx=24, pady=(2, 4), ipady=3, fill="x")

        err_lbl = tk.Label(win, text="", fg=ACCENT_RED, bg=BG_APP, font=sfont)
        err_lbl.pack()

        def _do():
            h = host_var.get().strip()
            p_str = port_var.get().strip()
            if not h:
                err_lbl.config(text="Host is required.")
                return
            try:
                p = int(p_str)
                if not (1 <= p <= 65535):
                    raise ValueError
            except ValueError:
                err_lbl.config(text="Port must be a number (1-65535).")
                return

            lbl = save_var.get().strip()
            if lbl:
                # Save to list (avoid duplicate labels)
                self._saved_servers = [s for s in self._saved_servers
                                       if s["label"] != lbl]
                self._saved_servers.insert(0, {"label": lbl, "host": h, "port": p})
                # Cap at 10 saved servers
                self._saved_servers = self._saved_servers[:10]

            win.destroy()
            self.host = h
            self.port = p
            self._save_config()
            self._connect()

        btn_row = tk.Frame(win, bg=BG_APP)
        btn_row.pack(fill="x", padx=24, pady=(8, 16))
        tk.Button(btn_row, text="Connect", fg=fg, bg="#0d2a0d",
                  font=(self._game_font, 10, "bold"), relief="flat", bd=0,
                  padx=14, pady=6, activebackground="#1a4a1a",
                  command=_do).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Cancel", fg=dim, bg=BG_INPUT,
                  font=sfont, relief="flat", bd=0, padx=10, pady=5,
                  activebackground=BORDER_CLR,
                  command=win.destroy).pack(side="left")

        # Bind Enter key
        win.bind("<Return>", lambda _: _do())
        host_entry.focus_set()

    def _run_auto_login(self):
        """
        Replay the manual login sequence automatically:
          800ms after connect  -> send "1"  (select Login option)
          1600ms               -> send username
          2400ms               -> send password
          4000ms               -> send character slot number
        Delays are generous so the server has time to send each prompt.
        Only fires once per connection.
        """
        if self._auto_login_fired:
            return
        if not self._auto_login_enabled:
            return
        if not self._auto_login_username or not self._auto_login_password:
            self._sys("[Auto-Login] Username or password not set — skipping.")
            return
        self._auto_login_fired = True
        slot = str(max(1, self._auto_login_char_slot))
        self.root.after(0,    lambda: self._send("1"))                          # step 1: login menu
        self.root.after(800,  lambda: self._send(self._auto_login_username))    # step 2: username
        self.root.after(1600, lambda: self._send(self._auto_login_password))    # step 3: password
        self.root.after(3200, lambda: self._send(slot))                         # step 4: pick character

    def _send(self, text: str):
        if self._telnet:
            self._telnet.send(text)

    # ════════════════════════════════════════════
    # Event polling (tkinter main loop)
    # ════════════════════════════════════════════

    def _poll(self):
        # root.after is in finally so the loop ALWAYS reschedules even if
        # an exception occurs in dispatch — prevents the game going silent.
        try:
            # Drain main telnet queue
            try:
                while True:
                    msg_type, payload = self.rx_q.get_nowait()
                    self._dispatch(msg_type, payload)
            except queue.Empty:
                pass

            # Drain real-time sync queue — wrapped separately so a sync
            # error never kills the main telnet display loop
            try:
                while True:
                    stype, spayload = self.sync_q.get_nowait()
                    try:
                        self._dispatch_sync(stype, spayload)
                    except Exception:
                        pass  # never let sync errors kill the poll loop
            except queue.Empty:
                pass
        finally:
            self.root.after(30, self._poll)

    def _dispatch(self, msg_type: str, payload):
        if msg_type == "connected":
            self._sys(f"Connected to {self.host}:{self.port}")
            self._conn_btn.config(text="✕ Disconnect", bg="#2a0d0d", fg=ACCENT_RED,
                                  state="normal", activebackground="#4a1a1a")
            self._conn_status.config(text=f"{self.host}:{self.port}", fg=ACCENT_GRN)
            self._auto_login_fired = False
            if self._auto_login_enabled:
                self.root.after(800, self._run_auto_login)
        elif msg_type == "disconnected":
            self._sys("Disconnected from server.")
            self._conn_btn.config(text="⚡ Connect", bg="#0d2a0d", fg=ACCENT_GRN,
                                  state="normal", activebackground="#1a4a1a")
            self._conn_status.config(text="Disconnected", fg=ACCENT_RED)
            self._stop_sync()
        elif msg_type == "error":
            self._append(f"[ERROR] {payload}\n", "err")
            self._conn_btn.config(text="⚡ Connect", bg="#0d2a0d", fg=ACCENT_GRN,
                                  state="normal", activebackground="#1a4a1a")
            self._conn_status.config(text="Connection failed", fg=ACCENT_RED)
        elif msg_type == "line":
            self._handle_line(payload)

    # ════════════════════════════════════════════
    # Line processing
    # ════════════════════════════════════════════

    def _handle_line(self, raw: str):
        # ── Real-time sync init control line ──────────────────────────────────
        # Server injects: \x00SYNC:<64-hex-token>:<port>\x00
        # Client strips it silently and fires up the sync connection.
        sm = SYNC_INIT_RE.search(raw)
        if sm:
            token    = sm.group(1)
            syn_port = int(sm.group(2))
            self._start_sync(token, syn_port)
            return   # never display this line

        # ── Auto-open browser for training/character-creator URLs ─────────
        # The server sends the URL as a visible text line. Detect it here and
        # open the browser on THIS machine so the right player's browser opens.
        au = AUTOOPEN_URL_RE.search(ANSI_RE.sub('', raw))
        if au:
            import subprocess
            subprocess.Popen(f'start "" "{au.group(0)}"', shell=True)

        # ── Shop catalog tag (injected by ORDER command) ───────────────────
        # Strip it from display and pre-load items into _known_items so every
        # item name in the catalog listing becomes a clickable link.
        sc = SHOP_CATALOG_RE.search(raw)
        if sc:
            try:
                import json as _json
                catalog = _json.loads(sc.group(1))
                self._shop_catalog = {}
                for entry in catalog:
                    idx  = str(entry.get("idx", ""))
                    key  = self._item_key(entry.get("name", ""))
                    noun = entry.get("noun", key.split()[-1] if key else "")
                    self._shop_catalog[idx] = entry
                    if key:
                        self._known_items[f"shop:{idx}:{key}"] = {
                            "full_name":  entry.get("name", ""),
                            "match_key":  key,
                            "noun":       noun,
                            "state":      "shop",
                            "container":  "",
                            "item_type":  entry.get("item_type", "misc"),
                            "shop_idx":   idx,
                            "shop_data":  entry,
                        }
            except Exception as e:
                print(f"[HUD] SHOP_CATALOG parse error: {e}")
            return   # never display this line

        # ── Customize material/color tag (injected by CUSTOMIZE command) ───
        cm = CUSTOMIZE_MENU_RE.search(raw)
        if cm:
            try:
                import json as _json
                payload = _json.loads(cm.group(1))
                self._customize_payload = payload
                mat_list = payload.get("materials", [])
                colors   = payload.get("colors", [])
                for entry in mat_list:
                    mat_key = entry.get("display", "").lower().strip()
                    if mat_key:
                        self._known_items[mat_key] = {
                            "full_name":  entry.get("display", ""),
                            "noun":       mat_key,
                            "state":      "customize_material",
                            "container":  "",
                            "item_type":  "material",
                            "mat_data":   entry,
                            "colors":     colors,
                        }
            except Exception as e:
                print(f"[HUD] CUSTOMIZE_MENU parse error: {e}")
            return   # never display this line

        cc = CUSTOMIZE_COLORS_RE.search(raw)
        if cc:
            try:
                import json as _json
                payload = _json.loads(cc.group(1))
                self._customize_color_payload = payload
            except Exception as e:
                print(f"[HUD] CUSTOMIZE_COLORS parse error: {e}")
            return   # never display this line


        # ── GSIV status tag (injected by patched session.py) ──
        m = GSIV_STATUS_RE.search(raw)
        if m:
            self._hp_bar.update(int(m.group(1)), int(m.group(2)))
            self._mp_bar.update(int(m.group(3)), int(m.group(4)))
            self._sp_bar.update(int(m.group(5)), int(m.group(6)))
            self._st_bar.update(int(m.group(7)), int(m.group(8)))
            rt = int(m.group(9))
            self._roundtime = rt
            if rt > 0:
                self._rt_label.config(text=f"RT {rt}s")
                self._start_rt_remaining(rt)
            else:
                self._rt_label.config(text="")
                self._clear_rt()
                self._nav_on_ready()   # RT just cleared — safe to send next nav step
            if m.group(10):
                self._update_room(int(m.group(10)))
            return  # Don't display this line

        # ── Prompt line ──
        # Also extract RT from "[RT: 2s]>" prompts directly
        rtp = RT_PROMPT_RE.match(raw.strip())
        if rtp:
            rt_val = int(rtp.group(1))
            if rt_val > 0:
                self._start_rt_remaining(rt_val)
                # Cancel the nav fallback timer — RT is still active.
                # _nav_on_ready() will fire when _tick_rt sees remaining <= 0.
                if self._pathfind_timer:
                    self.root.after_cancel(self._pathfind_timer)
                    self._pathfind_timer = None
            else:
                # RT is 0 on this prompt — clear and allow nav
                self._clear_rt()
                self._nav_on_ready()
            self._append(raw, "prompt")
            self._append("\n", "default")
            return

        if PROMPT_RE.match(raw):
            self._append(raw, "prompt")
            self._append("\n", "default")
            self._nav_on_ready()   # Clean prompt (no RT) — safe to send next nav step
            # Safety reset — ensure inv parse flags never bleed past a prompt
            self._inv_parsing          = False
            self._inv_unplaced_section = False
            return

        # ── Parse room title (from LOOK output) ──
        clean = re.sub(r'\x1b\[[0-9;]*m', '', raw)  # strip ANSI for regex matching
        self._handle_sfx_for_line(clean.strip())

        # ── "Roundtime: 3 sec." — start bar at full duration ──
        rsm = RT_START_RE.search(clean)
        if rsm:
            self._start_rt_full(int(rsm.group(1)))

        # ── "Roundtime: 2 seconds remaining." — resync remaining ──
        rrm = RT_REMAIN_RE.search(clean)
        if rrm and not rsm:
            self._start_rt_remaining(int(rrm.group(1)))

        # ── Server input-prompt lines ("Choice (1-2):", "Username:", etc.) ──
        # Highlight them in yellow+bold so the user knows to type something
        if SERVER_ASK_RE.match(clean.strip()):
            self._append(raw.rstrip() + "  ◄ type your answer below\n", "ask")
            return
        tm = ROOM_TITLE_RE.match(clean)
        if tm:
            self._current_room_title = tm.group(1)
            self._update_room(int(tm.group(2)))

        # ── Parse exits from LOOK output (supplement graph) ──
        em = EXITS_RE.match(clean)
        if em:
            exit_str = em.group(1).strip().rstrip(".")
            self._live_exits = {}
            if self._current_room_id is not None:
                room = self.graph.get(self._current_room_id)
                if room:
                    exits = room.get("exits", {})
                    # Build a lookup: last_word_of_key → (full_key, target_id)
                    # e.g. "go_bridge" → last word "bridge", send cmd "go bridge"
                    suffix_map: Dict[str, Tuple[str, int]] = {}
                    for gkey, nid in exits.items():
                        last = gkey.split("_")[-1]
                        spaced = gkey.replace("_", " ")
                        suffix_map[last] = (spaced, nid)
                        # also store full spaced key directly
                        suffix_map[spaced] = (spaced, nid)
                        # store display name (prefix stripped, underscores to spaces)
                        # so "go_verdant_path" -> clickable "verdant path"
                        for prefix in ("go_", "climb_", "swim_"):
                            if gkey.startswith(prefix):
                                display = gkey[len(prefix):].replace("_", " ")
                                cmd = gkey.replace("_", " ")
                                suffix_map[display] = (cmd, nid)
                                break

                    for part in exit_str.split(","):
                        part = part.strip().lower()
                        if not part:
                            continue
                        if part in suffix_map:
                            cmd, nid = suffix_map[part]
                            self._live_exits[part] = (nid, cmd)
                        else:
                            # compass dirs — cmd == part
                            gkey = part.replace(" ", "_")
                            if gkey in exits:
                                self._live_exits[part] = (exits[gkey], part)
                            elif part in exits:
                                self._live_exits[part] = (exits[part], part)
            # Render the exits line with clickable direction links
            self._append_exits_line(raw, self._live_exits)
            return  # already appended, skip normal display below

        # ── Parse stats from health / exp command output ──────────────────
        for pat, bar in ((HEALTH_HP_RE, "_hp_bar"), (HEALTH_MP_RE, "_mp_bar"),
                         (HEALTH_SP_RE, "_sp_bar"), (HEALTH_ST_RE, "_st_bar")):
            hm = pat.search(clean)
            if hm:
                getattr(self, bar).update(int(hm.group(2)), int(hm.group(1)))
        # Combat inline: "  Health: 128/132" — update HP bar in real time during fights
        chm = COMBAT_HP_RE.match(clean)
        if chm:
            self._hp_bar.update(int(chm.group(1)), int(chm.group(2)))

        # "Health Recovery: 13 points per round" — use server value directly
        hrm = HP_RECOVERY_RE.search(clean)
        if hrm:
            self._hp_regen_rate = float(hrm.group(1))

        # ── EXP command output parsing ────────────────────────────────────
        etm = EXP_TOTAL_RE.search(clean)
        if etm:
            try:
                self._exp_total = int(etm.group(1).replace(",", ""))
                self._update_exp_panel()
            except ValueError:
                pass
        tnlm = EXP_TNL_RE.search(clean)
        if tnlm:
            try:
                self._exp_tnl = int(tnlm.group(1).replace(",", ""))
                self._update_exp_panel()
            except ValueError:
                pass
        msm = EXP_MIND_RE.search(clean)
        if msm:
            self._mind_state = msm.group(1).strip().lower()
            self._update_exp_panel()
        # Inline mind state from kill XP line: "You gained 240 experience [kill].  Mind: becoming saturated"
        msm2 = EXP_MIND_INLINE_RE.search(clean)
        if msm2 and not msm:
            self._mind_state = msm2.group(1).strip().lower()
            self._update_exp_panel()
        elm = EXP_LEVEL_RE.search(clean)
        if elm:
            try:
                self._exp_level = int(elm.group(1))
                self._update_exp_panel()
            except ValueError:
                pass

        # Track combat state from server signals
        # Enter combat when a creature attacks or we attack
        if self._ENEMY_LINE_RE.match(clean) or "you swing" in clean.lower() or \
           "you attack" in clean.lower() or "you ambush" in clean.lower():
            self._in_combat = True

        # Exit combat on explicit server signals
        if COMBAT_CLEAR_RE.search(clean):
            self._in_combat = False
        ptm = EXP_PTP_RE.search(clean)
        if ptm:
            self._ptp_lbl.config(text=ptm.group(1))
        mtm = EXP_MTP_RE.search(clean)
        if mtm:
            self._mtp_lbl.config(text=mtm.group(1))
        sm = STANCE_CUR_RE.search(clean)
        if sm:
            self._stance_lbl.config(text=sm.group(1))

        # ── AIM preference confirmation parsing ───────────────────────────
        aim_set = AIM_SET_RE.search(clean)
        if aim_set:
            self._current_aim = aim_set.group(1).strip().lower()
            self._update_bodypart_btn()
        aim_clear = AIM_CLEAR_RE.search(clean)
        if aim_clear:
            self._current_aim = ""
            self._update_bodypart_btn()

        # ── Inventory model parsing ──────────────────────────────────────
        self._parse_inv_line(clean)

        # ── Normal display ──
        # Check for bracketed command menus: [Bank: CHECK BALANCE, DEPOSIT ...]
        mm = MENU_CMD_RE.match(clean.strip())
        if mm:
            self._append_menu_line(raw, mm.group(1), mm.group(2))
            return
        self._parse_enemies_from_line(clean)

        # Suppress "Unplaced items" block — only while actively inside an inv parse block
        if self._inv_unplaced_section and (self._inv_parsing or INV_UNPLACED_RE.match(clean.strip())):
            return

        self._append_line(raw)

    def _update_room(self, room_id: int):
        first_room = self._current_room_id is None
        was_shop = self._last_room_was_shop
        if room_id == self._current_room_id:
            return
        self._room_start_index = self._text.index("end-1c")
        self._current_room_id = room_id
        is_shop = room_id in self._shop_room_ids
        if not first_room:
            if is_shop and not was_shop:
                self._play_sfx(SFX_SHOP_ENTER)
            elif was_shop and not is_shop:
                self._play_sfx(SFX_SHOP_EXIT)
        self._last_room_was_shop = is_shop
        self._map.set_room(room_id)
        self.root.after_idle(lambda rid=room_id: self._map.set_room(rid))

        room = self.graph.get(room_id)
        title = self._current_room_title or (room.get("title", f"Room #{room_id}") if room else f"Room #{room_id}")
        zone  = room.get("zone_name", "Unknown Zone") if room else "Unknown Zone"
        map_zone = self._map._region_name_for_room(room_id) if hasattr(self._map, "_region_name_for_room") else zone
        audio_zone = map_zone or zone

        # Room panel has been removed — store for internal use only
        self._current_room_title = title
        self._current_room_zone  = zone
        if self._audio:
            self._audio.on_zone_changed(audio_zone)
        if hasattr(self, "_room_name_lbl"):
            self._room_name_lbl.config(text=title)
        if hasattr(self, "_room_id_lbl"):
            self._room_id_lbl.config(text=f"Room #{room_id}")
        if hasattr(self, "_room_zone_lbl"):
            self._room_zone_lbl.config(text=zone)

        # Clear enemy list on room change
        self._room_enemies.clear()
        self._room_npcs.clear()
        self._target_index = 0
        self._current_target = ""
        self._current_target_match = ""
        self._in_combat = False
        self._target_lbl.config(text="No target", fg=TEXT_DIM)

        # One-shot: seed bars on first room entry only if sync not yet live.
        # If the sync channel is already connected it will push full state
        # within 1 second so these commands are unnecessary.
        if first_room and not self._sync_connected:
            self.root.after(1200, lambda: self._telnet and not self._sync_connected and self._telnet.send("health\r\n"))
            self.root.after(2200, lambda: self._telnet and not self._sync_connected and self._telnet.send("exp\r\n"))
            self.root.after(3000, lambda: self._telnet and not self._sync_connected and self._telnet.send("stance\r\n"))

    # ════════════════════════════════════════════
    # Command input
    # ════════════════════════════════════════════

    def _current_input_mode_info(self) -> dict:
        for mode in INPUT_MODES:
            if mode["id"] == self._input_mode:
                return mode
        return INPUT_MODES[0]

    def _current_comm_mode_info(self) -> dict:
        for mode in COMM_INPUT_MODES:
            if mode["id"] == self._comm_input_mode:
                return mode
        return COMM_INPUT_MODES[0]

    def _apply_input_mode(self):
        mode = self._current_input_mode_info()
        color = mode.get("color", ACCENT_BLUE)
        prompt = mode.get("prompt", ">")
        if hasattr(self, "_prompt_lbl"):
            self._prompt_lbl.config(text=prompt, fg=color)
        if hasattr(self, "_entry"):
            self._entry.config(
                insertbackground=color,
                highlightcolor=color,
                highlightbackground=BORDER_CLR,
            )
        if hasattr(self, "_input_mode_btn"):
            self._input_mode_btn.config(
                text="◉",
                bg=BG_INPUT,
                fg=color,
                activebackground=BG_INPUT,
                activeforeground=color,
            )

    def _set_input_mode(self, mode_id: str):
        valid_ids = {mode["id"] for mode in INPUT_MODES}
        self._input_mode = mode_id if mode_id in valid_ids else "command"
        if self._input_mode != "command":
            self._comm_input_mode = self._input_mode
        self._apply_input_mode()
        if hasattr(self, "_save_config"):
            self._save_config()

    def _toggle_input_mode(self):
        if self._input_mode == "command":
            self._set_input_mode(self._comm_input_mode)
        else:
            self._set_input_mode("command")
        if hasattr(self, "_entry"):
            self._entry.focus_set()

    def _show_comm_mode_menu(self, event):
        menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            activebackground=BAR_BG,
            activeforeground=TEXT_MAIN,
        )
        for mode in COMM_INPUT_MODES:
            label = f'{mode["label"]}  ({mode["prompt"]})'
            menu.add_command(
                label=label,
                command=lambda mode_id=mode["id"]: self._select_comm_mode(mode_id),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    def _select_comm_mode(self, mode_id: str):
        valid_ids = {mode["id"] for mode in COMM_INPUT_MODES}
        if mode_id not in valid_ids:
            return
        self._comm_input_mode = mode_id
        if self._input_mode != "command":
            self._input_mode = mode_id
            self._apply_input_mode()
        if hasattr(self, "_save_config"):
            self._save_config()
        if hasattr(self, "_entry"):
            self._entry.focus_set()

    def _compose_input_command(self, typed_text: str) -> str:
        mode = self._current_input_mode_info()
        verb = str(mode.get("verb") or "").strip()
        text = typed_text.strip()
        if not verb:
            return text
        return f"{verb} {text}"

    def _on_enter(self, _ev=None):
        typed = self._entry_var.get().strip()
        if not typed:
            return
        self._entry_var.set("")
        self._hist.append(typed)
        self._hist_idx = -1

        # Cancel active pathfinding if player types manually
        if self._pathfind_steps:
            self._cancel_pathfind()

        cmd = self._compose_input_command(typed)
        if self._input_mode == "command" and typed.lower().startswith("go2"):
            self._append(f"> {cmd}\n", "prompt")
            self._handle_go2_command(typed)
            return "break"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")
        return "break"

    def _hist_prev(self, _ev):
        if not self._hist:
            return
        if self._hist_idx == -1:
            self._hist_idx = len(self._hist) - 1
        elif self._hist_idx > 0:
            self._hist_idx -= 1
        self._entry_var.set(self._hist[self._hist_idx])
        return "break"

    def _hist_next(self, _ev):
        if self._hist_idx == -1:
            return
        self._hist_idx += 1
        if self._hist_idx >= len(self._hist):
            self._hist_idx = -1
            self._entry_var.set("")
        else:
            self._entry_var.set(self._hist[self._hist_idx])
        return "break"

    # ════════════════════════════════════════════
    # Map click → pathfinding (:go2 behaviour)
    # ════════════════════════════════════════════

    def _map_room_center(self, zone_name: str, room_id: int) -> Optional[Tuple[float, float]]:
        zone = self.regions.get(zone_name, {})
        coords = zone.get("rooms", {}).get(room_id)
        if not coords and hasattr(self, "_map"):
            region_name = self._map._region_name_for_room(room_id)
            zone = self.regions.get(region_name, {})
            coords = zone.get("rooms", {}).get(room_id)
        if not coords:
            return None
        x, y, w, h = coords
        return x + (w / 2.0), y + (h / 2.0)

    def _start_pathfind_to(self, target_id: int, label: Optional[str] = None):
        if self._current_room_id is None:
            self._sys("Unknown current room — try LOOKing first.")
            return

        if target_id == self._current_room_id:
            self._sys("Already there.")
            return

        path = self.graph.find_path(self._current_room_id, target_id)
        if path is None:
            self._sys(f"No path found to room #{target_id}.")
            return
        if len(path) == 0:
            return

        self._pathfind_steps = path
        destination = label or f"#{target_id}"
        self._sys(
            f"Pathfinding to {destination} — {len(path)} step(s). "
            f"Click ✕ Cancel or type any command to abort."
        )
        self._cancel_btn.pack(side="right", padx=(4, 0))
        self._do_next_step()

    def _handle_go2_command(self, typed: str):
        parts = typed.split(None, 1)
        target = parts[1].strip() if len(parts) > 1 else ""
        target_id, message = self.graph.resolve_go2_target(target, from_id=self._current_room_id)
        if message and target_id is None:
            self._sys(message)
            return
        if target_id is None:
            self._sys("Usage: go2 <room id|lich id|u####|tag>")
            return

        room = self.graph.get(target_id) or {}
        lich_uid = room.get("lich_uid")
        if lich_uid:
            label = f"u{lich_uid} / #{target_id}"
        else:
            label = f"#{target_id}"
        self._start_pathfind_to(target_id, label=label)

    def _infer_map_direction(self, dx: float, dy: float) -> Optional[str]:
        if abs(dx) <= 1 and abs(dy) <= 1:
            return None
        if abs(dx) > abs(dy) * 1.5:
            return "east" if dx > 0 else "west"
        if abs(dy) > abs(dx) * 1.5:
            return "south" if dy > 0 else "north"
        vertical = "south" if dy > 0 else "north"
        horizontal = "east" if dx > 0 else "west"
        return f"{vertical}{horizontal}"

    def _resolve_adjacent_map_click(self, target_id: int) -> int:
        current_id = self._current_room_id
        if current_id is None:
            return target_id

        current_room = self.graph.get(current_id)
        if not current_room:
            return target_id

        zone_name = current_room.get("zone_name", "")
        current_center = self._map_room_center(zone_name, current_id)
        target_center = self._map_room_center(zone_name, target_id)
        if not current_center or not target_center:
            return target_id

        dx = target_center[0] - current_center[0]
        dy = target_center[1] - current_center[1]
        if (dx * dx + dy * dy) > (90 * 90):
            return target_id

        path = self.graph.find_path(current_id, target_id)
        if not path or len(path) != 1:
            return target_id

        intended_dir = self._infer_map_direction(dx, dy)
        if not intended_dir:
            return target_id

        exits = current_room.get("exits", {}) or {}
        corrected = exits.get(intended_dir)
        try:
            corrected = int(corrected)
        except (TypeError, ValueError):
            return target_id

        return corrected if corrected != current_id else target_id

    def _on_map_click(self, target_id: int):
        target_id = self._resolve_adjacent_map_click(target_id)
        self._start_pathfind_to(target_id)

    def _do_next_step(self):
        """Send the next queued pathfind direction.

        Normal moves (no RT): waits for a clean server prompt or GSIV RT=0 tag,
        with a 250ms fallback in case the server sends no status tag for a move.

        RT-generating moves (climb, swim, go <special>, etc.): the server will
        send a Roundtime line and a [RT: Ns]> prompt. _nav_on_ready() is hooked
        into the RT-clear path so the next step fires only after RT expires —
        never sooner.
        """
        if not self._pathfind_steps:
            self._pathfind_waiting = False
            self._cancel_btn.pack_forget()
            self._sys("Arrived at destination.")
            # Notify AUTO heal if it was driving navigation
            if getattr(self, "_auto_waiting_nav", False):
                self._auto_nav_arrived()
            return

        direction = self._pathfind_steps.pop(0)
        self._append(f"  → {direction}\n", "path")
        self._send(direction)

        if self._pathfind_steps:
            self._pathfind_waiting = True
            # Fallback: if the server sends no status/prompt tag within 250ms
            # (e.g. a move type we don't intercept), proceed anyway.
            # _nav_on_ready() cancels this timer if it fires first.
            if self._pathfind_timer:
                self.root.after_cancel(self._pathfind_timer)
            self._pathfind_timer = self.root.after(250, self._nav_fallback_tick)

    def _nav_fallback_tick(self):
        """Fires 250ms after a step is sent if the server hasn't signalled RT status.
        Covers normal room moves where no GSIV tag or RT prompt is produced."""
        self._pathfind_timer = None
        if self._pathfind_waiting and self._pathfind_steps:
            self._pathfind_waiting = False
            self._do_next_step()

    def _nav_on_ready(self):
        """Called by server-signal paths when it is safe to send the next nav step.

        Hooked into:
          • GSIV status tag when RT == 0
          • Clean prompt match (PROMPT_RE, no RT in prompt)
          • _clear_rt() when the RT bar expires naturally
        """
        if not self._pathfind_waiting or not self._pathfind_steps:
            return
        # Cancel fallback timer — server told us we're clear
        if self._pathfind_timer:
            self.root.after_cancel(self._pathfind_timer)
            self._pathfind_timer = None
        self._pathfind_waiting = False
        # Tiny buffer (50ms) so room-change data finishes arriving before next send
        self.root.after(50, self._do_next_step)

    def _do_next_step_deferred(self):
        """Legacy shim — kept for safety, routes through new logic."""
        if self._pathfind_waiting and self._pathfind_steps:
            self._nav_on_ready()

    def _cancel_pathfind(self):
        if self._pathfind_steps or self._pathfind_waiting:
            self._pathfind_steps.clear()
            self._pathfind_waiting = False
            if self._pathfind_timer:
                self.root.after_cancel(self._pathfind_timer)
                self._pathfind_timer = None
            self._cancel_btn.pack_forget()
            self._sys("Pathfinding cancelled.")

    def _reload_map_annotations(self):
        self.regions = load_map_regions(REGIONS_PATH)
        self._map.reload_regions()
        self._sys("Map annotations reloaded.")

    def _quick_cmd(self, cmd: str):
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    # ════════════════════════════════════════════
    # Inventory model + clickable items
    # ════════════════════════════════════════════

    def _register_item(self, full_name: str, state: str,
                       container: str = '', itype: str = '') -> None:
        """Register an item in _known_items.

        Key is the full article-stripped lowercase name so material+color
        combos are always unique. 'black invar dagger' and 'white invar dagger'
        get separate keys and never collide. No ordinal prefixes.
        """
        key = self._item_key(full_name)
        if not key:
            return
        if not itype:
            itype = self._guess_type(key)
        noun = key.split()[-1]

        self._known_items[key] = {
            'full_name': full_name.strip(),
            'noun':      noun,
            'state':     state,
            'container': container,
            'item_type': itype,
        }
        if state in ('right_hand', 'left_hand', 'worn', 'in_container'):
            self._inventory_counts[key] = self._inventory_counts.get(key, 0) + 1

        # Track last lockbox/coffer in hand for Pick/Detect/Disarm buttons
        if any(b in noun for b in ("box", "coffer", "chest", "strongbox", "lockbox")):
            if state in ('right_hand', 'left_hand'):
                self._last_lockbox_noun = noun

    def _parse_inv_line(self, clean: str):
        """Update _known_items from inv/inv full output lines (ANSI-stripped)."""
        line = clean.strip()

        # "Total items: N" marks end of inv block
        if INV_TOTAL_RE.match(line):
            self._inv_parsing           = False
            self._inv_parse_started     = False
            self._inv_cur_cont          = ""
            self._inv_unplaced_section  = False
            return

        # "Unplaced items (use GET then WEAR or STOW):" — suppress entire block
        if INV_UNPLACED_RE.match(line):
            self._inv_unplaced_section = True
            return

        # Skip all lines inside the Unplaced section
        if self._inv_unplaced_section:
            return

        # "You are holding X in your right hand [and Y in your left hand]"
        hm = INV_HOLD_RE.match(line)
        if hm:
            if not self._inv_parse_started:
                # First line of a fresh INV FULL — flush stale hand/worn/container items
                self._inv_parse_started = True
                for k in list(self._known_items.keys()):
                    st = self._known_items[k].get('state', '')
                    if st in ('right_hand', 'left_hand', 'worn', 'in_container'):
                        del self._known_items[k]
                self._worn_containers = []
                self._inventory_counts = {}

            self._inv_parsing = True
            items_hands = [(hm.group(1), hm.group(2))]
            if hm.group(3) and hm.group(4):
                items_hands.append((hm.group(3), hm.group(4)))
            for full_name, hand in items_hands:
                self._register_item(full_name.strip(), f"{hand}_hand")
            return

        # "You are wearing X, Y, and Z."
        wm = INV_WEAR_RE.match(line)
        if wm:
            if not self._inv_parse_started:
                self._inv_parse_started = True
                for k in list(self._known_items.keys()):
                    st = self._known_items[k].get('state', '')
                    if st in ('right_hand', 'left_hand', 'worn', 'in_container'):
                        del self._known_items[k]
                self._worn_containers = []
                self._inventory_counts = {}

            self._inv_parsing = True
            worn_str = wm.group(1)
            worn_str = re.sub(r',?\s+and\s+', ', ', worn_str)
            parts = [p.strip() for p in worn_str.split(',') if p.strip()]
            for full_name in parts:
                self._register_item(full_name, 'worn')
                # Rebuild worn container list
                base_key = self._item_key(full_name)
                if base_key and self._guess_type(base_key) == 'container':
                    if full_name not in self._worn_containers:
                        self._worn_containers.append(full_name)
            return

        # "In a leather backpack:"  — start of container section
        cm = INV_CONT_RE.match(clean)
        if cm:
            self._inv_parsing = True
            cont_name = cm.group(1).strip()
            cont_name = re.sub(r'\x1b\[[0-9;]*m', '', cont_name).strip()
            self._inv_cur_cont = cont_name
            return

        # Indented item line inside a container
        if self._inv_parsing and self._inv_cur_cont:
            im = INV_ITEM_RE.match(clean)
            if im:
                raw_name = im.group(1).strip()
                raw_name = re.sub(r'\x1b\[[0-9;]*m', '', raw_name).strip()
                self._register_item(raw_name, 'in_container', self._inv_cur_cont)

    @staticmethod
    def _strip_articles(name: str) -> str:
        """Strip ALL leading articles (a/an/the/some) from a name.
        Handles stacked articles like 'A some basal moss' → 'basal moss'.
        Loops until no leading article remains."""
        pattern = re.compile(r'^(a|an|the|some)\s+', re.IGNORECASE)
        prev = None
        while prev != name:
            prev = name
            name = pattern.sub('', name.strip())
        return name

    def _item_key(self, full_name: str) -> str:
        """Derive a lowercase lookup key from an item full name.
        Strips ALL leading articles (a/an/the/some) and lowercases."""
        name = re.sub(r'\x1b\[[0-9;]*m', '', full_name).strip().lower()
        name = self._strip_articles(name)
        return name

    _TYPE_KEYWORDS = {
        'weapon':    ['sword','dagger','knife','axe','mace','club','spear','bow',
                      'falchion','longsword','shortsword','scimitar','staff','wand',
                      'crossbow','lance','hammer','flail','halberd','rapier','saber',
                      'broadsword','wakizashi','naginata','katana','trident','dirk',
                      'estoc','cudgel','maul'],
        'armor':     ['armor','armour','brigandine','chainmail','plate','leather armor',
                      'mail','hauberk','breastplate','cuirass','gambeson'],
        'shield':    ['shield','buckler','targe','pavise'],
        'container': ['backpack','pouch','sack','bag','sheath','scabbard','cloak',
                      'purse','satchel','rucksack','haversack','pack','pouch','case',
                      'coffer','chest','box','trunk'],
        'jewelry':   ['ring','amulet','necklace','bracelet','earring','brooch',
                      'pin','circlet','anklet','torc'],
        'gem':       ['gem','crystal','topaz','sapphire','ruby','emerald','diamond',
                      'opal','amethyst','garnet','zircon','carbuncle'],
        'scroll':    ['scroll','tome','book','parchment'],
        'herb':      ['herb','leaf','root','flower','blossom','mushroom','berry',
                      'seed','sprig'],
        'lockpick':  ['lockpick','pick set','picks'],
        'key':       ['key ring','keyring','key'],
    }

    def _guess_type(self, key: str) -> str:
        for itype, words in self._TYPE_KEYWORDS.items():
            for w in words:
                if w in key:
                    return itype
        return 'misc'

    def _show_material_popup(self, event, mat_key: str):
        """
        Show a floating stat-card popup for a material in the CUSTOMIZE list.
        Includes all stats, special properties, color dropdown, and action buttons.
        """
        info = self._known_items.get(mat_key)
        if not info or info.get("state") != "customize_material":
            return

        data   = info.get("mat_data", {})
        colors = info.get("colors", [])
        idx    = data.get("idx", "?")
        name   = data.get("display", "unknown").title()
        rarity = data.get("rarity", "common")

        # Rarity → color
        _RARITY_CLR = {
            "common":          TEXT_MAIN,
            "infrequent":      "#8bbb8b",
            "uncommon":        ACCENT_GRN,
            "rare":            ACCENT_BLUE,
            "very_rare":       ACCENT_PRP,
            "extremely_rare":  ACCENT_YEL,
        }
        title_clr = _RARITY_CLR.get(rarity, TEXT_MAIN)

        # Special property descriptions
        _SPECIAL_DESC = {
            "fire_flare":      "Weapons deal bonus fire damage on hit.  Armor retaliates with fire.",
            "cold_flare":      "Weapons deal bonus cold damage on hit.  Armor retaliates with cold.",
            "lightning_flare": "Weapons deal bonus lightning damage on hit.  Armor retaliates with lightning.",
            "acid_flare":      "Weapons deal bonus acid damage on hit.  Armor retaliates with acid.",
            "ice_flare":       "Weapons deal bonus ice damage on hit.  Armor retaliates with ice.",
            "undead_bane":     "Deals significantly increased damage to undead creatures.",
            "anti_magic":      "Disrupts and resists magical effects.  Can dispel enchantments.",
            "featherweight":   "Extremely lightweight.  Dramatically reduces encumbrance.",
            "disintegrate":    "Can disintegrate targets on devastating critical hits.",
        }

        # ── Build stat lines ──────────────────────────────────────────────
        stat_lines = []
        eb = data.get("enchant_bonus", 0)
        stat_lines.append(("Enchant Bonus", f"+{eb}" if eb else "None"))

        am = data.get("attack_mod", 0)
        if am: stat_lines.append(("Attack Mod", f"+{am}"))

        dm = data.get("defense_mod", 0)
        if dm: stat_lines.append(("Defense Mod", f"+{dm}"))

        wm = data.get("weight_modifier", 1.0)
        if wm < 0.9:
            wt_str = f"Lighter ({wm:.2f}x)"
        elif wm > 1.0:
            wt_str = f"Heavier ({wm:.2f}x)"
        else:
            wt_str = f"Normal ({wm:.2f}x)"
        stat_lines.append(("Weight", wt_str))

        cm = data.get("cost_mult", 1.0)
        stat_lines.append(("Cost Multiplier", f"{cm:.1f}x"))

        lvl = data.get("level_req", 0)
        stat_lines.append(("Level Required", str(lvl) if lvl else "Any"))

        special = data.get("special", "")
        if special:
            stat_lines.append(("Special", special.replace("_", " ").title()))

        rarity_display = rarity.replace("_", " ").title()
        stat_lines.append(("Rarity", rarity_display))

        # ── Build popup window ────────────────────────────────────────────
        popup = tk.Toplevel(self.root)
        popup.title("Material Details")
        popup.configure(bg="#1a1e26")
        popup.resizable(False, False)
        popup.transient(self.root)

        # Title
        tk.Label(popup, text=name,
                 fg=title_clr, bg="#1a1e26",
                 font=(self._game_font, 13, "bold"),
                 wraplength=380, justify="left",
                 padx=12, pady=8).pack(fill="x")

        # Rarity + level badge
        badge_txt = f"[{rarity_display}]"
        if lvl: badge_txt += f"  •  Level {lvl}+"
        tk.Label(popup, text=badge_txt,
                 fg=TEXT_DIM, bg="#1a1e26",
                 font=(self._game_font, 9, "italic"),
                 padx=12).pack(anchor="w")

        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)

        # Stat grid
        frame = tk.Frame(popup, bg="#1a1e26")
        frame.pack(fill="x", padx=12, pady=2)
        for row_i, (label, value) in enumerate(stat_lines):
            fg_clr = ACCENT_RED if label == "Special" else ACCENT_CYN
            tk.Label(frame, text=label + ":",
                     fg=fg_clr, bg="#1a1e26",
                     font=(self._game_font, 10),
                     anchor="w").grid(row=row_i, column=0, sticky="w", padx=(0, 8), pady=1)
            val_clr = ACCENT_RED if label == "Special" else TEXT_MAIN
            tk.Label(frame, text=value,
                     fg=val_clr, bg="#1a1e26",
                     font=(self._game_font, 10),
                     anchor="w").grid(row=row_i, column=1, sticky="w", pady=1)

        # Special description
        if special and special in _SPECIAL_DESC:
            tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)
            tk.Label(popup, text=_SPECIAL_DESC[special],
                     fg="#dd8844", bg="#1a1e26",
                     font=(self._game_font, 9, "italic"),
                     wraplength=380, justify="left",
                     padx=12, pady=4).pack(fill="x")

        # Description
        desc = data.get("description", "")
        if desc:
            tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)
            tk.Label(popup, text=desc,
                     fg="#aaaaaa", bg="#1a1e26",
                     font=(self._game_font, 9, "italic"),
                     wraplength=380, justify="left",
                     padx=12, pady=4).pack(fill="x")

        # ── Color dropdown ────────────────────────────────────────────────
        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=6)
        clr_frame = tk.Frame(popup, bg="#1a1e26")
        clr_frame.pack(fill="x", padx=12, pady=4)

        tk.Label(clr_frame, text="Color (optional):",
                 fg=TEXT_DIM, bg="#1a1e26",
                 font=(self._game_font, 10)).pack(side="left", padx=(0, 8))

        color_options = ["None (default)"] + sorted(colors)
        selected_color = tk.StringVar(value="None (default)")

        # Dark-themed OptionMenu
        clr_menu = tk.OptionMenu(clr_frame, selected_color, *color_options)
        clr_menu.config(bg="#1e2a3a", fg=TEXT_MAIN, relief="flat", bd=0,
                        font=(self._game_font, 10),
                        activebackground="#2a3a5a", highlightthickness=0)
        clr_menu["menu"].config(bg="#1e2a3a", fg=TEXT_MAIN,
                                activebackground="#2a3a5a",
                                activeforeground=TEXT_MAIN,
                                font=(self._game_font, 10))
        clr_menu.pack(side="left", fill="x", expand=True)

        # ── Action buttons ────────────────────────────────────────────────
        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=6)
        btn_frame = tk.Frame(popup, bg="#1a1e26")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        btn_style = dict(
            bg="#1e2a3a", fg=TEXT_MAIN, relief="flat", bd=0,
            font=(self._game_font, 10), padx=10, pady=5,
            activebackground="#2a3a5a", cursor="hand2",
        )

        def _do_select():
            c = selected_color.get()
            if c and c != "None (default)":
                cmd = f"customize {idx} {c}"
            else:
                cmd = f"customize {idx}"
            popup.destroy()
            self._send(cmd)
            self._append(f"> {cmd}\n", "prompt")

        def _do_select_buy():
            c = selected_color.get()
            if c and c != "None (default)":
                cmd = f"customize {idx} {c}"
            else:
                cmd = f"customize {idx}"
            popup.destroy()
            self._send(cmd)
            self._append(f"> {cmd}\n", "prompt")
            self.root.after(300, lambda: (
                self._send("confirm yes"),
                self._append("> confirm yes\n", "prompt"),
            ))

        def _do_cancel():
            popup.destroy()

        tk.Button(btn_frame, text=f"SELECT #{idx}",
                  command=_do_select,
                  **btn_style).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="SELECT + BUY",
                  command=_do_select_buy,
                  bg="#1e3a2a", **{k: v for k, v in btn_style.items() if k != "bg"},
                  ).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Cancel",
                  command=_do_cancel,
                  bg="#2a2a2a", fg="#888888", relief="flat", bd=0,
                  font=(self._game_font, 10), padx=10, pady=5,
                  activebackground=BORDER_CLR, cursor="hand2",
                  ).pack(side="right")

        # Position near click
        popup.update_idletasks()
        x = min(event.x_root + 10, self.root.winfo_screenwidth()  - popup.winfo_width()  - 10)
        y = min(event.y_root + 10, self.root.winfo_screenheight() - popup.winfo_height() - 10)
        popup.geometry(f"+{x}+{y}")
        popup.grab_set()

    def _show_color_only_popup(self, event):
        """
        Show a color-selection popup for clothing items (color-only customization).
        Uses stored _customize_color_payload from CUSTOMIZE_COLORS tag.
        """
        payload = getattr(self, "_customize_color_payload", None)
        if not payload:
            return

        colors    = payload.get("colors", [])
        item_name = payload.get("item_name", "this item")

        popup = tk.Toplevel(self.root)
        popup.title("Color Selection")
        popup.configure(bg="#1a1e26")
        popup.resizable(False, False)
        popup.transient(self.root)

        tk.Label(popup, text=f"Choose color for: {item_name}",
                 fg=ACCENT_CYN, bg="#1a1e26",
                 font=(self._game_font, 12, "bold"),
                 wraplength=350, justify="left",
                 padx=12, pady=8).pack(fill="x")

        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)

        clr_frame = tk.Frame(popup, bg="#1a1e26")
        clr_frame.pack(fill="x", padx=12, pady=8)
        tk.Label(clr_frame, text="Color:",
                 fg=TEXT_DIM, bg="#1a1e26",
                 font=(self._game_font, 10)).pack(side="left", padx=(0, 8))

        color_options = sorted(colors) if colors else []
        selected_color = tk.StringVar(value=color_options[0] if color_options else "")
        clr_menu = tk.OptionMenu(clr_frame, selected_color, *color_options)
        clr_menu.config(bg="#1e2a3a", fg=TEXT_MAIN, relief="flat", bd=0,
                        font=(self._game_font, 10),
                        activebackground="#2a3a5a", highlightthickness=0)
        clr_menu["menu"].config(bg="#1e2a3a", fg=TEXT_MAIN,
                                activebackground="#2a3a5a",
                                activeforeground=TEXT_MAIN,
                                font=(self._game_font, 10))
        clr_menu.pack(side="left", fill="x", expand=True)

        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=6)
        btn_frame = tk.Frame(popup, bg="#1a1e26")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        def _do_select():
            c = selected_color.get()
            if c:
                cmd = f"customize {c}"
                popup.destroy()
                self._send(cmd)
                self._append(f"> {cmd}\n", "prompt")

        def _do_cancel():
            popup.destroy()

        btn_style = dict(bg="#1e2a3a", fg=TEXT_MAIN, relief="flat", bd=0,
                         font=(self._game_font, 10), padx=10, pady=5,
                         activebackground="#2a3a5a", cursor="hand2")
        tk.Button(btn_frame, text="SELECT",
                  command=_do_select, **btn_style).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Cancel",
                  command=_do_cancel,
                  bg="#2a2a2a", fg="#888888", relief="flat", bd=0,
                  font=(self._game_font, 10), padx=10, pady=5,
                  activebackground=BORDER_CLR, cursor="hand2",
                  ).pack(side="right")

        popup.update_idletasks()
        x = min(event.x_root + 10, self.root.winfo_screenwidth()  - popup.winfo_width()  - 10)
        y = min(event.y_root + 10, self.root.winfo_screenheight() - popup.winfo_height() - 10)
        popup.geometry(f"+{x}+{y}")
        popup.grab_set()


    def _show_item_menu(self, event, item_key: str):
        """Show a context popup menu for a clicked item."""
        info = self._known_items.get(item_key)
        if not info:
            return

        state     = info.get('state', 'unknown')

        # ── Customize material — show material stat popup ─────────────────
        if state == 'customize_material':
            self._show_material_popup(event, item_key)
            return

        itype     = info.get('item_type', 'misc')
        noun      = info.get('noun', item_key.split()[-1])
        container = info.get('container', '')
        full_name = info.get('full_name', noun)

        # Build the command target from the full item name (ALL articles stripped).
        # "An invar main gauche" → "invar main gauche"
        # "A some basal moss"    → "basal moss"  (stacked articles handled)
        cmd_target = self._strip_articles(full_name.strip())

        # ── Shop item — show stat popup window instead of plain menu ──────
        if state == 'shop':
            self._show_shop_item_popup(event, info)
            return

        menu = tk.Menu(self.root, tearoff=0, bg="#1a1e26", fg=TEXT_MAIN,
                       font=(self._game_font, 10),
                       activebackground="#2a3a5a",
                       activeforeground=TEXT_MAIN,
                       relief="flat", bd=1)

        def _add(label, cmd):
            menu.add_command(label=label,
                             command=lambda c=cmd: (self._send(c),
                                                    self._append(f"> {c}\n", "prompt")))

        def _add_sep():
            menu.add_separator()

        if state in ('right_hand', 'left_hand'):
            _add(f"Inspect {noun}", f"inspect {cmd_target}")
            _add_sep()

            # ── Type-specific actions first ────────────────────────────────
            if itype in ('armor', 'shield', 'jewelry', 'container'):
                _add(f"Wear {noun}", f"wear {cmd_target}")
            if itype == 'scroll':
                _add(f"Read {noun}", f"read {cmd_target}")
            if itype == 'container':
                _add(f"Open {noun}", f"open {cmd_target}")
                _add(f"Look in {noun}", f"look in {cmd_target}")
            if itype in ('key', 'lockpick') or noun.lower().endswith('key') or noun.lower() == 'key':
                _add(f"Stow on keyring", f"put {cmd_target} in keyring")

            # ── Stow with container picker — all item types ────────────────
            containers = self._worn_containers
            if len(containers) == 0:
                _add(f"Stow {noun}", f"stow {cmd_target}")
            elif len(containers) == 1:
                cont_noun = self._item_key(containers[0]).split()[-1]
                _add(f"Stow in {cont_noun}", f"put {cmd_target} in {cont_noun}")
            else:
                menu.add_command(label=f"Stow {noun} ▶", state="disabled")
                for cont in containers:
                    cont_noun = self._item_key(cont).split()[-1]
                    _add(f"  → in {cont_noun}", f"put {cmd_target} in {cont_noun}")

            # Sheathe option for weapons if a sheath/scabbard is worn
            if itype == 'weapon':
                for cont in self._worn_containers:
                    if 'sheath' in cont.lower() or 'scabbard' in cont.lower():
                        _add(f"Sheathe in {self._item_key(cont).split()[-1]}",
                             f"put {cmd_target} in {self._item_key(cont).split()[-1]}")

            _add(f"Drop {noun}", f"drop {cmd_target}")

            _add_sep()
            _add(f"Mark {noun} (protect from bulk sell)", f"mark {cmd_target}")
            _add(f"Unmark {noun}", f"mark remove {cmd_target}")
            _add_sep()
            _add("Swap hands", "swap")

        elif state == 'worn':
            _add(f"Inspect {noun}", f"inspect {cmd_target}")
            _add_sep()
            _add(f"Remove {noun}", f"remove {cmd_target}")
            if itype == 'container':
                _add(f"Open {noun}", f"open {cmd_target}")
                _add(f"Close {noun}", f"close {cmd_target}")
                _add(f"Look in {noun}", f"look in {cmd_target}")

        elif state == 'in_container':
            cont_cmd = self._strip_articles(container.strip()) if container else 'container'
            # Use just the last word of container name as the server identifier
            cont_noun = cont_cmd.split()[-1] if cont_cmd else 'container'
            _add(f"Inspect {noun}", f"inspect {cmd_target}")
            _add_sep()
            _add(f"Get {noun} from {cont_noun}", f"get {cmd_target} from {cont_noun}")
            if itype == 'container':
                _add(f"Get {noun} from {cont_noun} (open it)",
                     f"get {cmd_target} from {cont_noun}")
            _add_sep()
            _add(f"Mark {noun} (protect from bulk sell)", f"mark {cmd_target}")
            _add(f"Unmark {noun}", f"mark remove {cmd_target}")

        else:
            _add(f"Inspect {noun}", f"inspect {cmd_target}")
            _add(f"Get {noun}", f"get {cmd_target}")

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _show_shop_item_popup(self, event, info: dict):
        """
        Show a floating stat-card window for a shop item.
        Has ORDER #, BUY #, and CUSTOMIZE buttons.
        """
        data      = info.get("shop_data", {})
        idx       = info.get("shop_idx", "?")
        full_name = info.get("full_name", "unknown item")
        itype     = data.get("item_type", "misc")
        noun      = info.get("noun", "item")
        price     = data.get("price", 0)

        # ── Stat lines ────────────────────────────────────────────────────
        stat_lines = []

        def _kv(label, value):
            return (label, str(value))

        if itype == "weapon":
            df   = data.get("damage_factor") or 0.0
            spd  = data.get("weapon_speed") or 5
            cat  = (data.get("weapon_category") or "unknown").replace("_", " ").title()
            dt   = (data.get("damage_type") or "slash").replace(",", " / ")
            eb   = data.get("enchant_bonus") or 0
            ab   = data.get("attack_bonus") or 0
            db   = data.get("damage_bonus") or 0
            lvl  = data.get("level_required") or 0
            stat_lines += [
                _kv("Type",           cat),
                _kv("Damage type",    dt),
                _kv("Damage factor",  f"{float(df):.3f}"),
                _kv("Roundtime",      f"{spd}s"),
            ]
            if eb:  stat_lines.append(_kv("Enchantment", f"+{eb}"))
            if ab:  stat_lines.append(_kv("Attack bonus", f"+{ab}"))
            if db:  stat_lines.append(_kv("Damage bonus", f"+{db}"))
            if lvl: stat_lines.append(_kv("Level req.", str(lvl)))

        elif itype == "armor":
            asg_groups = {
                1:"cloth/unarmored",2:"cloth/unarmored",3:"soft leather",4:"soft leather",
                5:"hard leather",6:"hard leather",7:"double leather",8:"double leather",
                9:"metal breastplate",10:"metal breastplate",11:"chain mail",12:"chain mail",
                13:"double chain",14:"double chain",15:"plate armor",16:"plate armor",
                17:"heavy plate",18:"heavy plate",19:"full plate",20:"full plate",
            }
            asg  = data.get("armor_asg") or 1
            grp  = asg_groups.get(int(asg), f"ASG {asg}")
            eb   = data.get("enchant_bonus") or 0
            ap   = data.get("action_penalty") or 0
            sh   = data.get("spell_hindrance") or 0
            db   = data.get("defense_bonus") or 0
            lvl  = data.get("level_required") or 0
            stat_lines += [_kv("Armor type", grp.title()), _kv("ASG", str(asg))]
            if eb:  stat_lines.append(_kv("Enchantment", f"+{eb}"))
            if db:  stat_lines.append(_kv("Defense bonus", f"+{db}"))
            if ap:  stat_lines.append(_kv("Action penalty", f"{ap}%"))
            if sh:  stat_lines.append(_kv("Spell hindrance", f"{sh}%"))
            if lvl: stat_lines.append(_kv("Level req.", str(lvl)))

        elif itype == "shield":
            size = (data.get("shield_size") or "small").title()
            ds   = data.get("shield_ds") or 0
            eb   = data.get("enchant_bonus") or 0
            lvl  = data.get("level_required") or 0
            stat_lines += [_kv("Size", size), _kv("Shield DS", f"+{ds}")]
            if eb:  stat_lines.append(_kv("Enchantment", f"+{eb}"))
            if lvl: stat_lines.append(_kv("Level req.", str(lvl)))

        elif itype == "container":
            cap = data.get("container_capacity") or 0
            loc = (data.get("worn_location") or "").replace("_", " ").title()
            stat_lines.append(_kv("Capacity", f"{cap} items" if cap else "unlimited"))
            if loc: stat_lines.append(_kv("Worn on", loc))

        elif itype in ("herb", "consumable"):
            ht  = (data.get("herb_heal_type") or "").replace("_", " ").title()
            ha  = data.get("herb_heal_amount") or 0
            if ht: stat_lines.append(_kv("Heals", ht))
            if ha: stat_lines.append(_kv("Amount", f"+{ha}"))

        wt = data.get("weight") or 0.0
        stat_lines.append(_kv("Weight", f"{float(wt):.1f} lbs"))

        # ── Build popup window ────────────────────────────────────────────
        popup = tk.Toplevel(self.root)
        popup.title("Item Details")
        popup.configure(bg="#1a1e26")
        popup.resizable(False, False)
        popup.transient(self.root)

        # Title bar
        tk.Label(popup, text=full_name,
                 fg=ACCENT_YEL, bg="#1a1e26",
                 font=(self._game_font, 12, "bold"),
                 wraplength=340, justify="left",
                 padx=12, pady=8).pack(fill="x")

        # Price
        tk.Label(popup, text=f"Price:  {price:,} silver",
                 fg=ACCENT_GRN, bg="#1a1e26",
                 font=(self._game_font, 10),
                 padx=12).pack(anchor="w")

        # Separator
        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)

        # Stat grid
        frame = tk.Frame(popup, bg="#1a1e26")
        frame.pack(fill="x", padx=12, pady=2)
        for row_i, (label, value) in enumerate(stat_lines):
            tk.Label(frame, text=label + ":",
                     fg=ACCENT_CYN, bg="#1a1e26",
                     font=(self._game_font, 10),
                     anchor="w").grid(row=row_i, column=0, sticky="w", padx=(0, 8), pady=1)
            tk.Label(frame, text=value,
                     fg=TEXT_MAIN, bg="#1a1e26",
                     font=(self._game_font, 10),
                     anchor="w").grid(row=row_i, column=1, sticky="w", pady=1)

        # Description
        desc = data.get("description") or ""
        if desc:
            tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=4)
            tk.Label(popup, text=desc,
                     fg="#aaaaaa", bg="#1a1e26",
                     font=(self._game_font, 9, "italic"),
                     wraplength=340, justify="left",
                     padx=12, pady=4).pack(fill="x")

        # Action buttons
        tk.Frame(popup, bg=BORDER_CLR, height=1).pack(fill="x", padx=8, pady=6)
        btn_frame = tk.Frame(popup, bg="#1a1e26")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        btn_style = dict(
            bg="#1e2a3a", fg=TEXT_MAIN, relief="flat", bd=0,
            font=(self._game_font, 10), padx=10, pady=5,
            activebackground="#2a3a5a", cursor="hand2",
        )

        def _do(cmd):
            popup.destroy()
            self._send(cmd)
            self._append(f"> {cmd}\n", "prompt")

        tk.Button(btn_frame, text=f"ORDER {idx}",
                  command=lambda: _do(f"order {idx}"),
                  **btn_style).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text=f"BUY {idx}",
                  command=lambda: _do(f"buy {idx}"),
                  **btn_style).pack(side="left", padx=(0, 4))
        if itype in ("weapon", "armor", "shield", "jewelry"):
            tk.Button(btn_frame, text="CUSTOMIZE",
                      command=lambda: _do(f"order {idx}") or _do("customize"),
                      **btn_style).pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Close",
                  command=popup.destroy,
                  bg="#2a2a2a", fg="#888888", relief="flat", bd=0,
                  font=(self._game_font, 10), padx=10, pady=5,
                  activebackground=BORDER_CLR, cursor="hand2",
                  ).pack(side="right")

        # Position near click
        popup.update_idletasks()
        x = min(event.x_root + 10, self.root.winfo_screenwidth()  - popup.winfo_width()  - 10)
        y = min(event.y_root + 10, self.root.winfo_screenheight() - popup.winfo_height() - 10)
        popup.geometry(f"+{x}+{y}")
        popup.grab_set()

    def _set_stance(self, stance: str):
        cmd = f"stance {stance.lower()}"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")
        self._stance_lbl.config(text=stance)

    def _passive_hp_regen(self):
        """
        Tick HP up by the stored regen rate when the player is out of combat.
        The server regenerates every 10 seconds (100 ticks at 10/sec).
        We match that interval. Regen only fires when:
          - Player is in a room (logged in)
          - _in_combat is False (cleared by kill XP, flee, room change, or clear message)
          - HP is below max
          - HP > 0 (not dead)
        """
        REGEN_INTERVAL_MS = 10_000   # matches server _regen_tick (100 ticks @ 10/sec)
        try:
            in_room = self._current_room_id is not None
            cur     = self._hp_bar._cur
            max_hp  = self._hp_bar._max
            rate    = self._hp_regen_rate

            if in_room and not self._in_combat and rate > 0 and 0 < cur < max_hp:
                new_hp = min(cur + int(rate), max_hp)
                self._hp_bar.update(new_hp, max_hp)
        except Exception:
            pass
        self.root.after(REGEN_INTERVAL_MS, self._passive_hp_regen)

    def _start_rt_full(self, total_seconds: int):
        """Start RT bar with the full original duration (from 'Roundtime: N sec.')"""
        import time as _time
        self._rt_total    = float(total_seconds)
        self._rt_end_time = _time.time() + total_seconds
        self._tick_rt()

    def _start_rt_remaining(self, remaining_seconds: int):
        """Sync RT bar to remaining time without changing total (from GSIV tag or prompt)"""
        import time as _time
        if self._rt_total <= 0:
            # No full duration known yet — use remaining as total
            self._rt_total = float(remaining_seconds)
        self._rt_end_time = _time.time() + remaining_seconds
        if remaining_seconds > 0:
            self._tick_rt()
        else:
            self._clear_rt()

    def _clear_rt(self):
        self._rt_end_time = 0.0
        self._rt_total    = 0.0
        self._rt_canvas.delete("all")

    def _tick_rt(self):
        import time as _time
        remaining = self._rt_end_time - _time.time()
        w = self._rt_canvas.winfo_width()  or 60
        h = self._rt_canvas.winfo_height() or 28
        self._rt_canvas.delete("all")
        if remaining > 0 and self._rt_total > 0:
            fill_w = int(w * remaining / self._rt_total)
            fill_w = max(1, min(fill_w, w))
            # Bar colour shifts red→yellow→white as time runs out
            pct = remaining / self._rt_total
            if pct > 0.6:
                color = "#dddddd"
            elif pct > 0.3:
                color = "#e3b341"
            else:
                color = "#f85149"
            self._rt_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")
            self.root.after(50, self._tick_rt)  # 20 fps
        else:
            # RT just expired naturally — fire nav if waiting
            if self._rt_end_time > 0:   # only if we were actually timing (not just cleared)
                self._nav_on_ready()
            self._clear_rt()

    def _load_config(self):
        """Restore window geometry, sash position, font, and server list."""
        self._saved_sash = None
        self._saved_dock_layout = {}
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    cfg = json.load(f)
                if "geometry" in cfg:
                    try:
                        self.root.geometry(cfg["geometry"])
                    except Exception:
                        pass
                if "font_size" in cfg:
                    self._font_size = int(cfg["font_size"])
                if "font_family" in cfg:
                    self._game_font = cfg["font_family"]
                if "panel_font_size" in cfg:
                    self._panel_font_size = int(cfg["panel_font_size"])
                audio = cfg.get("audio", {})
                self._music_enabled = bool(audio.get("music_enabled", True))
                self._sfx_enabled = bool(audio.get("sfx_enabled", True))
                self._music_volume = int(audio.get("music_volume", 65))
                self._sfx_volume = int(audio.get("sfx_volume", 75))
                self._saved_sash = cfg.get("sash_x")
                # Restore last-used host/port
                if "host" in cfg:
                    self.host = cfg["host"]
                if "port" in cfg:
                    self.port = int(cfg["port"])
                # Restore saved server list
                self._saved_servers = cfg.get("saved_servers", [])
                self._saved_dock_layout = cfg.get("dock_layout", {})
                saved_input_mode = str(cfg.get("input_mode", "command")).strip().lower()
                saved_comm_mode = str(cfg.get("comm_input_mode", "")).strip().lower()
                valid_ids = {mode["id"] for mode in INPUT_MODES}
                valid_comm_ids = {mode["id"] for mode in COMM_INPUT_MODES}
                if saved_comm_mode in valid_comm_ids:
                    self._comm_input_mode = saved_comm_mode
                if saved_input_mode in valid_ids:
                    self._input_mode = saved_input_mode
                if self._input_mode in valid_comm_ids:
                    self._comm_input_mode = self._input_mode
                if self._comm_input_mode not in valid_comm_ids:
                    self._comm_input_mode = COMM_INPUT_MODES[0]["id"]
                # Restore auto-login settings
                al = cfg.get("auto_login", {})
                self._auto_login_enabled   = bool(al.get("enabled", False))
                self._auto_login_username  = str(al.get("username", ""))
                self._auto_login_password  = str(al.get("password", ""))
                self._auto_login_char_slot = int(al.get("char_slot", 1))
        except Exception:
            pass

        # Always ensure the default local server is in the list
        default = {"label": "Local Server", "host": "127.0.0.1", "port": DEFAULT_PORT}
        if not any(s["host"] == default["host"] and s["port"] == default["port"]
                   for s in self._saved_servers):
            self._saved_servers.append(default)

    def _save_config(self):
        try:
            sash_x = None
            try:
                sash_x = self._paned.sash_coord(0)[0]
            except Exception:
                pass
            dock_layout = {}
            if self._dock:
                dock_layout = self._dock.get_layout()
            cfg = {
                "geometry":        self.root.geometry(),
                "font_size":       self._font_size,
                "font_family":     self._game_font,
                "panel_font_size": self._panel_font_size,
                "sash_x":          sash_x,
                "host":            self.host,
                "port":            self.port,
                "saved_servers":   self._saved_servers,
                "dock_layout":     dock_layout,
                "input_mode":      self._input_mode,
                "comm_input_mode": self._comm_input_mode,
                "auto_login": {
                    "enabled":   self._auto_login_enabled,
                    "username":  self._auto_login_username,
                    "password":  self._auto_login_password,
                    "char_slot": self._auto_login_char_slot,
                },
                "audio": {
                    "music_enabled": self._music_enabled,
                    "sfx_enabled": self._sfx_enabled,
                    "music_volume": self._music_volume,
                    "sfx_volume": self._sfx_volume,
                },
            }
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def _audio_tick(self):
        try:
            if self._audio:
                self._audio.tick()
        finally:
            self.root.after(200, self._audio_tick)

    def _play_sfx(
        self,
        file_name: str,
        *,
        stop_after_ms: Optional[int] = None,
        stop_fraction: Optional[float] = None,
    ):
        if not self._audio:
            return
        try:
            self._audio.play_sfx(
                file_name,
                stop_after_ms=stop_after_ms,
                stop_fraction=stop_fraction,
            )
        except Exception:
            pass

    def _handle_sfx_for_line(self, clean: str):
        if not clean:
            return
        if LEVEL_UP_SFX_RE.search(clean):
            self._play_sfx(SFX_LEVEL_UP)
            return
        if HIDE_SFX_RE.search(clean):
            self._play_sfx(SFX_HIDE)
            return
        if AMBUSH_SFX_RE.search(clean):
            self._play_sfx(SFX_AMBUSH)
            return
        if SLEEP_SFX_RE.search(clean):
            self._play_sfx(SFX_SLEEP, stop_fraction=0.5)
            return
        if LOOT_SFX_RE.search(clean):
            self._play_sfx(SFX_LOOT)

    def _restore_layout(self):
        """Restore the last saved dock layout and main sash positions."""
        if not self._dock:
            return

        def _apply_once():
            try:
                self.root.update_idletasks()
            except Exception:
                pass
            try:
                if self._saved_dock_layout:
                    self._dock.apply_layout(self._saved_dock_layout)
                elif self._saved_sash is not None:
                    self._paned.sash_place(0, int(self._saved_sash), 1)
            except Exception:
                pass

        self.root.after(150, _apply_once)
        self.root.after(450, _apply_once)
        self.root.after(900, _apply_once)

    # ════════════════════════════════════════════
    # Combat button handlers
    # ════════════════════════════════════════════

    # Regex to detect creature/enemy lines from room description
    # Matches lines like "A large rat is here." / "A snow orc attacks you!"
    _ENEMY_LINE_RE = re.compile(
        r"^(?:A|An|The)\s+([\w\s\-]+?)\s+(?:is here|stands here|crouches|attacks|growls|eyes you|lunges|snarls|hisses|charges)",
        re.IGNORECASE)

    # Death/defeat message patterns from GemStone
    _DEATH_RE = re.compile(
        r"(?:rolls over and dies|is dead|crumples to the ground|"
        r"falls to the ground|has been slain|is slain|"
        r"you (have )?killed|stops moving|ceases to move|"
        r"collapses in a heap|is no more)",
        re.IGNORECASE)

    def _parse_enemies_from_line(self, line: str):
        """Check a line for creature mentions, deaths, flees, and update enemy/target state."""
        line_lower = line.lower()

        # Detect flee/retreat of current target
        if self._current_target and FLEE_RE.search(line):
            if self._current_target_match and self._current_target_match in line_lower:
                self._room_enemies = [
                    e for e in self._room_enemies
                    if e.get("token") != self._current_target
                ]
                self._clear_target()
                return

        # Detect death of current target
        if self._current_target and self._DEATH_RE.search(line):
            others = [
                e.get("match", "")
                for e in self._room_enemies
                if e.get("token") != self._current_target
            ]
            if self._current_target_match and (
                self._current_target_match in line_lower or
                not any(match and match in line_lower for match in others)
            ):
                self._room_enemies = [
                    e for e in self._room_enemies
                    if e.get("token") != self._current_target
                ]
                self._clear_target()
                return

        if self._sync_connected and self._room_enemies:
            return

        def _add_enemy(name: str):
            name = name.strip().lower()
            # Filter out non-mob words (common false positives)
            skip = {"obvious", "path", "exit", "you", "your", "the", "area", "room"}
            if not name or name in skip or len(name) < 3:
                return
            if not any(e.get("token") == name for e in self._room_enemies):
                self._room_enemies.append({
                    "token": name,
                    "display": name,
                    "match": name,
                })

        # Pattern 1: "A/An/The <name> is here / attacks / etc."
        m = self._ENEMY_LINE_RE.match(line)
        if m:
            _add_enemy(m.group(1))

        # Pattern 2: "You also see a fanged rodent [Level 1]."
        # Covers the room look description line
        for m2 in YOU_ALSO_SEE_RE.finditer(line):
            _add_enemy(m2.group(1))

        # Pattern 3: "A fanged rodent just arrived from the north."
        m3 = ARRIVED_RE.match(line)
        if m3:
            _add_enemy(m3.group(1))

    # ════════════════════════════════════════════
    # Combat command handlers
    # ════════════════════════════════════════════

    def _cmd_attack(self):
        """Attack current target. If no target set yet, auto-pick first known enemy."""
        if not self._current_target and self._room_enemies:
            self._set_target_entry(self._room_enemies[0], fg=ACCENT_RED)
        if self._current_target:
            cmd = f"attack {self._current_target}"
        else:
            cmd = "attack"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    def _cmd_ambush(self):
        """Ambush current target. Requires being hidden and having a target."""
        if not self._current_target and self._room_enemies:
            self._set_target_entry(self._room_enemies[0], fg=ACCENT_RED)
        if self._current_target:
            cmd = f"ambush {self._current_target}"
        else:
            self._append("[No target set — hide first, then set a target]\n", "sys")
            return
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    def _cmd_target_monster(self):
        """
        Cycle through known enemies in room on each click.
        1 enemy  → set it directly (no popup).
        2+ enemy → cycle: rat → orc → rat → orc …
        0 enemy  → show no target.
        """
        if not self._room_enemies:
            self._clear_target()
            return

        if len(self._room_enemies) == 1:
            self._set_target_entry(self._room_enemies[0])
            return

        # Cycle index
        tokens = [e.get("token") for e in self._room_enemies]
        if self._current_target in tokens:
            idx = tokens.index(self._current_target)
            next_idx = (idx + 1) % len(self._room_enemies)
        else:
            next_idx = 0
        self._set_target_entry(self._room_enemies[next_idx])

    def _set_target(self, name: str):
        self._set_target_entry({"token": name, "display": name, "match": name.lower()})

    def _set_target_entry(self, entry: dict, fg=ACCENT_YEL):
        token = str(entry.get("token") or "").strip()
        if not token:
            return
        display = str(entry.get("display") or token).strip()
        self._current_target = token
        self._current_target_match = str(entry.get("match") or display).strip().lower()
        self._target_lbl.config(text=f"▶ {display}", fg=fg)

    def _clear_target(self):
        self._current_target = ""
        self._current_target_match = ""
        self._target_lbl.config(text="No target", fg=TEXT_DIM)

    # ════════════════════════════════════════════
    # AIM body-part targeting (GS4 AIM command)
    # ════════════════════════════════════════════

    # All aimable locations grouped by body region (biped baseline — server
    # validates against creature body type on each attack).
    _AIM_GROUPS = [
        ("Head & Eyes",  ["head", "neck", "right eye", "left eye"]),
        ("Torso",        ["chest", "abdomen", "back"]),
        ("Arms & Hands", ["right arm", "left arm", "right hand", "left hand"]),
        ("Legs",         ["right leg", "left leg"]),
    ]

    # Short display labels for buttons (keeps grid compact)
    _AIM_LABELS = {
        "head":       "Head",
        "neck":       "Neck",
        "right eye":  "R.Eye",
        "left eye":   "L.Eye",
        "chest":      "Chest",
        "abdomen":    "Abdomen",
        "back":       "Back",
        "right arm":  "R.Arm",
        "left arm":   "L.Arm",
        "right hand": "R.Hand",
        "left hand":  "L.Hand",
        "right leg":  "R.Leg",
        "left leg":   "L.Leg",
    }

    # Aim difficulty hints shown in the popup tooltip (mirrors body_types.lua)
    _AIM_DIFFICULTY = {
        "head":       "Moderate",
        "neck":       "Hard",
        "right eye":  "Very Hard",
        "left eye":   "Very Hard",
        "chest":      "Easy",
        "abdomen":    "Easy",
        "back":       "Moderate",
        "right arm":  "Moderate",
        "left arm":   "Moderate",
        "right hand": "Moderate",
        "left hand":  "Moderate",
        "right leg":  "Moderate",
        "left leg":   "Moderate",
    }

    def _update_bodypart_btn(self):
        """Update the Body Part button label to reflect current AIM preference."""
        try:
            if self._current_aim:
                short = self._AIM_LABELS.get(self._current_aim,
                                              self._current_aim.title())
                self._bodypart_btn.config(
                    text=f"🎯 [{short}]",
                    fg="#ffdd88",
                    bg="#2a2a1a",
                )
            else:
                self._bodypart_btn.config(
                    text="🎯  Body Part",
                    fg="#88bbff",
                    bg="#1a2a3a",
                )
        except Exception:
            pass

    def _set_aim(self, location: str, popup=None):
        """Send AIM <location> and close the popup."""
        if popup:
            try:
                popup.destroy()
            except Exception:
                pass
        if location == "clear":
            cmd = "aim clear"
            self._current_aim = ""
        else:
            cmd = f"aim {location}"
            self._current_aim = location
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")
        self._update_bodypart_btn()

    def _cmd_aim_bodypart(self):
        """
        Open the AIM body part picker popup.
        Sends AIM <location> to set a persistent aim preference on the server.
        The aim persists across monsters — every attack goes for that spot
        until AIM CLEAR is used.
        """
        win = tk.Toplevel(self.root)
        win.title("Body Part")
        win.configure(bg=BG_APP)
        win.resizable(False, False)
        win.attributes("-topmost", True)

        # ── Header ────────────────────────────────────────────────────────
        header = tk.Frame(win, bg="#0d1a2a", pady=6)
        header.pack(fill="x")
        tk.Label(header, text="🎯  Body Part Targeting",
                 fg=ACCENT_BLUE, bg="#0d1a2a",
                 font=("Georgia", 11, "bold")).pack(side="left", padx=12)

        # Current aim status pill
        if self._current_aim:
            short = self._AIM_LABELS.get(self._current_aim,
                                          self._current_aim.title())
            status_text = f"Currently: {short}"
            status_fg   = "#ffdd88"
        else:
            status_text = "Currently: Random"
            status_fg   = TEXT_DIM
        tk.Label(header, text=status_text,
                 fg=status_fg, bg="#0d1a2a",
                 font=("Georgia", 9, "italic")).pack(side="right", padx=12)

        tk.Frame(win, bg=BORDER_CLR, height=1).pack(fill="x")

        # ── Hint text ─────────────────────────────────────────────────────
        tk.Label(win,
                 text="Aim persists across all enemies until cleared.\n"
                      "Success depends on Combat Maneuvers & creature level.",
                 fg=TEXT_DIM, bg=BG_APP,
                 font=("Georgia", 8, "italic"),
                 justify="center").pack(pady=(6, 2))

        tk.Frame(win, bg=BORDER_CLR, height=1).pack(fill="x", padx=12, pady=4)

        # ── Body part buttons by group ────────────────────────────────────
        body_frame = tk.Frame(win, bg=BG_APP)
        body_frame.pack(padx=14, pady=(2, 4), fill="x")

        btn_style = dict(
            relief="flat", bd=0,
            font=("Georgia", 10, "bold"),
            cursor="hand2",
            padx=10, pady=6,
            width=8,
        )

        for group_name, locations in self._AIM_GROUPS:
            # Group label
            grp_row = tk.Frame(body_frame, bg=BG_APP)
            grp_row.pack(fill="x", pady=(6, 2))
            tk.Label(grp_row, text=group_name.upper(),
                     fg="#444e5c", bg=BG_APP,
                     font=("Georgia", 7, "bold")).pack(side="left", padx=2)
            tk.Frame(grp_row, bg="#1c2535", height=1).pack(
                side="left", fill="x", expand=True, padx=(4, 0))

            # Button row for this group
            btn_row = tk.Frame(body_frame, bg=BG_APP)
            btn_row.pack(fill="x", pady=1)

            for loc in locations:
                is_active = (loc == self._current_aim)
                diff      = self._AIM_DIFFICULTY.get(loc, "Moderate")
                label     = self._AIM_LABELS.get(loc, loc.title())

                # Color coding: active = gold, by difficulty otherwise
                if is_active:
                    bg_col = "#3a2e00"
                    fg_col = "#ffdd44"
                    border = "#5a4800"
                elif diff == "Very Hard":
                    bg_col = "#2a1a2a"
                    fg_col = "#dd88ff"
                elif diff == "Hard":
                    bg_col = "#2a1a1a"
                    fg_col = "#ff9988"
                elif diff == "Easy":
                    bg_col = "#0d2a1a"
                    fg_col = "#88ffaa"
                else:
                    bg_col = "#1a2a3a"
                    fg_col = "#88bbff"

                btn = tk.Button(
                    btn_row,
                    text=("✓ " if is_active else "") + label,
                    bg=bg_col, fg=fg_col,
                    activebackground="#2a3a5a",
                    command=lambda l=loc, w=win: self._set_aim(l, w),
                    **btn_style,
                )
                btn.pack(side="left", padx=3, pady=1)

                # Difficulty tooltip on hover
                tip_shown = [None]
                def _show_tip(ev, d=diff, l=loc, b=btn):
                    if tip_shown[0]:
                        return
                    tip = tk.Toplevel(win)
                    tip.overrideredirect(True)
                    tip.attributes("-topmost", True)
                    tip.configure(bg="#1c2128")
                    tk.Frame(tip, bg=ACCENT_BLUE, height=1).pack(fill="x")
                    inner = tk.Frame(tip, bg="#1c2128", padx=8, pady=4)
                    inner.pack()
                    tk.Label(inner, text=l.title(),
                             fg="#ffffff", bg="#1c2128",
                             font=("Georgia", 9, "bold")).pack(anchor="w")
                    tk.Label(inner, text=f"Aim difficulty: {d}",
                             fg=TEXT_DIM, bg="#1c2128",
                             font=("Georgia", 8)).pack(anchor="w")
                    tk.Frame(tip, bg="#30363d", height=1).pack(fill="x")
                    tip.update_idletasks()
                    tx = min(ev.x_root + 10,
                             tip.winfo_screenwidth() - tip.winfo_reqwidth() - 4)
                    ty = min(ev.y_root + 10,
                             tip.winfo_screenheight() - tip.winfo_reqheight() - 4)
                    tip.geometry(f"+{tx}+{ty}")
                    tip_shown[0] = tip
                def _hide_tip(_ev=None):
                    if tip_shown[0]:
                        try:
                            tip_shown[0].destroy()
                        except Exception:
                            pass
                        tip_shown[0] = None
                btn.bind("<Enter>", _show_tip)
                btn.bind("<Leave>", _hide_tip)

        # ── Separator ─────────────────────────────────────────────────────
        tk.Frame(win, bg=BORDER_CLR, height=1).pack(fill="x", padx=12, pady=(6, 4))

        # ── None (Clear) button ────────────────────────────────────────────
        none_row = tk.Frame(win, bg=BG_APP)
        none_row.pack(fill="x", padx=14, pady=(2, 12))

        none_active = (self._current_aim == "")
        tk.Button(
            none_row,
            text=("✓ " if none_active else "") + "None  (Random)",
            bg="#2a1a1a" if not none_active else "#1a2a1a",
            fg="#cc6666" if not none_active else "#88ff88",
            activebackground="#3a2a2a",
            font=("Georgia", 10, "bold"),
            relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2",
            command=lambda w=win: self._set_aim("clear", w),
        ).pack(side="left", padx=3)

        tk.Label(none_row,
                 text="Clears aim — each attack\nhits a random location.",
                 fg=TEXT_DIM, bg=BG_APP,
                 font=("Georgia", 8, "italic")).pack(side="left", padx=(8, 0))

        # Position near button
        win.update_idletasks()
        try:
            bx = self._bodypart_btn.winfo_rootx()
            by = self._bodypart_btn.winfo_rooty()
            bh = self._bodypart_btn.winfo_height()
            wx = bx
            wy = by + bh + 4
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            ww = win.winfo_reqwidth()
            wh = win.winfo_reqheight()
            if wx + ww > sw:
                wx = sw - ww - 8
            if wy + wh > sh:
                wy = by - wh - 4
            win.geometry(f"+{wx}+{wy}")
        except Exception:
            pass

        win.grab_set()
        win.focus_set()

    def _cmd_loot(self):
        self._send("loot all")
        self._append("> loot all\n", "prompt")

    def _cmd_look(self):
        self._send("look")
        self._append("> look\n", "prompt")

    # ── Lockbox helpers ───────────────────────────────────────────────────────

    def _get_lockbox_noun(self) -> str:
        """
        Return the noun of the live lockbox/coffer in hand.
        Prefer sync state, then parsed inventory, and only fall back to the
        remembered noun when sync is unavailable.
        """
        BOX_NOUNS = {"box", "coffer", "chest", "crate", "strongbox", "lockbox", "safe"}
        for hand_key in ("right_hand", "left_hand"):
            noun = str(self._last_sync.get(hand_key) or "").strip().lower()
            if noun and any(b in noun for b in BOX_NOUNS):
                self._last_lockbox_noun = noun
                return noun

        if self._sync_connected:
            return ""

        for item in [
            self._known_items.get(k)
            for k in self._known_items
            if self._known_items[k].get("state") in ("right_hand", "left_hand")
        ]:
            if item:
                noun = item.get("noun", "")
                if any(b in noun for b in BOX_NOUNS):
                    self._last_lockbox_noun = noun
                    return noun
        # Return empty string if nothing lockable is in hand — callers guard
        return self._last_lockbox_noun

    def _cmd_pick(self):
        noun = self._get_lockbox_noun()
        if not noun:
            self._append("[You aren't holding a lockable container.]\n", "system")
            return
        cmd  = f"pick {noun}"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    def _cmd_detect(self):
        noun = self._get_lockbox_noun()
        if not noun:
            self._append("[You aren't holding a lockable container.]\n", "system")
            return
        cmd  = f"detect {noun}"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    def _cmd_disarm(self):
        noun = self._get_lockbox_noun()
        if not noun:
            self._append("[You aren't holding a lockable container.]\n", "system")
            return
        cmd  = f"disarm {noun}"
        self._send(cmd)
        self._append(f"> {cmd}\n", "prompt")

    # ════════════════════════════════════════════
    # Cleanup
    # ════════════════════════════════════════════

    def on_close(self):
        self._save_config()
        if self._audio:
            self._audio.shutdown()
        if self._telnet:
            self._telnet.stop()
        self.root.destroy()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="GemStone IV HUD Client")
    ap.add_argument("--host", default=DEFAULT_HOST, help="Server hostname")
    ap.add_argument("--port", default=DEFAULT_PORT, type=int, help="Server port")
    args = ap.parse_args()

    root = tk.Tk()
    if not os.path.exists(CONFIG_PATH):
        root.geometry("1180x680")

    app = HUDApp(root, args.host, args.port)
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_close()


if __name__ == "__main__":
    main()
