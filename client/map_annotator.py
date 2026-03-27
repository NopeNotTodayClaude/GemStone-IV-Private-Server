#!/usr/bin/env python3
"""
map_annotator.py — GemStone IV HUD  ·  Map Room Annotator
==========================================================
A standalone GUI tool that lets you click directly on a zone map image
to mark which pixel region corresponds to which room ID.

Usage:
    python client/map_annotator.py

Workflow per zone:
  1. Select zone from the dropdown at the top.
  2. Type a Room ID in the "Room ID" box.
  3. Click-and-drag a rectangle over that room's box on the map.
  4. The overlay turns green/blue when placed — repeat for every room.
  5. Click  [Save]  when done with a zone (auto-saves to map_regions.json).

Tips:
  • Scroll wheel  = zoom in/out around mouse
  • Middle-drag or right-drag = pan the view
  • Click an existing green box = select it (shows room ID in the field)
  • Delete key = remove the selected annotation
  • Ctrl+Z = undo last placed annotation
  • [Clear Zone] = wipe all annotations for the current zone (asks first)

Requires: Pillow  (pip install Pillow)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from typing import Optional, Dict, Tuple, List

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow is required: pip install Pillow")
    sys.exit(1)

# ── paths ──────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(BASE_DIR, "data")
REGIONS_PATH = os.path.join(DATA_DIR, "map_regions.json")
GRAPH_PATH   = os.path.join(DATA_DIR, "room_graph.json")

# ── colours ─────────────────────────────────────────────────────────────
BG      = "#0d1117"
FG      = "#e6edf3"
DIM     = "#8b949e"
ACCENT  = "#58a6ff"
GREEN   = "#3fb950"
YELLOW  = "#e3b341"
RED     = "#f85149"
PANEL   = "#161b22"
INPUT   = "#1c2128"
BORDER  = "#30363d"


# ── helpers ──────────────────────────────────────────────────────────────

def load_graph() -> Dict[int, dict]:
    if not os.path.exists(GRAPH_PATH):
        return {}
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.get("rooms", {}).items()}


def load_regions() -> dict:
    if not os.path.exists(REGIONS_PATH):
        return {"maps": {}}
    with open(REGIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_regions(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REGIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── main app ─────────────────────────────────────────────────────────────

class AnnotatorApp:
    ZOOM_MIN = 0.05
    ZOOM_MAX = 8.0

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GemStone IV — Map Annotator")
        self.root.configure(bg=BG)
        self.root.geometry("1100x780")
        self.root.minsize(800, 600)

        self.graph   = load_graph()
        self.regions = load_regions()

        # Derive zone list from graph + existing regions
        graph_zones  = sorted({r.get("zone_name", "") for r in self.graph.values() if r.get("zone_name")})
        region_zones = sorted(self.regions.get("maps", {}).keys())
        all_zones    = sorted(set(graph_zones) | set(region_zones))
        self._zones  = all_zones if all_zones else ["(no zones found)"]

        # State
        self._zone:      str  = self._zones[0]
        self._pil_img           = None
        self._tk_img            = None
        self._zoom:      float = 1.0
        self._pan_x:     float = 0.0
        self._pan_y:     float = 0.0
        self._drag_start        = None
        self._drag_btn:  int   = 0    # 1=draw, 2/3=pan
        self._draw_start        = None   # canvas coords for rect drag
        self._rubber_id: Optional[int] = None

        # {room_id: (img_x, img_y, img_w, img_h)}
        self._annotations: Dict[int, Tuple[int,int,int,int]] = {}
        self._selected:  Optional[int] = None
        self._undo_stack: List[Tuple[str, int, Optional[Tuple]]] = []  # (op, rid, prev)
        self._overlay_ids: Dict[int, List[int]] = {}  # room_id → [canvas item ids]

        self._build_ui()
        self._load_zone(self._zone)

    # ── UI construction ────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top toolbar ──
        tb = tk.Frame(self.root, bg=PANEL, pady=4)
        tb.pack(fill="x", padx=4, pady=(4, 0))

        tk.Label(tb, text="Zone:", fg=DIM, bg=PANEL, font=("Courier New", 9)).pack(side="left", padx=(6,2))
        self._zone_var = tk.StringVar(value=self._zone)
        zone_cb = ttk.Combobox(tb, textvariable=self._zone_var, values=self._zones,
                               state="readonly", width=28,
                               font=("Courier New", 9))
        zone_cb.pack(side="left", padx=2)
        zone_cb.bind("<<ComboboxSelected>>", lambda _: self._on_zone_change())

        tk.Label(tb, text="Room ID:", fg=DIM, bg=PANEL, font=("Courier New", 9)).pack(side="left", padx=(14,2))
        self._rid_var = tk.StringVar()
        self._rid_entry = tk.Entry(tb, textvariable=self._rid_var, width=8,
                                   bg=INPUT, fg=FG, insertbackground=ACCENT,
                                   font=("Courier New", 9), bd=0,
                                   highlightthickness=1, highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self._rid_entry.pack(side="left", padx=2, ipady=2)
        self._rid_entry.bind("<Return>", lambda _: self._canvas.focus_set())

        # Room name lookup label
        self._rname_var = tk.StringVar(value="")
        tk.Label(tb, textvariable=self._rname_var, fg=ACCENT, bg=PANEL,
                 font=("Courier New", 8), width=30, anchor="w").pack(side="left", padx=(4,0))

        self._rid_var.trace_add("write", self._on_rid_change)

        tk.Button(tb, text="Save", fg=FG, bg="#1a3a1a",
                  font=("Courier New", 9, "bold"), relief="flat", bd=0, padx=10,
                  activebackground="#2a5a2a", command=self._save).pack(side="right", padx=4)
        tk.Button(tb, text="Clear Zone", fg=RED, bg=PANEL,
                  font=("Courier New", 9), relief="flat", bd=0, padx=6,
                  activebackground="#3a1010", command=self._clear_zone).pack(side="right", padx=2)

        # ── Status bar ──
        self._status_var = tk.StringVar(value="Drag a rectangle over a room box to annotate it.  Scroll=zoom  Middle-drag=pan")
        tk.Label(self.root, textvariable=self._status_var, fg=DIM, bg=PANEL,
                 font=("Courier New", 8), anchor="w", padx=6).pack(fill="x", side="bottom")

        # ── Count label ──
        self._count_var = tk.StringVar(value="0 rooms annotated")
        tk.Label(self.root, textvariable=self._count_var, fg=GREEN, bg=PANEL,
                 font=("Courier New", 8), anchor="e", padx=6).pack(fill="x", side="bottom")

        # ── Canvas ──
        self._canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True, padx=4, pady=4)

        self._canvas.bind("<Configure>",        lambda _: self._render())
        self._canvas.bind("<MouseWheel>",        self._on_wheel)
        self._canvas.bind("<Button-4>",          self._on_wheel)
        self._canvas.bind("<Button-5>",          self._on_wheel)
        self._canvas.bind("<ButtonPress-1>",     self._on_lpress)
        self._canvas.bind("<B1-Motion>",         self._on_lmove)
        self._canvas.bind("<ButtonRelease-1>",   self._on_lrelease)
        self._canvas.bind("<ButtonPress-2>",     self._on_pan_start)
        self._canvas.bind("<B2-Motion>",         self._on_pan_move)
        self._canvas.bind("<ButtonPress-3>",     self._on_pan_start)
        self._canvas.bind("<B3-Motion>",         self._on_pan_move)
        self._canvas.bind("<Delete>",            lambda _: self._delete_selected())
        self._canvas.bind("<Control-z>",         lambda _: self._undo())
        self._canvas.bind("<Motion>",            self._on_motion)

    # ── zone management ───────────────────────────────────────────────

    def _on_zone_change(self):
        self._zone = self._zone_var.get()
        self._load_zone(self._zone)

    def _load_zone(self, zone_name: str):
        self._zone = zone_name
        self._selected = None
        self._undo_stack.clear()

        # Load existing annotations for this zone
        zone_data = self.regions.get("maps", {}).get(zone_name, {})
        self._annotations = {}
        for rid_str, coords in zone_data.get("rooms", {}).items():
            self._annotations[int(rid_str)] = tuple(coords)

        # Load image
        self._pil_img = None
        img_rel  = zone_data.get("image", "")
        img_path = img_rel if os.path.isabs(img_rel) else \
                   (os.path.join(DATA_DIR, img_rel) if img_rel else "")
        if img_path and os.path.exists(img_path):
            try:
                self._pil_img = Image.open(img_path).convert("RGBA")
            except Exception as e:
                self._status(f"Image load error: {e}")

        # If no image set yet, try to find one by zone name slug
        if not self._pil_img:
            maps_dir = os.path.join(DATA_DIR, "maps")
            slug     = zone_name.lower().replace("'", "").replace(" ", "-")
            for fname in os.listdir(maps_dir) if os.path.exists(maps_dir) else []:
                if slug in fname.lower() and fname.lower().endswith(".png"):
                    path = os.path.join(maps_dir, fname)
                    try:
                        self._pil_img = Image.open(path).convert("RGBA")
                        # Record image path in regions
                        self._ensure_zone(zone_name)
                        rel = os.path.relpath(path, DATA_DIR)
                        self.regions["maps"][zone_name]["image"] = rel
                        break
                    except Exception:
                        pass

        # Fit zoom to canvas
        self.root.update_idletasks()
        if self._pil_img:
            cw = self._canvas.winfo_width() or 800
            ch = self._canvas.winfo_height() or 600
            iw, ih = self._pil_img.size
            self._zoom = min(cw / iw, ch / ih) * 0.97
        else:
            self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._render()
        self._update_count()

    def _ensure_zone(self, zone_name: str):
        if "maps" not in self.regions:
            self.regions["maps"] = {}
        if zone_name not in self.regions["maps"]:
            self.regions["maps"][zone_name] = {"image": "", "rooms": {}}

    # ── rendering ─────────────────────────────────────────────────────

    def _render(self):
        self._canvas.delete("all")
        self._overlay_ids.clear()

        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 600

        if not self._pil_img:
            self._canvas.create_text(cw//2, ch//2,
                text=(f"No image found for zone:\n'{self._zone}'\n\n"
                      "Place a PNG in  data/maps/  named after the zone\n"
                      "e.g.  data/maps/en-tavaalor.png\n"
                      "then re-select the zone."),
                fill=DIM, font=("Courier New", 10), justify="center")
            return

        iw, ih = self._pil_img.size
        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        scaled       = self._pil_img.resize((nw, nh), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(scaled)

        ox = cw // 2 + int(self._pan_x)
        oy = ch // 2 + int(self._pan_y)
        self._canvas.create_image(ox, oy, image=self._tk_img, anchor="center")

        # Draw annotations
        for rid, (rx, ry, rw, rh) in self._annotations.items():
            self._draw_overlay(rid, rx, ry, rw, rh)

    def _draw_overlay(self, rid: int, rx, ry, rw, rh):
        x1, y1 = self._img_to_canvas(rx, ry)
        x2, y2 = self._img_to_canvas(rx + rw, ry + rh)
        is_sel  = rid == self._selected
        color   = YELLOW if is_sel else GREEN
        width   = 2     if is_sel else 1
        rect = self._canvas.create_rectangle(x1, y1, x2, y2,
                   outline=color, fill="", width=width, tags="ann")
        # Label only when zoomed in enough
        items = [rect]
        if self._zoom > 0.4:
            lbl = self._canvas.create_text((x1+x2)/2, (y1+y2)/2,
                      text=str(rid), fill=color,
                      font=("Courier New", max(6, min(10, int(9*self._zoom)))),
                      tags="ann")
            items.append(lbl)
        self._overlay_ids[rid] = items

    # ── coordinate transforms ──────────────────────────────────────────

    def _img_to_canvas(self, ix, iy):
        if not self._pil_img:
            return 0, 0
        iw, ih = self._pil_img.size
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 600
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return ox + (ix - iw/2)*self._zoom, oy + (iy - ih/2)*self._zoom

    def _canvas_to_img(self, cx, cy):
        if not self._pil_img:
            return 0, 0
        iw, ih = self._pil_img.size
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 600
        ox = cw / 2 + self._pan_x
        oy = ch / 2 + self._pan_y
        return (cx - ox) / self._zoom + iw/2, (cy - oy) / self._zoom + ih/2

    # ── event handlers ─────────────────────────────────────────────────

    def _on_wheel(self, ev):
        zoom_in = ev.num == 4 or (hasattr(ev, "delta") and ev.delta > 0)
        factor  = 1.12 if zoom_in else (1/1.12)
        old     = self._zoom
        self._zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self._zoom * factor))
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 600
        self._pan_x = ev.x - (ev.x - cw/2 - self._pan_x) * (self._zoom/old) - cw/2
        self._pan_y = ev.y - (ev.y - ch/2 - self._pan_y) * (self._zoom/old) - ch/2
        self._render()

    def _on_pan_start(self, ev):
        self._drag_start = (ev.x, ev.y)
        self._drag_btn   = ev.num
        self._canvas.config(cursor="fleur")

    def _on_pan_move(self, ev):
        if self._drag_start:
            self._pan_x += ev.x - self._drag_start[0]
            self._pan_y += ev.y - self._drag_start[1]
            self._drag_start = (ev.x, ev.y)
            self._render()

    def _on_lpress(self, ev):
        self._canvas.focus_set()
        # Check if clicking an existing annotation → select it
        rid = self._ann_at(ev.x, ev.y)
        if rid is not None:
            self._selected = rid
            self._rid_var.set(str(rid))
            self._render()
            self._status(f"Selected room #{rid}.  Delete key removes it.")
            return
        # Otherwise start drawing a new rect
        self._draw_start  = (ev.x, ev.y)
        self._rubber_id   = None
        self._canvas.config(cursor="crosshair")

    def _on_lmove(self, ev):
        if self._draw_start is None:
            return
        sx, sy = self._draw_start
        if self._rubber_id:
            self._canvas.delete(self._rubber_id)
        self._rubber_id = self._canvas.create_rectangle(
            sx, sy, ev.x, ev.y, outline=ACCENT, fill="", width=2, dash=(4,3))

    def _on_lrelease(self, ev):
        self._canvas.config(cursor="")
        if self._draw_start is None:
            return
        sx, sy = self._draw_start
        self._draw_start = None
        if self._rubber_id:
            self._canvas.delete(self._rubber_id)
            self._rubber_id = None

        # Minimum drag of 4px required
        if abs(ev.x - sx) < 4 or abs(ev.y - sy) < 4:
            return

        rid_str = self._rid_var.get().strip()
        if not rid_str.isdigit():
            self._status("Enter a Room ID first, then drag a rectangle.", error=True)
            return
        rid = int(rid_str)

        # Convert to image coords
        ix1, iy1 = self._canvas_to_img(min(sx, ev.x), min(sy, ev.y))
        ix2, iy2 = self._canvas_to_img(max(sx, ev.x), max(sy, ev.y))
        x = int(ix1); y = int(iy1)
        w = max(1, int(ix2 - ix1)); h = max(1, int(iy2 - iy1))

        # Save for undo
        old_val = self._annotations.get(rid)
        self._undo_stack.append(("set", rid, old_val))

        self._annotations[rid] = (x, y, w, h)
        self._selected = rid
        self._render()
        self._update_count()
        self._status(f"Room #{rid} annotated at ({x},{y}) {w}×{h}px.  Ctrl+Z to undo.")

    def _on_motion(self, ev):
        rid = self._ann_at(ev.x, ev.y)
        if rid:
            room = self.graph.get(rid, {})
            title = room.get("title", "unknown room")
            self._canvas.config(cursor="hand2")
            self._status(f"#{rid}  {title}")
        else:
            self._canvas.config(cursor="")
            ix, iy = self._canvas_to_img(ev.x, ev.y)
            self._status(f"Image pixel ({int(ix)}, {int(iy)})  — Room ID: {self._rid_var.get() or '?'}")

    # ── annotation helpers ─────────────────────────────────────────────

    def _ann_at(self, cx, cy) -> Optional[int]:
        for rid, (rx, ry, rw, rh) in self._annotations.items():
            x1, y1 = self._img_to_canvas(rx, ry)
            x2, y2 = self._img_to_canvas(rx+rw, ry+rh)
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return rid
        return None

    def _delete_selected(self):
        if self._selected is None:
            return
        rid = self._selected
        old_val = self._annotations.pop(rid, None)
        if old_val is not None:
            self._undo_stack.append(("del", rid, old_val))
        self._selected = None
        self._render()
        self._update_count()
        self._status(f"Deleted annotation for room #{rid}.")

    def _undo(self):
        if not self._undo_stack:
            self._status("Nothing to undo.")
            return
        op, rid, prev = self._undo_stack.pop()
        if op == "set":
            if prev is None:
                self._annotations.pop(rid, None)
            else:
                self._annotations[rid] = prev
        elif op == "del":
            if prev is not None:
                self._annotations[rid] = prev
        self._render()
        self._update_count()
        self._status(f"Undid last action for room #{rid}.")

    # ── room-id entry trace ────────────────────────────────────────────

    def _on_rid_change(self, *_):
        rid_str = self._rid_var.get().strip()
        if rid_str.isdigit():
            rid  = int(rid_str)
            room = self.graph.get(rid)
            if room:
                self._rname_var.set(room.get("title", "")[:42])
            else:
                self._rname_var.set("(room not in graph)")
        else:
            self._rname_var.set("")

    # ── save / clear ──────────────────────────────────────────────────

    def _save(self):
        self._ensure_zone(self._zone)
        self.regions["maps"][self._zone]["rooms"] = {
            str(rid): list(coords) for rid, coords in self._annotations.items()
        }
        save_regions(self.regions)
        self._status(f"Saved {len(self._annotations)} annotations for '{self._zone}'  →  {REGIONS_PATH}")

    def _clear_zone(self):
        if not messagebox.askyesno("Clear Zone",
                f"Remove ALL {len(self._annotations)} annotations for '{self._zone}'?"):
            return
        self._annotations.clear()
        self._undo_stack.clear()
        self._selected = None
        self._render()
        self._update_count()
        self._status(f"Cleared all annotations for '{self._zone}'.")

    # ── misc ──────────────────────────────────────────────────────────

    def _status(self, msg: str, error: bool = False):
        self._status_var.set(msg)
        self._canvas.itemconfig("status_lbl", fill=RED if error else DIM) \
            if self._canvas.find_withtag("status_lbl") else None

    def _update_count(self):
        n = len(self._annotations)
        self._count_var.set(f"{n} room{'s' if n != 1 else ''} annotated in '{self._zone}'")


def main():
    root = tk.Tk()
    app  = AnnotatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
