"""
npc_registry_loader.py
----------------------
Keeps the SQL npc registry synchronized with Lua-authored NPC templates.

The registry is used for durable room overrides, enable/disable flags, and
manual placement work that should survive Lua resyncs.
"""

from __future__ import annotations

import logging
import os

from server.core.scripting.loaders.npc_room_resolver import _hint_matches_room, _load_room_index

log = logging.getLogger(__name__)


def _zone_slug_for_room(world, room_id: int) -> str | None:
    if not world:
        return None
    try:
        room = world.get_room(int(room_id or 0))
    except Exception:
        return None
    if not room:
        return None
    zone = getattr(room, "zone", None)
    slug = getattr(zone, "slug", None) if zone else None
    if slug:
        return str(slug).strip() or None
    slug = getattr(room, "zone_slug", None)
    return str(slug).strip() or None if slug else None


def build_npc_registry_rows(templates: dict[str, dict], scripts_path: str, world=None) -> list[dict]:
    scripts_path = os.path.abspath(scripts_path)
    rows = []
    for template_id in sorted(templates):
        template = dict(templates.get(template_id) or {})
        try:
            home_room_id = int(template.get("home_room_id") or template.get("room_id") or 0)
        except (TypeError, ValueError):
            home_room_id = 0
        lua_file = str(template.get("lua_file") or "").strip()
        lua_script = ""
        if lua_file:
            try:
                lua_script = os.path.relpath(lua_file, scripts_path).replace("\\", "/")
            except ValueError:
                lua_script = lua_file.replace("\\", "/")
        if not lua_script:
            lua_script = str(template.get("lua_module") or "").strip()

        rows.append({
            "template_id": str(template.get("template_id") or template_id).strip(),
            "display_name": str(template.get("name") or "").strip(),
            "lua_script": lua_script,
            "home_room_id": home_room_id,
            "zone_slug": _zone_slug_for_room(world, home_room_id),
            "location_hint": str(template.get("location_hint") or "").strip() or None,
        })
    return rows


def _room_matches_location_hint(room_index: dict, room_id: int, location_hint: str | None) -> bool:
    try:
        room_id = int(room_id or 0)
    except (TypeError, ValueError):
        return False
    if room_id <= 0:
        return False
    room = dict((room_index or {}).get("rooms_by_id") or {}).get(room_id)
    if not room:
        return False
    return _hint_matches_room(str(location_hint or "").strip(), room)


def sync_npc_registry(db, rows: list[dict], scripts_path: str | None = None) -> int:
    if not db or not rows:
        return 0

    conn = None
    cur = None
    try:
        conn = db._get_conn()
        cur = conn.cursor()

        cur.execute("SHOW COLUMNS FROM npcs")
        columns = {str(row[0]).strip().lower() for row in (cur.fetchall() or [])}
        if "display_name" not in columns:
            cur.execute(
                "ALTER TABLE npcs "
                "ADD COLUMN display_name VARCHAR(128) NOT NULL DEFAULT '' AFTER template_id"
            )
        if "location_hint" not in columns:
            cur.execute(
                "ALTER TABLE npcs "
                "ADD COLUMN location_hint VARCHAR(128) DEFAULT NULL AFTER zone_slug"
            )

        cur.executemany(
            """
            INSERT INTO npcs (
                template_id, display_name, lua_script, home_room_id, zone_slug, location_hint, enabled
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 1
            )
            ON DUPLICATE KEY UPDATE
                display_name = VALUES(display_name),
                lua_script = VALUES(lua_script),
                home_room_id = CASE
                    WHEN COALESCE(home_room_id, 0) = 0 THEN VALUES(home_room_id)
                    ELSE home_room_id
                END,
                zone_slug = CASE
                    WHEN zone_slug IS NULL OR zone_slug = '' THEN NULLIF(VALUES(zone_slug), '')
                    ELSE zone_slug
                END,
                location_hint = CASE
                    WHEN location_hint IS NULL OR location_hint = '' THEN NULLIF(VALUES(location_hint), '')
                    ELSE location_hint
                END
            """,
            [
                (
                    row["template_id"],
                    row["display_name"],
                    row["lua_script"],
                    int(row["home_room_id"] or 0),
                    row.get("zone_slug"),
                    row.get("location_hint"),
                )
                for row in rows
                if row.get("template_id")
            ],
        )

        repaired = 0
        row_map = {
            str(row.get("template_id") or "").strip(): dict(row)
            for row in rows
            if str(row.get("template_id") or "").strip()
        }
        room_index = _load_room_index(str(scripts_path or "")) if scripts_path else {}
        if row_map and room_index:
            cur.execute(
                "SELECT template_id, home_room_id, location_hint FROM npcs "
                "WHERE template_id IN ({})".format(", ".join(["%s"] * len(row_map))),
                list(row_map.keys()),
            )
            repairs = []
            for template_id, current_room_id, current_hint in cur.fetchall() or []:
                template_id = str(template_id or "").strip()
                row = row_map.get(template_id)
                if not row:
                    continue
                try:
                    current_room_id = int(current_room_id or 0)
                except (TypeError, ValueError):
                    current_room_id = 0
                try:
                    incoming_room_id = int(row.get("home_room_id") or 0)
                except (TypeError, ValueError):
                    incoming_room_id = 0
                if incoming_room_id <= 0 or current_room_id <= 0 or incoming_room_id == current_room_id:
                    continue
                location_hint = str(row.get("location_hint") or current_hint or "").strip()
                if not location_hint:
                    continue
                if _room_matches_location_hint(room_index, current_room_id, location_hint):
                    continue
                if not _room_matches_location_hint(room_index, incoming_room_id, location_hint):
                    continue
                repairs.append(
                    (
                        incoming_room_id,
                        row.get("zone_slug"),
                        row.get("location_hint"),
                        template_id,
                    )
                )
            if repairs:
                cur.executemany(
                    """
                    UPDATE npcs
                    SET home_room_id = %s,
                        zone_slug = CASE
                            WHEN %s IS NULL OR %s = '' THEN zone_slug
                            ELSE %s
                        END,
                        location_hint = CASE
                            WHEN location_hint IS NULL OR location_hint = '' THEN NULLIF(%s, '')
                            ELSE location_hint
                        END
                    WHERE template_id = %s
                    """,
                    [
                        (
                            room_id,
                            zone_slug,
                            zone_slug,
                            zone_slug,
                            location_hint,
                            template_id,
                        )
                        for room_id, zone_slug, location_hint, template_id in repairs
                    ],
                )
                repaired = len(repairs)
        conn.commit()
        if repaired:
            log.info("npc_registry_loader: repaired %d hint-mismatched npc registry rooms", repaired)
        return len(rows)
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
