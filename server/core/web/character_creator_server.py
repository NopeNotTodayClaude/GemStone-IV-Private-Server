"""
character_creator_server.py — Web-based character creation portal.

Runs a lightweight HTTP server on localhost:8766 in a background thread.
When a player selects "Create new character" from character select, the game
generates a one-time token, opens the browser to http://127.0.0.1:8766/create?token=XXX
and the full character creation flow happens in the browser.

On completion the web server finalises the character in the DB and signals
the game session (via asyncio) so the session advances to playing.

Static files are served from N:\\GemStoneIVServer\\character-creator\\static\\
Set CC_STATIC_DIR env var to override the auto-detected path.
"""

import asyncio
import json
import logging
import math
import mimetypes
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

log = logging.getLogger(__name__)

CC_PORT   = 8766
TOKEN_TTL = 1200   # 20 minutes — creation takes longer than training

# ── Resolve static files directory ────────────────────────────────────────────
# Resolved relative to this file — works on any machine, any drive letter.
# This file lives at:  <server_root>/server/core/web/character_creator_server.py
# Three levels up  →   <server_root>/
# character-creator/static/ sits alongside the server/ folder at root level.
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT      = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", ".."))
CC_STATIC  = os.environ.get("CC_STATIC_DIR",
                             os.path.join(_ROOT, "character-creator", "static"))


# ── Pull all game data from character_creation.py (single source of truth) ───
from server.core.character_creation import (
    STAT_NAMES, STAT_ABBREVS, STAT_KEYS, STAT_DESCRIPTIONS,
    TOTAL_STAT_POINTS, STAT_MIN, STAT_MAX, PRIME_MIN, NUM_STATS,
    stat_bonus, calc_tp, _require_lua_data,
)


# ── Culture data (inlined from character_creation.py _CULTURES) ───────────────
def _build_culture_data():
    """Build culture data dict keyed by race_id."""
    _SKIP = {"key": "none", "name": "No Culture",
             "desc": "No cultural affiliation. Set later with TITLE SET CULTURE."}
    return {
        1:  {"label": "Human Cultures", "options": [
                {"key": "aelendyl",  "name": "Aelendyl",   "desc": "Maritime culture of the western coastlands."},
                {"key": "aradenai",  "name": "Aradenai",   "desc": "Highland culture known for fierce independence."},
                {"key": "bourth",    "name": "Bourth",     "desc": "Central plains farmers who value community."},
                {"key": "cynarith",  "name": "Cynarith",   "desc": "River delta merchants and diplomats."},
                {"key": "estild",    "name": "Estild",     "desc": "Northern forest hunters and trappers."},
                {"key": "tehir",     "name": "Tehir",      "desc": "Desert nomads of the Tehir sands."},
                {"key": "seareach",  "name": "Seareach",   "desc": "Island seafarers known for exploration."},
                _SKIP]},
        2:  {"label": "Elven Houses", "options": [
                {"key": "ardenai",   "name": "Ardenai",   "desc": "The forest elves, deeply connected to nature."},
                {"key": "illistim",  "name": "Illistim",  "desc": "Scholars of House Illistim, seekers of arcane knowledge."},
                {"key": "loenthra",  "name": "Loenthra",  "desc": "Artists of House Loenthra, celebrating beauty."},
                {"key": "nalfein",   "name": "Nalfein",   "desc": "Merchants of House Nalfein, masters of subtlety."},
                {"key": "vaalor",    "name": "Vaalor",    "desc": "Warriors of House Vaalor, disciplined defenders."},
                _SKIP]},
        3:  {"label": "Dark Elf Cultures", "options": [
                {"key": "dhenar",    "name": "Dhe'nar",   "desc": "Shadow-walkers, followers of Luukos."},
                {"key": "faendryl",  "name": "Faendryl",  "desc": "Exiled sorcerers, masters of forbidden magic."},
                {"key": "evashir",   "name": "Evashir",   "desc": "Dark elves of the eastern reaches."},
                _SKIP]},
        4:  {"label": "Half-Elf Upbringings", "options": [
                {"key": "ardenai",   "name": "Ardenai-raised",  "desc": "Raised among the Ardenai forest elves."},
                {"key": "vaalor",    "name": "Vaalor-raised",   "desc": "Raised in the martial culture of Vaalor."},
                {"key": "human",     "name": "Human-raised",    "desc": "Raised among humans."},
                {"key": "tehir",     "name": "Tehir-raised",    "desc": "Raised among Tehir desert nomads."},
                _SKIP]},
        5:  {"label": "Dwarf Clans", "options": [
                {"key": "borthuum",  "name": "Borthuum",  "desc": "Iron miners of the deep stone."},
                {"key": "egrentek",  "name": "Egrentek",  "desc": "Weapon-crafters renowned across Elanthia."},
                {"key": "grevnek",   "name": "Grevnek",   "desc": "Fierce warriors with berserker traditions."},
                {"key": "kazunel",   "name": "Kazunel",   "desc": "Scholars of dwarven history and runic lore."},
                {"key": "khanshael", "name": "Khanshael", "desc": "Outcast dwarves who walk between two worlds."},
                {"key": "mithrenek", "name": "Mithrenek", "desc": "Mithril-smiths producing legendary arms."},
                _SKIP]},
        6:  {"label": "Halfling Cultures", "options": [
                {"key": "shire",     "name": "Shire",     "desc": "Homebodies of the fertile lowlands."},
                {"key": "wanderer",  "name": "Wandering", "desc": "Footloose halflings, acquiring skills and stories."},
                {"key": "burrow",    "name": "Burrow",    "desc": "Tunnel-dwellers sharing dwarven traditions."},
                _SKIP]},
        7:  {"label": "Giantman Clans", "options": [
                {"key": "aradenai",  "name": "Aradenai",  "desc": "Highland giantmen, most common in western lands."},
                {"key": "blood",     "name": "Blood Clan","desc": "Fierce warriors with ritual combat traditions."},
                {"key": "dobrek",    "name": "Dobrek",    "desc": "Northern giantmen adapted to arctic conditions."},
                {"key": "kalerk",    "name": "Kalerk",    "desc": "Coastal giantmen skilled in seafaring."},
                _SKIP]},
        8:  {"label": "Forest Gnome Bloodlines", "options": [
                {"key": "greel",     "name": "Greel",     "desc": "Gnomes with affinity for animals and deep forest."},
                {"key": "loaber",    "name": "Loaber",    "desc": "Gnomes known for tinkering with the natural world."},
                {"key": "mhoragian", "name": "Mhoragian", "desc": "Gnomes of the northern woods, hardy and resourceful."},
                _SKIP]},
        9:  {"label": "Burghal Gnome Bloodlines", "options": [
                {"key": "aledotter", "name": "Aledotter", "desc": "Urban gnomes known for breweries."},
                {"key": "neimhean",  "name": "Neimhean",  "desc": "Gnomes with a gift for illusion magic."},
                {"key": "nylem",     "name": "Nylem",     "desc": "Clockwork artificers pushing gnomish invention."},
                {"key": "vylem",     "name": "Vylem",     "desc": "Merchants moving silver through hidden channels."},
                _SKIP]},
        10: {"label": "Sylvankind D'ahranals", "options": [
                {"key": "forest",    "name": "Forest",    "desc": "Sylvans of the deep wood, communing with ancient trees."},
                {"key": "glade",     "name": "Glade",     "desc": "Sylvans of the open glades, light-touched."},
                {"key": "river",     "name": "River",     "desc": "Sylvans of the river valleys, adaptable."},
                _SKIP]},
        11: {"label": "Aelotoi Clans", "options": [
                {"key": "cyrtaeni",  "name": "Cyrtae'ni", "desc": "Aelotoi known for adaptability and quick thinking."},
                {"key": "gaehdeh",   "name": "Gaeh'deh",  "desc": "Warriors bearing the scars of their escape."},
                {"key": "mraeni",    "name": "Mrae'ni",   "desc": "Healers tending wounds of body and spirit."},
                {"key": "vaersah",   "name": "Vaer'sah",  "desc": "Scholars preserving Aelotoi culture."},
                _SKIP]},
        12: {"label": "Erithian Dai", "options": [
                {"key": "eloth",     "name": "Eloth Dai",  "desc": "Scholars of arcane and philosophical knowledge."},
                {"key": "nathala",   "name": "Nathala Dai","desc": "Martial artists, disciplined warrior-monks."},
                {"key": "surath",    "name": "Surath Dai", "desc": "Merchants building wealth across Elanthia."},
                {"key": "tichan",    "name": "Tichan Dai", "desc": "Healers, practitioners of herb-craft."},
                {"key": "volnath",   "name": "Volnath Dai","desc": "Warriors, sworn blades in service of Erithia."},
                {"key": "yachan",    "name": "Yachan Dai", "desc": "Spirit-speakers communing with ancestors."},
                _SKIP]},
        13: {"label": "Half-Krolvin Klinasts", "options": [
                {"key": "froskar",   "name": "Froskar",   "desc": "Raised among the Krolvin sea raiders."},
                {"key": "sharath",   "name": "Sharath",   "desc": "Raised on land, straddling both worlds."},
                _SKIP]},
    }


CULTURE_DATA = _build_culture_data()

AGE_STAGES = [
    "New Adult","Young Adult","Adult","Approaching Middle Age","Middle Aged",
    "Leaving Middle Aged","Mature","Retiring","Old","Very Old","Extremely Old",
]


# ── Request Handler ────────────────────────────────────────────────────────────

class CharacterCreatorHandler(BaseHTTPRequestHandler):
    server_ref = None   # set to GameServer instance on startup

    def log_message(self, fmt, *args):
        pass  # silence HTTP access log

    # ── Routing ───────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        p = parsed.path

        if p in ("/create", "/create/"):
            self._serve_index(params)
        elif p.startswith("/cc/static/"):
            rel = p[len("/cc/static/"):]
            self._serve_static(rel)
        elif p == "/api/cc/data":
            self._serve_game_data(params)
        else:
            self._send_html("<h1 style='color:#c94040;font-family:serif'>404</h1>", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body) if length else {}
        except Exception:
            self._json_error("Invalid JSON", 400)
            return

        if parsed.path == "/api/cc/check_name":
            self._handle_check_name(data)
        elif parsed.path == "/api/cc/create":
            self._handle_create(data)
        else:
            self._send_html("<h1>404</h1>", 404)

    # ── Token helpers ─────────────────────────────────────────────────────────

    def _resolve_token(self, token_str):
        if not token_str:
            return None, "No token provided"
        server = CharacterCreatorHandler.server_ref
        tokens = getattr(server, "cc_tokens", {})
        entry = tokens.get(token_str)
        if not entry:
            return None, "Invalid or expired token — please try again from the game"
        if time.time() > entry["expires"]:
            del tokens[token_str]
            return None, "Token expired — please select Create Character again in-game"
        return entry["session"], None

    def _token_from_params(self, params):
        return params.get("token", [None])[0]

    def _token_from_body(self, data):
        return data.get("token")

    # ── GET handlers ──────────────────────────────────────────────────────────

    def _serve_index(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._send_html(_error_page(err), 401)
            return
        # Serve index.html from static dir
        index_path = os.path.join(CC_STATIC, "index.html")
        try:
            with open(index_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_html(_error_page(
                f"Character creator not installed.<br>Expected: {index_path}"), 500)

    def _serve_static(self, rel_path):
        # Security: block path traversal
        rel_path = rel_path.replace("\\", "/")
        if ".." in rel_path or rel_path.startswith("/"):
            self._send_html("", 403)
            return
        abs_path = os.path.normpath(os.path.join(CC_STATIC, rel_path))
        if not abs_path.startswith(os.path.normpath(CC_STATIC)):
            self._send_html("", 403)
            return
        try:
            with open(abs_path, "rb") as f:
                content = f.read()
            mime, _ = mimetypes.guess_type(abs_path)
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_html("", 404)

    def _serve_game_data(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return

        # Build full game data payload
        server        = CharacterCreatorHandler.server_ref
        cc            = server.char_creator
        _races        = cc._get_races()
        _race_mods    = cc._get_race_stat_mods()
        _start_rooms  = cc._get_race_starting_rooms()
        _town_names   = cc._get_race_town_names()
        _starter_towns = cc._get_starter_towns()
        _default_start = cc._get_default_starting_room()
        _professions  = cc._get_professions()
        _prof_stats   = cc._get_profession_stats()
        _primes       = cc._get_prime_requisites()
        _appearance   = _require_lua_data(server, "get_appearance")
        _suggested    = (_appearance or {}).get("suggested_stats", {})
        _cultures     = (_appearance or {}).get("cultures", {})
        _age_stages   = (_appearance or {}).get("age_stage_names", AGE_STAGES)

        races_out = []
        for r in _races:
            mods = _race_mods.get(r["id"], [0]*10)
            start_room = _start_rooms.get(r["id"], _default_start)
            start_town = _town_names.get(start_room, "Unknown")
            races_out.append({
                "id":          r["id"],
                "name":        r["name"],
                "desc":        r["desc"],
                "stat_mods":   mods,
                "start_room":  start_room,
                "start_town":  start_town,
            })

        profs_out = []
        for p in _professions:
            stats    = _prof_stats.get(p["id"], {"hp": 10, "mana": 0})
            primes   = list(_primes.get(p["id"], (0, 1)))
            profs_out.append({
                "id":       p["id"],
                "name":     p["name"],
                "type":     p["type"],
                "desc":     p["desc"],
                "hp":       stats["hp"],
                "mana":     stats["mana"],
                "primes":   primes,
                "suggested_stats": list(_suggested.get(p["id"], [20] * NUM_STATS)),
            })

        cultures_out = {}
        for race_id, cd in _cultures.items():
            cultures_out[str(race_id)] = cd

        payload = {
            "races":      races_out,
            "professions": profs_out,
            "cultures":   cultures_out,
            "starter_towns": _starter_towns,
            "default_starting_room": _default_start,
            "stat_names":  STAT_NAMES,
            "stat_abbrevs": STAT_ABBREVS,
            "stat_descriptions": STAT_DESCRIPTIONS,
            "hair_colors": cc._get_hair_colors(session),
            "hair_styles": cc._get_hair_styles(session),
            "eye_colors":  cc._get_eye_colors(session),
            "skin_tones":  cc._get_skin_tones(session),
            "age_stages":  _age_stages,
            "total_stat_points": TOTAL_STAT_POINTS,
            "stat_min":    STAT_MIN,
            "stat_max":    STAT_MAX,
            "prime_min":   PRIME_MIN,
            "account_name": getattr(session, "account_username", ""),
        }
        self._json_response(payload)

    # ── POST handlers ─────────────────────────────────────────────────────────

    def _handle_check_name(self, data):
        token_str = data.get("token")
        session, err = self._resolve_token(token_str)
        if not session:
            self._json_error(err, 401)
            return
        name = str(data.get("name", "")).strip().capitalize()
        if len(name) < 2 or len(name) > 20 or not name.isalpha():
            self._json_response({"available": False,
                                 "reason": "Names must be 2-20 letters only."})
            return
        server = CharacterCreatorHandler.server_ref
        taken = server.db and server.db.character_name_exists(name)
        self._json_response({
            "available": not taken,
            "reason": f"'{name}' is already taken." if taken else ""
        })

    def _handle_create(self, data):
        token_str = data.get("token")
        server = CharacterCreatorHandler.server_ref
        tokens = getattr(server, "cc_tokens", {})
        entry = tokens.get(token_str) if token_str else None
        if not entry or time.time() > entry["expires"]:
            self._json_error("Invalid or expired token", 401)
            return

        session = entry["session"]

        # ── Validate payload ──────────────────────────────────────────────────
        try:
            name       = str(data["name"]).strip().capitalize()
            gender     = str(data["gender"]).lower()
            race_id    = int(data["race_id"])
            prof_id    = int(data["profession_id"])
            stats      = [int(x) for x in data["stats"]]
            hair_color = str(data["hair_color"])
            hair_style = str(data["hair_style"])
            eye_color  = str(data["eye_color"])
            skin_tone  = str(data["skin_tone"])
            height     = int(data["height"])
            age        = data.get("age")
            culture_key  = data.get("culture_key")
            culture_name = data.get("culture_name", "")
        except (KeyError, ValueError, TypeError) as e:
            self._json_error(f"Invalid payload: {e}", 400)
            return

        # Basic validation
        if len(stats) != 10:
            self._json_error("Expected 10 stats", 400)
            return
        if sum(stats) != TOTAL_STAT_POINTS:
            self._json_error(
                f"Stat total must be {TOTAL_STAT_POINTS} (got {sum(stats)})", 400)
            return
        if server.db and server.db.character_name_exists(name):
            self._json_error(f"Name '{name}' is already taken.", 409)
            return

        # ── Finalise character (mirrors _finalize_character in character_creation.py) ──
        _cc         = server.char_creator
        race_mods   = _cc._get_race_stat_mods().get(race_id, [0]*10)
        prof_stats  = _cc._get_profession_stats().get(prof_id, {"hp": 10, "mana": 0})
        primes      = _cc._get_prime_requisites().get(prof_id, (0, 1))
        default_start = _cc._get_default_starting_room()
        start_room = int(_cc._get_race_starting_rooms().get(race_id, default_start) or default_start)

        char_data = {
            "name":         name,
            "race_id":      race_id,
            "profession_id": prof_id,
            "gender":       gender,
            "culture_key":  culture_key,
            "strength":     stats[0] + race_mods[0],
            "constitution": stats[1] + race_mods[1],
            "dexterity":    stats[2] + race_mods[2],
            "agility":      stats[3] + race_mods[3],
            "discipline":   stats[4] + race_mods[4],
            "aura":         stats[5] + race_mods[5],
            "logic":        stats[6] + race_mods[6],
            "intuition":    stats[7] + race_mods[7],
            "wisdom":       stats[8] + race_mods[8],
            "influence":    stats[9] + race_mods[9],
            "health_max":   100 + prof_stats["hp"],
            "mana_max":     prof_stats["mana"] * 3,
            "spirit_max":   10,
            "stamina_max":  100,
            "starting_room": start_room,
            "height":       height,
            "hair_color":   hair_color,
            "hair_style":   hair_style,
            "eye_color":    eye_color,
            "skin_tone":    skin_tone,
            "age":          age,
        }

        char_id = None
        if server.db:
            char_id = server.db.create_character(session.account_id, char_data)

        if not char_id:
            self._json_error("Failed to save character to database", 500)
            return

        # Calculate and store starting TPs
        total_stats = [char_data[k] for k in [
            "strength","constitution","dexterity","agility","discipline",
            "aura","logic","intuition","wisdom","influence"]]
        ptp, mtp = calc_tp(total_stats, prof_id, primes)
        if server.db:
            server.db.save_character_tps(char_id, ptp, mtp)

        # Give starter gear from Lua, matching the terminal creator flow.
        starting_silver = 500
        if server.db:
            starter_spells = _cc._get_starter_spells().get(prof_id, {})
            starter_spell_ranks = starter_spells.get("ranks", {})
            lua_gear = _require_lua_data(server, "get_starter_gear")
            gear_cfg = lua_gear.get("kits", {}).get(prof_id)
            starting_silver = lua_gear.get("starting_silver", {}).get(prof_id, 500)
            char_data["starting_silver"] = starting_silver
            log.info(
                "starter_gear: loaded Lua kit for prof %d (%s)",
                prof_id,
                gear_cfg.get("description", "?") if gear_cfg else "none",
            )
            if starter_spells:
                log.info(
                    "starter_spells: loaded Lua kit for prof %d (%s)",
                    prof_id,
                    starter_spells.get("description", "?"),
                )

            server.db.save_character_resources(
                char_id,
                char_data["health_max"],
                char_data["mana_max"],
                10,
                100,
                starting_silver,
            )
            if starter_spell_ranks:
                server.db.save_character_spell_ranks(char_id, starter_spell_ranks)

            if gear_cfg:
                container_inv_ids = {}
                for item_entry in gear_cfg.get("items", []):
                    item_id = item_entry.get("item_id")
                    if not item_id:
                        continue

                    slot = item_entry.get("slot")
                    container_noun = item_entry.get("container")
                    hand = item_entry.get("hand")

                    if hand:
                        hand_slot = "right_hand" if hand == "right" else "left_hand"
                        inv_id = server.db.add_item_to_inventory(char_id, item_id, slot=hand_slot)
                    elif slot:
                        inv_id = server.db.add_item_to_inventory(char_id, item_id, slot=slot)
                        noun = item_entry.get("name", "").split()[-1]
                        container_inv_ids[noun] = inv_id
                    elif container_noun and container_noun in container_inv_ids:
                        inv_id = server.db.add_item_to_inventory(char_id, item_id)
                        if inv_id:
                            try:
                                conn = server.db._get_conn()
                                cur = conn.cursor()
                                cur.execute(
                                    "UPDATE character_inventory SET container_id = %s WHERE id = %s",
                                    (container_inv_ids[container_noun], inv_id),
                                )
                                conn.close()
                            except Exception as e:
                                log.error("Failed to set starter gear container: %s", e)
                    else:
                        server.db.add_item_to_inventory(char_id, item_id)

                log.info(
                    "Gave starter gear to %s (prof %s): %d items, %d silver",
                    name,
                    data.get("profession_name", prof_id),
                    len(gear_cfg.get("items", [])),
                    starting_silver,
                )

        # ── Signal the game session via asyncio ──────────────────────────────
        loop = getattr(server, "_loop", None)
        if loop and not loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                _notify_session_char_created(session, char_id, char_data, ptp, mtp, server),
                loop
            )

        # Remove token so it can't be reused
        tokens.pop(token_str, None)

        self._json_response({
            "success": True,
            "char_id": char_id,
            "name": name,
            "message": f"{name} the {data.get('race_name','')} {data.get('profession_name','')} enters the world..."
        })

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _send_html(self, html, code=200):
        b = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _json_response(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _json_error(self, msg, code=400):
        self._json_response({"error": msg}, code)


# ── Async notification ─────────────────────────────────────────────────────────

async def _notify_session_char_created(session, char_id, char_data, ptp, mtp, server):
    """Called from a thread via run_coroutine_threadsafe to advance the session.
    Loads all character data onto the session then immediately calls
    _finish_web_character so the player is placed in the world without
    needing to type anything in the game client.
    """
    try:
        profession_name = str(char_data.get("profession_name") or "").strip()
        race_name = str(char_data.get("race_name") or "").strip()
        try:
            if not profession_name:
                for row in (server.char_creator._get_professions() or []):
                    if int(row.get("id", 0) or 0) == int(char_data.get("profession_id", 0) or 0):
                        profession_name = str(row.get("name") or "").strip()
                        break
            if not race_name:
                for row in (server.char_creator._get_races() or []):
                    if int(row.get("id", 0) or 0) == int(char_data.get("race_id", 0) or 0):
                        race_name = str(row.get("name") or "").strip()
                        break
        except Exception:
            pass

        session.character_id      = char_id
        session.character_name    = char_data["name"]
        session.race_id           = int(char_data.get("race_id", 0) or 0)
        session.race              = race_name
        session.profession_id     = int(char_data.get("profession_id", 0) or 0)
        session.profession        = profession_name
        session.profession_name   = profession_name
        session.physical_tp       = ptp
        session.mental_tp         = mtp
        session.stat_strength     = char_data["strength"]
        session.stat_constitution = char_data["constitution"]
        session.stat_dexterity    = char_data["dexterity"]
        session.stat_agility      = char_data["agility"]
        session.stat_discipline   = char_data["discipline"]
        session.stat_aura         = char_data["aura"]
        session.stat_logic        = char_data["logic"]
        session.stat_intuition    = char_data["intuition"]
        session.stat_wisdom       = char_data["wisdom"]
        session.stat_influence    = char_data["influence"]
        session.health_max        = char_data["health_max"]
        session.health_current    = char_data["health_max"]
        session.mana_max          = char_data["mana_max"]
        session.mana_current      = char_data["mana_max"]
        session.silver            = int(char_data.get("starting_silver") or 500)
        session.starting_room_id  = int(char_data.get("starting_room") or 221)

        # Ensure tutorial fields are set so save_character doesn't blow up
        session.tutorial_stage    = 0
        session.tutorial_flags    = 0
        session.tutorial_complete = False

        # Advance the session immediately — no player input required
        await server._finish_web_character(session)

    except Exception as e:
        log.error("_notify_session_char_created error: %s", e)


# ── Error page ─────────────────────────────────────────────────────────────────

def _error_page(msg):
    return (
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8">'
        '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&display=swap" rel="stylesheet">'
        "<style>body{background:#0d0b08;color:#c94040;font-family:Cinzel,serif;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh;"
        "text-align:center;flex-direction:column;gap:1rem}</style></head><body>"
        "<h1 style='font-size:1.5rem'>⚔ Access Denied</h1>"
        f"<p style='color:#8a6e30;font-size:1rem'>{msg}</p>"
        "</body></html>"
    )


# ── Web server class ───────────────────────────────────────────────────────────

class CharacterCreatorWebServer:
    """Manages the character creation web portal thread."""

    def __init__(self, game_server):
        self._server    = game_server
        self._httpd     = None
        self._thread    = None
        CharacterCreatorHandler.server_ref = game_server
        if not hasattr(game_server, "cc_tokens"):
            game_server.cc_tokens = {}

    def start(self):
        try:
            self._httpd = HTTPServer(("0.0.0.0", CC_PORT), CharacterCreatorHandler)
            self._thread = threading.Thread(
                target=self._httpd.serve_forever, daemon=True, name="cc-web")
            self._thread.start()
            log.info("Character Creator web portal: http://127.0.0.1:%d/create", CC_PORT)
            log.info("Static files: %s", CC_STATIC)
            if not os.path.isdir(CC_STATIC):
                log.warning("CC_STATIC directory not found: %s", CC_STATIC)
        except Exception as e:
            log.error("Failed to start Character Creator web server: %s", e)

    def generate_token(self, session):
        token = str(uuid.uuid4()).replace("-", "")
        self._server.cc_tokens[token] = {
            "session": session,
            "expires": time.time() + TOKEN_TTL,
        }
        # Clean up old tokens
        now = time.time()
        expired = [k for k, v in self._server.cc_tokens.items()
                   if now > v["expires"]]
        for k in expired:
            del self._server.cc_tokens[k]
        return token

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
