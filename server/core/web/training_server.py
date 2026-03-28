"""
training_server.py - Skill training web portal.

Runs a lightweight HTTP server on localhost:8765 in a background thread.
When a player types TRAIN with no arguments, the game generates a one-time
token, opens their browser to http://127.0.0.1:8765/train?token=XXX, and
the page logs them in automatically as their character.

No external dependencies — uses Python's built-in http.server.
"""

import threading
import json
import time
import uuid
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

log = logging.getLogger(__name__)

WEB_PORT  = 8765
TOKEN_TTL = 600  # 10 minutes


# ── Request Handler ────────────────────────────────────────────────────────────

class TrainingRequestHandler(BaseHTTPRequestHandler):

    server_ref = None  # set to GameServer instance on startup

    def log_message(self, format, *args):
        pass  # silence HTTP access log spam

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if parsed.path == '/train':
            self._serve_train_page(params)
        elif parsed.path == '/api/character':
            self._serve_character_data(params)
        else:
            self._send_html('<h1 style="color:#c94040">404</h1>', 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self._json_error('Invalid JSON', 400)
            return
        if parsed.path == '/api/save':
            self._handle_save(data)
        elif parsed.path == '/api/convert':
            self._handle_convert(data)
        elif parsed.path == '/api/fixstats':
            self._handle_fixstats(data)
        elif parsed.path == '/api/refund':
            self._handle_refund(data)
        else:
            self._send_html('<h1>404</h1>', 404)

    def _resolve_token(self, token_str):
        if not token_str:
            return None, 'No token provided'
        server = TrainingRequestHandler.server_ref
        tokens = getattr(server, 'training_tokens', {})
        entry  = tokens.get(token_str)
        if not entry:
            return None, 'Invalid or expired token — please type TRAIN again in-game'
        if time.time() > entry['expires']:
            del tokens[token_str]
            return None, 'Token expired — please type TRAIN again in-game'
        return entry['session'], None

    def _token_from_params(self, params):
        return params.get('token', [None])[0]

    def _serve_train_page(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._send_html(_error_page(err), 401)
            return
        self._send_html(_build_html(token), 200)

    def _serve_character_data(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return

        from server.core.commands.player.training import (
            SKILL_NAMES, SKILL_COSTS, SKILL_CATEGORIES,
            get_train_limit, get_max_ranks
        )

        prof_id = session.profession_id
        level   = session.level

        skills_out = {}
        for skill_id, name in SKILL_NAMES.items():
            raw   = (session.skills or {}).get(skill_id, {})
            ranks = int(raw.get('ranks', 0)) if isinstance(raw, dict) else 0
            bonus = int(raw.get('bonus', 0)) if isinstance(raw, dict) else 0
            ptp, mtp = SKILL_COSTS.get(skill_id, {}).get(prof_id, (0, 0))
            max_r    = get_max_ranks(skill_id, prof_id, level)
            limit    = get_train_limit(skill_id, prof_id)
            skills_out[skill_id] = {
                'name':       name,
                'ranks':      ranks,
                'bonus':      bonus,
                'ptp':        ptp,
                'mtp':        mtp,
                'trainable':  not (ptp == 0 and mtp == 0),
                'max_ranks':  max_r,   # total rank ceiling at current level
                'limit':      limit,   # ranks per level (for cost-doubling display)
            }

        import time as _time
        from server.core.commands.player.fixstat_convert import (
            STATS, _get_stat, _get_base_stat, _total_stats,
            _fixstat_uses_remaining, _fixstat_can_use_free, CONVERT_RATE
        )
        stats_out = {s: _get_stat(session, s) for s in STATS}
        base_stats_out = {s: _get_base_stat(session, s) for s in STATS}
        total_stats = _total_stats(session)
        fixstat_can, fixstat_reason = _fixstat_can_use_free(session)
        fixstat_uses = _fixstat_uses_remaining(session)

        self._json_response({
            'name':              session.character_name,
            'level':             level,
            'profession_id':     prof_id,
            'physical_tp':       session.physical_tp,
            'mental_tp':         session.mental_tp,
            'skills':            skills_out,
            'categories':        {cat: ids for cat, ids in SKILL_CATEGORIES.items()},
            'stats':             stats_out,
            'base_stats':        base_stats_out,
            'total_stats':       total_stats,
            'fixstat_can':       fixstat_can,
            'fixstat_reason':    fixstat_reason,
            'fixstat_uses':      fixstat_uses,
            'convert_rate':      CONVERT_RATE,
            'ptp_loaned':        getattr(session, 'ptp_loaned', 0),
            'mtp_loaned':        getattr(session, 'mtp_loaned', 0),
        })

    def _handle_save(self, data):
        token_str = data.get('token')
        server    = TrainingRequestHandler.server_ref
        tokens    = getattr(server, 'training_tokens', {})
        entry     = tokens.get(token_str) if token_str else None

        if not entry or time.time() > entry['expires']:
            self._json_error('Invalid or expired token', 401)
            return

        session = entry['session']
        desired = data.get('skills', {})
        prof_id = session.profession_id

        from server.core.commands.player.training import (
            SKILL_NAMES, SKILL_COSTS, calc_skill_bonus,
            get_train_limit, get_max_ranks, cost_for_rank_range
        )

        level   = session.level
        total_ptp = 0
        total_mtp = 0
        changes   = []
        cap_errors = []

        for skill_id_str, new_ranks in desired.items():
            skill_id  = int(skill_id_str)
            new_ranks = max(0, int(new_ranks))
            raw       = (session.skills or {}).get(skill_id, {})
            old_ranks = int(raw.get('ranks', 0)) if isinstance(raw, dict) else 0
            if new_ranks == old_ranks:
                continue
            ptp_per, mtp_per = SKILL_COSTS.get(skill_id, {}).get(prof_id, (0, 0))
            if ptp_per == 0 and mtp_per == 0:
                continue

            # ── Enforce total rank cap: max = train_limit × level ─────────────
            max_r = get_max_ranks(skill_id, prof_id, level)
            if new_ranks > max_r:
                name = SKILL_NAMES.get(skill_id, 'Skill {}'.format(skill_id))
                cap_errors.append(
                    '{}: requested {} ranks but cap is {} ({}x per level, level {})'.format(
                        name, new_ranks, max_r,
                        get_train_limit(skill_id, prof_id), level
                    )
                )
                continue

            # ── Cost uses slot-position doubling formula ───────────────────────
            # Only adds cost for ranks being purchased (delta > 0).
            # Untraining (delta < 0) refunds at a flat base rate.
            if new_ranks > old_ranks:
                limit   = get_train_limit(skill_id, prof_id) or 1
                rp, rm  = cost_for_rank_range(ptp_per, mtp_per, limit, level, old_ranks, new_ranks)
                total_ptp += rp
                total_mtp += rm
            else:
                # Untrain: refund flat base (no doubling on refunds)
                delta      = old_ranks - new_ranks
                total_ptp -= ptp_per * delta
                total_mtp -= mtp_per * delta

            changes.append((skill_id, old_ranks, new_ranks))

        if cap_errors:
            self._json_error('Rank cap exceeded:\n' + '\n'.join(cap_errors))
            return

        new_ptp = session.physical_tp - total_ptp
        new_mtp = session.mental_tp   - total_mtp

        if new_ptp < 0:
            self._json_error(
                'Not enough physical TPs (need {}, have {})'.format(total_ptp, session.physical_tp)
            )
            return
        if new_mtp < 0:
            self._json_error(
                'Not enough mental TPs (need {}, have {})'.format(total_mtp, session.mental_tp)
            )
            return

        change_lines = []
        for skill_id, old_ranks, new_ranks in changes:
            new_bonus = calc_skill_bonus(new_ranks)
            if not session.skills:
                session.skills = {}
            session.skills[skill_id] = {'ranks': new_ranks, 'bonus': new_bonus}
            if server.db and session.character_id:
                server.db.save_character_skill(
                    session.character_id, skill_id, new_ranks, new_bonus
                )
            name = SKILL_NAMES.get(skill_id, 'Skill {}'.format(skill_id))
            change_lines.append(
                '{}: {} \u2192 {} ranks  (bonus +{})'.format(name, old_ranks, new_ranks, new_bonus)
            )

        session.physical_tp = new_ptp
        session.mental_tp   = new_mtp

        if server.db and session.character_id:
            server.db.save_character_tps(session.character_id, new_ptp, new_mtp)

        if server._loop and change_lines:
            async def _notify():
                from server.core.protocol.colors import colorize, TextPresets
                await session.send_line('')
                await session.send_line(colorize(
                    '  *** Training Hall: your skills have been updated! ***',
                    TextPresets.EXPERIENCE
                ))
                for line in change_lines:
                    await session.send_line(colorize('  ' + line, TextPresets.EXPERIENCE))
                await session.send_line(colorize(
                    '  Remaining TPs: {} physical, {} mental'.format(
                        session.physical_tp, session.mental_tp
                    ),
                    TextPresets.SYSTEM
                ))
                await session.send_line('')
                await session.send_prompt()
            asyncio.run_coroutine_threadsafe(_notify(), server._loop)

        del tokens[token_str]

        self._json_response({
            'success':     True,
            'changes':     change_lines,
            'physical_tp': new_ptp,
            'mental_tp':   new_mtp,
        })

    def _handle_refund(self, data):
        token_str = data.get('token')
        server    = TrainingRequestHandler.server_ref
        tokens    = getattr(server, 'training_tokens', {})
        entry     = tokens.get(token_str) if token_str else None
        if not entry or time.time() > entry['expires']:
            self._json_error('Invalid or expired token', 401)
            return
        session    = entry['session']
        scope      = (data.get('scope') or 'all').lower()  # 'all', 'ptp', 'mtp'
        ptp        = getattr(session, 'physical_tp', 0)
        mtp        = getattr(session, 'mental_tp',   0)
        ptp_loaned = getattr(session, 'ptp_loaned',  0)
        mtp_loaned = getattr(session, 'mtp_loaned',  0)

        from server.core.commands.player.fixstat_convert import CONVERT_RATE

        do_ptp = scope in ('all', 'ptp')
        do_mtp = scope in ('all', 'mtp')

        # Validate sufficient TPs to return
        if do_ptp and ptp_loaned > 0 and ptp < ptp_loaned:
            self._json_error(
                f'PTP refund needs {ptp_loaned} PTP to return, but you only have {ptp}. '
                f'Try refunding MTP loan first, or train to recover more PTP.'
            )
            return
        if do_mtp and mtp_loaned > 0 and mtp < mtp_loaned:
            self._json_error(
                f'MTP refund needs {mtp_loaned} MTP to return, but you only have {mtp}. '
                f'Try refunding PTP loan first, or train to recover more MTP.'
            )
            return

        changes = []
        if do_ptp and ptp_loaned > 0:
            recovered = ptp_loaned * CONVERT_RATE
            session.physical_tp -= ptp_loaned
            session.mental_tp   += recovered
            session.ptp_loaned   = 0
            changes.append(f'PTP loan cleared: returned {ptp_loaned} PTP, recovered {recovered} MTP')
        if do_mtp and mtp_loaned > 0:
            recovered = mtp_loaned * CONVERT_RATE
            session.mental_tp   -= mtp_loaned
            session.physical_tp += recovered
            session.mtp_loaned   = 0
            changes.append(f'MTP loan cleared: returned {mtp_loaned} MTP, recovered {recovered} PTP')

        if not changes:
            self._json_error('No loans outstanding to refund')
            return

        if server.db and session.character_id:
            server.db.save_character_tps(
                session.character_id, session.physical_tp, session.mental_tp
            )
            server.db.save_convert_loans(
                session.character_id, session.ptp_loaned, session.mtp_loaned
            )

        if server._loop:
            async def _notify_refund():
                from server.core.protocol.colors import colorize, TextPresets
                await session.send_line('')
                await session.send_line(colorize(
                    '  *** Training Hall: conversion loan(s) refunded! ***',
                    TextPresets.EXPERIENCE
                ))
                for line in changes:
                    await session.send_line(colorize(f'  {line}', TextPresets.EXPERIENCE))
                await session.send_line(colorize(
                    f'  Remaining — Physical: {session.physical_tp}  Mental: {session.mental_tp}',
                    TextPresets.SYSTEM
                ))
                await session.send_line('')
                await session.send_prompt()
            asyncio.run_coroutine_threadsafe(_notify_refund(), server._loop)

        self._json_response({
            'success':     True,
            'changes':     changes,
            'physical_tp': session.physical_tp,
            'mental_tp':   session.mental_tp,
            'ptp_loaned':  session.ptp_loaned,
            'mtp_loaned':  session.mtp_loaned,
        })

    def _handle_convert(self, data):
        token_str = data.get('token')
        server    = TrainingRequestHandler.server_ref
        tokens    = getattr(server, 'training_tokens', {})
        entry     = tokens.get(token_str) if token_str else None
        if not entry or time.time() > entry['expires']:
            self._json_error('Invalid or expired token', 401)
            return
        session   = entry['session']
        direction = (data.get('direction') or '').lower()
        try:
            amount = int(data.get('amount', 0))
        except (ValueError, TypeError):
            self._json_error('Invalid amount', 400)
            return
        if direction not in ('ptp', 'mtp') or amount <= 0:
            self._json_error('Provide direction (ptp/mtp) and a positive amount', 400)
            return

        from server.core.commands.player.fixstat_convert import CONVERT_RATE
        cost = amount * CONVERT_RATE
        ptp  = getattr(session, 'physical_tp', 0)
        mtp  = getattr(session, 'mental_tp',   0)

        if direction == 'ptp':
            if mtp < cost:
                self._json_error(f'Not enough MTP (need {cost}, have {mtp})')
                return
            session.mental_tp   = mtp - cost
            session.physical_tp = ptp + amount
            session.ptp_loaned  = getattr(session, 'ptp_loaned', 0) + amount
            msg = f'Converted {cost} MTP → {amount} PTP'
        else:
            if ptp < cost:
                self._json_error(f'Not enough PTP (need {cost}, have {ptp})')
                return
            session.physical_tp = ptp - cost
            session.mental_tp   = mtp + amount
            session.mtp_loaned  = getattr(session, 'mtp_loaned', 0) + amount
            msg = f'Converted {cost} PTP → {amount} MTP'

        if server.db and session.character_id:
            server.db.save_character_tps(
                session.character_id, session.physical_tp, session.mental_tp
            )
            server.db.save_convert_loans(
                session.character_id,
                getattr(session, 'ptp_loaned', 0),
                getattr(session, 'mtp_loaned', 0),
            )

        if server._loop:
            async def _notify_convert():
                from server.core.protocol.colors import colorize, TextPresets
                await session.send_line('')
                await session.send_line(colorize(
                    f'  *** Training Hall: {msg} ***', TextPresets.EXPERIENCE
                ))
                await session.send_line(colorize(
                    f'  Remaining — Physical: {session.physical_tp}  Mental: {session.mental_tp}',
                    TextPresets.SYSTEM
                ))
                await session.send_line('')
                await session.send_prompt()
            asyncio.run_coroutine_threadsafe(_notify_convert(), server._loop)

        self._json_response({
            'success':     True,
            'message':     msg,
            'physical_tp': session.physical_tp,
            'mental_tp':   session.mental_tp,
            'ptp_loaned':  getattr(session, 'ptp_loaned', 0),
            'mtp_loaned':  getattr(session, 'mtp_loaned', 0),
        })

    def _handle_fixstats(self, data):
        token_str = data.get('token')
        server    = TrainingRequestHandler.server_ref
        tokens    = getattr(server, 'training_tokens', {})
        entry     = tokens.get(token_str) if token_str else None
        if not entry or time.time() > entry['expires']:
            self._json_error('Invalid or expired token', 401)
            return
        session  = entry['session']
        proposed = data.get('stats', {})  # {stat_name: int, ...}

        from server.core.commands.player.fixstat_convert import (
            STATS, _get_stat, _total_stats,
            _fixstat_can_use_free, _fixstat_consume
        )
        can, reason = _fixstat_can_use_free(session)
        if not can:
            self._json_error(reason)
            return

        current_total = _total_stats(session)
        new_vals = {}
        for s in STATS:
            try:
                val = int(proposed.get(s, _get_stat(session, s)))
            except (TypeError, ValueError):
                self._json_error(f'Invalid value for stat {s}', 400)
                return
            if not (1 <= val <= 130):
                self._json_error(f'Stat {s} must be between 1 and 130 (got {val})')
                return
            new_vals[s] = val

        new_total = sum(new_vals.values())
        if new_total != current_total:
            delta = new_total - current_total
            self._json_error(
                f'Total stat points must stay at {current_total}. '
                f'Your new total is {new_total} ({"+".join(str(delta)) if delta > 0 else str(delta)} off).'
            )
            return

        changes = []
        for s in STATS:
            old_val = _get_stat(session, s)
            new_val = new_vals[s]
            if new_val != old_val:
                setattr(session, f'stat_{s}', new_val)
                diff = new_val - old_val
                changes.append(f'{s.capitalize()}: {old_val} → {new_val} ({"+"+str(diff) if diff > 0 else str(diff)})')

        if not changes:
            self._json_error('No stats were changed')
            return

        _fixstat_consume(session, reason, server)

        if server.db and session.character_id:
            server.db.save_character_stats(session.character_id, session)

        level = getattr(session, 'level', 1)
        uses  = getattr(session, 'fixstat_uses_remaining', 0)
        if level < 20:
            uses_msg = f'{uses} free use(s) remaining before level 20'
        else:
            uses_msg = 'Next free reallocation available in 24 hours'

        if server._loop:
            async def _notify_fixstat():
                from server.core.protocol.colors import colorize, TextPresets
                await session.send_line('')
                await session.send_line(colorize(
                    '  *** Training Hall: stat reallocation applied! ***',
                    TextPresets.EXPERIENCE
                ))
                for line in changes:
                    await session.send_line(colorize(f'  {line}', TextPresets.EXPERIENCE))
                await session.send_line(colorize(f'  {uses_msg}', TextPresets.SYSTEM))
                await session.send_line('')
                await session.send_prompt()
            asyncio.run_coroutine_threadsafe(_notify_fixstat(), server._loop)

        self._json_response({
            'success':              True,
            'changes':              changes,
            'uses_msg':             uses_msg,
            'fixstat_uses':         uses,
            'stats':                {s: getattr(session, f'stat_{s}', 50) for s in STATS},
        })

    def _send_html(self, html, status=200):
        body = html.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',   'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',   'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, msg, status=400):
        self._json_response({'error': msg}, status)


# ── Skill tooltip data ─────────────────────────────────────────────────────────
# Plain Python dict serialized via json.dumps — no f-string brace issues.

_SKILL_INFO = {
    1:  {"d": "Wield a weapon in each hand simultaneously. Without training your off-hand strike rarely lands.",
         "m": "Strike chance ~20% untrained, 80%+ at 1 rank/lvl, 100% at 1.5 ranks/lvl. Off-hand AS: -25 penalty reduced by half your TWC bonus."},
    2:  {"d": "Reduces the action penalty of heavier armor, letting you move and fight more freely inside it.",
         "m": "Every 2 ranks removes 1 point of armor action penalty from both AS and DS."},
    3:  {"d": "Proficiency with shields of all sizes. Adds directly to your Defensive Strength.",
         "m": "Every 2 ranks = +1 DS on top of the shield base value."},
    4:  {"d": "Specialized combat techniques including feints, parries, and situational maneuvers that bolster your defense.",
         "m": "Every 4 ranks = +1 DS."},
    5:  {"d": "Mastery of swords, daggers, and all bladed weapons. Directly increases your Attack Strength.",
         "m": "Skill bonus / 3 added to AS. Bonus = ranks x 3 up to rank 40, then 120 + (ranks - 40)."},
    6:  {"d": "Proficiency with maces, hammers, clubs, and other crushing weapons.",
         "m": "Skill bonus / 3 added to AS. Same bonus curve as Edged Weapons."},
    7:  {"d": "Skill with greatswords, war mattocks, halberds, and other two-handed weapons.",
         "m": "Skill bonus / 3 added to AS. Two-handed weapons carry higher base damage factors."},
    8:  {"d": "Accuracy and power with bows, crossbows, and other ranged weapons.",
         "m": "Live for READY and FIRE. Uses ranged AS against ranged DS, consumes arrows or bolts, and supports aimed ranged shots."},
    9:  {"d": "Technique for hurling axes, daggers, javelins, and other projectiles with precision.",
         "m": "Live for HURL. Uses thrown AS against ranged DS and supports aimed thrown attacks."},
    10: {"d": "Fighting with spears, tridents, pikes, and other pole weapons. Long reach is their hallmark.",
         "m": "Skill bonus / 3 added to AS. Polearms have extended reach advantages."},
    11: {"d": "Unarmed combat covering punches, kicks, and grapples. Also governs brawling weapons.",
         "m": "Skill bonus / 3 added to AS when fighting empty-handed or with brawling weapons."},
    12: {"d": "The art of handling multiple opponents at once without being overwhelmed.",
         "m": "Live for MSTRIKE. Higher ranks increase the number of strikes you can spread across nearby foes."},
    13: {"d": "General conditioning that improves stamina and contributes to climbing endurance.",
         "m": "Ranks / 4 added as a secondary bonus to climbing checks."},
    14: {"d": "The ability to read attacks and move out of the way. Pure defensive value.",
         "m": "Skill bonus / 3 added to DS. Bonus = ranks x 3 up to rank 40."},
    15: {"d": "Knowledge of magical glyphs, runes, and symbols inscribed on scrolls and items.",
         "m": "Live for READ and INVOKE from scrolls with level-aware deciphering and activation checks."},
    16: {"d": "Activating wands, scrolls, and enchanted objects without formal spell training.",
         "m": "Supports charged item activation. Stronger ranks improve reliability with unfamiliar wands and rods."},
    17: {"d": "Accuracy when targeting creatures with bolt spells and directed magical attacks.",
         "m": "Live in the spell engine. Used for bolt attack resolution and related magical aim checks."},
    18: {"d": "The capacity to draw ambient mana from the environment and store it for casting.",
         "m": "Live in the mana engine. Increases max mana and feeds mana pool calculations."},
    19: {"d": "Fine control over elemental mana flows. Essential for wizards and sorcerers.",
         "m": "Live in the mana engine for regeneration, spell hooks, and mana sharing where elemental control applies."},
    20: {"d": "Fine control over spiritual mana. Essential for clerics, empaths, and paladins.",
         "m": "Live in the mana engine for regeneration, SEND mana transfers, and spiritual transference effects."},
    21: {"d": "Control over mental mana flows used by monks, bards, and mental lore specialists.",
         "m": "Live in the mana engine where mental mana control matters to regeneration, routing, and SEND support."},
    22: {"d": "Scholarly pursuit and memorization of new spells beyond your base circle.",
         "m": "Live in the spell engine. Governs which spell circles and spell ranks you can prepare and cast."},
    23: {"d": "Wilderness craft covering tracking, foraging, and the art of skinning creatures for their hides.",
         "m": "Skinning: 0 ranks falls back to level x 5 + 50 as base chance. Ranks x 3 improves it."},
    24: {"d": "Detecting and safely neutralizing mechanical traps on chests, doors, and containers.",
         "m": "Endroll = (ranks x 3 + DEX bonus) - trap difficulty + d100. Success if >= 100."},
    25: {"d": "Coaxing open locks without the original key. The bread and butter of any rogue.",
         "m": "Endroll = (ranks x 3 + DEX bonus) x pick quality - lock difficulty + d100."},
    26: {"d": "Moving unseen and melting into shadows. Drives your HIDE roll and your stealth-based ambush accuracy and weighting.",
         "m": "Hide: ranks x 3 + DISC bonus + prof bonus vs difficulty 100. Ambush tuning is loader-driven for hidden weighting, defense pushdown, and aimed strikes."},
    27: {"d": "Sharp awareness of your surroundings for spotting hidden creatures, traps, and passages.",
         "m": "Live for stealth detection, hidden-exit SEARCH checks, and forage awareness bonuses. Trap perception is still lighter than retail."},
    28: {"d": "Scaling walls, cliffs, ladders, and grates. Without training vertical travel is treacherous.",
         "m": "Endroll = d100 + ranks x 3 + (PF ranks / 4) + DEX bonus - encumbrance vs difficulty."},
    29: {"d": "Moving through water without drowning. Required for water rooms and some crossings.",
         "m": "Live for SWIM exits. Uses a swimming maneuver check influenced by Swimming, Physical Fitness, stats, encumbrance, and armor."},
    30: {"d": "Tending wounds with bandages and herbs to reduce injury severity after combat.",
         "m": "Success = min(90%, 40% + ranks x 3 / 2). Each success lowers wound severity by 1."},
    31: {"d": "The merchant's art covering haggling, appraisal, and knowing when the price is right.",
         "m": "Each rank = 0.2% discount buying and 0.2% bonus selling. Hard cap of 15% each way."},
    32: {"d": "Lifting coin purses and small items from NPCs and other players without being noticed.",
         "m": "Live for STEAL. Current first pass focuses on coin-purse theft, with stronger item theft still to come."},
    33: {"d": "Knowledge of spiritual blessings covering warding spells, protective prayers, and holy shields.",
         "m": "Lore training exists, but most spell-specific blessings hooks are still being expanded."},
    34: {"d": "Theological knowledge of the Arkati pantheon and their divine practices.",
         "m": "Lore training exists, but religion-specific spell bonuses are still limited in the current build."},
    35: {"d": "The art of summoning spirits, elementals, and other entities to serve your will.",
         "m": "Lore training exists, but deeper summoning interactions remain future-facing for many spells."},
    36: {"d": "Mastery of air-based elemental lore covering wind, lightning, and movement magic.",
         "m": "Lore training exists, but only a small number of air-lore spell hooks are currently wired."},
    37: {"d": "Mastery of earth-based elemental lore covering stone, metal, and endurance magic.",
         "m": "Lore training exists, but most earth-lore spell scaling is still to be expanded."},
    38: {"d": "Mastery of fire-based elemental lore covering flame, heat, and destruction magic.",
         "m": "Lore training exists, but most fire-lore spell scaling is still to be expanded."},
    39: {"d": "Mastery of water-based elemental lore covering ice, tides, and healing magic.",
         "m": "Lore training exists, but most water-lore spell scaling is still to be expanded."},
    40: {"d": "Mental lore focused on influencing and bending the will of others.",
         "m": "Live spell hooks currently improve Confusion and other mental control effects."},
    41: {"d": "Mental lore focused on mind-to-mind communication and reading surface thoughts.",
         "m": "Live spell hooks currently strengthen Mindward and related mental defenses."},
    42: {"d": "Mental lore focused on transferring energy to drain foes and bolster allies.",
         "m": "Live spell hooks currently improve Powersink and other mana-transfer effects."},
    43: {"d": "The dedicated skill for aimed attacks from hiding and lethal precision strikes.",
         "m": "Live for AMBUSH through the Lua-driven ambush profile and combat engine aimed-strike math."},
    44: {"d": "Mental lore concerned with foresight, omens, and predictive insight.",
         "m": "Live spell hooks currently improve Foresight and Premonition."},
    45: {"d": "Mental lore concerned with reshaping the body through force of will.",
         "m": "Live spell hooks currently improve Mind over Body and related self-alteration effects."},
    46: {"d": "Sorcerous lore focused on demonic entities, planar bargains, and summoning.",
         "m": "Live spell hooks currently improve Minor Summoning and sorcerous shadow defenses."},
    47: {"d": "Sorcerous lore focused on undeath, corpses, and gravebound power.",
         "m": "Live spell hooks currently improve Animate Dead, Grasp of the Grave, and related necromantic effects."},
}

_SKILL_INFO_JS = "const SKILL_INFO = " + json.dumps(_SKILL_INFO, ensure_ascii=False) + ";"


# ── HTML helpers ───────────────────────────────────────────────────────────────

def _error_page(msg):
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8">'
        '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&display=swap" rel="stylesheet">'
        '<style>body{background:#0d0b08;color:#c94040;font-family:Cinzel,serif;'
        'display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}</style>'
        '</head><body><div>'
        '<h1 style="font-size:1.4rem;margin-bottom:1rem">Access Denied</h1>'
        '<p style="color:#8a6e30;font-size:1rem">' + msg + '</p>'
        '</div></body></html>'
    )


# Raw string so regex patterns in the JS don't trigger SyntaxWarnings.
# TOKEN_PLACEHOLDER and SKILL_INFO_PLACEHOLDER are replaced at serve time
# using plain str.replace() — no f-string involved.
_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Training Hall</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0d0b08; --surface:#161210; --surface2:#1e1914; --surface3:#251f18;
  --border:#3d2e1a; --border-hi:#6b4f2a;
  --gold:#c9a84c; --gold-dim:#8a6e30;
  --parchment:#ddc89a; --parchment2:#b09b72; --muted:#6b5c42;
  --green:#5a9e5a; --green-dim:#3a6e3a;
  --red:#b84040; --red-dim:#7a2828; --amber:#c9842c; --blue:#4a8ec2;
}
body{background:var(--bg);color:var(--parchment);font-family:'Crimson Text',Georgia,serif;font-size:17px;line-height:1.5;min-height:100vh;}
header{background:var(--surface);border-bottom:1px solid var(--border);padding:0.9rem 2rem;display:flex;align-items:center;gap:1.5rem;position:sticky;top:0;z-index:100;}
.logo{font-family:'Cinzel',serif;font-size:1.4rem;font-weight:600;color:var(--gold);letter-spacing:0.06em;white-space:nowrap;}
.char-badge{color:var(--parchment2);font-size:0.95rem;border-left:1px solid var(--border);padding-left:1.2rem;}
.tp-bar{margin-left:auto;display:flex;align-items:center;gap:1.2rem;}
.tp-block{text-align:right}
.tp-label{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;font-family:'Cinzel',serif;}
.tp-val{font-family:'Cinzel',serif;font-size:1.5rem;font-weight:600;line-height:1.1;transition:color 0.2s;}
.ok{color:var(--green)}.low{color:var(--amber)}.over{color:var(--red)}
.header-btn{font-family:'Cinzel',serif;font-size:0.8rem;font-weight:600;letter-spacing:0.05em;background:transparent;border:1px solid var(--border);padding:0.4rem 1rem;cursor:pointer;transition:all 0.15s;white-space:nowrap;}
.header-btn.stats-btn{color:var(--blue);border-color:var(--blue);}
.header-btn.stats-btn:hover{background:var(--blue);color:var(--bg);}
.header-btn.conv-btn{color:var(--amber);border-color:var(--amber);}
.header-btn.conv-btn:hover{background:var(--amber);color:var(--bg);}
.save-btn{font-family:'Cinzel',serif;font-size:0.95rem;font-weight:600;letter-spacing:0.06em;background:transparent;color:var(--gold);border:1px solid var(--gold);padding:0.55rem 1.6rem;cursor:pointer;transition:all 0.15s;white-space:nowrap;}
.save-btn:hover:not(:disabled){background:var(--gold);color:var(--bg)}
.save-btn:disabled{opacity:0.3;cursor:not-allowed}
main{max-width:920px;margin:0 auto;padding:2rem 1.5rem 5rem;}
.cat{margin-bottom:2.5rem}
.cat-title{font-family:'Cinzel',serif;font-size:0.78rem;font-weight:600;letter-spacing:0.14em;color:var(--gold-dim);text-transform:uppercase;border-bottom:1px solid var(--border);padding-bottom:0.35rem;margin-bottom:0.5rem;}
.sk-head{display:grid;grid-template-columns:1fr 70px 70px 50px 50px 90px 120px;gap:0.5rem;padding:0.2rem 0.6rem 0.35rem;font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-family:'Cinzel',serif;border-bottom:1px solid var(--surface3);margin-bottom:0.15rem;}
.sk-row{display:grid;grid-template-columns:1fr 70px 70px 50px 50px 90px 120px;align-items:center;gap:0.5rem;padding:0.4rem 0.6rem;border-radius:2px;border-left:2px solid transparent;transition:background 0.1s;cursor:default;}
.sk-row:hover{background:var(--surface2)}.sk-row.changed{background:#1b1608;border-left-color:var(--gold-dim)}.sk-row.untrained{opacity:0.38}
.sk-name{color:var(--parchment);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sk-name.mod{color:var(--gold);font-weight:600}.sk-name.dim{color:var(--muted)}
.sk-ranks{font-family:'Cinzel',serif;font-size:1rem;font-weight:600;color:var(--parchment2);text-align:center;}.sk-ranks.mod{color:var(--gold)}
.sk-bonus{text-align:center;color:var(--muted);font-size:0.88rem}
.sk-cost{text-align:center;font-size:0.85rem;color:var(--muted)}.sk-cost.act{color:var(--amber)}
.controls{display:flex;align-items:center;gap:0.3rem;justify-content:flex-end}
.btn{width:26px;height:26px;background:var(--surface2);border:1px solid var(--border);color:var(--parchment2);font-size:1.1rem;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.1s;border-radius:2px;line-height:1;flex-shrink:0;}
.btn:hover{border-color:var(--border-hi);background:var(--surface)}.btn:active{transform:scale(0.93)}.btn:disabled{opacity:0.2;cursor:not-allowed}
.btn.minus{color:var(--red-dim)}.btn.minus:hover{color:var(--red);border-color:var(--red-dim)}
.btn.plus{color:var(--green-dim)}.btn.plus:hover{color:var(--green);border-color:var(--green-dim)}
.rk-input{width:36px;background:var(--surface);border:1px solid var(--border);color:var(--parchment);text-align:center;font-family:'Cinzel',serif;font-size:0.92rem;padding:2px 0;border-radius:2px;-moz-appearance:textfield;}
.rk-input::-webkit-inner-spin-button{display:none}.rk-input:focus{outline:none;border-color:var(--border-hi)}
/* ── Generic overlay ── */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.82);z-index:200;align-items:center;justify-content:center;}
.overlay.show{display:flex}
.modal{background:var(--surface);border:1px solid var(--border-hi);padding:2rem 2.2rem;max-width:540px;width:94%;max-height:90vh;overflow-y:auto;}
.modal-title{font-family:'Cinzel',serif;font-size:1.15rem;font-weight:600;color:var(--gold);letter-spacing:0.05em;margin-bottom:1.2rem;}
.modal-body{font-size:0.97rem;line-height:1.9;color:var(--parchment2);padding:0.9rem 1rem;background:var(--surface2);border:1px solid var(--border);margin-bottom:1.2rem;}
.chg{color:var(--gold)}.modal-foot{text-align:right;display:flex;gap:0.7rem;justify-content:flex-end;}
.close-btn{font-family:'Cinzel',serif;font-size:0.88rem;background:transparent;color:var(--parchment2);border:1px solid var(--border);padding:0.4rem 1.3rem;cursor:pointer;transition:all 0.15s;}
.close-btn:hover{background:var(--surface2);color:var(--parchment)}
.modal-save-btn{font-family:'Cinzel',serif;font-size:0.88rem;font-weight:600;background:transparent;border:1px solid var(--gold);color:var(--gold);padding:0.4rem 1.4rem;cursor:pointer;transition:all 0.15s;}
.modal-save-btn:hover:not(:disabled){background:var(--gold);color:var(--bg)}.modal-save-btn:disabled{opacity:0.3;cursor:not-allowed;}
.modal-save-btn.blue{border-color:var(--blue);color:var(--blue)}.modal-save-btn.blue:hover:not(:disabled){background:var(--blue);color:var(--bg)}
.spinner{display:inline-block;width:12px;height:12px;border:2px solid var(--border);border-top-color:var(--gold);border-radius:50%;animation:spin 0.7s linear infinite;vertical-align:middle;margin-right:6px;}
@keyframes spin{to{transform:rotate(360deg)}}
/* ── Stat grid (fixstats modal) ── */
.stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1.5rem;margin-bottom:1rem;}
.stat-row{display:flex;align-items:center;gap:0.4rem;}
.stat-label{font-family:'Cinzel',serif;font-size:0.8rem;color:var(--parchment2);width:100px;flex-shrink:0;}
.stat-stepper{display:flex;align-items:center;gap:0;background:var(--surface);border:1px solid var(--border);border-radius:2px;overflow:hidden;}
.stat-step-btn{width:28px;height:32px;background:transparent;border:none;color:var(--parchment2);font-size:1.1rem;font-weight:700;cursor:pointer;transition:all 0.12s;display:flex;align-items:center;justify-content:center;flex-shrink:0;user-select:none;}
.stat-step-btn:hover:not(:disabled){background:var(--surface2);color:var(--parchment);}
.stat-step-btn:active:not(:disabled){background:var(--surface3);}
.stat-step-btn:disabled{opacity:0.2;cursor:not-allowed;}
.stat-step-btn.minus:hover:not(:disabled){color:var(--red);}
.stat-step-btn.plus:hover:not(:disabled){color:var(--green);}
.stat-val{font-family:'Cinzel',serif;font-size:0.95rem;font-weight:600;color:var(--parchment);text-align:center;width:36px;padding:0 2px;line-height:32px;}
.stat-val.changed{color:var(--gold);}
.stat-sep{width:1px;height:32px;background:var(--border);flex-shrink:0;}
.stat-bonus{font-size:0.72rem;color:var(--blue);margin-left:2px;font-family:'Cinzel',serif;white-space:nowrap;}
.stat-total-val{font-size:0.72rem;color:var(--muted);white-space:nowrap;}
.stat-total-row{font-family:'Cinzel',serif;font-size:0.85rem;margin-top:0.4rem;padding:0.4rem 0.6rem;background:var(--surface2);border:1px solid var(--border);display:flex;justify-content:space-between;}
.stat-total-ok{color:var(--green)}.stat-total-over{color:var(--red)}.stat-total-under{color:var(--amber)}
.stat-avail-msg{font-size:0.85rem;margin-bottom:1rem;padding:0.5rem 0.7rem;border:1px solid var(--border);background:var(--surface2);}
/* ── Convert modal ── */
.conv-info{font-family:'Cinzel',serif;font-size:0.82rem;color:var(--muted);margin-bottom:1rem;padding:0.5rem 0.7rem;background:var(--surface2);border:1px solid var(--border);}
.conv-row{display:flex;align-items:center;gap:0.8rem;margin-bottom:0.9rem;flex-wrap:wrap;}
.conv-label{font-family:'Cinzel',serif;font-size:0.82rem;color:var(--parchment2);width:160px;flex-shrink:0;}
.conv-input{width:80px;background:var(--surface);border:1px solid var(--border);color:var(--parchment);text-align:center;font-family:'Cinzel',serif;font-size:1rem;padding:3px 4px;border-radius:2px;-moz-appearance:textfield;}
.conv-input::-webkit-inner-spin-button{display:none}.conv-input:focus{outline:none;border-color:var(--amber)}
.conv-cost{font-size:0.85rem;color:var(--muted);}
.conv-divider{border:none;border-top:1px solid var(--border);margin:0.8rem 0;}
/* ── Tooltip ── */
.tt{position:fixed;z-index:500;max-width:300px;background:var(--surface);border:1px solid var(--border-hi);padding:0.85rem 1rem;pointer-events:none;opacity:0;transition:opacity 0.15s;box-shadow:0 6px 28px rgba(0,0,0,0.8);}
.tt.show{opacity:1}
.tt-name{font-family:'Cinzel',serif;font-size:0.82rem;font-weight:600;color:var(--gold);letter-spacing:0.05em;margin-bottom:0.45rem;}
.tt-desc{font-size:0.95rem;color:var(--parchment2);line-height:1.55;margin-bottom:0.55rem;}
.tt-math{font-size:0.8rem;color:var(--muted);font-style:italic;border-top:1px solid var(--border);padding-top:0.45rem;line-height:1.6;}
.tt-math b{color:var(--gold-dim);font-style:normal;font-weight:600;}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo">Training Hall</div>
    <div class="char-badge" id="char-badge">Loading...</div>
  </div>
  <div class="tp-bar">
    <div class="tp-block"><div class="tp-label">Physical TPs</div><div class="tp-val ok" id="ptp">&#8212;</div></div>
    <div class="tp-block"><div class="tp-label">Mental TPs</div><div class="tp-val ok" id="mtp">&#8212;</div></div>
    <button class="header-btn stats-btn" id="stats-modal-btn" onclick="openStatsModal()" title="Reallocate stat points">&#9878; Stats</button>
    <button class="header-btn conv-btn" id="conv-modal-btn" onclick="openConvModal()" title="Convert PTP &#8596; MTP">&#8646; Convert</button>
    <button class="save-btn" id="save-btn" onclick="doSave()" disabled>Save Skills</button>
  </div>
</header>

<main id="main"><p style="color:var(--muted);font-style:italic;margin-top:2rem">Consulting the scrolls...</p></main>

<!-- ── Skill save result overlay ── -->
<div class="overlay" id="skill-overlay">
  <div class="modal">
    <div class="modal-title" id="skill-m-title">Training Complete</div>
    <div class="modal-body" id="skill-m-body"></div>
    <div class="modal-foot"><button class="close-btn" onclick="closeSkillModal()">Close</button></div>
  </div>
</div>

<!-- ── Stat Reallocation modal ── -->
<div class="overlay" id="stats-overlay">
  <div class="modal" style="max-width:600px;">
    <div class="modal-title">&#9878; Stat Reallocation</div>
    <div class="stat-avail-msg" id="fixstat-avail"></div>
    <div class="stat-total-row">
      <span>Total stat points</span>
      <span id="stat-total-display" class="stat-total-ok">&#8212;</span>
    </div>
    <br>
    <div class="stat-grid" id="stat-grid"><!-- filled by JS --></div>
    <div class="modal-foot">
      <button class="close-btn" onclick="closeStatsModal()">Cancel</button>
      <button class="modal-save-btn blue" id="fixstat-save-btn" onclick="doFixstatSave()">Apply Stats</button>
    </div>
  </div>
</div>

<!-- ── Convert TPs modal ── -->
<div class="overlay" id="conv-overlay">
  <div class="modal" style="max-width:440px;">
    <div class="modal-title">&#8646; Convert Training Points</div>
    <div class="conv-info" id="conv-info">Loading...</div>
    <div class="conv-row">
      <div class="conv-label">Gain PTP<br><small style="color:var(--muted);">(costs 2x MTP)</small></div>
      <input type="number" class="conv-input" id="conv-ptp-amount" min="1" placeholder="0" oninput="updateConvCost('ptp')">
      <span class="conv-cost" id="conv-ptp-cost"></span>
    </div>
    <hr class="conv-divider">
    <div class="conv-row">
      <div class="conv-label">Gain MTP<br><small style="color:var(--muted);">(costs 2x PTP)</small></div>
      <input type="number" class="conv-input" id="conv-mtp-amount" min="1" placeholder="0" oninput="updateConvCost('mtp')">
      <span class="conv-cost" id="conv-mtp-cost"></span>
    </div>
    <div class="modal-body" id="conv-result" style="display:none;margin-top:0.8rem;"></div>
    <div class="modal-foot" style="margin-top:1rem;flex-wrap:wrap;gap:0.5rem;">
      <button class="close-btn" onclick="closeConvModal()">Close</button>
      <button class="modal-save-btn" id="conv-refund-all-btn" onclick="doRefund('all')" style="display:none;border-color:var(--red);color:var(--red);" title="Losslessly undo ALL conversions">↶ Refund All</button>
      <button class="modal-save-btn" id="conv-refund-ptp-btn" onclick="doRefund('ptp')" style="display:none;border-color:var(--red-dim);color:var(--red-dim);font-size:0.78rem;" title="Refund PTP loan only">↶ Refund PTP</button>
      <button class="modal-save-btn" id="conv-refund-mtp-btn" onclick="doRefund('mtp')" style="display:none;border-color:var(--red-dim);color:var(--red-dim);font-size:0.78rem;" title="Refund MTP loan only">↶ Refund MTP</button>
      <button class="modal-save-btn" id="conv-ptp-btn" onclick="doConvert('ptp')" style="border-color:var(--blue);color:var(--blue);" title="Spend MTP, gain PTP">Convert → PTP</button>
      <button class="modal-save-btn" id="conv-mtp-btn" onclick="doConvert('mtp')" style="border-color:var(--amber);color:var(--amber);" title="Spend PTP, gain MTP">Convert → MTP</button>
    </div>
  </div>
</div>

<div class="tt" id="tt"><div class="tt-name" id="tt-name"></div><div class="tt-desc" id="tt-desc"></div><div class="tt-math" id="tt-math"></div></div>

<script>
const TOKEN='TOKEN_PLACEHOLDER';
let char=null,pending={};
SKILL_INFO_PLACEHOLDER

/* ── Skill bonus formula ── */
function bonus(r){if(r<=0)return 0;if(r<=40)return r*3;return 120+(r-40);}

/* ── Initial load ── */
async function load(){
  try{
    const r=await fetch('/api/character?token='+TOKEN);
    char=await r.json();
    if(char.error){mainErr(char.error);return;}
    render();
    initStatsModal();
    initConvModal();
  }catch(e){mainErr('Could not connect to game server.');}
}

/* ════════════════════════════════════════════════════
   SKILL TRAINING
   ════════════════════════════════════════════════════ */
function render(){
  document.getElementById('char-badge').textContent=char.name+' \u00b7 Level '+char.level;
  refreshTP();
  const main=document.getElementById('main');main.innerHTML='';
  const preferredOrder = ['Combat', 'Magic', 'Survival', 'General', 'Lore'];
  const orderedCats = [];
  for(const cat of preferredOrder){
    if(char.categories && Object.prototype.hasOwnProperty.call(char.categories, cat)){
      orderedCats.push([cat, char.categories[cat]]);
    }
  }
  for(const [cat, ids] of Object.entries(char.categories || {})){
    if(!preferredOrder.includes(cat)) orderedCats.push([cat, ids]);
  }
  for(const[cat,ids]of orderedCats){
    const sec=document.createElement('div');sec.className='cat';
    sec.innerHTML='<div class="cat-title">'+cat+'</div><div class="sk-head"><span>Skill</span><span style="text-align:center">Ranks</span><span style="text-align:center">Bonus</span><span style="text-align:center">PTP</span><span style="text-align:center">MTP</span><span style="text-align:center">Rnk/Cap</span><span></span></div>';
    for(const id of ids){const sk=char.skills[id];if(sk)sec.appendChild(mkRow(id,sk));}
    main.appendChild(sec);
  }
}
function mkRow(id,sk){
  const cur=pending[id]!==undefined?pending[id]:sk.ranks;
  const changed=cur!==sk.ranks,empty=cur===0;
  const atCap=sk.max_ranks>0&&cur>=sk.max_ranks;
  const row=document.createElement('div');
  row.className='sk-row'+(changed?' changed':'')+(!sk.trainable&&empty?' untrained':'');
  row.id='row-'+id;
  row.innerHTML=
    '<div class="sk-name'+(changed?' mod':empty&&!sk.trainable?' dim':'')+'\" id="nm-'+id+'">'+sk.name+'</div>'+
    '<div class="sk-ranks'+(changed?' mod':'')+'\" id="rk-'+id+'">'+cur+'</div>'+
    '<div class="sk-bonus" id="bn-'+id+'">+'+bonus(cur)+'</div>'+
    '<div class="sk-cost'+(sk.ptp?' act':'')+'\" id="cp-'+id+'">'+( sk.ptp?slotCost(sk.ptp,sk.limit||1,char.level,cur,cur+1):'\u2014')+'</div>'+
    '<div class="sk-cost'+(sk.mtp?' act':'')+'\" id="cm-'+id+'">'+( sk.mtp?slotCost(sk.mtp,sk.limit||1,char.level,cur,cur+1):'\u2014')+'</div>'+
    '<div class="sk-cost" id="cap-'+id+'" style="text-align:center;color:'+(atCap?'var(--amber)':'var(--muted)')+'">'+(sk.max_ranks>0?cur+'/'+sk.max_ranks:'\u2014')+'</div>'+
    '<div class="controls" id="ct-'+id+'"></div>';
  const ct=row.querySelector('#ct-'+id);
  if(sk.trainable){
    const m=document.createElement('button');m.className='btn minus';m.textContent='\u2212';m.title='Remove rank';m.onclick=()=>adj(id,-1);
    const inp=document.createElement('input');inp.type='number';inp.className='rk-input';inp.id='inp-'+id;inp.value=cur;inp.min=0;inp.max=sk.max_ranks>0?sk.max_ranks:9999;inp.onchange=()=>setRk(id,parseInt(inp.value)||0);inp.oninput=()=>setRk(id,parseInt(inp.value)||0);
    const p=document.createElement('button');p.className='btn plus';p.textContent='+';p.title='Add rank (cap: '+sk.max_ranks+')';p.onclick=()=>adj(id,1);
    ct.appendChild(m);ct.appendChild(inp);ct.appendChild(p);
  }else{ct.innerHTML='<span style="color:var(--muted);font-size:0.8rem">N/A</span>';}
  ttAttach(row,id);
  return row;
}
function adj(id,d){const cur=pending[id]!==undefined?pending[id]:char.skills[id].ranks;setRk(id,Math.max(0,cur+d));}
function setRk(id,v){
  const sk=char.skills[id];v=Math.max(0,v);
  if(sk.max_ranks>0&&v>sk.max_ranks){v=sk.max_ranks;}
  if(v===sk.ranks)delete pending[id];else pending[id]=v;
  const inp=document.getElementById('inp-'+id);if(inp&&parseInt(inp.value)!==v)inp.value=v;
  const rkEl=document.getElementById('rk-'+id);if(rkEl){rkEl.textContent=v;rkEl.className='sk-ranks'+(v!==sk.ranks?' mod':'');}
  const bnEl=document.getElementById('bn-'+id);if(bnEl)bnEl.textContent='+'+bonus(v);
  const lim=sk.limit||1;
  const cpEl=document.getElementById('cp-'+id);if(cpEl&&sk.ptp)cpEl.textContent=slotCost(sk.ptp,lim,char.level,v,v+1);
  const cmEl=document.getElementById('cm-'+id);if(cmEl&&sk.mtp)cmEl.textContent=slotCost(sk.mtp,lim,char.level,v,v+1);
  const nmEl=document.getElementById('nm-'+id);if(nmEl)nmEl.className='sk-name'+(v!==sk.ranks?' mod':v===0&&!sk.trainable?' dim':'');
  const row=document.getElementById('row-'+id);if(row)row.classList.toggle('changed',v!==sk.ranks);
  const capEl=document.getElementById('cap-'+id);if(capEl){const atCap=sk.max_ranks>0&&v>=sk.max_ranks;capEl.textContent=v+'/'+sk.max_ranks;capEl.style.color=atCap?'var(--amber)':'var(--muted)';}
  refreshTP();
}
function slotCost(base,limit,level,fromRank,toRank){
  if(limit<=0)limit=1;const prevCap=limit*(level-1);let t=0;
  for(let r=fromRank+1;r<=toRank;r++){const sp=r<=prevCap?1:Math.min(r-prevCap,2);t+=base*sp;}return t;
}
function tpDelta(){
  let p=0,m=0;
  for(const[s,v]of Object.entries(pending)){
    const id=parseInt(s);const sk=char.skills[id];const lim=sk.limit||1;
    if(v>sk.ranks){p+=slotCost(sk.ptp,lim,char.level,sk.ranks,v);m+=slotCost(sk.mtp,lim,char.level,sk.ranks,v);}
    else{const d=sk.ranks-v;p-=sk.ptp*d;m-=sk.mtp*d;}
  }
  return[p,m];
}
function refreshTP(){
  if(!char)return;
  const[dp,dm]=tpDelta(),rp=char.physical_tp-dp,rm=char.mental_tp-dm;
  const pEl=document.getElementById('ptp'),mEl=document.getElementById('mtp');
  pEl.textContent=rp;mEl.textContent=rm;
  pEl.className='tp-val '+(rp<0?'over':rp<5?'low':'ok');
  mEl.className='tp-val '+(rm<0?'over':rm<5?'low':'ok');
  document.getElementById('save-btn').disabled=Object.keys(pending).length===0||rp<0||rm<0;
}
async function doSave(){
  const btn=document.getElementById('save-btn');btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Saving...';
  const skills={};for(const[s,sk]of Object.entries(char.skills)){const id=parseInt(s);skills[id]=pending[id]!==undefined?pending[id]:sk.ranks;}
  try{
    const res=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,skills})});
    const result=await res.json();
    if(result.error){showSkillModal('Error','<span style="color:var(--red)">'+result.error+'</span>',true);btn.disabled=false;btn.textContent='Save Skills';return;}
    let html='';
    if(result.changes&&result.changes.length)result.changes.forEach(l=>html+='<div class="chg">\u2756 '+l+'</div>');else html='No changes recorded.';
    html+='<hr style="border:none;border-top:1px solid var(--border);margin:0.9rem 0">';
    html+='Physical TPs: <strong style="color:var(--gold)">'+result.physical_tp+'</strong>&nbsp;&nbsp;Mental TPs: <strong style="color:var(--gold)">'+result.mental_tp+'</strong>';
    showSkillModal('Training Complete',html,false);
    char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
    for(const[s,v]of Object.entries(pending)){const id=parseInt(s);char.skills[id].ranks=v;char.skills[id].bonus=bonus(v);}
    pending={};btn.textContent='Save Skills';
  }catch(e){showSkillModal('Error','<span style="color:var(--red)">Could not reach game server.</span>',true);btn.disabled=false;btn.textContent='Save Skills';}
}
function showSkillModal(title,body,isErr){
  document.getElementById('skill-m-title').textContent=title;
  document.getElementById('skill-m-title').style.color=isErr?'var(--red)':'var(--gold)';
  document.getElementById('skill-m-body').innerHTML=body;
  document.getElementById('skill-overlay').classList.add('show');
}
function closeSkillModal(){document.getElementById('skill-overlay').classList.remove('show');render();}

/* ════════════════════════════════════════════════════
   STAT REALLOCATION MODAL
   ════════════════════════════════════════════════════ */
const STAT_NAMES=['strength','constitution','dexterity','agility','discipline','aura','logic','intuition','wisdom','influence'];
const STAT_LABELS={strength:'Strength',constitution:'Constitution',dexterity:'Dexterity',agility:'Agility',discipline:'Discipline',aura:'Aura',logic:'Logic',intuition:'Intuition',wisdom:'Wisdom',influence:'Influence'};
const STAT_BASE_CAP=130;
const STAT_STEP=5;
let statDraft={};

function _statBonus(s){return 0;}  // bonus tracking deferred — stats rewrite pending
function _totalBonuses(){return 0;}
function _totalDraftExcept(s){let t=0;for(const n of STAT_NAMES)if(n!==s)t+=statDraft[n];return t;}

function initStatsModal(){
  const grid=document.getElementById('stat-grid');grid.innerHTML='';
  for(const s of STAT_NAMES){
    const baseVal=Math.min(char.base_stats[s]||50, STAT_BASE_CAP);
    statDraft[s]=baseVal;
    let bonusHtml='';
    const div=document.createElement('div');div.className='stat-row';
    // Use data-s attribute to avoid all quoting issues in onclick
    div.innerHTML=
      '<div class="stat-label">'+STAT_LABELS[s]+'</div>'+
      '<div class="stat-stepper" id="stepper-'+s+'">'+
        '<button class="stat-step-btn minus" id="sminus-'+s+'" data-s="'+s+'" onclick="stepStat(this.dataset.s,false)" title="Decrease by 5">\u2212</button>'+
        '<div class="stat-sep"></div>'+
        '<div class="stat-val" id="sval-'+s+'">'+baseVal+'</div>'+
        '<div class="stat-sep"></div>'+
        '<button class="stat-step-btn plus" id="splus-'+s+'" data-s="'+s+'" onclick="stepStat(this.dataset.s,true)" title="Increase by 5">+</button>'+
      '</div>'+
      bonusHtml+
      '<span style="font-size:0.78rem;margin-left:4px;" id="sd-'+s+'"></span>';
    grid.appendChild(div);
    _refreshStatButtons(s);
  }
  updateStatTotal();
  const avail=document.getElementById('fixstat-avail');
  if(char.fixstat_can){
    avail.innerHTML=char.level<20
      ?'<span style="color:var(--green);">\u2714 '+char.fixstat_uses+' free use'+(char.fixstat_uses===1?'':'s')+' remaining (before level 20)</span>'
      :'<span style="color:var(--green);">\u2714 Free reallocation available (1 per 24 hours after level 20)</span>';
  }else{
    avail.innerHTML='<span style="color:var(--amber);">\u26a0 '+char.fixstat_reason+'</span>';
    document.getElementById('fixstat-save-btn').disabled=true;
  }
}

function stepStat(s,increase){
  const current=statDraft[s];
  const budget=char.total_stats-_totalBonuses();
  const spentElsewhere=_totalDraftExcept(s);
  let v=increase?current+STAT_STEP:current-STAT_STEP;
  v=Math.max(1,Math.min(STAT_BASE_CAP,v));
  if(increase){
    const remaining=budget-spentElsewhere;
    if(v>remaining)v=remaining;
    if(v<=current)return;
  }
  if(v===current)return;
  statDraft[s]=v;
  _refreshStat(s);
  updateStatTotal();
}

function _refreshStat(s){
  const v=statDraft[s];
  const base=char.base_stats[s]||50;
  const diff=v-base;
  const valEl=document.getElementById('sval-'+s);
  if(valEl){valEl.textContent=v;valEl.className='stat-val'+(v!==base?' changed':'');}
  const dEl=document.getElementById('sd-'+s);
  if(dEl){dEl.textContent=diff===0?'':(diff>0?'+'+diff:''+diff);dEl.style.color=diff>0?'var(--green)':diff<0?'var(--red)':'var(--muted)';}
  _refreshStatButtons(s);
}

function _refreshStatButtons(s){
  const v=statDraft[s];
  const budget=char.total_stats-_totalBonuses();
  const spentElsewhere=_totalDraftExcept(s);
  const remaining=budget-spentElsewhere;
  const mb=document.getElementById('sminus-'+s);
  const pb=document.getElementById('splus-'+s);
  if(mb)mb.disabled=(v<=1);
  if(pb)pb.disabled=(v>=STAT_BASE_CAP||v>=remaining);
}

function updateStatTotal(){
  const bonusTotal=_totalBonuses();
  const baseDraftTotal=Object.values(statDraft).reduce((a,b)=>a+b,0);
  const budget=char.total_stats-bonusTotal;
  const el=document.getElementById('stat-total-display');
  el.textContent=baseDraftTotal+' / '+budget;
  const ok=(baseDraftTotal===budget);
  el.className=ok?'stat-total-ok':(baseDraftTotal>budget?'stat-total-over':'stat-total-under');
  document.getElementById('fixstat-save-btn').disabled=!ok||!char.fixstat_can;
  for(const s of STAT_NAMES)_refreshStatButtons(s);
}
function openStatsModal(){
  if(!char){return;}
  initStatsModal();
  document.getElementById('stats-overlay').classList.add('show');
}
function closeStatsModal(){document.getElementById('stats-overlay').classList.remove('show');}
async function doFixstatSave(){
  const btn=document.getElementById('fixstat-save-btn');
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Applying...';
  try{
    const res=await fetch('/api/fixstats',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,stats:statDraft})});
    const result=await res.json();
    if(result.error){
      alert('\u26a0 '+result.error);btn.disabled=false;btn.textContent='Apply Stats';return;
    }
    // Update local char stats
    for(const s of STAT_NAMES)char.stats[s]=statDraft[s];
    char.fixstat_uses=result.fixstat_uses;
    if(result.fixstat_uses===0&&char.level<20)char.fixstat_can=false;
    let msg='<div style="margin-bottom:0.5rem;color:var(--green);font-family:Cinzel,serif">Stats updated!</div>';
    result.changes.forEach(l=>msg+='<div class="chg">\u2756 '+l+'</div>');
    msg+='<div style="margin-top:0.6rem;color:var(--muted);font-size:0.85rem">'+result.uses_msg+'</div>';
    const body=document.getElementById('skill-m-body');body.innerHTML=msg;
    document.getElementById('skill-m-title').textContent='Stat Reallocation Complete';
    document.getElementById('skill-m-title').style.color='var(--blue)';
    document.getElementById('skill-overlay').classList.add('show');
    closeStatsModal();
    btn.textContent='Apply Stats';
  }catch(e){alert('Could not reach game server.');btn.disabled=false;btn.textContent='Apply Stats';}
}

/* ════════════════════════════════════════════════════
   CONVERT TP MODAL
   ════════════════════════════════════════════════════ */
function initConvModal(){
  const rate=char.convert_rate||2;
  const pl=char.ptp_loaned||0, ml=char.mtp_loaned||0;
  let loanHtml='';
  if(pl>0||ml>0){
    loanHtml='<div style="margin-top:0.5rem;padding:0.4rem 0.6rem;border:1px solid var(--amber);background:var(--surface);font-size:0.85rem;">';
    loanHtml+='<span style="color:var(--amber);font-family:Cinzel,serif;font-size:0.75rem;">OUTSTANDING LOANS</span>';
    if(pl>0)loanHtml+='<br><span style="color:var(--amber)">PTP loan: '+pl+' PTP borrowed (refund: return '+pl+' PTP, recover '+(pl*rate)+' MTP)</span>';
    if(ml>0)loanHtml+='<br><span style="color:var(--amber)">MTP loan: '+ml+' MTP borrowed (refund: return '+ml+' MTP, recover '+(ml*rate)+' PTP)</span>';
    loanHtml+='</div>';
  }
  document.getElementById('conv-info').innerHTML=
    'Current TPs &mdash; Physical: <strong style="color:var(--green)" id="cv-ptp">'+char.physical_tp+'</strong>&nbsp;&nbsp;'+
    'Mental: <strong style="color:var(--green)" id="cv-mtp">'+char.mental_tp+'</strong>'+
    '<br><span style="color:var(--muted)">Exchange rate: '+rate+' → 1 (both directions)</span>'+loanHtml;
  document.getElementById('conv-ptp-amount').value='';
  document.getElementById('conv-mtp-amount').value='';
  document.getElementById('conv-ptp-cost').textContent='';
  document.getElementById('conv-mtp-cost').textContent='';
  // Show/hide refund buttons based on loan balances
  const refundAll=document.getElementById('conv-refund-all-btn');
  const refundPtp=document.getElementById('conv-refund-ptp-btn');
  const refundMtp=document.getElementById('conv-refund-mtp-btn');
  if(refundAll)refundAll.style.display=(pl>0||ml>0)?'inline-block':'none';
  if(refundPtp)refundPtp.style.display=pl>0?'inline-block':'none';
  if(refundMtp)refundMtp.style.display=ml>0?'inline-block':'none';
  const res=document.getElementById('conv-result');res.style.display='none';res.innerHTML='';
}
function updateConvCost(dir){
  const rate=char.convert_rate||2;
  if(dir==='ptp'){
    const v=parseInt(document.getElementById('conv-ptp-amount').value)||0;
    const cost=v*rate;
    document.getElementById('conv-ptp-cost').textContent=v>0?'costs '+cost+' MTP':'';
  }else{
    const v=parseInt(document.getElementById('conv-mtp-amount').value)||0;
    const cost=v*rate;
    document.getElementById('conv-mtp-cost').textContent=v>0?'costs '+cost+' PTP':'';
  }
}
function openConvModal(){if(!char)return;initConvModal();document.getElementById('conv-overlay').classList.add('show');}
function closeConvModal(){document.getElementById('conv-overlay').classList.remove('show');}
async function doRefund(scope){
  const btn=document.getElementById('conv-refund-all-btn');
  if(btn){btn.disabled=true;btn.innerHTML='<span class="spinner"></span>';}
  try{
    const res=await fetch('/api/refund',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,scope:scope||'all'})});
    const result=await res.json();
    const resBox=document.getElementById('conv-result');
    if(result.error){
      resBox.style.display='block';resBox.innerHTML='<span style="color:var(--red)">⚠ '+result.error+'</span>';
    }else{
      char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
      char.ptp_loaned=result.ptp_loaned||0;char.mtp_loaned=result.mtp_loaned||0;
      document.getElementById('ptp').textContent=result.physical_tp;
      document.getElementById('mtp').textContent=result.mental_tp;
      let html='';
      result.changes.forEach(l=>html+='<div style="color:var(--green)">✔ '+l+'</div>');
      html+='<span style="color:var(--muted);font-size:0.88rem">Physical: '+result.physical_tp+'&nbsp;&nbsp;Mental: '+result.mental_tp+'</span>';
      resBox.style.display='block';resBox.innerHTML=html;
      initConvModal();  // refresh loan display + hide refund buttons if loans cleared
    }
    if(btn){btn.disabled=false;btn.textContent='Refund All';}
  }catch(e){
    alert('Could not reach game server.');
    if(btn){btn.disabled=false;btn.textContent='Refund All';}
  }
}
async function doConvert(dir){
  const amtEl=document.getElementById('conv-'+dir+'-amount');
  const amount=parseInt(amtEl.value)||0;
  if(amount<=0){alert('Enter a positive amount to convert.');return;}
  const btnId='conv-'+dir+'-btn';const btn=document.getElementById(btnId);
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>';
  try{
    const res=await fetch('/api/convert',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,direction:dir,amount})});
    const result=await res.json();
    const resBox=document.getElementById('conv-result');
    if(result.error){
      resBox.style.display='block';resBox.innerHTML='<span style="color:var(--red)">\u26a0 '+result.error+'</span>';
    }else{
      char.physical_tp=result.physical_tp;char.mental_tp=result.mental_tp;
      if(result.ptp_loaned!==undefined)char.ptp_loaned=result.ptp_loaned;
      if(result.mtp_loaned!==undefined)char.mtp_loaned=result.mtp_loaned;
      document.getElementById('cv-ptp').textContent=result.physical_tp;
      document.getElementById('cv-mtp').textContent=result.mental_tp;
      document.getElementById('ptp').textContent=result.physical_tp;
      document.getElementById('mtp').textContent=result.mental_tp;
      resBox.style.display='block';
      resBox.innerHTML='<span style="color:var(--green)">\u2714 '+result.message+'</span>'+
        '<br><span style="color:var(--muted);font-size:0.88rem">Physical: '+result.physical_tp+'&nbsp;&nbsp;Mental: '+result.mental_tp+'</span>';
      amtEl.value='';
      updateConvCost(dir);
      initConvModal();
    }
    btn.disabled=false;btn.textContent=dir==='ptp'?'Convert \u2192 PTP':'Convert \u2192 MTP';
  }catch(e){alert('Could not reach game server.');btn.disabled=false;btn.textContent=dir==='ptp'?'Convert \u2192 PTP':'Convert \u2192 MTP';}
}

/* ════════════════════════════════════════════════════
   TOOLTIP
   ════════════════════════════════════════════════════ */
const _tt=document.getElementById('tt'),_ttN=document.getElementById('tt-name'),_ttD=document.getElementById('tt-desc'),_ttM=document.getElementById('tt-math');
let _ttT=null,_ttOn=false;
function _ttShow(id,x,y){
  const info=SKILL_INFO[id];if(!info)return;
  const sk=char&&char.skills[id];
  _ttN.textContent=sk?sk.name:'Skill '+id;_ttD.textContent=info.d;
  _ttM.innerHTML=info.m.replace(/([\d]+ ?[x\/] ?[\d]+|~?[\d]+%|>= ?[\d]+|[\d]+ ?ranks?|\bmin\b|\bmax\b|d100|\bAS\b|\bDS\b|\bDEX\b|\bDISC\b|\bPF\b|\bPTP\b|\bMTP\b)/g,'<b>$1</b>');
  _ttOn=true;_ttPos(x,y);_tt.classList.add('show');
}
function _ttPos(x,y){
  const W=window.innerWidth,H=window.innerHeight,tw=_tt.offsetWidth||300,th=_tt.offsetHeight||130;
  let lx=x+18,ly=y+18;
  if(lx+tw>W-8)lx=x-tw-8;if(ly+th>H-8)ly=y-th-8;
  _tt.style.left=Math.max(4,lx)+'px';_tt.style.top=Math.max(4,ly)+'px';
}
document.addEventListener('mousemove',e=>{if(_ttOn)_ttPos(e.clientX,e.clientY);});
function ttAttach(el,id){
  el.addEventListener('mouseenter',e=>{clearTimeout(_ttT);_ttT=setTimeout(()=>_ttShow(id,e.clientX,e.clientY),900);});
  el.addEventListener('mouseleave',()=>{clearTimeout(_ttT);_tt.classList.remove('show');_ttOn=false;});
}

/* ── Close overlays on Escape ── */
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'));
  }
});

load();
</script>
</body>
</html>"""


def _build_html(token):
    """Inject token and skill data into the HTML template."""
    return (
        _HTML_TEMPLATE
        .replace('TOKEN_PLACEHOLDER',      token)
        .replace('SKILL_INFO_PLACEHOLDER', _SKILL_INFO_JS)
    )


# ── Public class ───────────────────────────────────────────────────────────────

class TrainingWebServer:
    """Manages the background HTTP server for the training portal."""

    def __init__(self, game_server, port=WEB_PORT):
        self.game_server = game_server
        self.port        = port
        self._httpd      = None
        self._thread     = None

    def start(self):
        TrainingRequestHandler.server_ref = self.game_server
        self.game_server.training_tokens  = {}
        self._httpd  = HTTPServer(('0.0.0.0', self.port), TrainingRequestHandler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, daemon=True, name='TrainingWebServer'
        )
        self._thread.start()
        log.info("Training web portal: http://127.0.0.1:%d", self.port)

    def generate_token(self, session):
        token = str(uuid.uuid4())
        self.game_server.training_tokens[token] = {
            'session': session,
            'expires': time.time() + TOKEN_TTL,
        }
        return token

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
