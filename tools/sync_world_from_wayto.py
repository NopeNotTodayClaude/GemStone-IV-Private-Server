"""
sync_world_from_wayto.py
------------------------
Apply the local LICH wayto map as the authoritative source for canonical room
identity and room exits in the live MariaDB world tables.

This is an admin/data repair tool, not gameplay logic.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.core.world.lich_wayto import (  # noqa: E402
    _load_wayto_index,
    build_lich_exit_rows,
    build_lich_room_snapshot,
)

MYSQL_CANDIDATES = [
    shutil.which("mysql"),
    r"C:\Program Files\MariaDB 12.1\bin\mysql.exe",
    r"C:\Program Files\MariaDB 11.4\bin\mysql.exe",
    r"C:\Program Files\MariaDB 11.3\bin\mysql.exe",
]


def _find_mysql() -> str:
    for candidate in MYSQL_CANDIDATES:
        if candidate and os.path.exists(candidate):
            return candidate
    raise FileNotFoundError("mysql.exe not found")


def _run_mysql_query(sql: str) -> str:
    cmd = [
        _find_mysql(),
        "--skip-ssl",
        "-N",
        "-B",
        "-u",
        "root",
        "gemstone_dev",
        "-e",
        sql,
    ]
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")


def _sql_text(value: str | None) -> str:
    if value is None:
        return "NULL"
    text = str(value)
    if text == "":
        return "''"
    raw = text.encode("utf-8")
    return "0x" + raw.hex()


def _room_rows_from_db() -> dict[int, dict]:
    out = {}
    sql = (
        "SELECT id, title, IFNULL(location_name,''), "
        "IFNULL(lich_uid,0), IFNULL(paths_text,'') "
        "FROM rooms"
    )
    for line in _run_mysql_query(sql).splitlines():
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        rid = int(parts[0])
        out[rid] = {
            "title": parts[1],
            "location_name": parts[2],
            "lich_uid": int(parts[3] or 0),
            "paths_text": parts[4],
        }
    return out


def _exit_rows_from_db() -> dict[int, dict[str, tuple[int, int, int, str, int]]]:
    out: dict[int, dict[str, tuple[int, int, int, str, int]]] = {}
    sql = (
        "SELECT room_id, direction, target_room_id, IFNULL(is_hidden,0), "
        "IFNULL(is_special,0), IFNULL(exit_verb,''), IFNULL(search_dc,0) "
        "FROM room_exits"
    )
    for line in _run_mysql_query(sql).splitlines():
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        rid = int(parts[0])
        direction = parts[1]
        out.setdefault(rid, {})[direction] = (
            int(parts[2]),
            int(parts[3] or 0),
            int(parts[4] or 0),
            parts[5],
            int(parts[6] or 0),
        )
    return out


def _expected_exit_map(entry: dict) -> dict[str, tuple[int, int, int, str, int]]:
    out = {}
    for row in build_lich_exit_rows(entry):
        out[row["direction"]] = (
            int(row["target_room_id"]),
            int(row["is_hidden"]),
            int(row["is_special"]),
            str(row["exit_verb"] or ""),
            int(row["search_dc"]),
        )
    return out


def build_sync_sql() -> tuple[str, dict]:
    wayto = _load_wayto_index()
    db_rooms = _room_rows_from_db()
    db_exits = _exit_rows_from_db()

    room_updates = 0
    exit_rewrites = 0
    missing_dirs = 0
    wrong_dirs = 0
    extra_dirs = 0
    statements: list[str] = []

    for rid, entry in sorted(wayto.items()):
        snapshot = build_lich_room_snapshot(entry)
        current_room = db_rooms.get(rid)
        if current_room:
            if (
                current_room["title"] != snapshot["title"]
                or current_room["location_name"] != snapshot["location_name"]
                or current_room["lich_uid"] != int(snapshot["lich_uid"] or 0)
                or current_room["paths_text"] != snapshot["paths_text"]
            ):
                room_updates += 1
                statements.append(
                    "UPDATE rooms SET "
                    f"title={_sql_text(snapshot['title'])}, "
                    f"location_name={_sql_text(snapshot['location_name'])}, "
                    f"lich_uid={int(snapshot['lich_uid'] or 0)}, "
                    f"paths_text={_sql_text(snapshot['paths_text'])} "
                    f"WHERE id={rid};"
                )

        expected_exits = _expected_exit_map(entry)
        current_exits = db_exits.get(rid, {})
        if expected_exits != current_exits:
            exit_rewrites += 1
            for direction, expected in expected_exits.items():
                got = current_exits.get(direction)
                if got is None:
                    missing_dirs += 1
                elif got != expected:
                    wrong_dirs += 1
            for direction in current_exits:
                if direction not in expected_exits:
                    extra_dirs += 1

            statements.append(f"DELETE FROM room_exits WHERE room_id={rid};")
            if expected_exits:
                values = []
                for direction, row in sorted(expected_exits.items()):
                    target_room_id, is_hidden, is_special, exit_verb, search_dc = row
                    values.append(
                        "("
                        f"{rid},"
                        f"{_sql_text(direction)},"
                        f"{_sql_text(exit_verb) if exit_verb else 'NULL'},"
                        f"{target_room_id},"
                        f"{is_hidden},"
                        f"{is_special},"
                        f"{search_dc}"
                        ")"
                    )
                statements.append(
                    "INSERT INTO room_exits "
                    "(room_id, direction, exit_verb, target_room_id, is_hidden, is_special, search_dc) VALUES\n"
                    + ",\n".join(values)
                    + ";"
                )

    summary = {
        "room_updates": room_updates,
        "exit_rewrites": exit_rewrites,
        "missing_dirs": missing_dirs,
        "wrong_dirs": wrong_dirs,
        "extra_dirs": extra_dirs,
        "map_rooms": len(wayto),
    }
    return "\n".join(statements) + ("\n" if statements else ""), summary


def apply_sql(sql_text: str) -> None:
    if not sql_text.strip():
        return
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as handle:
        handle.write("START TRANSACTION;\n")
        handle.write(sql_text)
        handle.write("COMMIT;\n")
        temp_path = handle.name
    try:
        cmd = [
            _find_mysql(),
            "--skip-ssl",
            "-u",
            "root",
            "gemstone_dev",
            "-e",
            f"source {temp_path.replace('\\', '\\\\')}",
        ]
        subprocess.check_call(cmd)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply the generated SQL to gemstone_dev")
    parser.add_argument("--write-sql", default="", help="Optional path to write the generated SQL")
    args = parser.parse_args()

    sql_text, summary = build_sync_sql()
    print(json.dumps(summary, indent=2))

    if args.write_sql:
        Path(args.write_sql).write_text(sql_text, encoding="utf-8")

    if args.apply and sql_text.strip():
        apply_sql(sql_text)
        print("applied")
    elif args.apply:
        print("no changes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
