"""
room_hints.py - Context-sensitive command hints shown on room entry.

After a player enters any room, this module inspects what's present
(NPCs, room type, room ID) and prints a single highlighted hint line
showing only the commands that are relevant to that location.

Examples:
  [Bank: CHECK BALANCE, DEPOSIT {#|ALL|NOTE}, WITHDRAW {#} [NOTE]]
  [Shop: ORDER, BUY {#}, SELL {item}, APPRAISE {item}, CUSTOMIZE]
  [Locksmith: ORDER, BUY {#}, SELL {item}, APPRAISE {pick}, RING BELL]
  [Healer: TALK TO {healer}, ASK {healer} ABOUT healing]
"""

from server.core.protocol.colors import colorize, BOLD, BRIGHT_CYAN

HINT_COLOR = BOLD + BRIGHT_CYAN

SHOP_TYPE_HINTS = {
    "weapon":  ("Shop",       ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}", "CUSTOMIZE"]),
    "armor":   ("Shop",       ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}", "CUSTOMIZE"]),
    "magic":   ("Magic Shop", ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}", "CUSTOMIZE"]),
    "herb":    ("Herb Shop",  ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}"]),
    "gem":     ("Gem Shop",   ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}"]),
    "food":    ("Eatery",     ["ORDER", "BUY {#}"]),
    "general": ("Shop",       ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}"]),
    "pawn":    ("Pawn Shop",  ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}", "BACKROOM", "LOOK ON {weapon|armor|arcana|misc} TABLE", "BUY BACKROOM {table} {#}"]),
    "other":   ("Shop",       ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}", "CUSTOMIZE"]),
    "default": ("Shop",       ["ORDER", "BUY {#}", "SELL {item}", "APPRAISE {item}"]),
}

LOCKSMITH_TEMPLATE_IDS = {
    "shind",
    "wl_locksmith_jyhm",
    "tai_locksmith_tai",
    "ti_locksmith_ti",
    "zl_locksmith_zl",
    "cys_locksmith_hihaeim",
    "kf_locksmith_kf",
    "imt_blackfinger",
}

NPC_SERVICE_HINTS = {
    "bank_teller":       ("Bank",       ["CHECK BALANCE", "DEPOSIT {#|ALL|NOTE}", "WITHDRAW {#} [NOTE]", "LOCKER INFO"]),
    "empath_healer":     ("Healer",     ["TALK TO {healer}", "ASK {healer} ABOUT healing"]),
    "guild_clerk":       ("Guild",      ["TALK TO {clerk}", "ASK {clerk} ABOUT register", "ASK {clerk} ABOUT bounty", "ASK {clerk} ABOUT rank", "ASK {clerk} ABOUT checkin", "ASK {clerk} ABOUT vouchers"]),
    "hall_steward":      ("Hall",       ["TALK TO {steward}", "ASK {steward} ABOUT hall"]),
    "wyvern_registrar":  ("Registry",   ["TALK TO {registrar}", "ASK {registrar} ABOUT registration"]),
    "justice_clerk":     ("Justice",    ["TALK TO {clerk}", "ASK {clerk} ABOUT justice"]),
    "travel_clerk":      ("Travel",     ["TALK TO {clerk}", "ASK {clerk} ABOUT travel"]),
    "moving_foreman":    ("Moving Co.", ["TALK TO {foreman}", "ASK {foreman} ABOUT moving"]),
    "historian":         ("Historical Society", ["TALK TO {historian}", "ASK {historian} ABOUT history"]),
    "springs_attendant": ("Spa",        ["TALK TO {attendant}", "ASK {attendant} ABOUT springs"]),
    "arkarti_priest":    ("Temple",     ["TALK TO {priest}", "ASK {priest} ABOUT arkati"]),
    "garden_keeper":     ("Garden",     ["TALK TO {keeper}", "ASK {keeper} ABOUT garden"]),
    "fisherman":         ("Fisherman",  ["TALK TO {fisherman}", "ASK {fisherman} ABOUT fishing"]),
    "halline":           ("Taskmaster", ["TALK TO {taskmaster}", "ASK {taskmaster} ABOUT register", "ASK {taskmaster} ABOUT bounty", "ASK {taskmaster} ABOUT rank", "ASK {taskmaster} ABOUT checkin", "ASK {taskmaster} ABOUT vouchers", "BOUNTY STATUS", "BOUNTY SWAP", "BOUNTY REMOVE"]),
    "rheteger":          ("Taskmaster", ["TALK TO {taskmaster}", "ASK {taskmaster} ABOUT register", "ASK {taskmaster} ABOUT bounty", "ASK {taskmaster} ABOUT rank", "ASK {taskmaster} ABOUT checkin", "ASK {taskmaster} ABOUT vouchers", "BOUNTY STATUS", "BOUNTY SWAP", "BOUNTY REMOVE"]),
    "torsidr":           ("Taskmaster", ["TALK TO {taskmaster}", "ASK {taskmaster} ABOUT register", "ASK {taskmaster} ABOUT bounty", "ASK {taskmaster} ABOUT rank", "ASK {taskmaster} ABOUT checkin", "ASK {taskmaster} ABOUT vouchers", "BOUNTY STATUS", "BOUNTY SWAP", "BOUNTY REMOVE"]),
}

SERVICE_TAG_HINTS = {
    "bank":       ("Bank",       ["CHECK BALANCE", "DEPOSIT {#|ALL|NOTE}", "WITHDRAW {#} [NOTE]", "LOCKER INFO"]),
    "healer":     ("Healer",     ["TALK TO {healer}", "ASK {healer} ABOUT healing"]),
    "guild":      ("Guild",      ["TALK TO {clerk}", "ASK {clerk} ABOUT guild"]),
    "travel":     ("Travel",     ["TALK TO {clerk}", "ASK {clerk} ABOUT travel"]),
    "registrar":  ("Registry",   ["TALK TO {registrar}", "ASK {registrar} ABOUT registration"]),
    "inn":        ("Inn",        ["TALK TO {innkeeper}"]),
    "pawnbroker": ("Pawnbroker", ["ORDER", "APPRAISE {item}", "SELL {item}", "BACKROOM", "LOOK ON {weapon|armor|arcana|misc} TABLE", "BUY BACKROOM {table} {#}"]),
    "priest":     ("Temple",     ["TALK TO {priest}", "ASK {priest} ABOUT arkati"]),
}

MENAGERIE_HINT = (
    "Menagerie",
    [
        "PET SHOP",
        "PET STATUS",
        "PET HELP",
        "TALK TO {keeper}",
        "ASK {keeper} ABOUT floofer",
        "ASK {keeper} ABOUT treat",
        "ASK {keeper} ABOUT swap",
        "PET FEED {treat}",
        "PET CALL",
        "PET DISMISS",
        "PET RELEASE",
    ],
)


def _fmt(label, commands):
    return colorize(f"[{label}: {', '.join(commands)}]", HINT_COLOR)


def _get_guild_label(server, guild_id):
    if not guild_id or not getattr(server, "db", None):
        return "Guild"
    try:
        row = server.db.get_guild_definition(guild_id)
        if row and row.get("name"):
            return row["name"]
    except Exception:
        pass
    return "Guild"


def _get_shop_type(server, shop_id):
    """Look up shop_type from DB for the given shop_id. Returns '' on failure."""
    if not shop_id or not getattr(server, "db", None):
        return ""
    try:
        rows = server.db.execute_query(
            "SELECT shop_type FROM shops WHERE id = %s", (shop_id,)
        )
        if rows:
            return (rows[0][0] or "").lower().strip()
    except Exception:
        pass
    return ""


def _get_pawn_backroom_shop(server, room_id):
    if not getattr(server, "db", None):
        return None
    try:
        rows = server.db.execute_query(
            "SELECT id, name FROM shops WHERE backroom_room_id = %s AND shop_type = 'pawn' LIMIT 1",
            (room_id,),
        )
        if rows:
            return {"id": rows[0][0], "name": rows[0][1]}
    except Exception:
        pass
    return None


def _get_public_locker_context(server, room_id):
    if not getattr(server, "db", None):
        return None
    try:
        return server.db.get_public_locker_location_for_room(room_id)
    except Exception:
        return None


def _get_locker_entry_commands(server, room, locker_ctx):
    if not getattr(server, "db", None) or not locker_ctx:
        return []
    try:
        locker_room_ids = set(server.db.get_public_locker_room_ids(locker_ctx["id"], "locker"))
    except Exception:
        locker_room_ids = set()
    commands = []
    for exit_key, target_room_id in getattr(room, "exits", {}).items():
        if int(target_room_id or 0) not in locker_room_ids:
            continue
        if exit_key.startswith("go_"):
            commands.append("GO " + exit_key[3:].replace("_", " ").upper())
        else:
            commands.append(exit_key.replace("_", " ").upper())
    return sorted(dict.fromkeys(commands))


def _is_locksmith_npc(npc):
    """Best-effort locksmith detection without tying hints to one city."""
    tid = (getattr(npc, "template_id", None) or "").lower().strip()
    if tid in LOCKSMITH_TEMPLATE_IDS:
        return True

    text = " ".join([
        getattr(npc, "name", "") or "",
        getattr(npc, "title", "") or "",
        getattr(npc, "description", "") or "",
    ]).lower()
    return "locksmith" in text or "lockpick" in text


async def show_room_hints(session, room, server):
    """Called after cmd_look on every room entry."""
    shown = set()

    pets = getattr(server, "pets", None)
    if pets and getattr(pets, "is_pet_shop_room", None) and pets.is_pet_shop_room(room.id):
        keeper = "keeper"
        if hasattr(server, "npcs"):
            for npc in server.npcs.get_npcs_in_room(room.id):
                name = str(getattr(npc, "name", "") or "").strip()
                if name:
                    keeper = name
                    break
        label, cmds = MENAGERIE_HINT
        cmds = [cmd.replace("{keeper}", keeper).replace("{treat}", "treat") for cmd in cmds]
        await session.send_line(_fmt(label, cmds))
        shown.add("menagerie")

    if room.id == 17805 and "tv_rogue_shed" not in shown:
        await session.send_line(_fmt("Rogue Entry", [
            "LOOK TOOL",
            "PULL HOE",
            "PULL RAKE",
            "PULL SHOVEL",
            "GO PANEL",
            "OUT",
        ]))
        shown.add("tv_rogue_shed")

    if room.id == 18348 and "tv_rogue_basement" not in shown:
        await session.send_line(_fmt("Rogue Inner Door", [
            "LEAN",
            "PULL",
            "PULL",
            "SLAP",
            "RUB",
            "RUB",
            "PUSH",
            "TURN",
            "OPEN DOOR",
            "GO TUNNEL",
        ]))
        shown.add("tv_rogue_basement")

    if room.id in {36780, 36781, 36782, 36783} and "tv_rogue_guild" not in shown:
        await session.send_line(_fmt("Rogue Guild", [
            "GLD STATUS",
            "GLD JOIN",
            "GLD PAY {months}",
            "GLD CHECKIN",
            "GLD SKILLS",
            "GLD TASK {skill}",
            "GLD PRACTICE",
            "GLD COMPLETE",
            "GLD QUEST START",
            "GLD QUEST",
            "GO CHUTE",
        ]))
        shown.add("tv_rogue_guild")

    guild_engine = getattr(server, "guild", None)
    if room.id == 10434 and guild_engine and "tv_rogue_chute" not in shown:
        membership = getattr(session, "guild_membership", None) or {}
        access = guild_engine.get_access_row(getattr(session, "character_id", 0) or 0, "rogue") or {}
        if str(membership.get("guild_id") or "").lower() == "rogue" or access.get("member_access_at"):
            await session.send_line(_fmt("Rogue Guild", ["GO CHUTE"]))
            shown.add("tv_rogue_chute")

    locker_ctx = _get_public_locker_context(server, room.id)
    if locker_ctx:
        roles = set(locker_ctx.get("roles") or [])
        if "locker" in roles:
            await session.send_line(_fmt("Locker", [
                "OPEN LOCKER",
                "LOCKER MANIFEST",
                "LOOK IN LOCKER",
                "PUT {item} IN LOCKER",
                "GET {item} FROM LOCKER",
                "INSPECT LOCKER",
                "CLOSE LOCKER",
            ]))
            shown.add("locker")
        elif "access" in roles:
            entry_cmds = _get_locker_entry_commands(server, room, locker_ctx)
            if entry_cmds:
                await session.send_line(_fmt("Locker", entry_cmds + ["LOCKER INFO"]))
                shown.add("locker_access")
        elif "bank" in roles:
            await session.send_line(_fmt("Bank", [
                "CHECK BALANCE",
                "DEPOSIT {#|ALL|NOTE}",
                "WITHDRAW {#} [NOTE]",
                "LOCKER INFO",
                "OPEN LOCKER",
                "LOCKER MANIFEST",
                "PUT {item} IN LOCKER",
                "GET {item} FROM LOCKER",
            ]))
            shown.add("bank")

    pawn_backroom = _get_pawn_backroom_shop(server, room.id)
    if pawn_backroom:
        await session.send_line(_fmt("Pawn Backroom", [
            "BACKROOM",
            "LOOK ON {weapon|armor|arcana|misc} TABLE",
            "BUY {table} {#}",
            "BUY BACKROOM {table} {#}",
        ]))
        shown.add("pawn_backroom")

    if not hasattr(server, "npcs"):
        return

    for npc in server.npcs.get_npcs_in_room(room.id):
        tid = getattr(npc, "template_id", None) or ""

        if getattr(npc, "guild_id", None) and "profession_guild" not in shown:
            label = _get_guild_label(server, getattr(npc, "guild_id", None))
            cmds = [
                "GLD STATUS",
                "GLD JOIN",
                "GLD PAY {months}",
                "GLD CHECKIN",
                "GLD RANK",
                "GLD SKILLS",
                "GLD TASK {skill}",
                "GLD PRACTICE",
                "GLD COMPLETE",
                "GLD QUEST START",
                "GLD QUEST",
                "GLD VOUCHERS",
                "GLD SWAP {skill}",
                "GLD PASSWORD",
                "GLD NOMINATE {person}",
                "GLD PROMOTE {person} IN {skill}",
                "TALK TO {master}",
            ]
            if getattr(npc, "guild_id", None) == "rogue":
                cmds.insert(-1, "CHEAPSHOT {maneuver} {target}")
                cmds.insert(-1, "LMASTER HELP")
            await session.send_line(_fmt(label, cmds))
            shown.add("profession_guild")

        if _is_locksmith_npc(npc) and "locksmith" not in shown:
            await session.send_line(_fmt("Locksmith", [
                "ORDER",
                "BUY {#}",
                "SELL {item}",
                "APPRAISE {pick}",
                "RING BELL",
                "PAY {amount}",
                "MYJOBS",
                "CLAIM {#}",
                "BOXPICK",
            ]))
            shown.add("locksmith")
            continue

        if getattr(npc, "role", "") == "shopkeeper" and getattr(npc, "shop_id", None):
            if tid not in shown:
                shop_type = _get_shop_type(server, npc.shop_id)
                label, cmds = SHOP_TYPE_HINTS.get(shop_type, SHOP_TYPE_HINTS["default"])
                await session.send_line(_fmt(label, cmds))
                shown.add(tid)
            continue

        if tid and tid in NPC_SERVICE_HINTS and tid not in shown:
            label, cmds = NPC_SERVICE_HINTS[tid]
            await session.send_line(_fmt(label, cmds))
            shown.add(tid)
            continue

        for service_tag, (label, cmds) in SERVICE_TAG_HINTS.items():
            if service_tag in shown:
                continue
            if npc.matches_service(service_tag):
                await session.send_line(_fmt(label, cmds))
                shown.add(service_tag)
                break

    if not shown:
        for item in getattr(room, "_ground_items", []):
            if item.get("noun") in ("coffer", "chest", "box", "lockbox"):
                await session.send_line(_fmt("Locked Container", ["PICK {coffer}", "DISARM {coffer}"]))
                break
