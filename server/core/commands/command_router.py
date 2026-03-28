"""
CommandRouter - Parses player input and dispatches to command handlers.
"""

import logging
from typing import Dict, Callable
from server.core.commands.player.movement import cmd_move, cmd_go, cmd_look
from server.core.commands.player.communication import (
    cmd_say, cmd_whisper, cmd_shout, cmd_sing, cmd_ask, cmd_tell
)
from server.core.commands.player.info import (
    cmd_health, cmd_skills, cmd_who, cmd_experience, cmd_info,
    cmd_wealth, cmd_help, cmd_time, cmd_calendar, cmd_status, cmd_weight,
    cmd_fame, cmd_set
)
from server.core.commands.player.inventory import (
    cmd_inventory, cmd_get, cmd_drop, cmd_give, cmd_loot, cmd_yell,
    cmd_swap, cmd_wear, cmd_remove, cmd_put, cmd_stow, cmd_open, cmd_close,
    cmd_inspect, cmd_get_all, cmd_look_in
)
from server.core.commands.player.actions import (
    cmd_stand, cmd_sit, cmd_kneel, cmd_lie, cmd_rest, cmd_sleep, cmd_use, cmd_tend, cmd_wounds,
    cmd_read, cmd_invoke, cmd_steal,
    # Legacy hardcoded emotes kept as fallback if Lua is unavailable
    cmd_bow, cmd_wave, cmd_nod, cmd_grin, cmd_smile, cmd_frown,
    cmd_laugh, cmd_cry, cmd_sigh, cmd_shrug, cmd_wince, cmd_ponder,
    cmd_gasp, cmd_groan, cmd_dance, cmd_cheer, cmd_salute, cmd_curtsy,
    cmd_growl, cmd_snicker, cmd_cackle, cmd_hug, cmd_kiss,
    # Lua-driven emote loader + free-form EMOTE command
    load_emotes_from_lua, cmd_emote,
)
from server.core.commands.player.combat import (
    cmd_attack, cmd_kill, cmd_ambush, cmd_hide, cmd_sneak, cmd_stance,
    cmd_search, cmd_skin, cmd_autoskin, cmd_feint, cmd_aim, cmd_sweep, cmd_subdue, cmd_cheapshot,
    cmd_stunman, cmd_rgambit, cmd_ready, cmd_fire, cmd_hurl, cmd_mstrike
)
from server.core.commands.player.lockpicking import cmd_pick, cmd_disarm, cmd_detect, cmd_lmaster
from server.core.commands.player.boxpick import (
    cmd_submit, cmd_boxpick, cmd_claim, cmd_done, cmd_ring, cmd_pay,
    cmd_cancel_job, cmd_forfeit, cmd_myjobs, cmd_repair
)
from server.core.commands.player.shop import (
    cmd_order, cmd_buy, cmd_sell, cmd_appraise, cmd_ask_npc, cmd_talk_npc, cmd_mark, cmd_backroom
)
from server.core.commands.player.bank import (
    cmd_deposit, cmd_withdraw, cmd_check, cmd_bank, cmd_locker
)
from server.core.commands.player.customize import cmd_customize, cmd_confirm, cmd_redeem
from server.core.commands.player.dye import cmd_dye, cmd_dye_colors
from server.core.commands.player.climbing import cmd_climb, cmd_swim
from server.core.commands.player.training import cmd_train
from server.core.commands.player.spellcasting import cmd_prepare, cmd_cast, cmd_incant, cmd_release, cmd_send
from server.core.commands.player.fixstat_convert import cmd_fixstats, cmd_convert
from server.core.commands.player.weapon_techniques import cmd_weapon
from server.core.commands.player.party import cmd_party
from server.core.commands.player.esp import cmd_esp, cmd_think, cmd_chat
from server.core.commands.player.foraging import cmd_forage
from server.core.commands.player.crafting import cmd_artisan, cmd_fletching, cmd_cobbling, cmd_cut, cmd_measure
from server.core.commands.player.guild import cmd_gld, cmd_questlog, cmd_questslog, cmd_answer, cmd_bounty

log = logging.getLogger(__name__)


async def cmd_ask_combined(session, cmd, args, server):
    """ASK - Try NPC first, then fall back to player communication."""
    if not args:
        await session.send_line("Ask whom about what?")
        return

    # Parse out the target name
    lower = args.lower()
    if ' about ' in lower:
        idx = lower.index(' about ')
        target_name = args[:idx].strip()
    else:
        parts = args.split(None, 1)
        target_name = parts[0]

    # Check if there's an NPC by that name in the room
    if hasattr(server, 'npcs') and session.current_room:
        npc = server.npcs.find_npc_in_room(session.current_room.id, target_name.lower())
        if npc:
            await cmd_ask_npc(session, cmd, args, server)
            return

    # Fall back to player ASK
    await cmd_ask(session, cmd, args, server)


class CommandRouter:
    """Routes raw player input to the appropriate command handler."""

    def __init__(self, server):
        self.server = server
        self._commands: Dict[str, Callable] = {}
        self._aliases: Dict[str, str] = {}

    def register(self, name, handler, aliases=None):
        """Register a command handler."""
        self._commands[name.lower()] = handler
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = name.lower()

    def register_default_commands(self):
        """Register all built-in commands."""

        # ---- Movement ----
        self.register("look", cmd_look, aliases=["l"])
        self.register("north", cmd_move, aliases=["n"])
        self.register("south", cmd_move, aliases=["s"])
        self.register("east", cmd_move, aliases=["e"])
        self.register("west", cmd_move, aliases=["w"])
        self.register("northeast", cmd_move, aliases=["ne"])
        self.register("northwest", cmd_move, aliases=["nw"])
        self.register("southeast", cmd_move, aliases=["se"])
        self.register("southwest", cmd_move, aliases=["sw"])
        self.register("up", cmd_move, aliases=["u"])
        self.register("down", cmd_move, aliases=["d"])
        self.register("out", cmd_move)
        self.register("go", cmd_go)

        # ---- Communication ----
        self.register("say", cmd_say, aliases=["'"])
        self.register("whisper", cmd_whisper)
        self.register("yell", cmd_yell)
        self.register("shout", cmd_shout)
        self.register("sing", cmd_sing)
        self.register("ask", cmd_ask_combined)
        self.register("talk", cmd_talk_npc, aliases=["speak"])
        self.register("tell", cmd_tell)

        # ---- Information ----
        self.register("health", cmd_health, aliases=["hp"])
        self.register("status", cmd_status, aliases=["stat"])
        self.register("inventory", cmd_inventory, aliases=["inv"])
        self.register("skills", cmd_skills, aliases=["skill"])
        self.register("who", cmd_who)
        self.register("experience", cmd_experience, aliases=["exp"])
        self.register("fame", cmd_fame)
        self.register("info", cmd_info)
        self.register("wealth", cmd_wealth)
        self.register("help", cmd_help)
        self.register("set", cmd_set)
        self.register("time", cmd_time)
        self.register("calendar", cmd_calendar)
        self.register("weight", cmd_weight, aliases=["wt", "encumbrance", "encumb"])

        # ---- Inventory Management ----
        self.register("get", cmd_get, aliases=["take"])
        self.register("get all", cmd_get_all, aliases=["getall"])
        self.register("look in", cmd_look_in)
        self.register("empty", cmd_get_all)   # alias: EMPTY coffer
        self.register("drop", cmd_drop)
        self.register("give", cmd_give)
        self.register("loot", cmd_loot)
        self.register("swap", cmd_swap)
        self.register("wear", cmd_wear, aliases=["wield"])
        self.register("remove", cmd_remove)
        self.register("put", cmd_put, aliases=["place"])
        self.register("stow", cmd_stow)
        self.register("open", cmd_open)
        self.register("close", cmd_close)
        self.register("inspect", cmd_inspect, aliases=["insp"])

        # ---- Actions / Social ----
        self.register("stand", cmd_stand)
        self.register("sit",   cmd_sit)
        self.register("rest",  cmd_rest)
        self.register("sleep", cmd_sleep)
        self.register("kneel", cmd_kneel)
        self.register("lie",   cmd_lie)
        self.register("use",   cmd_use, aliases=["eat", "drink", "apply"])
        self.register("steal", cmd_steal)
        self.register("tend",   cmd_tend)
        self.register("wounds", cmd_wounds, aliases=["wound", "injuries", "inj"])
        self.register("prepare", cmd_prepare, aliases=["prep"])
        self.register("cast", cmd_cast)
        self.register("channel", cmd_cast)
        self.register("evoke", cmd_cast)
        self.register("summon", cmd_cast)
        self.register("incant", cmd_incant)
        self.register("release", cmd_release)
        self.register("send", cmd_send)
        self.register("read", cmd_read)
        self.register("invoke", cmd_invoke)
        self.register("forage", cmd_forage)
        self.register("artisan", cmd_artisan)
        self.register("fletching", cmd_fletching)
        self.register("cobbling", cmd_cobbling)
        self.register("cut", cmd_cut)
        self.register("measure", cmd_measure)
        self.register("swim", cmd_swim)
        self.register("quest", cmd_questlog)
        self.register("quests", cmd_questslog)
        self.register("answer", cmd_answer)
        self.register("bounty", cmd_bounty)

        # Free-form custom emote — always available
        self.register("emote", cmd_emote, aliases=["em"])

        # ── Lua-driven emotes ─────────────────────────────────────────────
        # Load all emotes from scripts/data/emotes.lua.
        # Any verb not returned by Lua falls back to the hardcoded handler.
        # To add / edit emotes: edit scripts/data/emotes.lua only.
        _LEGACY_EMOTES = {
            "bow": cmd_bow, "wave": cmd_wave, "nod": cmd_nod,
            "grin": cmd_grin, "smile": cmd_smile, "frown": cmd_frown,
            "laugh": cmd_laugh, "cry": cmd_cry, "sigh": cmd_sigh,
            "shrug": cmd_shrug, "wince": cmd_wince, "ponder": cmd_ponder,
            "gasp": cmd_gasp, "groan": cmd_groan, "dance": cmd_dance,
            "cheer": cmd_cheer, "salute": cmd_salute, "curtsy": cmd_curtsy,
            "growl": cmd_growl, "snicker": cmd_snicker, "cackle": cmd_cackle,
            "hug": cmd_hug, "kiss": cmd_kiss,
        }

        lua_emotes = load_emotes_from_lua(self.server)
        if lua_emotes:
            for verb, handler in lua_emotes.items():
                self.register(verb, handler)
            # Register any legacy verbs not covered by the Lua file
            for verb, handler in _LEGACY_EMOTES.items():
                if verb not in lua_emotes:
                    self.register(verb, handler)
            log.info("CommandRouter: %d emotes registered from Lua", len(lua_emotes))
        else:
            # Lua unavailable — fall back to hardcoded set
            log.warning("CommandRouter: Lua emotes unavailable, using %d legacy emotes",
                        len(_LEGACY_EMOTES))
            for verb, handler in _LEGACY_EMOTES.items():
                self.register(verb, handler)

        # Track all registered emote verbs for RT-exempt set (built dynamically)
        self._emote_verbs = set(lua_emotes.keys() if lua_emotes else _LEGACY_EMOTES.keys())
        self._emote_verbs.update(_LEGACY_EMOTES.keys())
        self._emote_verbs.add("emote")
        self._emote_verbs.add("em")

        # ---- Combat ----
        self.register("attack", cmd_attack, aliases=["att"])
        self.register("kill", cmd_kill)
        self.register("ambush", cmd_ambush)
        self.register("ready", cmd_ready)
        self.register("fire", cmd_fire)
        self.register("hurl", cmd_hurl, aliases=["throw"])
        self.register("mstrike", cmd_mstrike, aliases=["mstr"])
        self.register("hide", cmd_hide)
        self.register("sneak", cmd_sneak)
        self.register("stance", cmd_stance)
        self.register("sweep", cmd_sweep)
        self.register("subdue", cmd_subdue)
        self.register("cheapshot", cmd_cheapshot)
        self.register("stunman", cmd_stunman)
        self.register("rgambit", cmd_rgambit, aliases=["divert"])
        self.register("feint",  cmd_feint)
        self.register("aim",    cmd_aim)
        self.register("search", cmd_search)
        self.register("skin", cmd_skin)
        self.register("autoskin", cmd_autoskin)

        # ---- Shop ----
        self.register("order", cmd_order)
        self.register("buy", cmd_buy, aliases=["purchase"])
        self.register("sell", cmd_sell)
        self.register("appraise", cmd_appraise)
        self.register("backroom", cmd_backroom)
        self.register("mark", cmd_mark)

        # ---- Lockpicking ----
        self.register("pick", cmd_pick)
        self.register("disarm", cmd_disarm)
        self.register("detect", cmd_detect)
        self.register("lmaster", cmd_lmaster, aliases=["lm"])

        # ---- Locksmith services / picking queue ----
        self.register("ring", cmd_ring)
        self.register("pay", cmd_pay)
        self.register("submit", cmd_submit)
        self.register("boxpick", cmd_boxpick, aliases=["pickjobs"])
        self.register("claim", cmd_claim)
        self.register("done", cmd_done)
        self.register("cancel", cmd_cancel_job)
        self.register("forfeit", cmd_forfeit)
        self.register("myjobs", cmd_myjobs)
        self.register("repair", cmd_repair)

        # ---- Banking ----
        self.register("deposit", cmd_deposit)
        self.register("withdraw", cmd_withdraw)
        self.register("check", cmd_check)
        self.register("bank", cmd_bank)
        self.register("locker", cmd_locker)

        # ---- Shop customization ----
        self.register("customize", cmd_customize)
        self.register("confirm",   cmd_confirm)
        self.register("redeem",    cmd_redeem)

        # ---- Dye ----
        self.register("dye",    cmd_dye)

        # ---- Climbing ----
        self.register("climb", cmd_climb)
        self.register("train", cmd_train)
        self.register("fixstats", cmd_fixstats)
        self.register("convert", cmd_convert)
        self.register("weapon", cmd_weapon)
        self.register("party",  cmd_party, aliases=["pt"])
        self.register("gld", cmd_gld)

        # ---- ESP / Channels ----
        self.register("esp",   cmd_esp)
        self.register("think", cmd_think)
        self.register("chat",  cmd_chat)

    async def handle(self, session, raw_input: str):
        """Parse and dispatch a command."""
        if not raw_input:
            await session.send_prompt()
            return

        # ── Death menu intercept ───────────────────────────────────────────
        if getattr(session, 'death_choice_pending', False):
            if hasattr(self.server, 'death'):
                await self.server.death.process_death_choice(session, raw_input.strip())
            await session.send_prompt()
            return

        # ── Ghost state — only LOOK and communication allowed ──────────────
        if getattr(session, 'is_dead', False):
            parts = raw_input.split(None, 1)
            cmd_check = parts[0].lower() if parts else ""
            resolved_check = self._aliases.get(cmd_check, cmd_check)
            GHOST_ALLOWED = {"look", "l", "say", "yell", "whisper", "think",
                             "ooc", "who", "experience", "exp", "party", "pt",
                             "esp", "chat", "tell"}
            if resolved_check not in GHOST_ALLOWED:
                await session.send_line(
                    "You are incorporeal.  You can only LOOK and speak while waiting for Sergeant Beefy."
                )
                await session.send_prompt()
                return

        # Split into command and arguments
        parts = raw_input.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # ── Multi-word command matching (e.g. "get all", "look in") ────────
        # Check if the first two words form a registered command/alias.
        if args:
            first_arg = args.split(None, 1)[0].lower()
            two_word = cmd + " " + first_arg
            resolved_two = self._aliases.get(two_word, two_word)
            if resolved_two in self._commands:
                cmd = resolved_two
                remaining = args.split(None, 1)
                args = remaining[1] if len(remaining) > 1 else ""

        # Check roundtime (some commands bypass RT)
        rt_exempt = {
            "look", "l", "who", "health", "inventory", "inv", "think",
            "experience", "exp", "fame", "info", "skills", "skill", "stance",
            "wealth", "help", "time", "order", "list", "appraise", "sneak", "status", "stat",
            "set", "answer",
            "weight", "wt", "encumbrance", "encumb",
            "rest", "sit", "stand", "sleep", "lie", "kneel", "tend", "wounds", "wound", "injuries", "inj", "use", "eat", "drink",
            "bank", "check", "deposit", "withdraw",
            "boxpick", "pickjobs", "myjobs", "repair", "ring", "pay",
            "claim", "done", "cancel", "forfeit", "submit",
            "customize", "order", "list", "mark",
            "look in", "detect", "get all", "getall", "empty",
            "party", "pt", "gld",
            "esp", "think", "chat", "tell", "whisper",
        }
        # All social emotes (Lua + legacy) bypass RT automatically
        rt_exempt.update(getattr(self, "_emote_verbs", set()))

        # Resolve aliases first for RT check
        resolved_cmd = self._aliases.get(cmd, cmd)

        guild_engine = getattr(self.server, "guild", None)
        if guild_engine and guild_engine.handles_interaction(resolved_cmd):
            handled = await guild_engine.try_handle_interaction(session, resolved_cmd, args)
            if handled:
                await session.send_prompt()
                return

        rt = session.get_roundtime()
        if rt > 0 and resolved_cmd not in rt_exempt:
            from server.core.protocol.colors import colorize, TextPresets
            await session.send_line(colorize(
                'Roundtime: ' + str(rt) + ' seconds remaining.',
                TextPresets.ROUNDTIME
            ))
            await session.send_prompt()
            return

        # Use resolved command
        cmd = resolved_cmd

        # Tutorial interception - let tutorial handle commands first
        if hasattr(session, 'tutorial_complete') and not session.tutorial_complete:
            if hasattr(self.server, 'tutorial'):
                try:
                    handled = await self.server.tutorial.on_command(session, cmd, args)
                    if handled:
                        await session.send_prompt()
                        return
                except Exception as e:
                    log.error("Tutorial command error (%s): %s", raw_input, e, exc_info=True)

        # Find handler
        handler = self._commands.get(cmd)
        if handler:
            try:
                await handler(session, cmd, args, self.server)
            except Exception as e:
                log.error("Command error (%s): %s", raw_input, e, exc_info=True)
                await session.send_line("Something went wrong.")
        else:
            await session.send_line("What are you trying to do?  Type HELP for a list of commands.")

        # Send prompt after command
        await session.send_prompt()

    @property
    def command_count(self):
        return len(self._commands)
