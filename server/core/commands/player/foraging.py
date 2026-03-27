"""
FORAGE / FORAGE SENSE
---------------------
SQL-driven foraging backed by room tags_json + items.short_name.
"""

import random
from typing import List

from server.core.protocol.colors import roundtime_msg

FORAGE_SLOT_MAX = 5
FORAGE_MIN_REGEN = 300
FORAGE_MAX_REGEN = 600
SKILL_SURVIVAL = 23

_PROFESSION_BONUS = {
    1: 0,
    2: -10,
    3: -20,
    4: -5,
    5: 0,
    6: -20,
    7: 10,
    8: -10,
    9: -10,
    10: -5,
}


def _canonical_room_tag(tag: str) -> str:
    text = (tag or "").strip()
    lower = text.lower()
    for prefix in ("some ", "an ", "a "):
        if lower.startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _normalise_request(text: str) -> List[str]:
    lower = (text or "").strip().lower()
    if lower.startswith("for "):
        lower = lower[4:].strip()
    return [tok for tok in lower.split() if tok not in {"a", "an", "some", "of"}]


def _stat_bonus(raw_value) -> int:
    try:
        return int((int(raw_value) - 50) // 2)
    except Exception:
        return 0


def _race_bonus(session, room) -> int:
    race_id = int(getattr(session, "race_id", 0) or 0)
    terrain = (getattr(room, "terrain_type", "") or getattr(room, "terrain", "") or "").lower()
    cave_like = "subterranean" in terrain or "cave" in terrain

    if race_id in (1, 12):
        return 5
    if race_id in (7, 13):
        return -5
    if race_id == 6:
        return -10
    if race_id in (9, 11):
        return -15
    if race_id in (2, 3, 4):
        return -5 if cave_like else 5
    if race_id == 10:
        return -10 if cave_like else 10
    if race_id == 5:
        return 10 if cave_like else -5
    if race_id == 8:
        return -5 if cave_like else 10
    return 0


def _profession_bonus(session, item_row) -> int:
    profession_id = int(getattr(session, "profession_id", 0) or 0)
    if profession_id == 5 and (item_row.get("item_type") or "").lower() == "herb":
        return 10
    return _PROFESSION_BONUS.get(profession_id, 0)


def _position_bonus(session) -> int:
    pos = (getattr(session, "position", "") or "").lower()
    if pos == "kneeling":
        return 10
    if pos in {"sitting", "lying", "prone", "resting"}:
        return 5
    return 0


def _free_hands(session) -> int:
    hands = 0
    if not getattr(session, "right_hand", None):
        hands += 1
    if not getattr(session, "left_hand", None):
        hands += 1
    return hands


def _open_d100() -> int:
    total = random.randint(1, 100)
    while total >= 96:
        bump = random.randint(1, 100)
        total += bump
        if bump < 96:
            break
    while total <= 5:
        dip = random.randint(1, 100)
        total -= dip
        if dip > 5:
            break
    return total


def _sense_remaining_message(remaining: int) -> str:
    if remaining >= 4:
        return "The surroundings look lush and verdant."
    if remaining == 3:
        return "The surroundings look a bit browsed."
    if remaining == 2:
        return "The surroundings look picked over."
    if remaining == 1:
        return "The surroundings look scavenged."
    return (
        "As you glance around, it becomes apparent that someone has been "
        "foraging around here recently, and you will be unable to find anything useful."
    )


def _db_rows(server, query, params=None):
    db = getattr(server, "db", None)
    if not db:
        return []
    conn = db._get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def _db_execute(server, query, params=None):
    db = getattr(server, "db", None)
    if not db:
        return
    conn = db._get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
    finally:
        conn.close()


def _room_forage_candidates(server, room):
    raw_tags = getattr(room, "tags", []) or []
    canonical = []
    seen = set()

    for raw_tag in raw_tags:
        tag = (raw_tag or "").strip()
        if not tag:
            continue
        lower = tag.lower()
        if lower.startswith("meta:") or lower in {"no forageables", "gone"}:
            continue
        short_name = _canonical_room_tag(tag).strip()
        if not short_name:
            continue
        key = short_name.lower()
        if key in seen:
            continue
        seen.add(key)
        canonical.append(short_name)

    if not canonical:
        return []

    placeholders = ", ".join(["%s"] * len(canonical))
    return _db_rows(
        server,
        f"""
        SELECT id, name, short_name, noun, article, item_type
        FROM items
        WHERE is_template = 1
          AND LOWER(short_name) IN ({placeholders})
        ORDER BY short_name
        """,
        tuple(name.lower() for name in canonical),
    )


def _room_remaining_slots(server, room_lich_uid: int) -> int:
    _db_execute(
        server,
        """
        DELETE FROM forage_room_depletions
        WHERE room_lich_uid = %s
          AND TIMESTAMPDIFF(SECOND, consumed_at, NOW()) >= regen_seconds
        """,
        (room_lich_uid,),
    )
    rows = _db_rows(
        server,
        "SELECT COUNT(*) AS used_slots FROM forage_room_depletions WHERE room_lich_uid = %s",
        (room_lich_uid,),
    )
    used = int((rows[0] or {}).get("used_slots", 0)) if rows else 0
    return max(0, FORAGE_SLOT_MAX - used)


def _consume_room_slot(server, room_lich_uid: int):
    _db_execute(
        server,
        """
        INSERT INTO forage_room_depletions (room_lich_uid, regen_seconds)
        VALUES (%s, %s)
        """,
        (room_lich_uid, random.randint(FORAGE_MIN_REGEN, FORAGE_MAX_REGEN)),
    )


def _match_requested_candidate(args: str, candidates: list):
    if not args.strip():
        return random.choice(candidates) if candidates else None

    request_tokens = _normalise_request(args)
    if not request_tokens:
        return random.choice(candidates) if candidates else None

    wanted_noun = request_tokens[-1]
    wanted_adjs = request_tokens[:-1]
    matches = []

    for item in candidates:
        cand_tokens = _normalise_request(item.get("short_name") or "")
        if not cand_tokens or cand_tokens[-1] != wanted_noun:
            continue
        cand_adjs = cand_tokens[:-1]
        if len(wanted_adjs) > len(cand_adjs):
            continue
        ok = True
        for idx, adj in enumerate(wanted_adjs):
            if not cand_adjs[idx].startswith(adj):
                ok = False
                break
        if ok:
            matches.append(item)

    if not matches:
        return None
    return random.choice(matches)


def _place_in_free_hand(session, server, item_row: dict):
    hand_attr = None
    slot_name = None
    if not getattr(session, "right_hand", None):
        hand_attr = "right_hand"
        slot_name = "right_hand"
    elif not getattr(session, "left_hand", None):
        hand_attr = "left_hand"
        slot_name = "left_hand"
    else:
        return None

    item_id = int(item_row["id"])
    inv_id = None
    if getattr(server, "db", None) and getattr(session, "character_id", None):
        inv_id = server.db.add_item_to_inventory(session.character_id, item_id, slot=slot_name)

    item = {
        "item_id": item_id,
        "id": item_id,
        "inv_id": inv_id,
        "name": item_row.get("name"),
        "short_name": item_row.get("short_name"),
        "noun": item_row.get("noun"),
        "article": item_row.get("article") or "a",
        "item_type": item_row.get("item_type") or "forage",
        "slot": slot_name,
        "container_id": None,
    }
    setattr(session, hand_attr, item)
    return hand_attr


async def _advance_tutorial_after_forage(session, server, room_id: int):
    if getattr(session, "tutorial_complete", True):
        return
    if int(getattr(session, "tutorial_stage", 0) or 0) != 41:
        return
    session.tutorial_stage = 42
    if getattr(server, "db", None) and getattr(session, "character_id", None):
        server.db.save_quest_progress(session.character_id, session.tutorial_stage, False)
    tutorial = getattr(server, "tutorial", None)
    if tutorial:
        try:
            await tutorial._play_dialogue(session, room_id, 42)
        except Exception:
            pass


async def _cmd_forage_sense(session, server, room, candidates: list):
    skills = getattr(session, "skills", {}) or {}
    surv = skills.get(SKILL_SURVIVAL, {}) if isinstance(skills, dict) else {}
    survival_ranks = int(surv.get("ranks", 0)) if isinstance(surv, dict) else 0
    if survival_ranks < 25:
        await session.send_line("You are not yet skilled enough in Survival to FORAGE SENSE.")
        return

    room_lich_uid = int(getattr(room, "lich_uid", 0) or 0)
    if room_lich_uid <= 0:
        await session.send_line("You cannot get a clear sense of this area's forageables.")
        return

    remaining = _room_remaining_slots(server, room_lich_uid)
    if not candidates:
        await session.send_line("Glancing about, you notice nothing in the immediate area that seems forageable.")
        await session.send_line(_sense_remaining_message(remaining))
        return

    names = [row.get("short_name") for row in candidates if row.get("short_name")]
    if len(names) == 1:
        listing = names[0]
    else:
        listing = ", ".join(names[:-1]) + ", and " + names[-1]
    await session.send_line(
        "Glancing about, you notice the immediate area should support specimens of "
        + listing
        + "."
    )
    await session.send_line(_sense_remaining_message(remaining))


async def cmd_forage(session, cmd, args, server):
    room = getattr(session, "current_room", None)
    if not room:
        return

    sub = (args or "").strip()
    candidates = _room_forage_candidates(server, room)
    if sub.lower() == "sense":
        await _cmd_forage_sense(session, server, room, candidates)
        return

    free_hands = _free_hands(session)
    if free_hands == 0:
        await session.send_line("You need at least one free hand to forage.")
        return

    room_lich_uid = int(getattr(room, "lich_uid", 0) or 0)
    if room_lich_uid <= 0:
        await session.send_line("You cannot get your bearings well enough to forage here.")
        return

    if not candidates:
        await session.send_line("You forage around but find nothing of interest.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    remaining_slots = _room_remaining_slots(server, room_lich_uid)
    if remaining_slots <= 0:
        await session.send_line(
            "As you forage around, you notice that someone has been foraging here recently "
            "and you are unable to find anything useful."
        )
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    target = _match_requested_candidate(sub, candidates)
    if sub and not target:
        await session.send_line(
            "As you carefully forage around you can find no hint of what you are looking for. "
            "You are not even positive where it may be found."
        )
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    if not target:
        await session.send_line("You forage around but find nothing of interest.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    skills = getattr(session, "skills", {}) or {}
    surv = skills.get(SKILL_SURVIVAL, {}) if isinstance(skills, dict) else {}
    perc = skills.get(27, {}) if isinstance(skills, dict) else {}
    survival_ranks = int(surv.get("ranks", 0)) if isinstance(surv, dict) else 0
    perception_bonus = int(perc.get("bonus", 0)) if isinstance(perc, dict) else 0

    score = _open_d100()
    score += _profession_bonus(session, target)
    score += _race_bonus(session, room)
    score += _position_bonus(session)
    score += max(0, survival_ranks // 3)
    score += max(0, perception_bonus // 15)
    score += _stat_bonus(getattr(session, "stat_agility", 50)) // 5
    score += _stat_bonus(getattr(session, "stat_intuition", 50)) // 2

    if getattr(session, "hidden", False):
        score -= 10
    if free_hands == 1:
        score -= 10
    if sub:
        score += 5

    difficulty = 55 if (target.get("item_type") or "").lower() == "herb" else 50
    if score < difficulty:
        await session.send_line("You forage around but find nothing of interest.")
        session.set_roundtime(3)
        await session.send_line(roundtime_msg(3))
        return

    hand_attr = _place_in_free_hand(session, server, target)
    if not hand_attr:
        await session.send_line("You need at least one free hand to forage.")
        return

    _consume_room_slot(server, room_lich_uid)
    found_name = target.get("short_name") or target.get("name") or "something"
    await session.send_line(f"You carefully forage around and manage to find {found_name}!")
    await server.world.broadcast_to_room(
        room.id,
        f"{session.character_name} forages around and finds something.",
        exclude=session,
    )
    if getattr(server, "guild", None):
        try:
            await server.guild.record_event(session, "forage_success")
        except Exception:
            pass
    await _advance_tutorial_after_forage(session, server, room.id)

    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))
