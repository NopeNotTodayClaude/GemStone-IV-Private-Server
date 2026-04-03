"""
justice_manager.py
------------------
Canonical justice runtime.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta

from server.core.protocol.colors import colorize, npc_speech, TextPresets

log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.utcnow()


def _fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return "unknown"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _as_dt(value):
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    if isinstance(value, str):
        text = value.replace("T", " ").replace("Z", "").strip()
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return None
    return None


def _norm(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().replace("_", " ").split())


def _json_loads(raw, default):
    if raw in (None, ""):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return default


class JusticeManager:
    def __init__(self, server):
        self.server = server
        self._config: dict = {}
        self._charge_defs: dict[str, dict] = {}
        self._question_sets: dict[str, list[dict]] = {}
        self._service_verbs: dict[str, dict] = {}
        self._jurisdictions: dict[str, dict] = {}
        self._npc_templates: dict[str, dict] = {}
        self._room_to_jurisdiction: dict[int, str] = {}

    async def initialize(self):
        data = getattr(self.server.lua, "get_justice", lambda: {})() or {}
        self._config = dict(data.get("config") or {})
        self._charge_defs = dict(data.get("charge_defs") or {})
        self._question_sets = dict(data.get("question_sets") or {})
        self._service_verbs = dict(data.get("service_verbs") or {})
        self._jurisdictions = dict(data.get("jurisdictions") or {})
        self._npc_templates = dict(data.get("npcs") or {})
        self._room_to_jurisdiction = {}
        for jurisdiction_id, row in self._jurisdictions.items():
            for room_id in row.get("room_ids") or []:
                rid = int(room_id or 0)
                if rid > 0:
                    self._room_to_jurisdiction[rid] = jurisdiction_id
            for field in (
                "courtroom_room_id",
                "clerk_room_id",
                "jail_room_id",
                "stockade_room_id",
                "pit_room_id",
                "release_room_id",
            ):
                rid = int(row.get(field) or 0)
                if rid > 0:
                    self._room_to_jurisdiction[rid] = jurisdiction_id
        log.info(
            "JusticeManager ready (%d jurisdictions, %d charges, %d NPC templates)",
            len(self._jurisdictions),
            len(self._charge_defs),
            len(self._npc_templates),
        )

    async def tick(self, tick_count: int):
        if tick_count % 10 != 0:
            return
        now = _utcnow()
        for session in self.server.sessions.playing():
            try:
                await self._tick_session(session, now)
            except Exception:
                log.exception("Justice tick failed for %s", getattr(session, "character_name", "?"))
        if hasattr(self.server, "fake_players"):
            for actor in self.server.fake_players.get_all():
                try:
                    await self._tick_session(actor, now)
                except Exception:
                    log.exception("Justice tick failed for synthetic %s", getattr(actor, "character_name", "?"))

    async def _tick_session(self, session, now: datetime):
        if not getattr(session, "character_id", None):
            return
        case = self.get_active_case(session)
        if case:
            status = str(case.get("status") or "")
            if status == "fined":
                fine_due_at = _as_dt(case.get("fine_due_at"))
                if fine_due_at and now >= fine_due_at:
                    await session.send_line("Your time to settle your justice fine has expired.  A fresh warrant has been issued.")
                    self._append_history(session.character_id, case["jurisdiction_id"], "fine_defaulted", "Fine defaulted and warrant renewed.")
                    self._execute(
                        "UPDATE character_justice_cases SET status = 'warrant', updated_at = NOW() WHERE id = %s",
                        (case["id"],),
                    )
            elif status == "awaiting_sentence":
                question_due = _as_dt(case.get("question_due_at"))
                if question_due and now >= question_due:
                    await session.send_line("The magistrate's patience expires.  Contempt is added to your record.")
                    self._add_charge_to_case(case["id"], "contempt", 1)
                    await self._restate_sentence(session, case)
            elif status == "incarcerated":
                await self._tick_incarceration(session, case, now)
            elif status == "service":
                await self._tick_service(session, case, now)
        await self._enforce_banishment(session, now)

    def get_npc_templates(self) -> dict:
        return self._npc_templates

    def get_actions_for_npc(self, session, npc) -> list[dict]:
        if not getattr(npc, "justice_role", None):
            return []
        target = str(getattr(npc, "name", "") or getattr(npc, "display_name", "") or "").strip()
        if not target:
            return []
        actions = [
            {"label": "Justice status", "command": f"ask {target} about justice", "prefill": False},
            {"label": "Warrants", "command": f"ask {target} about warrant", "prefill": False},
            {"label": "History", "command": f"ask {target} about history", "prefill": False},
            {"label": "Inquire", "command": "inquire", "prefill": False},
            {"label": "Justice", "command": "justice status", "prefill": False},
        ]
        role = str(getattr(npc, "justice_role", "") or "")
        if role in {"judge", "clerk"}:
            actions.append({"label": "Pay fine", "command": "pay fine", "prefill": False})
            actions.append({"label": "Sentence status", "command": f"ask {target} about sentence", "prefill": False})
        if role in {"watchman", "warden"}:
            actions.append({"label": "Service task", "command": f"ask {target} about service", "prefill": False})
        return actions

    async def maybe_handle_npc_response(self, session, npc, topic: str, response: dict) -> bool:
        if not isinstance(response, dict):
            return False
        action = str(response.get("justice_action") or "").strip().lower()
        if not action:
            return False
        jurisdiction_id = str(
            response.get("jurisdiction_id")
            or getattr(npc, "justice_jurisdiction", "")
            or self._resolve_jurisdiction_id(getattr(session, "current_room", None))
            or ""
        ).strip().lower()
        if action == "status":
            request_kind = _norm(response.get("request_kind") or topic or "status")
            if request_kind in {"warrant", "warrants"}:
                await self._send_warrants(session)
            elif request_kind == "history":
                await self._send_history(session)
            elif request_kind in {"banish", "banishment"}:
                await self._send_banishment(session)
            else:
                await self._send_npc_status(session, npc.display_name, jurisdiction_id)
            return True
        if action == "inquire":
            await self.inquire(session)
            return True
        if action == "pay_prompt":
            case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
            if case and str(case.get("status") or "") == "fined":
                await session.send_line(npc_speech(npc.display_name, f'says, "Your fine stands at {int(case.get("fine_amount") or 0)} silvers.  You may PAY FINE here."'))
            else:
                await session.send_line(npc_speech(npc.display_name, 'says, "You have no outstanding justice fine with us."'))
            return True
        if action == "service_status":
            await self._send_service_help(session, jurisdiction_id=jurisdiction_id, speaker=npc.display_name)
            return True
        if action == "judge_review":
            case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
            if case and str(case.get("status") or "") == "awaiting_sentence":
                await self._restate_sentence(session, case, speaker=npc.display_name)
            else:
                await self._send_current_case_summary(session, jurisdiction_id=jurisdiction_id, speaker=npc.display_name)
            return True
        if action == "accuse_help":
            await session.send_line(npc_speech(npc.display_name, 'says, "Use ACCUSE <target> OF <charge> if you are naming a specific offense before the law."'))
            return True
        return False

    async def maybe_handle_answer(self, session, args: str) -> bool:
        answer = _norm(args)
        if not answer:
            await session.send_line("Answer what?")
            return True
        case = self.get_active_case(session)
        if not case:
            return False
        status = str(case.get("status") or "")
        if status == "awaiting_sentence":
            await self._handle_sentence_answer(session, case, answer)
            return True
        if status == "incarcerated":
            await self._handle_jail_answer(session, case, answer)
            return True
        return False

    async def maybe_handle_pay(self, session, args: str) -> bool:
        raw = _norm(args)
        case = self.get_active_case(session)
        if not case or str(case.get("status") or "") != "fined":
            return False
        if raw and raw not in {"fine", "justice", "debt", "warrant"}:
            return False
        fine = int(case.get("fine_amount") or 0)
        if fine <= 0:
            await session.send_line("You have no justice fine outstanding.")
            return True
        funds = int(getattr(session, "silver", 0) or 0)
        if funds < fine:
            await session.send_line(f"You need {fine} silvers to clear your justice debt.")
            return True
        session.silver = max(0, funds - fine)
        self._close_case(case["id"], "fine_paid")
        self._append_history(session.character_id, case["jurisdiction_id"], "fine_paid", f"Paid justice fine of {fine} silvers.")
        await session.send_line(colorize(f"You pay {fine} silvers to clear your justice debt.", TextPresets.SYSTEM))
        return True

    async def maybe_handle_help(self, session, topic: str) -> bool:
        key = _norm(topic)
        if key not in {"justice", "service", "task", "accuse", "inquire"}:
            return False
        if key == "justice":
            await session.send_line("JUSTICE STATUS shows local law status.  JUSTICE WARRANT lists warrants.  JUSTICE BANISH lists banishments.  JUSTICE HISTORY lists recent criminal history.")
            await session.send_line("ACCUSE <target> OF <charge> lodges an accusation in a justice area.  INQUIRE reports remaining incarceration or service time.")
            return True
        if key in {"service", "task"}:
            await self._send_service_help(session)
            return True
        if key == "accuse":
            await session.send_line("Usage: ACCUSE <target> OF impropriety|hooliganism|assault|theft|banishment")
            return True
        if key == "inquire":
            await session.send_line("INQUIRE reports the time remaining on incarceration or community service and repeats your current justice instructions.")
            return True
        return False

    async def maybe_handle_service_inspect(self, session, target: str) -> bool:
        case = self.get_active_case(session)
        if not case or str(case.get("status") or "") != "service":
            return False
        state = _json_loads(case.get("service_state_json"), {})
        task = self._task_for_case(case, state)
        if not task or _norm(target) != _norm(task.get("object_name")):
            return False
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if room_id != int(task.get("room_id") or 0):
            await session.send_line(f"You need to inspect the {task.get('object_name')} in the proper work area first.")
            return True
        sequence = list(task.get("sequence") or [])
        step_index = int(state.get("step_index") or 0)
        remaining = sequence[step_index:] if step_index < len(sequence) else sequence
        await session.send_line(task.get("inspect_intro") or "The work demands a precise sequence.")
        if remaining:
            await session.send_line("Current sequence: " + ", ".join(v.upper() for v in remaining))
            await session.send_line(f"Start with {remaining[0].upper()}.")
        return True

    async def maybe_handle_service_verb(self, session, verb: str, args: str) -> bool:
        case = self.get_active_case(session)
        if not case or str(case.get("status") or "") != "service":
            return False
        verb_key = _norm(verb)
        if verb_key not in self._service_verbs:
            return False
        state = _json_loads(case.get("service_state_json"), {})
        task = self._task_for_case(case, state)
        if not task:
            await session.send_line("Your community service assignment is missing its work order.")
            return True
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if room_id != int(task.get("room_id") or 0):
            await session.send_line(f"You need to report to the {task.get('label') or 'assigned work area'} first.")
            return True
        target = _norm(args or task.get("object_name") or "")
        if target and target != _norm(task.get("object_name")):
            await session.send_line(f"Your current assignment is to work on the {task.get('object_name')}.")
            return True
        sequence = list(task.get("sequence") or [])
        step_index = int(state.get("step_index") or 0)
        expected = sequence[step_index] if step_index < len(sequence) else None
        if not expected:
            await self._grant_service_credit(session, case, task, state)
            return True
        if verb_key != expected:
            await session.send_line(f"You are out of sequence.  Inspect the {task.get('object_name')} again and begin with {expected.upper()}.")
            return True
        step_index += 1
        state["step_index"] = step_index
        self._update_service_state(case["id"], state)
        await session.send_line(colorize(f"You {verb_key} the {task.get('object_name')} as ordered.", TextPresets.SYSTEM))
        if step_index >= len(sequence):
            await self._grant_service_credit(session, case, task, state)
        return True

    async def before_move(self, session, from_room, to_room_id: int, direction: str) -> bool:
        del direction
        case = self.get_active_case(session)
        if case and str(case.get("status") or "") == "incarcerated":
            jail_room_id = int(case.get("jail_room_id") or 0)
            room_id = int(getattr(from_room, "id", 0) or 0)
            if room_id == jail_room_id and to_room_id != jail_room_id:
                await session.send_line("The law is not finished with you yet.")
                return False
        target_room = self.server.world.get_room(int(to_room_id or 0)) if getattr(self.server, "world", None) else None
        jurisdiction_id = self._resolve_jurisdiction_id(target_room)
        if jurisdiction_id:
            banishment = self._active_banishment_case(session, jurisdiction_id)
            if banishment and not (case and str(case.get("jurisdiction_id") or "") == str(jurisdiction_id) and str(case.get("status") or "") in {"awaiting_sentence", "incarcerated", "service"}):
                await session.send_line(f"You are banished from {self._display_jurisdiction(jurisdiction_id)}.")
                return False
        return True

    async def after_move(self, session, room) -> None:
        case = self.get_active_case(session)
        if case and str(case.get("status") or "") == "warrant":
            if self._resolve_jurisdiction_id(room) == str(case.get("jurisdiction_id") or ""):
                await self._arrest_player(session, case, speaker="A watching officer")
                return
        await self._enforce_banishment(session, _utcnow())

    async def on_theft(self, session, target_name: str, *, room_id: int | None = None):
        room = getattr(session, "current_room", None)
        room_id = int(room_id or getattr(room, "id", 0) or 0)
        jurisdiction_id = self._resolve_jurisdiction_id(room)
        if not jurisdiction_id:
            return
        await self.record_crime(session, jurisdiction_id, "theft", f"Theft reported against {target_name}.", room_id=room_id)

    async def on_public_disturbance(self, session, room_id: int, trap_type: str, harmed_players):
        jurisdiction_id = self._resolve_jurisdiction_id(self.server.world.get_room(room_id) if room_id else None)
        if not jurisdiction_id:
            return
        victims = ", ".join(sorted({getattr(p, "character_name", "") for p in harmed_players if getattr(p, "character_name", "")}))
        detail = f"A {trap_type} trap endangered bystanders"
        if victims:
            detail += f": {victims}"
        detail += "."
        await self.record_crime(session, jurisdiction_id, "endangering_public_safety", detail, room_id=room_id)

    async def record_crime(self, session, jurisdiction_id: str, charge_code: str, detail_text: str, *, room_id: int = 0):
        if not getattr(session, "character_id", None):
            return
        charge = self._charge_defs.get(str(charge_code or "").strip().lower())
        if not charge:
            return
        case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        if case and str(case.get("status") or "") == "closed":
            case = None
        if not case:
            case = self._create_case(
                session.character_id,
                jurisdiction_id,
                room_id=room_id,
                release_room_id=self._release_room_for_jurisdiction(jurisdiction_id),
                jail_room_id=self._jail_room_for_jurisdiction(jurisdiction_id),
            )
        self._add_charge_to_case(case["id"], charge_code, 1)
        self._append_history(session.character_id, jurisdiction_id, "charge_added", detail_text)
        self._recalculate_case(case["id"])
        refreshed = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        if refreshed and str(refreshed.get("status") or "") == "warrant":
            await session.send_line(colorize(f"The law takes note of your crime in {self._display_jurisdiction(jurisdiction_id)}.", TextPresets.WARNING))

    async def justice(self, session, args: str):
        topic = _norm(args or "status")
        if topic in {"", "status", "case"}:
            await self._send_status(session)
            return
        if topic in {"warrant", "warrants", "charges"}:
            await self._send_warrants(session)
            return
        if topic == "history":
            await self._send_history(session)
            return
        if topic in {"banish", "banishment"}:
            await self._send_banishment(session)
            return
        if topic in {"service", "task"}:
            await self._send_service_help(session)
            return
        await session.send_line("Usage: JUSTICE STATUS | JUSTICE WARRANT | JUSTICE HISTORY | JUSTICE BANISH | JUSTICE SERVICE")

    async def inquire(self, session):
        case = self.get_active_case(session)
        if not case:
            await session.send_line("You have no current justice sentence to inquire about.")
            return
        status = str(case.get("status") or "")
        if status == "incarcerated":
            end_at = _as_dt(case.get("incarceration_end_at"))
            remaining = max(0, int((end_at - _utcnow()).total_seconds())) if end_at else 0
            await session.send_line(f"You have about {max(0, remaining // 60)} minute(s) of incarceration remaining.")
            prompt = str(case.get("question_prompt") or "").strip()
            if prompt:
                await session.send_line(f"Current jail question: {prompt}")
            return
        if status == "service":
            state = _json_loads(case.get("service_state_json"), {})
            task = self._task_for_case(case, state)
            required = int(state.get("required_cycles") or 0)
            completed = int(state.get("cycles_completed") or 0)
            label = task.get("label") if task else "community service"
            await session.send_line(f"You are assigned to {label}.  Progress: {completed}/{required} completed cycle(s).")
            await self._send_service_help(session, speaker=None)
            return
        if status == "fined":
            await session.send_line(f"You owe {int(case.get('fine_amount') or 0)} silvers by {_fmt_dt(_as_dt(case.get('fine_due_at')))}.")
            return
        if status == "awaiting_sentence":
            await self._restate_sentence(session, case)
            return
        if status == "warrant":
            await session.send_line(f"You have an active warrant in {self._display_jurisdiction(case.get('jurisdiction_id'))}.")
            return
        await self._send_current_case_summary(session)

    async def accuse(self, session, args: str):
        raw = str(args or "").strip()
        lower = raw.lower()
        if " of " not in lower:
            await session.send_line("Usage: ACCUSE <target> OF <charge>")
            return
        idx = lower.index(" of ")
        target_name = raw[:idx].strip()
        charge_text = raw[idx + 4 :].strip()
        charge_code = self._resolve_charge_code(charge_text)
        if not target_name or not charge_code:
            await session.send_line("Usage: ACCUSE <target> OF impropriety|hooliganism|assault|theft|banishment")
            return
        charge = self._charge_defs.get(charge_code) or {}
        if not charge.get("accusable"):
            await session.send_line("That is not a charge private citizens may accuse another person of.")
            return
        jurisdiction_id = self._resolve_jurisdiction_id(getattr(session, "current_room", None))
        if not jurisdiction_id:
            await session.send_line("You are not in a justice-aware jurisdiction.")
            return
        target_session = self._find_player_in_room(session, target_name)
        if not target_session:
            await session.send_line("The accused must be present.")
            return
        if target_session is session:
            await session.send_line("Accusing yourself would only save the court paperwork.")
            return
        self._insert_accusation(
            session.character_id,
            target_session.character_id,
            target_session.character_name,
            jurisdiction_id,
            charge_code,
        )
        case = self.get_active_case(target_session, jurisdiction_id=jurisdiction_id)
        room_id = int(getattr(getattr(session, "current_room", None), "id", 0) or 0)
        if not case:
            case = self._create_case(
                target_session.character_id,
                jurisdiction_id,
                room_id=room_id,
                release_room_id=self._release_room_for_jurisdiction(jurisdiction_id),
                jail_room_id=self._jail_room_for_jurisdiction(jurisdiction_id),
            )
        self._add_charge_to_case(case["id"], charge_code, 1)
        self._append_history(target_session.character_id, jurisdiction_id, "accused", f"Accused by {session.character_name} of {charge.get('label') or charge_code}.")
        self._recalculate_case(case["id"])
        await session.send_line(colorize(f"You formally accuse {target_session.character_name} of {charge.get('label') or charge_code}.", TextPresets.SYSTEM))
        await target_session.send_line(colorize(f"{session.character_name} levels a formal accusation of {charge.get('label') or charge_code} against you.", TextPresets.WARNING))

    def get_active_case(self, session_or_character, *, jurisdiction_id: str | None = None):
        character_id = getattr(session_or_character, "character_id", session_or_character)
        if not character_id:
            return None
        sql = """
            SELECT *
            FROM character_justice_cases
            WHERE character_id = %s
              AND status <> 'closed'
        """
        params = [int(character_id)]
        if jurisdiction_id:
            sql += " AND jurisdiction_id = %s"
            params.append(str(jurisdiction_id))
        sql += """
            ORDER BY FIELD(status, 'awaiting_sentence', 'incarcerated', 'service', 'fined', 'warrant'),
                     updated_at DESC, id DESC
            LIMIT 1
        """
        rows = self._query_dicts(sql, tuple(params))
        return rows[0] if rows else None

    def _query_dicts(self, sql: str, params=()):
        db = getattr(self.server, "db", None)
        if not db:
            return []
        conn = db._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params or ())
            return list(cur.fetchall() or [])
        finally:
            conn.close()

    def _execute(self, sql: str, params=()):
        db = getattr(self.server, "db", None)
        if not db:
            return 0
        conn = db._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            conn.commit()
            return int(cur.lastrowid or 0)
        finally:
            conn.close()

    def _create_case(self, character_id: int, jurisdiction_id: str, *, room_id: int = 0, release_room_id: int = 0, jail_room_id: int = 0):
        jurisdiction = self._jurisdictions.get(str(jurisdiction_id) or {}) or {}
        courtroom_room_id = int(jurisdiction.get("courtroom_room_id") or 0)
        clerk_room_id = int(jurisdiction.get("clerk_room_id") or 0)
        case_id = self._execute(
            """
            INSERT INTO character_justice_cases (
                character_id, jurisdiction_id, status, arrest_room_id, courtroom_room_id,
                jail_room_id, release_room_id, created_at, updated_at
            ) VALUES (%s, %s, 'warrant', %s, %s, %s, %s, NOW(), NOW())
            """,
            (
                int(character_id),
                str(jurisdiction_id),
                int(room_id or clerk_room_id or courtroom_room_id or 0),
                courtroom_room_id,
                int(jail_room_id or jurisdiction.get("jail_room_id") or 0),
                int(release_room_id or jurisdiction.get("release_room_id") or clerk_room_id or 0),
            ),
        )
        return self.get_active_case(character_id, jurisdiction_id=jurisdiction_id) or {"id": case_id, "character_id": character_id, "jurisdiction_id": jurisdiction_id, "status": "warrant"}

    def _get_case_charges(self, case_id: int) -> list[dict]:
        return self._query_dicts(
            """
            SELECT *
            FROM character_justice_case_charges
            WHERE case_id = %s
            ORDER BY severity DESC, charge_code
            """,
            (int(case_id),),
        )

    def _add_charge_to_case(self, case_id: int, charge_code: str, count: int = 1):
        charge = self._charge_defs.get(str(charge_code or "").strip().lower())
        if not charge:
            return
        self._execute(
            """
            INSERT INTO character_justice_case_charges (
                case_id, charge_code, count, fine_amount, incarceration_seconds,
                service_seconds, severity, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                count = count + VALUES(count),
                fine_amount = fine_amount + VALUES(fine_amount),
                incarceration_seconds = incarceration_seconds + VALUES(incarceration_seconds),
                service_seconds = service_seconds + VALUES(service_seconds),
                severity = GREATEST(severity, VALUES(severity))
            """,
            (
                int(case_id),
                str(charge_code),
                int(count or 1),
                int(charge.get("fine") or 0) * int(count or 1),
                int(charge.get("incarceration_min") or 0) * 60 * int(count or 1),
                int(charge.get("service_min") or 0) * 60 * int(count or 1),
                int(charge.get("severity") or 1),
            ),
        )

    def _append_history(self, character_id: int, jurisdiction_id: str, event_type: str, detail_text: str):
        self._execute(
            """
            INSERT INTO character_justice_history (
                character_id, jurisdiction_id, event_type, detail_text, created_at
            ) VALUES (%s, %s, %s, %s, NOW())
            """,
            (int(character_id), str(jurisdiction_id), str(event_type), str(detail_text or "")),
        )

    def _insert_accusation(self, accuser_character_id: int, accused_character_id: int, accused_name: str, jurisdiction_id: str, charge_code: str):
        self._execute(
            """
            INSERT INTO character_justice_accusations (
                accuser_character_id, accused_character_id, accused_name, jurisdiction_id, charge_code, created_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (
                int(accuser_character_id or 0),
                int(accused_character_id or 0),
                str(accused_name or ""),
                str(jurisdiction_id or ""),
                str(charge_code or ""),
            ),
        )

    def _close_case(self, case_id: int, close_reason: str):
        self._execute(
            """
            UPDATE character_justice_cases
            SET status = 'closed', close_reason = %s, closed_at = NOW(), updated_at = NOW()
            WHERE id = %s
            """,
            (str(close_reason or ""), int(case_id)),
        )

    def _recalculate_case(self, case_id: int):
        case_rows = self._query_dicts("SELECT * FROM character_justice_cases WHERE id = %s LIMIT 1", (int(case_id),))
        if not case_rows:
            return
        case = case_rows[0]
        charges = self._get_case_charges(case_id)
        fine_amount = sum(int(row.get("fine_amount") or 0) for row in charges)
        incarceration_seconds = sum(int(row.get("incarceration_seconds") or 0) for row in charges)
        service_seconds = sum(int(row.get("service_seconds") or 0) for row in charges)
        allow_service = all(bool((self._charge_defs.get(str(row.get("charge_code") or ""), {}) or {}).get("allow_service", True)) for row in charges)
        banishment_days = 0
        for row in charges:
            charge = self._charge_defs.get(str(row.get("charge_code") or ""), {}) or {}
            banishment_days = max(banishment_days, int(charge.get("banishment_days") or 0))
        banishment_expires = None
        if banishment_days > 0:
            banishment_expires = _utcnow() + timedelta(days=banishment_days)

        fields = {
            "fine_amount": fine_amount,
            "incarceration_seconds": incarceration_seconds,
            "service_seconds": service_seconds if allow_service else 0,
            "banishment_expires_at": banishment_expires,
        }
        status = str(case.get("status") or "warrant")
        if status in {"closed", "fined", "awaiting_sentence", "service", "incarcerated"}:
            status_sql = status
        else:
            status_sql = "warrant"
        self._execute(
            """
            UPDATE character_justice_cases
            SET status = %s,
                fine_amount = %s,
                incarceration_seconds = %s,
                service_seconds = %s,
                banishment_expires_at = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                status_sql,
                int(fields["fine_amount"]),
                int(fields["incarceration_seconds"]),
                int(fields["service_seconds"]),
                fields["banishment_expires_at"],
                int(case_id),
            ),
        )

    async def _send_status(self, session):
        case = self.get_active_case(session)
        if not case:
            await session.send_line("You have no current justice case.")
            await self._send_banishment(session)
            return
        await self._send_current_case_summary(session)

    async def _send_npc_status(self, session, speaker: str, jurisdiction_id: str):
        case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        if not case:
            await session.send_line(npc_speech(speaker, 'says, "Our ledgers show no active complaint against you here."'))
            return
        await session.send_line(npc_speech(speaker, f'says, "Your standing in {self._display_jurisdiction(jurisdiction_id)} is as follows."'))
        await self._send_current_case_summary(session, jurisdiction_id=jurisdiction_id, speaker=speaker)

    async def _send_current_case_summary(self, session, jurisdiction_id: str | None = None, speaker: str | None = None):
        case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        if not case:
            text = "No active justice case is recorded."
            if speaker:
                await session.send_line(npc_speech(speaker, f'says, "{text}"'))
            else:
                await session.send_line(text)
            return
        charges = self._get_case_charges(case["id"])
        charge_text = ", ".join(f"{(self._charge_defs.get(str(row.get('charge_code') or ''), {}) or {}).get('label', row.get('charge_code'))} x{int(row.get('count') or 0)}" for row in charges) or "none"
        await session.send_line(f"Jurisdiction: {self._display_jurisdiction(case.get('jurisdiction_id'))}")
        await session.send_line(f"Status: {str(case.get('status') or '').replace('_', ' ').title()}")
        await session.send_line(f"Charges: {charge_text}")
        fine = int(case.get("fine_amount") or 0)
        if fine:
            await session.send_line(f"Fine: {fine} silvers")
        jail_min = int(case.get("incarceration_seconds") or 0) // 60
        if jail_min:
            await session.send_line(f"Incarceration: {jail_min} minute(s)")
        svc_min = int(case.get("service_seconds") or 0) // 60
        if svc_min:
            await session.send_line(f"Community service: {svc_min} minute(s)")
        if case.get("banishment_expires_at"):
            await session.send_line(f"Banishment expires: {_fmt_dt(_as_dt(case.get('banishment_expires_at')))}")

    async def _send_warrants(self, session):
        rows = self._query_dicts(
            """
            SELECT jurisdiction_id, status, fine_amount, updated_at
            FROM character_justice_cases
            WHERE character_id = %s AND status IN ('warrant', 'awaiting_sentence', 'fined', 'service', 'incarcerated')
            ORDER BY updated_at DESC
            """,
            (int(getattr(session, "character_id", 0) or 0),),
        )
        if not rows:
            await session.send_line("You have no active warrants or justice holds.")
            return
        await session.send_line("Active justice holds:")
        for row in rows:
            await session.send_line(f"  {self._display_jurisdiction(row.get('jurisdiction_id'))}: {str(row.get('status') or '').replace('_', ' ')}")

    async def _send_history(self, session):
        rows = self._query_dicts(
            """
            SELECT jurisdiction_id, event_type, detail_text, created_at
            FROM character_justice_history
            WHERE character_id = %s
            ORDER BY created_at DESC
            LIMIT 8
            """,
            (int(getattr(session, "character_id", 0) or 0),),
        )
        if not rows:
            await session.send_line("Your justice history is clear.")
            return
        await session.send_line("Recent justice history:")
        for row in rows:
            await session.send_line(
                f"  [{self._display_jurisdiction(row.get('jurisdiction_id'))}] {str(row.get('event_type') or '').replace('_', ' ')}: {row.get('detail_text')}"
            )

    async def _send_banishment(self, session):
        now = _utcnow()
        rows = self._query_dicts(
            """
            SELECT jurisdiction_id, banishment_expires_at
            FROM character_justice_cases
            WHERE character_id = %s
              AND banishment_expires_at IS NOT NULL
              AND banishment_expires_at > NOW()
            ORDER BY banishment_expires_at DESC
            """,
            (int(getattr(session, "character_id", 0) or 0),),
        )
        if not rows:
            await session.send_line("No active banishments are recorded.")
            return
        await session.send_line("Active banishments:")
        for row in rows:
            end_at = _as_dt(row.get("banishment_expires_at"))
            remaining = max(0, int((end_at - now).total_seconds() // 3600)) if end_at else 0
            await session.send_line(f"  {self._display_jurisdiction(row.get('jurisdiction_id'))}: about {remaining} hour(s) remain.")

    async def _restate_sentence(self, session, case: dict, speaker: str | None = None):
        charges = self._get_case_charges(case["id"])
        labels = ", ".join((self._charge_defs.get(str(row.get("charge_code") or ""), {}) or {}).get("label", str(row.get("charge_code") or "")) for row in charges)
        line = f"Your charges stand as {labels or 'unspecified offenses'}."
        if speaker:
            await session.send_line(npc_speech(speaker, f'says, "{line}"'))
        else:
            await session.send_line(line)
        options = ["FINE", "JAIL"]
        if int(case.get("service_seconds") or 0) > 0:
            options.insert(1, "SERVICE")
        await session.send_line(f"Sentence options: {', '.join(options)}.  Use ANSWER <option>.")

    async def _handle_sentence_answer(self, session, case: dict, answer: str):
        choice = _norm(answer)
        if choice in {"fine", "pay", "payment"}:
            fine_due = _utcnow() + timedelta(seconds=int(self._config.get("fine_due_sec") or 1260))
            self._execute(
                "UPDATE character_justice_cases SET status = 'fined', fine_due_at = %s, updated_at = NOW() WHERE id = %s",
                (fine_due, int(case["id"])),
            )
            self._append_history(session.character_id, case["jurisdiction_id"], "sentence_fined", f"Fine imposed: {int(case.get('fine_amount') or 0)} silvers.")
            await session.send_line(f"The court fines you {int(case.get('fine_amount') or 0)} silvers.  PAY FINE by {_fmt_dt(fine_due)}.")
            return
        if choice in {"service", "community service", "labor", "labour"} and int(case.get("service_seconds") or 0) > 0:
            await self._start_service(session, case)
            return
        if choice in {"jail", "incarceration", "cell", "prison"}:
            await self._start_incarceration(session, case)
            return
        await self._restate_sentence(session, case)

    async def _start_incarceration(self, session, case: dict):
        end_at = _utcnow() + timedelta(seconds=int(case.get("incarceration_seconds") or 0))
        question_set = "jail"
        self._execute(
            """
            UPDATE character_justice_cases
            SET status = 'incarcerated', incarceration_end_at = %s, question_set = %s,
                question_due_at = NULL, question_prompt = NULL, question_answer_key = NULL,
                updated_at = NOW()
            WHERE id = %s
            """,
            (end_at, question_set, int(case["id"])),
        )
        await self._move_session(session, int(case.get("jail_room_id") or self._jail_room_for_jurisdiction(case.get("jurisdiction_id"))), announce="You are escorted into custody.")
        await session.send_line(colorize("The law remands you to incarceration.", TextPresets.WARNING))
        self._append_history(session.character_id, case["jurisdiction_id"], "sentence_incarcerated", f"Incarcerated until {_fmt_dt(end_at)}.")
        refreshed = self.get_active_case(session, jurisdiction_id=case.get("jurisdiction_id"))
        if refreshed:
            await self._issue_new_jail_prompt(session, refreshed)

    async def _start_service(self, session, case: dict):
        task = self._jurisdiction_service_task(case.get("jurisdiction_id"))
        if not task:
            await session.send_line("The court cannot find a valid community-service order.  It falls back to jail.")
            await self._start_incarceration(session, case)
            return
        step_credit = max(30, int(self._config.get("service_step_credit_sec") or 90))
        required_cycles = max(int(task.get("cycles_required") or 1), (int(case.get("service_seconds") or 0) + step_credit - 1) // step_credit)
        state = {
            "task_key": task.get("key"),
            "step_index": 0,
            "cycles_completed": 0,
            "required_cycles": required_cycles,
        }
        self._execute(
            """
            UPDATE character_justice_cases
            SET status = 'service', service_task_key = %s, service_state_json = %s, updated_at = NOW()
            WHERE id = %s
            """,
            (str(task.get("key") or ""), json.dumps(state), int(case["id"])),
        )
        await self._move_session(session, int(task.get("room_id") or case.get("release_room_id") or 0), announce="An officer marches you to your assigned labor.")
        await session.send_line(task.get("briefing") or "You are assigned to community service.")
        await self._send_service_help(session, jurisdiction_id=case.get("jurisdiction_id"))

    async def _tick_incarceration(self, session, case: dict, now: datetime):
        end_at = _as_dt(case.get("incarceration_end_at"))
        if end_at and now >= end_at:
            self._close_case(case["id"], "incarceration_served")
            self._append_history(session.character_id, case["jurisdiction_id"], "release", "Incarceration served.")
            await self._move_session(session, int(case.get("release_room_id") or self._release_room_for_jurisdiction(case.get("jurisdiction_id"))), announce="The guard opens the way and releases you.")
            await session.send_line("Your incarceration has ended.")
            return
        due_at = _as_dt(case.get("question_due_at"))
        if not case.get("question_prompt") or (due_at and now >= due_at):
            await self._issue_new_jail_prompt(session, case)

    async def _tick_service(self, session, case: dict, now: datetime):
        del now
        state = _json_loads(case.get("service_state_json"), {})
        task = self._task_for_case(case, state)
        if not task:
            return
        required = int(state.get("required_cycles") or 0)
        completed = int(state.get("cycles_completed") or 0)
        if completed >= required > 0:
            await self._complete_service_case(session, case, task)

    async def _issue_new_jail_prompt(self, session, case: dict):
        question_set = str(case.get("question_set") or "jail").strip().lower()
        questions = list(self._question_sets.get(question_set) or [])
        if not questions:
            return
        history_index = int(time.time()) % len(questions)
        row = questions[history_index]
        due_at = _utcnow() + timedelta(seconds=int(self._config.get("answer_timeout_sec") or 120))
        self._execute(
            """
            UPDATE character_justice_cases
            SET question_prompt = %s, question_answer_key = %s, question_due_at = %s, updated_at = NOW()
            WHERE id = %s
            """,
            (str(row.get("prompt") or ""), str(row.get("key") or ""), due_at, int(case["id"])),
        )
        await session.send_line(colorize(f'Jail question: {row.get("prompt")}  Use ANSWER <response>.', TextPresets.WARNING))

    async def _handle_jail_answer(self, session, case: dict, answer: str):
        expected = self._expected_answers(str(case.get("question_answer_key") or ""), session, case.get("jurisdiction_id"))
        if not expected:
            await session.send_line("There is no current jail question to answer.")
            return
        if _norm(answer) in expected:
            end_at = _as_dt(case.get("incarceration_end_at")) or _utcnow()
            new_end = max(_utcnow(), end_at - timedelta(seconds=60))
            self._execute(
                """
                UPDATE character_justice_cases
                SET incarceration_end_at = %s, question_due_at = NULL, question_prompt = NULL,
                    question_answer_key = NULL, updated_at = NOW()
                WHERE id = %s
                """,
                (new_end, int(case["id"])),
            )
            await session.send_line(colorize("Your answer earns a small measure of leniency.", TextPresets.SYSTEM))
            return
        penalty = int(self._config.get("wrong_answer_penalty_sec") or 120)
        end_at = (_as_dt(case.get("incarceration_end_at")) or _utcnow()) + timedelta(seconds=penalty)
        self._execute(
            """
            UPDATE character_justice_cases
            SET incarceration_end_at = %s, question_due_at = NULL, question_prompt = NULL,
                question_answer_key = NULL, updated_at = NOW()
            WHERE id = %s
            """,
            (end_at, int(case["id"])),
        )
        await session.send_line(colorize("Wrong.  Your jail time lengthens.", TextPresets.WARNING))

    def _expected_answers(self, question_key: str, session, jurisdiction_id: str | None) -> set[str]:
        key = str(question_key or "").strip().lower()
        if key == "city_name":
            return {_norm(self._display_jurisdiction(jurisdiction_id))}
        if key == "gender":
            return {_norm(getattr(session, "gender", ""))}
        if key == "race":
            race_name = getattr(session, "race", None) or getattr(session, "race_name", None) or ""
            return {_norm(race_name)}
        if key == "weekday_name":
            return {_norm(_utcnow().strftime("%A"))}
        if key == "hour_number":
            return {str(int(_utcnow().hour))}
        return set()

    def _task_for_case(self, case: dict, state: dict | None = None):
        state = state or _json_loads(case.get("service_state_json"), {})
        jurisdiction = self._jurisdictions.get(str(case.get("jurisdiction_id") or ""), {}) or {}
        task_key = str(state.get("task_key") or case.get("service_task_key") or "").strip().lower()
        for task in jurisdiction.get("service_tasks") or []:
            if str(task.get("key") or "").strip().lower() == task_key:
                return task
        tasks = list(jurisdiction.get("service_tasks") or [])
        return tasks[0] if tasks else None

    def _update_service_state(self, case_id: int, state: dict):
        self._execute(
            "UPDATE character_justice_cases SET service_state_json = %s, updated_at = NOW() WHERE id = %s",
            (json.dumps(state or {}), int(case_id)),
        )

    async def _grant_service_credit(self, session, case: dict, task: dict, state: dict):
        state = dict(state or {})
        state["cycles_completed"] = int(state.get("cycles_completed") or 0) + 1
        state["step_index"] = 0
        self._update_service_state(case["id"], state)
        await session.send_line(task.get("completion_text") or "You complete another round of court-ordered labor.")
        required = int(state.get("required_cycles") or 0)
        completed = int(state.get("cycles_completed") or 0)
        if completed >= required > 0:
            await self._complete_service_case(session, case, task)
        else:
            await session.send_line(f"Community service progress: {completed}/{required} completed cycle(s).")

    async def _complete_service_case(self, session, case: dict, task: dict):
        del task
        self._close_case(case["id"], "service_completed")
        self._append_history(session.character_id, case["jurisdiction_id"], "service_completed", "Community service completed.")
        await session.send_line(colorize("Your assigned community service is complete.  Your debt is satisfied.", TextPresets.SYSTEM))
        await self._move_session(session, int(case.get("release_room_id") or self._release_room_for_jurisdiction(case.get("jurisdiction_id"))), announce="A watchman waves you on once the labor is judged complete.")

    async def _arrest_player(self, session, case: dict, speaker: str = "A city guard"):
        if str(case.get("status") or "") not in {"warrant", "fined"}:
            return
        self._execute(
            """
            UPDATE character_justice_cases
            SET status = 'awaiting_sentence', updated_at = NOW()
            WHERE id = %s
            """,
            (int(case["id"]),),
        )
        courtroom_room = int(case.get("courtroom_room_id") or self._courtroom_room_for_jurisdiction(case.get("jurisdiction_id")))
        await session.send_line(colorize(f"{speaker} seizes you under lawful warrant.", TextPresets.WARNING))
        await self._move_session(session, courtroom_room, announce="You are hauled before the local court.")
        await self._restate_sentence(session, self.get_active_case(session, jurisdiction_id=case.get("jurisdiction_id")) or case, speaker=speaker)

    async def _move_session(self, session, room_id: int, announce: str | None = None):
        room = self.server.world.get_room(int(room_id or 0)) if getattr(self.server, "world", None) else None
        if not room:
            return
        from_room = getattr(session, "current_room", None)
        if from_room and getattr(self.server, "world", None):
            try:
                self.server.world.remove_player_from_room(session, from_room.id)
            except Exception:
                pass
        session.previous_room = from_room
        session.current_room = room
        self.server.world.add_player_to_room(session, room.id)
        if getattr(self.server, "db", None) and getattr(session, "character_id", None):
            self.server.db.save_character_room(session.character_id, room.id)
        if announce:
            await session.send_line(colorize(announce, TextPresets.SYSTEM))
        from server.core.commands.player.movement import cmd_look
        await cmd_look(session, "look", "", self.server)

    async def _send_service_help(self, session, jurisdiction_id: str | None = None, speaker: str | None = None):
        case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        state = _json_loads((case or {}).get("service_state_json"), {})
        task = self._task_for_case(case or {"jurisdiction_id": jurisdiction_id or self._resolve_jurisdiction_id(getattr(session, "current_room", None))}, state)
        if not task:
            text = "No active community-service task is recorded."
            if speaker:
                await session.send_line(npc_speech(speaker, f'says, "{text}"'))
            else:
                await session.send_line(text)
            return
        await session.send_line(f"Current service task: {task.get('label')}")
        await session.send_line(f"Assigned object: {task.get('object_name')}")
        await session.send_line(task.get("briefing") or "")
        await session.send_line(f"Inspect with INSPECT {task.get('object_name')}.")
        await session.send_line("Service verbs: " + ", ".join(v.upper() for v in (task.get("sequence") or [])))

    async def _enforce_banishment(self, session, now: datetime):
        del now
        room = getattr(session, "current_room", None)
        jurisdiction_id = self._resolve_jurisdiction_id(room)
        if not jurisdiction_id:
            return
        case = self._active_banishment_case(session, jurisdiction_id)
        live_case = self.get_active_case(session, jurisdiction_id=jurisdiction_id)
        if not case or (live_case and str(live_case.get("status") or "") in {"awaiting_sentence", "incarcerated", "service"}):
            return
        release_room_id = int(case.get("release_room_id") or self._release_room_for_jurisdiction(jurisdiction_id))
        if int(getattr(room, "id", 0) or 0) == release_room_id:
            return
        await session.send_line(colorize(f"You are banished from {self._display_jurisdiction(jurisdiction_id)} and are driven out.", TextPresets.WARNING))
        await self._move_session(session, release_room_id)

    def _jurisdiction_service_task(self, jurisdiction_id: str | None):
        jurisdiction = self._jurisdictions.get(str(jurisdiction_id or "").strip().lower(), {}) or {}
        tasks = list(jurisdiction.get("service_tasks") or [])
        return tasks[0] if tasks else None

    def _resolve_jurisdiction_id(self, room) -> str | None:
        if not room:
            return None
        room_id = int(getattr(room, "id", 0) or 0)
        if room_id in self._room_to_jurisdiction:
            return self._room_to_jurisdiction[room_id]
        fields = [
            getattr(room, "zone_name", None),
            getattr(room, "title", None),
            getattr(room, "location_name", None),
        ]
        combined = " ".join(str(v or "") for v in fields).strip().lower()
        for jurisdiction_id, row in self._jurisdictions.items():
            aliases = set(row.get("aliases") or []) | set(row.get("zone_aliases") or [])
            for alias in aliases:
                alias = _norm(alias)
                if alias and alias in _norm(combined):
                    return jurisdiction_id
        return None

    def _display_jurisdiction(self, jurisdiction_id: str | None) -> str:
        row = self._jurisdictions.get(str(jurisdiction_id or "").strip().lower(), {}) or {}
        return str(row.get("display_name") or str(jurisdiction_id or "Unknown Jurisdiction")).strip()

    def _courtroom_room_for_jurisdiction(self, jurisdiction_id: str | None) -> int:
        row = self._jurisdictions.get(str(jurisdiction_id or "").strip().lower(), {}) or {}
        return int(row.get("courtroom_room_id") or 0)

    def _jail_room_for_jurisdiction(self, jurisdiction_id: str | None) -> int:
        row = self._jurisdictions.get(str(jurisdiction_id or "").strip().lower(), {}) or {}
        return int(row.get("jail_room_id") or row.get("stockade_room_id") or 0)

    def _release_room_for_jurisdiction(self, jurisdiction_id: str | None) -> int:
        row = self._jurisdictions.get(str(jurisdiction_id or "").strip().lower(), {}) or {}
        return int(row.get("release_room_id") or row.get("clerk_room_id") or row.get("courtroom_room_id") or 0)

    def _active_banishment_case(self, session, jurisdiction_id: str | None):
        rows = self._query_dicts(
            """
            SELECT *
            FROM character_justice_cases
            WHERE character_id = %s
              AND jurisdiction_id = %s
              AND banishment_expires_at IS NOT NULL
              AND banishment_expires_at > NOW()
            ORDER BY banishment_expires_at DESC
            LIMIT 1
            """,
            (int(getattr(session, "character_id", 0) or 0), str(jurisdiction_id or "")),
        )
        return rows[0] if rows else None

    def _resolve_charge_code(self, text: str) -> str | None:
        key = _norm(text)
        if key in self._charge_defs:
            return key
        for charge_code, row in self._charge_defs.items():
            label = _norm(row.get("label"))
            if key == label:
                return charge_code
        aliases = {
            "disturbing peace": "disturbing_the_peace",
            "public safety": "endangering_public_safety",
            "endangering safety": "endangering_public_safety",
            "high crimes": "high_crimes_against_the_state",
        }
        return aliases.get(key)

    def _find_player_in_room(self, session, target_name: str):
        room = getattr(session, "current_room", None)
        if not room:
            return None
        needle = str(target_name or "").strip().lower()
        for other in self.server.world.get_players_in_room(room.id):
            if other is session:
                continue
            name = str(getattr(other, "character_name", "") or "").lower()
            if name == needle or name.startswith(needle):
                return other
        return None
