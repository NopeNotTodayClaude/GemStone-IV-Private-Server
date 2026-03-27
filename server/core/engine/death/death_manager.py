"""
DeathManager - Handles the full player death flow for the GemStone IV private server.

Two revival paths:

  [1] DEED REVIVAL
      Consumes one deed from inventory.
      Revives in place with 50% HP, no stat penalty, auto-hidden.

  [2] GHOST / SERGEANT BEEFY ROUTE
      - Player enters ghost state (LOOK + chat only).
      - Nearest cleric room found via BFS.
      - Sergeant Beefy NPC spawns there and travels 1 room/sec to the corpse.
        Others in rooms along the path see him pass.
      - Dead player gets a distance ping every 15 seconds.
      - Beefy arrives, does a 10-second arrival sequence (emotes + scolding).
      - Beefy drags the body back at 1 room/sec; player sees each room transition.
      - At the cleric room: randomly named cleric NPC spawns, raises player at 1% HP.
      - 90% stat penalty applied, recovers at +1.5% of base per 5 seconds (~5 min).
      - Beefy and cleric exchange a few lines then both depart and despawn.

Other players see the dead player's body in the room (shown in LOOK).
"""

import asyncio
import random
import logging
import time

from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)

# ── Cleric room registry ───────────────────────────────────────────────────────
# Maps zone_slug -> list of room_ids that have a cleric / revival service.
# Add more cities here as they are built out.
CLERIC_ROOMS = {
    "tavaalor": [10376, 10372, 10369],   # cleric_guild, cleric_shop, hall_of_arkarti
    # Future cities:
    # "wehnimers_landing": [XXXXX, XXXXX],
    # "icemule_trace":     [XXXXX],
}

# ── Cleric NPC name pool ───────────────────────────────────────────────────────
CLERIC_NAMES = [
    "Aelindra",
    "Taerivyn",
    "Ireniel",
    "Caerith",
    "Sylthara",
    "Vaelindor",
    "Miraeth",
    "Elowyn",
]

# ── Stat penalty constants ─────────────────────────────────────────────────────
DEATH_STAT_MULT       = 0.10   # 10% of normal stats after ghost revival
STAT_RECOVERY_PER_5S  = 0.015  # +1.5% of base every 5 seconds

# ── Beefy arrival emote sequence ──────────────────────────────────────────────
# Each entry is (delay_before_line_seconds, message)
BEEFY_ARRIVAL_EMOTES = [
    (1.5, "Sergeant Beefy surveys the carnage with a slow, measured look."),
    (2.0, "Sergeant Beefy shakes his head and mutters something under his breath."),
    (2.0, "Sergeant Beefy plants a boot beside your body and sighs with tremendous theatrical weight."),
    (2.0, "Sergeant Beefy looks down at you, up at the ceiling, then back down at you."),
    (2.5, "Sergeant Beefy cracks his knuckles loudly and rolls his shoulders."),
]

# Lines Beefy says once he decides to move
BEEFY_GRAB_LINES = [
    "Sergeant Beefy says, \"Right then.  Let's get you out of here.\"",
    "Sergeant Beefy kneels down and grabs a firm hold of your body.",
    "Sergeant Beefy begins dragging you toward the cleric.",
]

# ── Revival dialogue ───────────────────────────────────────────────────────────
CLERIC_RAISE_LINES = [
    "{cleric} kneels over you and raises both hands in quiet prayer.",
    "{cleric} says, \"May Lorminstra grant you one more chance.\"",
    "{cleric} draws upon the divine and calls your spirit back into the mortal realm.",
]

BEEFY_POST_RAISE = [
    "Sergeant Beefy says, \"Try to stay alive next time, eh?\"",
    "Sergeant Beefy says, \"Third time this week.  I'm keeping count.\"",
]

CLERIC_POST_RAISE = [
    "{cleric} says, \"Be more careful next time.  Even I have my limits.\"",
    "{cleric} says, \"Go rest somewhere safe before you go back out there.\"",
]


class DeathManager:
    """Manages player death, revival choices, and Sergeant Beefy."""

    def __init__(self, server):
        self.server = server
        # Track active Beefy tasks: session_id -> asyncio.Task
        self._beefy_tasks: dict = {}

    # ══════════════════════════════════════════════════════════════════════════
    # Entry point — called from combat engine when HP hits 0
    # ══════════════════════════════════════════════════════════════════════════

    async def handle_player_death(self, session, killer=None):
        """
        Full death entry point.
        Ends combat, plays death scene, presents revival menu.
        """
        # ── End all combat in the room ─────────────────────────────────────
        session.in_combat  = False
        session.target     = None
        if killer:
            killer.in_combat = False
            killer.target    = None

        # Drop all other creatures' aggro on this player too
        if session.current_room and hasattr(self.server, 'creatures'):
            for creature in self.server.creatures.get_creatures_in_room(
                    session.current_room.id):
                if getattr(creature, 'target', None) is session:
                    creature.in_combat = False
                    creature.target    = None

        # ── Mark dead ─────────────────────────────────────────────────────
        session.is_dead             = True
        session.death_choice_pending = True
        session.death_room_id       = session.current_room.id if session.current_room else 0
        session.health_current      = 0
        session.position            = "lying"

        # ── Notify party that this member has fallen ───────────────────────
        try:
            from server.core.commands.player.party import on_party_member_death
            await on_party_member_death(session, self.server)
        except Exception:
            pass

        # ── Immediately clear all DOT and debuff status effects ────────────
        # Dead players must not continue bleeding, poisoning, etc.
        # StatusManager.clear_all purges by category; we wipe DOTs + debuffs.
        status = getattr(self.server, "status", None)
        if status:
            for cat in ("DEBUFF_DOT", "DEBUFF_COMBAT", "DEBUFF_STAT", "DEBUFF_CONTROL"):
                status.clear_all(session, cat)
        elif hasattr(session, "status_effects") and session.status_effects:
            # Fallback: nuke the whole dict — nothing should tick on a corpse
            session.status_effects = {}

        # Broadcast to room
        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                colorize(
                    f"  {session.character_name} collapses lifelessly to the ground.",
                    TextPresets.COMBAT_DEATH
                ),
                exclude=session
            )

        # ── Dramatic pause + death text ────────────────────────────────────
        await asyncio.sleep(2)

        death_flavor = random.choice([
            "The world narrows to a cold pinpoint of light, and then... silence.",
            "A great weight presses down on you and the sounds of battle fade to nothing.",
            "Darkness rushes in from the edges of your vision.  You feel yourself slipping away.",
            "The ground rises up to meet you.  Everything goes terribly, absolutely quiet.",
        ])
        await session.send_line("")
        await session.send_line(colorize(f"  {death_flavor}", TextPresets.COMBAT_DEATH))
        await session.send_line("")

        await asyncio.sleep(2)

        # ── Revival menu ───────────────────────────────────────────────────
        await self._show_death_menu(session)

    # ══════════════════════════════════════════════════════════════════════════
    # Death menu
    # ══════════════════════════════════════════════════════════════════════════

    async def _show_death_menu(self, session):
        deed_count = self._count_deeds(session)
        deed_label = (
            colorize(f"  [1]  Use a Deed  ({deed_count} remaining)", TextPresets.EXPERIENCE)
            if deed_count > 0
            else colorize(f"  [1]  Use a Deed  (0 remaining)  -- unavailable", TextPresets.SYSTEM)
        )
        await session.send_line(colorize("  You have been slain.", TextPresets.COMBAT_DEATH))
        await session.send_line("")
        await session.send_line(deed_label)
        await session.send_line(colorize(
            "       Revive in place instantly.  No penalties.  50% HP.  You will be hidden.",
            TextPresets.SYSTEM
        ))
        await session.send_line("")
        await session.send_line(colorize("  [2]  Cry out as a spirit", TextPresets.WARNING))
        await session.send_line(colorize(
            "       Sergeant Beefy will come for you.  90% stat penalty on revival.",
            TextPresets.SYSTEM
        ))
        await session.send_line("")

    # ══════════════════════════════════════════════════════════════════════════
    # Choice handler — called by command router when session.death_choice_pending
    # ══════════════════════════════════════════════════════════════════════════

    async def process_death_choice(self, session, choice: str):
        choice = choice.strip()

        if choice == "1":
            deed_count = self._count_deeds(session)
            if deed_count == 0:
                await session.send_line(colorize(
                    "  You have no deeds.  Choose option 2 to cry out as a spirit.",
                    TextPresets.WARNING
                ))
                await self._show_death_menu(session)
                return
            await self._deed_revival(session)

        elif choice == "2":
            await self._begin_ghost_route(session)

        else:
            await session.send_line("  Please enter 1 or 2.")
            await self._show_death_menu(session)

    # ══════════════════════════════════════════════════════════════════════════
    # Path A — Deed revival
    # ══════════════════════════════════════════════════════════════════════════

    async def _deed_revival(self, session):
        session.death_choice_pending = False

        # Consume one deed
        self._consume_deed(session)

        # Revive
        session.is_dead        = False
        session.health_current = max(1, session.health_max // 2)
        session.position       = "standing"
        session.hidden         = True

        await session.send_line("")
        await session.send_line(colorize(
            "  The deed pulses with warm light and dissolves into your palm.",
            TextPresets.EXPERIENCE
        ))
        await session.send_line(colorize(
            "  You feel your spirit rush back into your body.  You are alive!",
            TextPresets.EXPERIENCE
        ))
        await session.send_line(colorize(
            "  You move quietly into the shadows, unseen for now.",
            TextPresets.SYSTEM
        ))
        await session.send_line("")

        if session.current_room:
            await self.server.world.broadcast_to_room(
                session.current_room.id,
                f"  {session.character_name}'s body stirs — and then is gone.",
                exclude=session
            )

        self._save_session(session)

    # ══════════════════════════════════════════════════════════════════════════
    # Path B — Ghost / Sergeant Beefy
    # ══════════════════════════════════════════════════════════════════════════

    async def _begin_ghost_route(self, session):
        session.death_choice_pending = False

        await session.send_line("")
        await session.send_line(colorize(
            "  You cry out into the void as a spirit, hoping someone hears...",
            TextPresets.COMBAT_DEATH
        ))
        await session.send_line(colorize(
            "  You are incorporeal.  You can LOOK and speak, but little else.",
            TextPresets.SYSTEM
        ))
        await session.send_line("")

        # Find nearest cleric room
        death_room_id  = session.death_room_id or 0
        cleric_room_id = self._find_nearest_cleric_room(death_room_id)

        if cleric_room_id is None:
            # Fallback — no cleric room found, just revive with penalty
            log.warning("No cleric room found from room %d — emergency revive", death_room_id)
            await self._ghost_revive(session, death_room_id, in_place=True)
            return

        # Fire and forget Beefy task
        task = asyncio.create_task(
            self._run_beefy_sequence(session, cleric_room_id, death_room_id)
        )
        self._beefy_tasks[id(session)] = task

    async def _run_beefy_sequence(self, session, cleric_room_id: int, death_room_id: int):
        """Full async Beefy journey: spawn → travel → arrive → drag → revive → despawn."""
        try:
            world = self.server.world

            # ── Build path from cleric room to death room ──────────────────
            path_to_corpse = world.find_path(cleric_room_id, death_room_id)
            if not path_to_corpse:
                log.warning(
                    "Beefy could not find path from %d to %d",
                    cleric_room_id, death_room_id
                )
                await self._ghost_revive(session, death_room_id, in_place=True)
                return

            beefy_room_id = cleric_room_id
            distance      = len(path_to_corpse) - 1  # steps remaining

            # ── Spawn Beefy in cleric room ─────────────────────────────────
            await world.broadcast_to_room(
                cleric_room_id,
                colorize(
                    "Sergeant Beefy strides purposefully out of the room.",
                    TextPresets.NPC_SPEECH if hasattr(TextPresets, 'NPC_SPEECH') else TextPresets.SYSTEM
                )
            )
            if session.is_dead:
                await session.send_line(colorize(
                    f"  Sergeant Beefy has been dispatched.  He is approximately "
                    f"{distance} second{'s' if distance != 1 else ''} away.",
                    TextPresets.SYSTEM
                ))

            # ── Beefy travels to corpse (1 room/sec) ──────────────────────
            last_ping_time = time.time()

            for i in range(1, len(path_to_corpse)):
                await asyncio.sleep(1)

                prev_room = path_to_corpse[i - 1]
                curr_room = path_to_corpse[i]

                from_dir = world.get_direction_between(prev_room, curr_room)
                to_dir   = _opposite_direction(from_dir)

                # Broadcast departure from prev room
                await world.broadcast_to_room(
                    prev_room,
                    f"Sergeant Beefy strides out to the {from_dir}."
                )

                # Broadcast arrival in curr room
                await world.broadcast_to_room(
                    curr_room,
                    f"Sergeant Beefy strides in from the {to_dir} and continues without stopping."
                )

                beefy_room_id = curr_room
                distance      = len(path_to_corpse) - 1 - i

                # Ping dead player every 15 seconds
                if session.is_dead and time.time() - last_ping_time >= 15:
                    last_ping_time = time.time()
                    await session.send_line(colorize(
                        f"  Sergeant Beefy is approximately "
                        f"{distance} second{'s' if distance != 1 else ''} away.",
                        TextPresets.SYSTEM
                    ))

            # ── Beefy arrives at death room ────────────────────────────────
            await world.broadcast_to_room(
                death_room_id,
                colorize(
                    f"Sergeant Beefy arrives, his jaw set and his expression unreadable.",
                    TextPresets.SYSTEM
                ),
                exclude=session
            )
            if session.is_dead:
                await session.send_line(colorize(
                    "  Sergeant Beefy has reached you.",
                    TextPresets.SYSTEM
                ))

            # ── 10-second arrival sequence ─────────────────────────────────
            for delay, emote in BEEFY_ARRIVAL_EMOTES:
                await asyncio.sleep(delay)
                await world.broadcast_to_room(death_room_id, emote)

            await asyncio.sleep(1.5)
            for line in BEEFY_GRAB_LINES:
                await world.broadcast_to_room(death_room_id, line)
                await asyncio.sleep(1.5)

            # ── Build return path from death room back to cleric room ──────
            path_back = list(reversed(path_to_corpse))

            # ── Drag sequence (1 room/sec) ─────────────────────────────────
            for i in range(1, len(path_back)):
                await asyncio.sleep(1)

                prev_room = path_back[i - 1]
                curr_room = path_back[i]

                from_dir = world.get_direction_between(prev_room, curr_room)
                to_dir   = _opposite_direction(from_dir)

                await world.broadcast_to_room(
                    prev_room,
                    f"Sergeant Beefy drags a body out to the {from_dir}."
                )
                await world.broadcast_to_room(
                    curr_room,
                    f"Sergeant Beefy drags a body in from the {to_dir}."
                )

                # Dead player sees each room they pass through
                if session.is_dead:
                    room_obj = world.get_room(curr_room)
                    if room_obj:
                        from server.core.protocol.colors import room_title, room_desc
                        await session.send_line("")
                        await session.send_line(
                            room_title(room_obj.title) +
                            colorize(f"  #{room_obj.id}", TextPresets.SYSTEM)
                        )
                        await session.send_line(
                            room_desc(room_obj.description)
                        )

            # ── Arrive at cleric room ──────────────────────────────────────
            await asyncio.sleep(2)

            cleric_name = random.choice(CLERIC_NAMES)

            await world.broadcast_to_room(
                cleric_room_id,
                colorize(
                    f"Sergeant Beefy carries a body into the room and sets it down carefully.",
                    TextPresets.SYSTEM
                )
            )
            await asyncio.sleep(2)

            # Cleric spawns
            await world.broadcast_to_room(
                cleric_room_id,
                colorize(
                    f"{cleric_name} appears from the shadows of the shrine.",
                    TextPresets.SYSTEM
                )
            )
            await asyncio.sleep(2)

            # Raise sequence
            for line in CLERIC_RAISE_LINES:
                msg = line.replace("{cleric}", cleric_name)
                await world.broadcast_to_room(cleric_room_id, msg)
                await asyncio.sleep(2)

            # ── Revive player ──────────────────────────────────────────────
            await self._ghost_revive(session, cleric_room_id, cleric_name)

            await asyncio.sleep(2)

            # ── Post-revival dialogue ──────────────────────────────────────
            beefy_line  = random.choice(BEEFY_POST_RAISE)
            cleric_line = random.choice(CLERIC_POST_RAISE).replace("{cleric}", cleric_name)

            await world.broadcast_to_room(cleric_room_id, beefy_line)
            await asyncio.sleep(2)

            await world.broadcast_to_room(cleric_room_id, cleric_line)
            await asyncio.sleep(2)

            # ── Beefy and cleric depart ────────────────────────────────────
            await world.broadcast_to_room(
                cleric_room_id,
                colorize(
                    f"{cleric_name} quietly slips out of the room.",
                    TextPresets.SYSTEM
                )
            )
            await asyncio.sleep(1)

            await world.broadcast_to_room(
                cleric_room_id,
                colorize(
                    "Sergeant Beefy nods once and strides out of the room.",
                    TextPresets.SYSTEM
                )
            )

        except asyncio.CancelledError:
            log.info("Beefy task cancelled for session %s", getattr(session, 'character_name', '?'))
        except Exception as e:
            log.error("Beefy sequence error: %s", e, exc_info=True)
            # Emergency fallback
            if session.is_dead:
                await self._ghost_revive(session, death_room_id, in_place=True)
        finally:
            self._beefy_tasks.pop(id(session), None)

    async def _ghost_revive(self, session, revive_room_id: int,
                            cleric_name: str = None, in_place: bool = False):
        """Apply ghost revival: 1% HP, 90% stat penalty.

        in_place=True  -> revive in the room the player is already in (emergency).
        in_place=False -> move player to revive_room_id (Beefy/cleric path).
        """
        session.is_dead  = False
        session.position = "standing"

        world = self.server.world

        if not in_place:
            # Move to cleric room
            old_room = session.current_room
            new_room = world.get_room(revive_room_id)
            if new_room:
                if old_room:
                    world.remove_player_from_room(session, old_room.id)
                session.current_room = new_room
                world.add_player_to_room(session, new_room.id)

        session.death_room_id = None

        # Set HP to 1% (min 1)
        session.health_current = max(1, session.health_max // 100)

        # 90% stat penalty
        session.death_stat_mult = DEATH_STAT_MULT

        # ── XP absorption penalty — drain all unabsorbed field experience ──
        xp_lost = int(getattr(session, 'field_experience', 0))
        session.field_experience = 0
        if self.server.db and session.character_id:
            try:
                self.server.db.save_character_experience(
                    session.character_id,
                    session.level,
                    session.experience,
                    0
                )
            except Exception as _e:
                log.error("_ghost_revive XP drain DB save failed: %s", _e)

        # ── Calculate actual penalized AS/DS for display ───────────────────
        try:
            from server.core.engine.combat.combat_engine import CombatEngine
            raw_as = CombatEngine._calc_player_as(self.server.combat, session)
            # Temporarily remove penalty to get base, then show both
            _saved = session.death_stat_mult
            session.death_stat_mult = 1.0
            full_as = CombatEngine._calc_player_as(self.server.combat, session)
            full_ds = self.server.combat._calc_player_ds(session)
            session.death_stat_mult = _saved
            pen_as  = int(full_as * DEATH_STAT_MULT)
            pen_ds  = int(full_ds * DEATH_STAT_MULT)
            stat_detail = (
                f"AS: {full_as} → {pen_as}  |  DS: {full_ds} → {pen_ds}  |  UAF reduced 90%"
            )
        except Exception:
            stat_detail = "AS, DS, and UAF reduced 90%"

        who = cleric_name or "Lorminstra's grace"

        await session.send_line("")
        await session.send_line(colorize(
            f"  {who} calls your spirit back into the mortal realm.",
            TextPresets.EXPERIENCE
        ))
        await session.send_line(colorize(
            "  You are alive, though barely.  Your body feels weak and sluggish.",
            TextPresets.WARNING
        ))
        await session.send_line(colorize(
            f"  HP: {session.health_current}/{session.health_max}",
            TextPresets.WARNING
        ))
        await session.send_line(colorize(
            f"  [Death penalty: 90% stat reduction -- recovers automatically over ~5 minutes]",
            TextPresets.WARNING
        ))
        await session.send_line(colorize(
            f"  [Affected: {stat_detail}]",
            TextPresets.WARNING
        ))
        if xp_lost > 0:
            await session.send_line(colorize(
                f"  [XP penalty: {xp_lost:,} unabsorbed experience lost]",
                TextPresets.WARNING
            ))
        await session.send_line("")

        # Show the room they woke up in
        from server.core.commands.player.movement import cmd_look
        await cmd_look(session, "look", "", self.server)

        self._save_session(session)

    # ══════════════════════════════════════════════════════════════════════════
    # Stat penalty recovery tick — called every 5s from game_loop
    # ══════════════════════════════════════════════════════════════════════════

    async def stat_penalty_tick(self, session):
        """Recover stat penalty by 1.5% per 5 seconds."""
        mult = getattr(session, 'death_stat_mult', 1.0)
        if mult >= 1.0:
            return

        new_mult = min(1.0, mult + STAT_RECOVERY_PER_5S)
        session.death_stat_mult = new_mult

        # Notify at certain milestones
        pct = int(new_mult * 100)
        prev_pct = int(mult * 100)
        milestones = {75, 50, 25, 10}
        if any(prev_pct < m <= pct for m in milestones):
            await session.send_line(colorize(
                f"  Your strength is returning.  Stats recovered to {pct}%.",
                TextPresets.EXPERIENCE
            ))
        elif new_mult >= 1.0:
            await session.send_line(colorize(
                "  You feel fully recovered.  Your strength has returned!",
                TextPresets.EXPERIENCE
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # Pathfinding helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _find_nearest_cleric_room(self, from_room_id: int):
        """BFS from death room, returns nearest cleric room_id or None."""
        world = self.server.world

        # Collect all cleric room IDs from registry
        all_cleric_rooms = set()
        for room_ids in CLERIC_ROOMS.values():
            all_cleric_rooms.update(room_ids)

        if not all_cleric_rooms:
            return None

        # If already in a cleric room
        if from_room_id in all_cleric_rooms:
            return from_room_id

        # BFS
        from collections import deque
        visited = {from_room_id}
        queue   = deque([from_room_id])

        while queue:
            current = queue.popleft()
            room    = world.get_room(current)
            if not room:
                continue
            for _, next_room_id in room.exits.items():
                if next_room_id in all_cleric_rooms:
                    return next_room_id
                if next_room_id not in visited:
                    visited.add(next_room_id)
                    queue.append(next_room_id)

        return None

    # ══════════════════════════════════════════════════════════════════════════
    # Deed helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _count_deeds(self, session) -> int:
        count = 0
        for item in getattr(session, 'inventory', []) or []:
            if isinstance(item, dict) and item.get('item_type') == 'deed':
                count += 1
        return count

    def _consume_deed(self, session):
        inventory = getattr(session, 'inventory', []) or []
        for i, item in enumerate(inventory):
            if isinstance(item, dict) and item.get('item_type') == 'deed':
                inventory.pop(i)
                if self.server.db and item.get('inv_id'):
                    self.server.db.remove_item_from_inventory(item['inv_id'])
                return

    # ══════════════════════════════════════════════════════════════════════════
    # Utility
    # ══════════════════════════════════════════════════════════════════════════

    def _save_session(self, session):
        if self.server.db and session.character_id:
            self.server.db.save_character_resources(
                session.character_id,
                session.health_current,
                getattr(session, 'mana_current', 0),
                getattr(session, 'spirit_current', 1),
                getattr(session, 'stamina_current', 0),
                getattr(session, 'silver', 0),
            )


# ── Direction helper ───────────────────────────────────────────────────────────

_OPPOSITES = {
    "north":     "south",
    "south":     "north",
    "east":      "west",
    "west":      "east",
    "northeast": "southwest",
    "southwest": "northeast",
    "northwest": "southeast",
    "southeast": "northwest",
    "up":        "down",
    "down":      "up",
    "out":       "in",
    "in":        "out",
}

def _opposite_direction(direction: str) -> str:
    return _OPPOSITES.get(direction.lower(), "somewhere")
