"""
travel_office_manager.py
------------------------
Lua-driven office travel runtime for travel guides, chronomages, airship
clerks, and portmasters.  Room identity stays anchored to local LICH wayto
room IDs; this manager only executes office interactions and item-based travel.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from server.core.character_unlocks import grant_unlock, has_unlock
from server.core.protocol.colors import colorize, TextPresets, npc_speech
from server.core.world.lich_wayto import get_lich_room_entry

log = logging.getLogger(__name__)


def _norm(text: str | None) -> str:
    return "_".join(str(text or "").strip().lower().replace("-", " ").replace("'", "").split())


def _pretty_topic(text: str | None) -> str:
    return str(text or "").strip().replace("_", " ")


def _room_title_from_lich(room_id: int) -> str:
    entry = get_lich_room_entry(int(room_id or 0)) or {}
    raw = entry.get("title")
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    text = str(raw or "").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    return text


class TravelOfficeManager:
    def __init__(self, server):
        self.server = server
        self._networks: dict[str, dict] = {}
        self._offices: dict[str, dict] = {}
        self._by_template: dict[str, dict] = {}
        self._by_room: dict[int, dict] = {}
        self._last_departure_slot: dict[str, int] = {}

    async def initialize(self):
        data = getattr(self.server.lua, "get_travel_offices", lambda: {})() or {}
        self._networks = dict((data.get("networks") or {}))
        self._offices = dict((data.get("offices") or {}))
        self._by_template = {}
        self._by_room = {}
        for office in self._offices.values():
            template_id = str(office.get("clerk_template_id") or "").strip()
            room_id = int(office.get("room_id") or 0)
            if template_id:
                self._by_template[template_id] = office
            if room_id > 0:
                self._by_room[room_id] = office
        log.info("TravelOfficeManager ready (%d offices across %d networks)", len(self._offices), len(self._networks))

    async def tick(self, tick_count: int):
        now = time.time()
        if tick_count % 50 == 0:
            for session in self.server.sessions.playing():
                self._prune_expired_passes(session, now=now)
        await self._process_chronomage_departures(now)

    def get_office_for_npc(self, npc) -> Optional[dict]:
        template_id = str(getattr(npc, "template_id", "") or "").strip()
        if template_id and template_id in self._by_template:
            return self._by_template[template_id]
        room_id = int(getattr(npc, "home_room_id", 0) or getattr(npc, "room_id", 0) or 0)
        return self._by_room.get(room_id)

    def get_actions_for_npc(self, session, npc) -> list[dict]:
        office = self.get_office_for_npc(npc)
        if not office:
            return []
        target = str(getattr(npc, "name", "") or getattr(npc, "display_name", "") or "").strip()
        if not target:
            return []

        actions = [
            {"label": "Destinations", "command": f"ask {target} about destinations", "prefill": False},
        ]
        service = self._network_service(office)
        for route in self._routes_for_office(office):
            town = route["town_name"]
            if service == "chronomage":
                actions.append({"label": f"Ticket to {town}", "command": f"ask {target} about ticket {town}", "prefill": False})
                actions.append({"label": f"Day pass: {town}", "command": f"ask {target} about pass {town}", "prefill": False})
            else:
                route_num = route.get("travel_index")
                label = f"Travel to {town}"
                if route_num:
                    label = f"Travel {route_num}: {town}"
                actions.append({"label": label, "command": f"ask {target} about {town}", "prefill": False})
        return actions

    async def maybe_handle_npc_response(self, session, npc, topic: str, response: dict) -> bool:
        if not isinstance(response, dict):
            return False
        action = str(response.get("travel_action") or "").strip().lower()
        if not action:
            return False

        office = None
        office_id = str(response.get("office_id") or "").strip().lower()
        if office_id:
            office = self._offices.get(office_id)
        if not office:
            office = self.get_office_for_npc(npc)
        if not office:
            return False

        if action == "list_destinations":
            await self._send_destination_list(session, npc, office, request_kind=str(response.get("request_kind") or "").strip().lower())
            return True

        if action == "route_request":
            request_kind = str(response.get("request_kind") or "travel").strip().lower()
            route_key = str(response.get("route_key") or topic or "").strip()
            route = self._resolve_route(office, route_key)
            if not route:
                await session.send_line(npc_speech(npc.display_name, f'says, "I do not have a route listed for {_pretty_topic(route_key)}."'))
                return True
            service = self._network_service(office)
            if service == "travel_guide":
                await self._handle_travel_guide(session, npc, office, route)
                return True
            if service == "chronomage":
                await self._handle_chronomage(session, npc, office, route, request_kind=request_kind)
                return True
            if service == "airship":
                await self._handle_airship(session, npc, office, route)
                return True
            if service == "portmaster":
                await self._handle_portmaster(session, npc, office, route)
                return True
        return False

    def describe_travel_item(self, item: dict) -> list[str] | None:
        return self.look_travel_item(item)

    def look_travel_item(self, item: dict, session=None) -> list[str] | None:
        extra = self._travel_item_data(item)
        if not extra:
            return None
        lines = []
        item_name = str(item.get("short_name") or item.get("name") or item.get("noun") or "item").strip()
        service = str(extra.get("service") or "").replace("_", " ")
        kind = str(extra.get("item_kind") or "paper").replace("_", " ")
        lines.append(f"You study {item_name}.")
        lines.append(f"It bears travel markings for the {service} system.")
        lines.append(f"Type: {kind.title()}")
        route_name = str(extra.get("route_name") or "").strip()
        if route_name:
            lines.append(f"Destination: {route_name}")
        owner_name = str(extra.get("owner_name") or "").strip()
        if owner_name:
            lines.append(f"Attuned traveler: {owner_name}")
        if extra.get("allowed_towns"):
            lines.append("Valid between: " + ", ".join(extra.get("allowed_towns") or []))
        expires_at = float(extra.get("expires_at") or 0.0)
        if expires_at > 0:
            remaining = max(0, int(expires_at - time.time()))
            if remaining > 0:
                minutes = max(1, remaining // 60)
                lines.append(f"Remaining duration: about {minutes} minute{'s' if minutes != 1 else ''}.")
            else:
                lines.append("It appears to be expired.")
        if extra.get("uses_remaining") is not None:
            uses = int(extra.get("uses_remaining") or 0)
            lines.append(f"Uses remaining: {uses}")
        if str(extra.get("service") or "").strip().lower() == "chronomage":
            origin = self._offices.get(str(extra.get("origin_office_id") or "").strip().lower()) or {}
            network = self._network_for_office(origin) if origin else {}
            if str(extra.get("item_kind") or "").strip().lower() == "ticket":
                depart_at = self._chronomage_next_departure_ts(network)
                depart_text = self._chronomage_departure_label(network, now=time.time(), next_departure=depart_at)
                lines.append(f"Next scheduled departure: {depart_text}")
                lines.append("Hold it in your right hand in the departure room and wait for the next jump.")
            else:
                lines.append("RAISE it in the correct departure room to travel immediately.")
        else:
            lines.append("RAISE it in the correct departure room to travel.")
        return lines

    def read_travel_item(self, session, item: dict) -> list[str] | None:
        extra = self._travel_item_data(item)
        if not extra:
            return None
        if str(extra.get("service") or "").strip().lower() != "chronomage":
            return self.look_travel_item(item, session)
        origin = self._offices.get(str(extra.get("origin_office_id") or "").strip().lower()) or {}
        network = self._network_for_office(origin) if origin else {}
        lines = []
        if str(extra.get("item_kind") or "").strip().lower() == "ticket":
            lines.append("The orb's etched sigils pulse with the chronomage departure schedule.")
            lines.append(f"Next departure: {self._chronomage_departure_label(network)}")
            if origin:
                lines.append(f"Board from: {origin.get('town_name')} departure room")
        else:
            lines.append("The pass details the paired offices and the short-lived transit imprint bound to it.")
            expires_at = float(extra.get("expires_at") or 0.0)
            if expires_at > 0:
                remaining = max(0, int(expires_at - time.time()))
                minutes = max(1, remaining // 60) if remaining else 0
                lines.append(f"Remaining validity: about {minutes} minute{'s' if minutes != 1 else ''}.")
        return lines

    def gaze_travel_item(self, session, item: dict) -> list[str] | None:
        extra = self._travel_item_data(item)
        if not extra:
            return None
        route_name = str(extra.get("route_name") or "").strip()
        if not route_name:
            return None
        service = str(extra.get("service") or "").strip().lower()
        if service == "chronomage":
            return [f"The travel markings settle into the image of {route_name}."]
        return [f"The item is marked for travel to {route_name}."]

    async def raise_travel_item(self, session, item: dict) -> bool:
        extra = self._travel_item_data(item)
        if not extra:
            return False
        service = str(extra.get("service") or "").strip().lower()
        if service != "chronomage":
            await session.send_line("Nothing happens.")
            return True

        office_id = str(extra.get("origin_office_id") or "").strip().lower()
        route_office_id = str(extra.get("dest_office_id") or "").strip().lower()
        office = self._offices.get(office_id)
        dest = self._offices.get(route_office_id)
        if not office or not dest:
            await session.send_line("The transit paper no longer seems valid.")
            return True
        owner_id = int(extra.get("owner_character_id") or 0)
        if owner_id and owner_id != int(getattr(session, "character_id", 0) or 0):
            await session.send_line("The transit markings reject you.  This item is attuned to someone else.")
            return True
        if int(getattr(getattr(session, "current_room", None), "id", 0) or 0) != int(office.get("departure_room_id") or 0):
            await session.send_line("The pass is not valid for departures from here.")
            return True
        expires_at = float(extra.get("expires_at") or 0.0)
        if expires_at and expires_at <= time.time():
            await session.send_line("The pass is expired.")
            return True
        uses_remaining = int(extra.get("uses_remaining") or 0)
        if uses_remaining <= 0:
            await session.send_line("The ticket has already been spent.")
            return True

        network = self._network_for_office(office)
        item_kind = str(extra.get("item_kind") or "").strip().lower()
        if item_kind == "ticket":
            if getattr(session, "right_hand", None) is not item:
                await session.send_line("You must hold the orb in your right hand while waiting for the jump.")
                return True
            await session.send_line(colorize(
                "The orb warms in your hand and attunes itself to the next scheduled chronomage departure.",
                TextPresets.SYSTEM,
            ))
            await session.send_line(colorize(
                f"Next departure: {self._chronomage_departure_label(network)}.",
                TextPresets.SYSTEM,
            ))
            return True

        depart_msg = str(network.get("depart_msg") or "You raise the paper and the world slips sideways.")
        arrive_msg = str(network.get("arrive_msg") or "The transit effect releases you in a distant office.")
        await session.send_line(colorize(depart_msg, TextPresets.SYSTEM))

        uses_remaining -= 1
        extra["uses_remaining"] = uses_remaining
        if item.get("inv_id") and getattr(self.server, "db", None):
            self.server.db.save_item_extra_data(item["inv_id"], extra)
        item.update(extra)

        if uses_remaining <= 0:
            await self._remove_item(session, item)

        await self._teleport_player(
            session,
            int(dest.get("arrival_room_id") or dest.get("room_id") or 0),
            arrive_msg=arrive_msg,
            roundtime_sec=int(network.get("roundtime_sec") or 0),
            transport_label="a swirl of chronomage light",
        )
        return True

    def _network_for_office(self, office: dict) -> dict:
        network_id = str(office.get("network") or "").strip().lower()
        return self._networks.get(network_id) or {"id": network_id, "service": network_id}

    def _network_service(self, office: dict) -> str:
        return str(self._network_for_office(office).get("service") or office.get("network") or "").strip().lower()

    def _routes_for_office(self, office: dict) -> list[dict]:
        service = self._network_service(office)
        if service == "portmaster":
            return self._portmaster_routes(office)

        network = self._network_for_office(office)
        routes = []
        for candidate in self._offices.values():
            if candidate["id"] == office["id"]:
                continue
            if str(candidate.get("network") or "") != str(office.get("network") or ""):
                continue
            group = str(network.get("route_group") or office.get("route_group") or "").strip().lower()
            if group:
                if str(candidate.get("route_group") or "").strip().lower() != group:
                    continue
            routes.append({
                "office_id": candidate["id"],
                "town_name": str(candidate.get("town_name") or candidate["id"]),
                "aliases": list(candidate.get("aliases") or []),
                "arrival_room_id": int(candidate.get("arrival_room_id") or candidate.get("room_id") or 0),
            })
        routes.sort(key=lambda row: row["town_name"])
        return routes

    def _resolve_route(self, office: dict, route_key: str) -> Optional[dict]:
        token = _norm(route_key)
        if not token:
            return None
        for route in self._routes_for_office(office):
            names = {_norm(route.get("office_id")), _norm(route.get("town_name"))}
            for alias in route.get("aliases") or []:
                names.add(_norm(alias))
            if token in names:
                return route
        for route in self._routes_for_office(office):
            candidates = [_norm(route.get("town_name"))]
            candidates.extend(_norm(alias) for alias in (route.get("aliases") or []))
            if any(token in candidate for candidate in candidates if candidate):
                return route
        return None

    def _portmaster_routes(self, office: dict) -> list[dict]:
        room_id = int(office.get("room_id") or 0)
        entry = get_lich_room_entry(room_id) or {}
        tags = [str(tag or "") for tag in (entry.get("tags") or [])]
        wayto = entry.get("wayto") if isinstance(entry.get("wayto"), dict) else {}
        fare_by_dest: dict[int, int] = {}
        route_index_by_dest: dict[int, str] = {}
        route_dest_ids: set[int] = set()

        for dest_key, command in wayto.items():
            try:
                dest_room_id = int(dest_key)
            except (TypeError, ValueError):
                continue
            match = re.search(r"travel\s+(\d+)", str(command or ""), re.IGNORECASE)
            if not match:
                continue
            route_dest_ids.add(dest_room_id)
            route_index_by_dest[dest_room_id] = match.group(1)

        routes = []
        for tag in tags:
            lower = tag.lower().strip()
            if not lower.startswith("silver-cost:"):
                continue
            parts = lower.split(":")
            if len(parts) != 3:
                continue
            try:
                dest_room_id = int(parts[1])
                fare = int(parts[2])
            except ValueError:
                continue
            route_dest_ids.add(dest_room_id)
            fare_by_dest[dest_room_id] = max(0, fare)

        for dest_room_id in list(route_dest_ids):
            dest_room = self.server.world.get_room(dest_room_id)
            if not dest_room:
                continue
            fare = fare_by_dest.get(dest_room_id)
            if fare is None:
                dest_entry = get_lich_room_entry(dest_room_id) or {}
                for raw_tag in (dest_entry.get("tags") or []):
                    lower = str(raw_tag or "").lower().strip()
                    if not lower.startswith("silver-cost:"):
                        continue
                    parts = lower.split(":")
                    if len(parts) != 3:
                        continue
                    try:
                        src_room_id = int(parts[1])
                        reverse_fare = int(parts[2])
                    except ValueError:
                        continue
                    if src_room_id == room_id:
                        fare = max(0, reverse_fare)
                        break
            if fare is None:
                fare = 0
            town_name = str(getattr(dest_room, "zone_name", "") or "").strip()
            title = _room_title_from_lich(dest_room_id)
            route = {
                "office_id": f"port_{dest_room_id}",
                "town_name": town_name or title or f"Room {dest_room_id}",
                "aliases": [],
                "arrival_room_id": dest_room_id,
                "fare": max(0, fare),
            }
            travel_index = route_index_by_dest.get(dest_room_id)
            if travel_index:
                route["travel_index"] = travel_index
                route["aliases"] = [travel_index, f"travel {travel_index}"]
            routes.append(route)
        routes.sort(key=lambda row: (int(row.get("travel_index") or 999), row["town_name"]))
        return routes

    async def _send_destination_list(self, session, npc, office: dict, request_kind: str = ""):
        service = self._network_service(office)
        network = self._network_for_office(office)
        routes = self._routes_for_office(office)
        if not routes:
            await session.send_line(npc_speech(npc.display_name, 'says, "There are no departures posted here right now."'))
            return

        lines = []
        if service == "chronomage":
            if request_kind in {"time", "times", "departure", "departures", "schedule"}:
                lines.append(
                    f"The next chronomage departure is {self._chronomage_departure_label(network)}."
                )
                lines.append("Tickets are for the next scheduled jump.  Day passes can be raised on demand from the paired departure room.")
            else:
                lines.append(
                    f"Chronomage routes from {office.get('town_name')}: tickets {int(network.get('ticket_fare') or 0)} silvers, day passes {int(network.get('day_pass_fare') or 0)} silvers."
                )
                lines.append("Ask for a route directly, ASK ... ABOUT TICKET <town>, or ASK ... ABOUT PASS <town>.")
            lines.append(
                f"Scheduled departures leave every {max(1, int(network.get('departure_interval_sec') or 1200) // 60)} minutes."
            )
        elif service == "travel_guide":
            fare = int(network.get("standard_fare") or 0)
            max_level = int(network.get("max_level") or 0)
            lines.append(
                f"Travel guide routes from {office.get('town_name')} are for characters up to level {max_level}. Standard fare is {fare} silvers, with one free starter trip if unused."
            )
        elif service == "airship":
            lines.append(
                f"The airship office currently books {office.get('town_name')} routes for {int(network.get('standard_fare') or 0)} silvers."
            )
        elif service == "portmaster":
            lines.append(f"Ships currently sailing from {office.get('town_name')}:")

        for route in routes:
            fare = route.get("fare")
            if fare is None:
                if service == "chronomage":
                    fare = int(network.get("ticket_fare") or 0)
                else:
                    fare = int(network.get("standard_fare") or 0)
            line = f"{route['town_name']} ({int(fare)} silvers)"
            if route.get("travel_index"):
                line = f"{route['travel_index']}. {line}"
            lines.append(line)

        await session.send_line(npc_speech(npc.display_name, f'says, "{lines[0]}"'))
        for line in lines[1:]:
            await session.send_line("  " + line)

    async def _handle_travel_guide(self, session, npc, office: dict, route: dict):
        network = self._network_for_office(office)
        max_level = int(network.get("max_level") or 0)
        if max_level and int(getattr(session, "level", 1) or 1) > max_level:
            await session.send_line(npc_speech(npc.display_name, f'says, "My guides only handle low-level transfers. You are past the level {max_level} limit for this office."'))
            return

        fare = int(network.get("standard_fare") or 0)
        unlock_key = str(network.get("free_use_unlock") or "").strip().lower()
        used_free = True if not unlock_key else has_unlock(session, unlock_key)
        used_free_text = ""
        if unlock_key and not used_free:
            fare = 0
            used_free_text = " Your starter travel token covers this one."

        if not await self._charge_silver(session, fare):
            await session.send_line(npc_speech(npc.display_name, f'says, "The fare to {route["town_name"]} is {fare} silvers.{used_free_text}"'))
            return

        if unlock_key and not used_free:
            grant_unlock(session, self.server, unlock_key, unlock_type="travel", notes="Used the free travel-guide trip.")

        await session.send_line(npc_speech(npc.display_name, f'says, "Right then. {route["town_name"]} it is.{used_free_text}"'))
        await self._teleport_player(
            session,
            int(route["arrival_room_id"]),
            arrive_msg=str(network.get("arrive_msg") or ""),
            roundtime_sec=int(network.get("roundtime_sec") or 0),
            transport_label="a guided transfer",
        )

    async def _handle_airship(self, session, npc, office: dict, route: dict):
        network = self._network_for_office(office)
        fare = int(network.get("standard_fare") or 0)
        if not await self._charge_silver(session, fare):
            await session.send_line(npc_speech(npc.display_name, f'says, "Passage to {route["town_name"]} costs {fare} silvers."'))
            return

        await session.send_line(npc_speech(npc.display_name, f'says, "Boarding for {route["town_name"]}. Keep your papers visible."'))
        await self._teleport_player(
            session,
            int(route["arrival_room_id"]),
            arrive_msg=str(network.get("arrive_msg") or ""),
            roundtime_sec=int(network.get("roundtime_sec") or 0),
            transport_label="an airship passage",
        )

    async def _handle_portmaster(self, session, npc, office: dict, route: dict):
        fare = int(route.get("fare") or 0)
        if not await self._charge_silver(session, fare):
            await session.send_line(npc_speech(npc.display_name, f'says, "The passage to {route["town_name"]} costs {fare} silvers."'))
            return

        await session.send_line(npc_speech(npc.display_name, f'says, "Casting off for {route["town_name"]}."'))
        network = self._network_for_office(office)
        await self._teleport_player(
            session,
            int(route["arrival_room_id"]),
            arrive_msg=str(network.get("arrive_msg") or ""),
            roundtime_sec=int(network.get("roundtime_sec") or 0),
            transport_label="a coastal voyage",
        )

    async def _handle_chronomage(self, session, npc, office: dict, route: dict, *, request_kind: str):
        network = self._network_for_office(office)
        request_kind = str(request_kind or "ticket").strip().lower()
        if request_kind not in {"ticket", "pass"}:
            request_kind = "ticket"
        item_kind = "day_pass" if request_kind == "pass" else "ticket"
        fare = int(network.get("day_pass_fare") if item_kind == "day_pass" else network.get("ticket_fare") or 0)
        if not await self._charge_silver(session, fare):
            await session.send_line(npc_speech(npc.display_name, f'says, "That {item_kind.replace("_", " ")} for {route["town_name"]} costs {fare} silvers."'))
            return

        expires_at = 0.0
        uses_remaining = 1
        allowed_towns = [str(office.get("town_name") or ""), str(route.get("town_name") or "")]
        if item_kind == "day_pass":
            expires_at = time.time() + float(network.get("pass_duration_sec") or 0)
            uses_remaining = 9999

        noun = "pass" if item_kind == "day_pass" else "orb"
        if item_kind == "day_pass":
            short_name = f"a {route['town_name'].lower()} day pass"
        else:
            short_name = "a brass and gold orb"
        item_extra = {
            "travel_office_item": True,
            "service": "chronomage",
            "item_kind": item_kind,
            "origin_office_id": office["id"],
            "dest_office_id": route["office_id"],
            "route_name": route["town_name"],
            "allowed_towns": allowed_towns,
            "expires_at": expires_at,
            "uses_remaining": uses_remaining,
            "owner_character_id": int(getattr(session, "character_id", 0) or 0),
            "owner_name": str(getattr(session, "character_name", "") or ""),
            "name": short_name,
            "short_name": short_name,
            "noun": noun,
        }
        item = await self._give_travel_item(
            session,
            name=short_name,
            short_name=short_name,
            noun=noun,
            item_type="misc",
            article="a",
            description=(
                f"A chronomage {'pass' if item_kind == 'day_pass' else 'orb'} marked for {route['town_name']}."
            ),
            extra=item_extra,
        )
        if not item:
            await session.send_line("The clerk fumbles with the paperwork and nothing is issued.")
            return

        if item_kind == "day_pass":
            await session.send_line(npc_speech(npc.display_name, f'says, "This pass will hold between {allowed_towns[0]} and {allowed_towns[1]} for roughly a day. Raise it in the departure room when you are ready."'))
        else:
            await session.send_line(npc_speech(
                npc.display_name,
                f'says, "Hold that orb in your right hand in the departure room.  The next jump for {route["town_name"]} is {self._chronomage_departure_label(network)}."',
            ))

    def _travel_item_data(self, item: dict) -> Optional[dict]:
        if not isinstance(item, dict):
            return None
        if not item.get("travel_office_item"):
            return None
        return {
            "travel_office_item": True,
            "service": item.get("service"),
            "item_kind": item.get("item_kind"),
            "origin_office_id": item.get("origin_office_id"),
            "dest_office_id": item.get("dest_office_id"),
            "route_name": item.get("route_name"),
            "allowed_towns": list(item.get("allowed_towns") or []),
            "expires_at": float(item.get("expires_at") or 0.0),
            "uses_remaining": int(item.get("uses_remaining") or 0),
            "owner_character_id": int(item.get("owner_character_id") or 0),
            "owner_name": item.get("owner_name"),
            "name": item.get("name"),
            "short_name": item.get("short_name"),
            "noun": item.get("noun"),
        }

    def _chronomage_next_departure_ts(self, network: dict, now: float | None = None) -> float:
        now = time.time() if now is None else float(now)
        interval = max(60, int(network.get("departure_interval_sec") or 1200))
        remainder = int(now) % interval
        if remainder == 0:
            return float(int(now))
        return float(int(now) + (interval - remainder))

    def _chronomage_departure_label(self, network: dict, now: float | None = None, next_departure: float | None = None) -> str:
        now = time.time() if now is None else float(now)
        next_departure = self._chronomage_next_departure_ts(network, now=now) if next_departure is None else float(next_departure)
        remaining = max(0, int(next_departure - now))
        if remaining <= 0:
            return "right now"
        minutes = remaining // 60
        seconds = remaining % 60
        if minutes <= 0:
            return f"in {seconds} second{'s' if seconds != 1 else ''}"
        if seconds == 0:
            return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        return f"in {minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"

    async def _process_chronomage_departures(self, now: float):
        for network_id, network in self._networks.items():
            if str(network.get("service") or "").strip().lower() != "chronomage":
                continue
            interval = max(60, int(network.get("departure_interval_sec") or 1200))
            slot = int(now // interval)
            if self._last_departure_slot.get(network_id) == slot:
                continue
            self._last_departure_slot[network_id] = slot
            for session in self.server.sessions.playing():
                item = getattr(session, "right_hand", None)
                extra = self._travel_item_data(item)
                if not extra:
                    continue
                if str(extra.get("service") or "").strip().lower() != "chronomage":
                    continue
                if str(extra.get("item_kind") or "").strip().lower() != "ticket":
                    continue
                office = self._offices.get(str(extra.get("origin_office_id") or "").strip().lower())
                dest = self._offices.get(str(extra.get("dest_office_id") or "").strip().lower())
                if not office or not dest:
                    continue
                if str(office.get("network") or "").strip().lower() != network_id:
                    continue
                if int(getattr(getattr(session, "current_room", None), "id", 0) or 0) != int(office.get("departure_room_id") or 0):
                    continue
                owner_id = int(extra.get("owner_character_id") or 0)
                if owner_id and owner_id != int(getattr(session, "character_id", 0) or 0):
                    continue
                expires_at = float(extra.get("expires_at") or 0.0)
                if expires_at and expires_at <= now:
                    continue
                uses_remaining = int(extra.get("uses_remaining") or 0)
                if uses_remaining <= 0:
                    continue
                await session.send_line(colorize(
                    "The orb flares to life as the scheduled departure window opens.",
                    TextPresets.SYSTEM,
                ))
                uses_remaining -= 1
                extra["uses_remaining"] = uses_remaining
                if item.get("inv_id") and getattr(self.server, "db", None):
                    self.server.db.save_item_extra_data(item["inv_id"], extra)
                item.update(extra)
                if uses_remaining <= 0:
                    await self._remove_item(session, item)
                await self._teleport_player(
                    session,
                    int(dest.get("arrival_room_id") or dest.get("room_id") or 0),
                    arrive_msg=str(network.get("arrive_msg") or ""),
                    roundtime_sec=int(network.get("roundtime_sec") or 0),
                    transport_label="a swirl of chronomage light",
                )

    def _prune_expired_passes(self, session, *, now: float):
        seen = []
        for item in list(getattr(session, "inventory", []) or []):
            if item:
                seen.append(item)
        for hand_name in ("right_hand", "left_hand"):
            held = getattr(session, hand_name, None)
            if held and held not in seen:
                seen.append(held)
        for item in seen:
            extra = self._travel_item_data(item)
            if not extra:
                continue
            expires_at = float(extra.get("expires_at") or 0.0)
            if expires_at and expires_at <= now:
                if getattr(session, "right_hand", None) is item:
                    session.right_hand = None
                if getattr(session, "left_hand", None) is item:
                    session.left_hand = None
                try:
                    session.inventory.remove(item)
                except ValueError:
                    pass
                if getattr(self.server, "db", None) and item.get("inv_id"):
                    self.server.db.remove_inventory_item(item["inv_id"])

    async def _charge_silver(self, session, amount: int) -> bool:
        amount = max(0, int(amount or 0))
        if amount <= 0:
            return True
        current = int(getattr(session, "silver", 0) or 0)
        if current < amount:
            return False
        session.silver = current - amount
        self._save_silver(session)
        return True

    def _save_silver(self, session):
        db = getattr(self.server, "db", None)
        if db and getattr(session, "character_id", None):
            try:
                db.save_character_resources(
                    session.character_id,
                    int(getattr(session, "health_current", 0) or 0),
                    int(getattr(session, "mana_current", 0) or 0),
                    int(getattr(session, "spirit_current", 0) or 0),
                    int(getattr(session, "stamina_current", 0) or 0),
                    int(getattr(session, "silver", 0) or 0),
                )
            except Exception:
                log.exception("Failed saving travel-office silver state for %s", getattr(session, "character_name", "?"))

    async def _give_travel_item(self, session, *, name: str, short_name: str, noun: str, item_type: str, article: str, description: str, extra: dict) -> Optional[dict]:
        db = getattr(self.server, "db", None)
        if not db or not getattr(session, "character_id", None):
            return None
        item_id = db.get_or_create_item(name, short_name, noun, item_type=item_type, article=article, value=0, description=description)
        if not item_id:
            return None
        slot = None
        if not getattr(session, "right_hand", None):
            slot = "right_hand"
        elif not getattr(session, "left_hand", None):
            slot = "left_hand"
        inv_id = db.insert_inventory_item_instance(session.character_id, item_id, slot=slot)
        if not inv_id:
            return None
        db.save_item_extra_data(inv_id, extra)

        session.inventory = db.get_character_inventory(session.character_id)
        from server.core.commands.player.inventory import restore_inventory_state
        restore_inventory_state(self.server, session)

        held = getattr(session, "right_hand", None)
        if slot == "left_hand":
            held = getattr(session, "left_hand", None)
        if held and held.get("inv_id") == inv_id:
            return held
        for item in getattr(session, "inventory", []) or []:
            if item.get("inv_id") == inv_id:
                return item
        return None

    async def _remove_item(self, session, item: dict):
        inv_id = int(item.get("inv_id") or 0)
        if inv_id <= 0:
            return
        if getattr(session, "right_hand", None) and session.right_hand.get("inv_id") == inv_id:
            session.right_hand = None
        if getattr(session, "left_hand", None) and session.left_hand.get("inv_id") == inv_id:
            session.left_hand = None
        try:
            session.inventory = [row for row in (session.inventory or []) if int(row.get("inv_id") or 0) != inv_id]
        except Exception:
            pass
        db = getattr(self.server, "db", None)
        if db:
            db.remove_inventory_item(inv_id)

    async def _teleport_player(self, session, room_id: int, *, arrive_msg: str, roundtime_sec: int = 0, transport_label: str = "travel"):
        target_room = self.server.world.get_room(int(room_id or 0))
        current_room = getattr(session, "current_room", None)
        if not target_room:
            await session.send_line(f"The {transport_label} fails to resolve properly.")
            return

        if current_room:
            await self.server.world.broadcast_to_room(
                current_room.id,
                f"{session.character_name} departs via {transport_label}.",
                exclude=session,
            )
            self.server.world.remove_player_from_room(session, current_room.id)

        self.server.world.add_player_to_room(session, target_room.id)
        session.previous_room = current_room
        session.current_room = target_room

        db = getattr(self.server, "db", None)
        if db and getattr(session, "character_id", None):
            try:
                db.execute_update(
                    "UPDATE characters SET current_room_id = %s WHERE id = %s",
                    (target_room.id, session.character_id),
                )
            except Exception:
                log.exception("Failed saving transport destination for %s", getattr(session, "character_name", "?"))

        if roundtime_sec > 0:
            session.set_roundtime(roundtime_sec)

        if arrive_msg:
            await session.send_line(colorize(arrive_msg, TextPresets.SYSTEM))

        await self.server.world.broadcast_to_room(
            target_room.id,
            f"{session.character_name} arrives via {transport_label}.",
            exclude=session,
        )

        from server.core.commands.player.movement import cmd_look
        await cmd_look(session, "look", "", self.server)
