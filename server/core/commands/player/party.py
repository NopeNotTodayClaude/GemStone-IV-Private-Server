"""
party.py — Co-op Party system for GemStone IV private server.

Commands
--------
PARTY START          Create a new party; you become leader.
PARTY JOIN           Join the party of a player in the same room.
PARTY LEAVE          Leave the party (you stop following / being followed).
PARTY END            Disband the entire party (leader or any member).
PARTY LIST / PARTY   Show party roster and current room of each member.

Movement behavior
-----------------
When any party member moves, every OTHER living member in the SAME room is
moved silently along with them (no sneak / climb / roundtime checks — they
just follow).  Members who are dead, in a different room (de-synced), or in
combat do NOT follow.  Once de-synced members re-join the same room as the
rest of the party the follow behavior resumes automatically — no rejoining
required.

XP behavior
-----------
When any monster dies, every living party member (regardless of room — they
might be de-synced) receives full XP calculated against their own level.
This is handled by hooking into award_party_kill_xp(), which is called from
combat_engine.py instead of the solo award_kill_xp().

Data model
----------
Parties are stored in server.party_manager (a PartyManager instance attached
to the server at startup in game_server.py).

  PartyManager.parties : dict[int, Party]   party_id -> Party
  Party.members        : list[Session]       all members (including leader)
  Party.leader         : Session             the member who did PARTY START

There is no persistent storage — parties are in-memory only and dissolve on
server restart.  Members that disconnect are pruned lazily.
"""

import logging
from server.core.protocol.colors import colorize, TextPresets

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Party data structures
# ─────────────────────────────────────────────────────────────────────────────

class Party:
    _id_counter = 0

    def __init__(self, leader):
        Party._id_counter += 1
        self.id     = Party._id_counter
        self.leader = leader
        self.members: list = [leader]

    # ── Membership helpers ────────────────────────────────────────────────

    def add(self, session) -> bool:
        if session in self.members:
            return False
        self.members.append(session)
        return True

    def remove(self, session):
        if session in self.members:
            self.members.remove(session)
        if self.leader is session and self.members:
            self.leader = self.members[0]

    def is_alive_and_connected(self, session) -> bool:
        """True if the session is still connected and the character is alive."""
        if not getattr(session, 'character_name', None):
            return False
        if getattr(session, 'is_dead', False):
            return False
        return True

    def living_members(self) -> list:
        return [m for m in self.members if self.is_alive_and_connected(m)]

    def members_in_room(self, room_id: int) -> list:
        return [m for m in self.living_members()
                if m.current_room and m.current_room.id == room_id]

    def size(self) -> int:
        return len(self.members)


class PartyManager:
    """Singleton attached to server; manages all active parties."""

    def __init__(self):
        self._parties: dict[int, Party] = {}   # party_id -> Party
        self._member_map: dict = {}             # session -> Party

    # ── Lookup ────────────────────────────────────────────────────────────

    def get_party(self, session) -> Party | None:
        """Return the Party a session belongs to, or None."""
        return self._member_map.get(session)

    def find_party_in_room(self, room_id: int) -> Party | None:
        """Return the first party with a leader currently in room_id, or None."""
        for party in self._parties.values():
            if party.leader.current_room and party.leader.current_room.id == room_id:
                return party
            for m in party.members:
                if m.current_room and m.current_room.id == room_id:
                    return party
        return None

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def create_party(self, leader) -> Party:
        party = Party(leader)
        self._parties[party.id] = party
        self._member_map[leader] = party
        return party

    def join_party(self, party: Party, session) -> bool:
        if not party.add(session):
            return False
        self._member_map[session] = party
        return True

    def leave_party(self, session):
        """Remove session from their party; disband if empty."""
        party = self._member_map.pop(session, None)
        if not party:
            return None
        party.remove(session)
        if len(party.members) == 0:
            self._parties.pop(party.id, None)
            return None
        return party

    def disband(self, party: Party):
        """Remove all members from party and delete it."""
        for m in list(party.members):
            self._member_map.pop(m, None)
        party.members.clear()
        self._parties.pop(party.id, None)

    def prune_disconnected(self, party: Party):
        """Drop members that have disconnected (no character_name)."""
        stale = [m for m in party.members if not getattr(m, 'character_name', None)]
        for m in stale:
            party.remove(m)
            self._member_map.pop(m, None)

    # ── XP helper ─────────────────────────────────────────────────────────

    def get_party_members_for_xp(self, session) -> list:
        """All living party members to receive XP when session's kill lands."""
        party = self.get_party(session)
        if not party:
            return [session]
        return party.living_members() or [session]


# ─────────────────────────────────────────────────────────────────────────────
# Movement helper — called from movement.py after _move_player succeeds
# ─────────────────────────────────────────────────────────────────────────────

async def party_follow_move(mover_session, from_room, to_room, direction, server):
    """
    Pull every living party member that is currently in from_room along with
    mover_session into to_room.  Dead members and de-synced members are skipped
    silently.  This uses the internal _move_player directly to avoid sneak /
    climb / RT checks.
    """
    mgr = getattr(server, 'party_manager', None)
    if not mgr:
        return

    party = mgr.get_party(mover_session)
    if not party:
        return

    mgr.prune_disconnected(party)

    followers = [
        m for m in party.members_in_room(from_room.id)
        if m is not mover_session
    ]
    if not followers:
        return

    from server.core.commands.player.movement import _move_player
    status_mgr = getattr(server, "status", None)
    creature_mgr = getattr(server, "creatures", None)

    def _clear_old_room_combat_state(follower):
        if status_mgr and status_mgr.has(follower, "in_combat"):
            status_mgr.exit_combat(follower)
        else:
            follower.in_combat = False
            follower.target = None
        if not creature_mgr or not from_room:
            return
        for creature in (creature_mgr.get_creatures_in_room(from_room.id) or []):
            if getattr(creature, "target", None) is follower:
                creature.in_combat = False
                creature.target = None

    moved_sessions = [mover_session]
    for follower in followers:
        try:
            _clear_old_room_combat_state(follower)
            # Notify the follower what's happening
            await follower.send_line(
                colorize(
                    f"  You follow {mover_session.character_name} {direction.replace('_', ' ')}.",
                    TextPresets.SYSTEM
                )
            )
            await _move_player(follower, from_room, to_room, direction, server,
                               sneaking=False)
            moved_sessions.append(follower)
        except Exception as e:
            log.error("party_follow_move: error moving %s: %s",
                      getattr(follower, 'character_name', '?'), e)

    # Party-dragged members do not generate a fresh sync snapshot until the
    # next 1-second sync tick. Push immediately so companion visibility stays
    # in lockstep for the mover and every dragged member.
    broadcaster = getattr(server, "sync_broadcaster", None)
    if broadcaster and moved_sessions:
        try:
            await broadcaster.broadcast_sessions(moved_sessions)
        except Exception as e:
            log.error("party_follow_move: sync refresh failed: %s", e)


# ─────────────────────────────────────────────────────────────────────────────
# XP helper — called from combat_engine.py on creature death
# ─────────────────────────────────────────────────────────────────────────────

async def award_party_kill_xp(session, creature, server):
    """
    Award kill XP to every living party member.  Each member gets XP
    calculated against their own level so high-level members still get
    appropriate reward.  If session is not in a party, falls back to solo XP.
    """
    mgr = getattr(server, 'party_manager', None)
    if not mgr:
        await server.experience.award_kill_xp(session, creature)
        return

    recipients = mgr.get_party_members_for_xp(session)

    for member in recipients:
        try:
            try:
                guild_engine = getattr(server, 'guild', None)
                if guild_engine:
                    await guild_engine.record_bounty_kill(member, creature)
            except Exception:
                log.exception("award_party_kill_xp: failed to record bounty kill for %s", getattr(member, 'character_name', '?'))
            xp = server.experience.calculate_kill_xp(member, creature)
            if xp <= 0:
                continue
            await server.experience.award_xp_to_pool(member, xp, source="kill")
            if member is not session:
                # Notify party members who aren't the killer
                await member.send_line(
                    colorize(
                        f"  [Party] {session.character_name} kills {creature.full_name}."
                        f"  You gain {xp} experience.",
                        TextPresets.EXPERIENCE
                    )
                )
        except Exception as e:
            log.error("award_party_kill_xp: error awarding XP to %s: %s",
                      getattr(member, 'character_name', '?'), e)


# ─────────────────────────────────────────────────────────────────────────────
# Death hook — called when a player dies, to de-sync them from follow
# ─────────────────────────────────────────────────────────────────────────────

async def on_party_member_death(session, server):
    """
    Notify party when a member dies.  They are automatically de-synced from
    movement because party_follow_move checks is_alive_and_connected().
    No explicit removal needed — they re-sync when they're alive and in the
    same room again.
    """
    mgr = getattr(server, 'party_manager', None)
    if not mgr:
        return
    party = mgr.get_party(session)
    if not party:
        return

    name = session.character_name or 'Someone'
    for m in party.members:
        if m is session:
            continue
        if not getattr(m, 'character_name', None):
            continue
        try:
            await m.send_line(
                colorize(
                    f"  [Party] {name} has fallen!  They will rejoin movement when they recover.",
                    TextPresets.WARNING
                )
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Command handlers
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_party(session, cmd, args, server):
    """
    PARTY               Show party status.
    PARTY START         Create a new party.
    PARTY JOIN          Join a party in your room.
    PARTY LEAVE         Leave your current party.
    PARTY END           Disband the entire party.
    PARTY LIST          Show party roster.
    """
    mgr = getattr(server, 'party_manager', None)
    if not mgr:
        await session.send_line(colorize("  Party system is not available.", TextPresets.WARNING))
        return

    sub = (args or "").strip().lower()

    # ── PARTY / PARTY LIST ────────────────────────────────────────────────
    if sub in ("", "list", "status"):
        await _cmd_party_list(session, mgr)
        return

    if sub == "start":
        await _cmd_party_start(session, mgr, server)
        return

    if sub == "join":
        await _cmd_party_join(session, mgr, server)
        return

    if sub in ("leave",):
        await _cmd_party_leave(session, mgr, server)
        return

    if sub == "end":
        await _cmd_party_end(session, mgr, server)
        return

    await session.send_line("Usage: PARTY START | JOIN | LEAVE | END | LIST")


async def _cmd_party_list(session, mgr):
    party = mgr.get_party(session)
    if not party:
        await session.send_line(colorize("  You are not in a party.", TextPresets.SYSTEM))
        await session.send_line("  Use PARTY START to form one, or PARTY JOIN if there is one in your room.")
        return

    mgr.prune_disconnected(party)
    await session.send_line(colorize(f"  ── Party Roster ──────────────────────────", TextPresets.SYSTEM))
    for m in party.members:
        name     = m.character_name or "Unknown"
        room_str = m.current_room.title if m.current_room else "Unknown"
        dead_str = colorize(" [DEAD]", TextPresets.HEALTH_CRIT) if getattr(m, 'is_dead', False) else ""
        leader_str = colorize(" [Leader]", TextPresets.EXPERIENCE) if m is party.leader else ""
        you_str    = colorize(" [You]",    TextPresets.SYSTEM)     if m is session    else ""
        await session.send_line(
            f"  {colorize(name, TextPresets.ITEM_NAME)}{leader_str}{you_str}{dead_str}"
            f"  —  {room_str}"
        )
    await session.send_line(colorize(f"  ─────────────────────────────────────────", TextPresets.SYSTEM))


async def _cmd_party_start(session, mgr, server):
    existing = mgr.get_party(session)
    if existing:
        await session.send_line(colorize("  You are already in a party.", TextPresets.WARNING))
        await session.send_line("  Use PARTY END to disband it first, or PARTY LEAVE to leave.")
        return

    party = mgr.create_party(session)
    await session.send_line(
        colorize("  You form a party.  Others in your room can type PARTY JOIN to join you.", TextPresets.SYSTEM)
    )

    # Announce to room
    room = session.current_room
    if room:
        await server.world.broadcast_to_room(
            room.id,
            colorize(
                f"  {session.character_name} has formed a party.  "
                f"Type PARTY JOIN to join them.",
                TextPresets.SYSTEM
            ),
            exclude=session
        )


async def _cmd_party_join(session, mgr, server):
    existing = mgr.get_party(session)
    if existing:
        await session.send_line(colorize("  You are already in a party.", TextPresets.WARNING))
        return

    room = session.current_room
    if not room:
        await session.send_line("  You can't do that right now.")
        return

    # Find a party with at least one member in this room
    party = None
    for p in mgr._parties.values():
        if any(m.current_room and m.current_room.id == room.id and m is not session
               for m in p.members):
            party = p
            break

    if not party:
        await session.send_line(colorize("  There is no party to join in this room.", TextPresets.WARNING))
        return

    mgr.join_party(party, session)

    await session.send_line(
        colorize(
            f"  You join {party.leader.character_name}'s party.  "
            f"There are now {party.size()} members.",
            TextPresets.SYSTEM
        )
    )

    # Notify existing members
    for m in party.members:
        if m is session:
            continue
        if not getattr(m, 'character_name', None):
            continue
        await m.send_line(
            colorize(
                f"  [Party] {session.character_name} has joined the party!",
                TextPresets.SYSTEM
            )
        )


async def _cmd_party_leave(session, mgr, server):
    party = mgr.get_party(session)
    if not party:
        await session.send_line(colorize("  You are not in a party.", TextPresets.WARNING))
        return

    name = session.character_name

    remaining_party = mgr.leave_party(session)

    await session.send_line(colorize("  You leave the party.", TextPresets.SYSTEM))

    if remaining_party:
        for m in remaining_party.members:
            if not getattr(m, 'character_name', None):
                continue
            await m.send_line(
                colorize(f"  [Party] {name} has left the party.", TextPresets.WARNING)
            )
        if len(remaining_party.members) == 1:
            sole = remaining_party.members[0]
            mgr.disband(remaining_party)
            await sole.send_line(
                colorize("  [Party] You are now alone.  The party has been disbanded.", TextPresets.WARNING)
            )


async def _cmd_party_end(session, mgr, server):
    party = mgr.get_party(session)
    if not party:
        await session.send_line(colorize("  You are not in a party.", TextPresets.WARNING))
        return

    members_snapshot = list(party.members)
    mgr.disband(party)

    name = session.character_name
    for m in members_snapshot:
        if not getattr(m, 'character_name', None):
            continue
        if m is session:
            await m.send_line(colorize("  You disband the party.", TextPresets.WARNING))
        else:
            await m.send_line(
                colorize(f"  [Party] {name} has disbanded the party.", TextPresets.WARNING)
            )
