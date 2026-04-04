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
import re
from typing import Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

log = logging.getLogger(__name__)

WEB_PORT  = 8765
TOKEN_TTL = 600  # 10 minutes


_WT_CATEGORY_LABELS = {
    'brawling': 'Brawling',
    'blunt': 'Blunt Weapons',
    'edged': 'Edged Weapons',
    'polearm': 'Polearm Weapons',
    'ranged': 'Ranged Weapons',
    'twohanded': 'Two-Handed Weapons',
}

_WT_GEAR_LABELS = {
    'both_hands': 'Both hands committed',
    'right_hand': 'Right-hand weapon',
}


def _wt_profession_key(session, server) -> str:
    explicit = getattr(session, 'profession_name', None) or getattr(session, 'profession', None)
    if explicit:
        return str(explicit).strip().lower()
    lua = getattr(server, 'lua', None)
    if not lua:
        return ''
    try:
        professions = (lua.get_professions() or {}).get('professions', [])
        prof_id = int(getattr(session, 'profession_id', 0) or 0)
        for row in professions:
            if int(row.get('id', 0) or 0) == prof_id:
                name = str(row.get('name') or '').strip().lower()
                if name:
                    return name
    except Exception:
        pass
    return ''


def _wt_compute_max_rank(skill_ranks: int, thresholds: list[int]) -> int:
    max_rank = 0
    for idx, threshold in enumerate(thresholds or [], start=1):
        if skill_ranks >= int(threshold or 0):
            max_rank = idx
    return max_rank


def _wt_normalize_category(raw: str) -> str:
    key = str(raw or '').strip().lower().replace('-', '_').replace(' ', '_')
    if key in ('two_handed', 'twohanded_weapons', 'two_handed_weapons'):
        return 'twohanded'
    if key in ('blunt_weapons',):
        return 'blunt'
    if key in ('edged_weapons',):
        return 'edged'
    if key in ('polearm_weapons',):
        return 'polearm'
    if key in ('ranged_weapons',):
        return 'ranged'
    return key


def _wt_current_weapon_categories(session) -> set[str]:
    categories: set[str] = set()
    hands = [getattr(session, 'right_hand', None), getattr(session, 'left_hand', None)]
    has_non_brawling_weapon = False
    for item in hands:
        if not item or item.get('item_type') != 'weapon':
            continue
        category = _wt_normalize_category(item.get('weapon_category') or item.get('weapon_type') or '')
        if not category:
            continue
        categories.add(category)
        if category != 'brawling':
            has_non_brawling_weapon = True
    if not has_non_brawling_weapon:
        categories.add('brawling')
    return categories


def _wt_command_syntax(tech: dict[str, Any]) -> str:
    mnemonic = str(tech.get('mnemonic') or '').strip().lower()
    kind = str(tech.get('type') or '').strip().lower()
    limbs = tech.get('valid_limbs') or []
    if kind == 'aoe':
        return f"WEAPON {mnemonic}"
    if limbs:
        return f"WEAPON {mnemonic} <target> <limb>"
    return f"WEAPON {mnemonic} <target>"


def _wt_unlock_reason(learned_rank: int, skill_ranks: int, min_ranks: int, profession_ok: bool, loadout_ok: bool, loadout_msg: str) -> str:
    if not profession_ok:
        return "Your profession cannot learn this technique."
    if learned_rank > 0:
        return ""
    if skill_ranks < min_ranks:
        needed = max(0, min_ranks - skill_ranks)
        return f"Need {needed} more weapon-skill rank{'s' if needed != 1 else ''} to unlock rank 1."
    if not loadout_ok and loadout_msg:
        return loadout_msg
    return "Your current training qualifies for this technique, but it has not been granted yet."


def _wt_room_targets(session, server) -> list[str]:
    room = getattr(session, 'current_room', None)
    room_id = getattr(room, 'id', None) if room else None
    if room_id is None:
        return []
    targets = []
    try:
        creatures = getattr(server, 'creatures', None)
        if creatures:
            for creature in creatures.get_creatures_in_room(int(room_id)) or []:
                if getattr(creature, 'is_alive', True):
                    name = getattr(creature, 'full_name', None) or getattr(creature, 'name', None)
                    if name:
                        targets.append(str(name))
    except Exception:
        pass
    deduped = []
    seen = set()
    for target in targets:
        key = target.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(target)
    return deduped


def _build_weapon_state(session, server) -> dict[str, Any]:
    lua = getattr(server, 'lua', None)
    if not lua or not lua.engine:
        return {'error': 'Weapon technique system unavailable.'}

    from server.core.scripting.lua_bindings.weapon_api import (
        _get_skill_ranks,
        _normalize_weapon_skill_key,
        _validate_technique_loadout,
    )

    try:
        defs_lua = lua.engine.require("weapon_techniques/definitions")
        defs = lua.engine.lua_to_python(defs_lua) if defs_lua else {}
    except Exception as e:
        log.error("Training weapon tab: Lua definitions load failed: %s", e, exc_info=True)
        return {'error': 'Could not load weapon techniques.'}

    profession_key = _wt_profession_key(session, server)
    learned = dict(getattr(session, 'weapon_techniques', {}) or {})
    cooldowns = dict(getattr(session, 'technique_cooldowns', {}) or {})
    now = int(time.time())
    current_categories = _wt_current_weapon_categories(session)
    techniques = []

    for mnemonic, tech in (defs or {}).items():
        if not isinstance(tech, dict):
            continue
        if str(mnemonic).startswith('_'):
            continue
        canonical = str(tech.get('mnemonic') or mnemonic).strip().lower()
        if canonical != str(mnemonic).strip().lower():
            continue

        category_key = str(tech.get('category') or '').strip().lower()
        skill_key = _normalize_weapon_skill_key(str(tech.get('weapon_skill') or category_key).strip().lower())
        thresholds = [int(x or 0) for x in (tech.get('rank_thresholds') or [])]
        if not thresholds:
            thresholds = [int(tech.get('min_ranks', 0) or 0), 35, 60, 85, 110]
        skill_ranks = _get_skill_ranks(session, skill_key)
        max_rank = _wt_compute_max_rank(skill_ranks, thresholds)
        learned_rank = int(learned.get(canonical, 0) or 0)
        available_to = [str(v).strip().lower() for v in (tech.get('available_to') or [])]
        profession_ok = profession_key in available_to if available_to else True
        loadout_ok, loadout_msg = _validate_technique_loadout(session, tech)
        cooldown_remaining = max(0, int(cooldowns.get(canonical, 0) or 0) - now)
        min_ranks = int((thresholds[0] if thresholds else tech.get('min_ranks', 0)) or 0)

        if not profession_ok:
            availability = 'profession_locked'
        elif learned_rank > 0:
            availability = 'learned'
        elif skill_ranks >= min_ranks:
            availability = 'available'
        else:
            availability = 'locked'

        techniques.append({
            'mnemonic': canonical,
            'name': str(tech.get('name') or canonical).strip(),
            'category': category_key,
            'category_label': _WT_CATEGORY_LABELS.get(category_key, category_key.title()),
            'type': str(tech.get('type') or '').strip().lower(),
            'weapon_skill': skill_key,
            'weapon_skill_label': skill_key.replace('_', ' ').title(),
            'description': str(tech.get('description') or '').strip(),
            'mechanics_notes': str(tech.get('mechanics_notes') or '').strip(),
            'stamina_cost': int(tech.get('stamina_cost', 0) or 0),
            'cooldown': int(tech.get('cooldown', 0) or 0),
            'cooldown_remaining': cooldown_remaining,
            'base_rt': int(tech.get('base_rt', 0) or 0),
            'rt_mod': int(tech.get('rt_mod', 0) or 0),
            'reaction_trigger': str(tech.get('reaction_trigger') or '').strip(),
            'gear_requirement': str(tech.get('offensive_gear') or '').strip().lower(),
            'gear_requirement_label': _WT_GEAR_LABELS.get(str(tech.get('offensive_gear') or '').strip().lower(), ''),
            'available_to': available_to,
            'profession_ok': profession_ok,
            'skill_ranks': skill_ranks,
            'min_ranks': min_ranks,
            'rank_thresholds': thresholds,
            'learned_rank': learned_rank,
            'max_rank': max_rank,
            'availability': availability,
            'loadout_ok': bool(loadout_ok),
            'loadout_message': str(loadout_msg or ''),
            'valid_limbs': [str(v) for v in (tech.get('valid_limbs') or [])],
            'is_aoe': str(tech.get('type') or '').strip().lower() == 'aoe',
            'requires_target': str(tech.get('type') or '').strip().lower() != 'aoe',
            'command_syntax': _wt_command_syntax({'mnemonic': canonical, 'type': tech.get('type'), 'valid_limbs': tech.get('valid_limbs') or []}),
            'unlock_reason': _wt_unlock_reason(learned_rank, skill_ranks, min_ranks, profession_ok, loadout_ok, loadout_msg),
            'current_weapon_match': category_key in current_categories,
        })

    type_order = {'setup': 0, 'assault': 1, 'reaction': 2, 'aoe': 3, 'concentration': 4}
    techniques.sort(key=lambda row: (row['category_label'], type_order.get(row['type'], 9), row['min_ranks'], row['name']))

    ready_now = [
        row for row in techniques
        if row['current_weapon_match']
        and row['profession_ok']
        and row['learned_rank'] > 0
        and row['loadout_ok']
        and row['cooldown_remaining'] <= 0
    ]
    unlock_path = [
        row for row in techniques
        if row['current_weapon_match']
        and row['profession_ok']
        and row['learned_rank'] == 0
    ]

    assault_state = dict(getattr(session, 'weapon_assault_state', {}) or {})
    active_assault = {
        'active': bool(assault_state),
        'mnemonic': str(assault_state.get('mnemonic') or ''),
        'target': str(assault_state.get('target_name') or ''),
    }

    return {
        'stamina': int(getattr(session, 'stamina_current', getattr(session, 'stamina', 0)) or 0),
        'roundtime': int(session.get_roundtime()) if hasattr(session, 'get_roundtime') else 0,
        'targets': _wt_room_targets(session, server),
        'active_assault': active_assault,
        'current_categories': sorted(current_categories),
        'ready_now': ready_now,
        'unlock_path': unlock_path,
    }


def _cm_category_label(meta: dict[str, Any]) -> str:
    raw = str(meta.get('raw_category') or '').strip()
    if raw:
        return raw
    category = str(meta.get('category') or 'general').strip().replace('_', ' ')
    return category.title()


def _cm_unlock_reason(meta: dict[str, Any], direct_rank: int, max_rank: int, next_cost: int, free_points: int, profession_ok: bool) -> str:
    if meta.get('is_guild_skill'):
        return 'Guild-trained maneuver.'
    if not meta.get('is_learnable', True):
        return 'Not directly trainable.'
    if not profession_ok:
        return 'Profession locked.'
    if direct_rank >= max_rank:
        return 'Mastered.'
    if next_cost <= 0:
        return 'No additional ranks available.'
    if next_cost > free_points:
        needed = next_cost - free_points
        return f'Need {needed} more CMAN point{"s" if needed != 1 else ""}.'
    return f'Rank {direct_rank + 1} is available now.'


def _cm_current_loadout(session) -> dict[str, Any]:
    hands = [getattr(session, 'right_hand', None), getattr(session, 'left_hand', None)]
    categories = _wt_current_weapon_categories(session)
    return {
        'weapon_categories': categories,
        'has_weapon': any(item and item.get('item_type') == 'weapon' for item in hands),
        'has_shield': any(item and item.get('item_type') == 'shield' for item in hands),
    }


def _cm_weapon_loadout_match(meta: dict[str, Any], loadout: dict[str, Any]) -> bool:
    requirements = str(meta.get('requirements') or '').strip().lower()
    if not requirements:
        return True

    categories = set(loadout.get('weapon_categories') or set())
    required: set[str] = set()
    excluded: set[str] = set()
    require_shield = False

    if 'polearms cannot be used' in requirements:
        excluded.add('polearm')
    if 'not twohanded' in requirements or 'not two-handed' in requirements:
        excluded.add('twohanded')
    if 'closed fist attacks' in requirements:
        excluded.add('brawling')

    if 'quarterstaff' in requirements or re.search(r'\bstaff\b', requirements):
        required.add('twohanded')
    if 'polearm' in requirements and 'polearms cannot be used' not in requirements:
        required.add('polearm')
    if 'two-handed weapon' in requirements or 'two handed weapon' in requirements or 'twohanded weapon' in requirements:
        required.add('twohanded')
    if 'slashing weapon' in requirements:
        required.add('edged')
    if 'brawling weapon' in requirements or 'empty right hand' in requirements or 'bare-handed' in requirements:
        required.add('brawling')

    if 'requires a shield' in requirements or 'require a shield' in requirements:
        require_shield = True

    if require_shield and not bool(loadout.get('has_shield')):
        return False
    if required and not (categories & required):
        return False
    if excluded and (categories & excluded):
        return False
    return True


def _cm_passive_summary(session, server) -> list[str]:
    from server.core.scripting.lua_bindings.combat_maneuver_api import get_passive_combat_mods

    passive = get_passive_combat_mods(session, server)
    lines = []
    if int(passive.get('as_bonus', 0) or 0):
        lines.append(f"+{int(passive['as_bonus'])} AS")
    if int(passive.get('ds_bonus', 0) or 0):
        lines.append(f"+{int(passive['ds_bonus'])} DS")
    if int(passive.get('td_bonus', 0) or 0):
        lines.append(f"+{int(passive['td_bonus'])} TD")
    if int(passive.get('smr_def_bonus', 0) or 0):
        lines.append(f"+{int(passive['smr_def_bonus'])} SMR defense")
    if int(passive.get('hp_bonus', 0) or 0):
        lines.append(f"+{int(passive['hp_bonus'])} max HP")
    if int(passive.get('evade_pct_bonus', 0) or 0):
        lines.append(f"+{int(passive['evade_pct_bonus'])}% evade")
    if int(passive.get('parry_pct_bonus', 0) or 0):
        lines.append(f"+{int(passive['parry_pct_bonus'])}% parry")
    if int(passive.get('block_pct_bonus', 0) or 0):
        lines.append(f"+{int(passive['block_pct_bonus'])}% block")
    if passive.get('auto_stand'):
        lines.append('Combat Mobility active')
    return lines


def _build_cman_state(session, server) -> dict[str, Any]:
    from server.core.scripting.lua_bindings.combat_maneuver_api import (
        _available_cman_points,
        _combat_defs,
        _effective_maneuver_rank,
        _profession_allowed,
        _spent_cman_points,
    )

    defs = _combat_defs(server)
    if not defs:
        return {'error': 'Combat maneuver system unavailable.'}

    learned = dict(getattr(session, 'combat_maneuvers', {}) or {})
    free_points = int(_available_cman_points(session, server) or 0)
    spent_points = int(_spent_cman_points(session, server) or 0)
    total_points = free_points + spent_points
    loadout = _cm_current_loadout(session)
    maneuvers = []

    for mnemonic, meta in (defs or {}).items():
        if str(mnemonic).startswith('_') or not isinstance(meta, dict):
            continue
        canonical = str(meta.get('mnemonic') or mnemonic).strip().lower()
        if canonical != str(mnemonic).strip().lower():
            continue

        direct_rank = int(learned.get(canonical, 0) or 0)
        effective_rank = int(_effective_maneuver_rank(session, canonical, meta) or 0)
        max_rank = int(meta.get('max_rank', 1) or 1)
        costs = [int(v or 0) for v in (meta.get('rank_costs') or [])]
        next_cost = costs[direct_rank] if direct_rank < len(costs) else 0
        profession_ok = bool(_profession_allowed(session, server, meta))
        is_guild_skill = bool(meta.get('is_guild_skill'))
        is_learnable = bool(meta.get('is_learnable', True))
        loadout_ok = _cm_weapon_loadout_match(meta, loadout)

        if is_guild_skill:
            availability = 'guild'
        elif not is_learnable:
            availability = 'special'
        elif not profession_ok:
            availability = 'profession_locked'
        elif direct_rank >= max_rank:
            availability = 'mastered'
        elif next_cost > 0 and next_cost <= free_points:
            availability = 'available'
        else:
            availability = 'locked'

        row = {
            'mnemonic': canonical,
            'name': str(meta.get('name') or canonical.title()).strip(),
            'type': str(meta.get('type') or '').strip().lower(),
            'type_label': str(meta.get('raw_type') or str(meta.get('type') or '').replace('_', ' ').title()).strip(),
            'category': str(meta.get('category') or '').strip().lower(),
            'category_label': _cm_category_label(meta),
            'description': str(meta.get('description') or '').strip(),
            'mechanics': str(meta.get('mechanics') or '').strip(),
            'requirements': str(meta.get('requirements') or '').strip(),
            'targeting': str(meta.get('targeting') or 'none').strip().lower(),
            'targeting_label': str(meta.get('targeting') or 'none').strip().replace('_', ' ').title(),
            'roundtime': str(meta.get('roundtime') or '').strip(),
            'stamina': str(meta.get('stamina') or '').strip(),
            'direct_rank': direct_rank,
            'effective_rank': effective_rank,
            'max_rank': max_rank,
            'rank_costs': costs,
            'next_cost': int(next_cost or 0),
            'is_guild_skill': is_guild_skill,
            'is_learnable': is_learnable,
            'profession_ok': profession_ok,
            'loadout_ok': loadout_ok,
            'availability': availability,
            'can_learn': bool(
                not is_guild_skill
                and is_learnable
                and profession_ok
                and loadout_ok
                and direct_rank < max_rank
                and next_cost > 0
                and next_cost <= free_points
            ),
            'can_unlearn': bool(not is_guild_skill and direct_rank > 0),
            'status_text': _cm_unlock_reason(meta, direct_rank, max_rank, next_cost, free_points, profession_ok),
        }
        if direct_rank > 0 or loadout_ok:
            maneuvers.append(row)

    category_order = {'general': 0, 'warrior_guild': 1, 'rogue_guild': 2}
    type_order = {'passive': 0, 'buff': 1, 'martial_stance': 2, 'setup': 3, 'attack': 4, 'aoe': 5, 'concentration': 6}
    maneuvers.sort(
        key=lambda row: (
            category_order.get(row['category'], 9),
            row['category_label'],
            type_order.get(row['type'], 9),
            row['name'],
        )
    )

    return {
        'free_points': free_points,
        'spent_points': spent_points,
        'total_points': total_points,
        'trained_count': sum(1 for row in maneuvers if int(row.get('direct_rank', 0) or 0) > 0),
        'available_count': sum(1 for row in maneuvers if row.get('can_learn')),
        'granted_count': sum(1 for row in maneuvers if int(row.get('effective_rank', 0) or 0) > 0),
        'passive_summary': _cm_passive_summary(session, server),
        'maneuvers': maneuvers,
    }


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
        elif parsed.path == '/api/weapon':
            self._serve_weapon_data(params)
        elif parsed.path == '/api/cman':
            self._serve_cman_data(params)
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
        elif parsed.path == '/api/weapon_action':
            self._handle_weapon_action(data)
        elif parsed.path == '/api/cman_action':
            self._handle_cman_action(data)
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
            build_training_catalog, get_spell_rank_cap,
        )

        prof_id = session.profession_id
        level   = session.level
        skills_out, display_categories = build_training_catalog(session, TrainingRequestHandler.server_ref)

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
            'categories':        {cat: ids for cat, ids in display_categories.items()},
            'spell_rank_cap':    get_spell_rank_cap(prof_id, level),
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

    def _serve_weapon_data(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        payload = _build_weapon_state(session, TrainingRequestHandler.server_ref)
        self._json_response(payload)

    def _serve_cman_data(self, params):
        token = self._token_from_params(params)
        session, err = self._resolve_token(token)
        if not session:
            self._json_error(err, 401)
            return
        payload = _build_cman_state(session, TrainingRequestHandler.server_ref)
        self._json_response(payload)

    def _handle_weapon_action(self, data):
        token_str = data.get('token')
        session, err = self._resolve_token(token_str)
        if not session:
            self._json_error(err, 401)
            return

        action = str(data.get('action') or '').strip().lower()
        server = TrainingRequestHandler.server_ref

        if action == 'stop_assault':
            from server.core.scripting.lua_bindings.weapon_api import stop_active_weapon_assault
            stopped, message = stop_active_weapon_assault(session)
            if server._loop and message:
                async def _notify():
                    await session.send_line(message)
                    await session.send_prompt()
                asyncio.run_coroutine_threadsafe(_notify(), server._loop).result(timeout=5)
            self._json_response({
                'success': bool(stopped),
                'message': message or ("You are not committed to an assault right now." if not stopped else "You stop your assault."),
                'state': _build_weapon_state(session, server),
            })
            return

        if action != 'execute':
            self._json_error('Unknown weapon action.')
            return

        mnemonic = str(data.get('mnemonic') or '').strip().lower()
        target = str(data.get('target') or '').strip()
        limb = str(data.get('limb') or '').strip().lower()
        if not mnemonic:
            self._json_error('No technique selected.')
            return

        from server.core.scripting.lua_bindings.weapon_api import execute_technique

        try:
            future = asyncio.run_coroutine_threadsafe(
                execute_technique(session, mnemonic, target, server, limb=limb),
                server._loop,
            )
            message = future.result(timeout=20) or ''
            if server._loop and message:
                async def _notify():
                    await session.send_line(message)
                    await session.send_prompt()
                asyncio.run_coroutine_threadsafe(_notify(), server._loop).result(timeout=5)
            self._json_response({
                'success': True,
                'message': message or 'Technique executed.',
                'state': _build_weapon_state(session, server),
            })
        except Exception as e:
            log.error("Training weapon action error [%s]: %s", mnemonic, e, exc_info=True)
            self._json_error(f'Weapon technique failed: {e}')

    def _handle_cman_action(self, data):
        token_str = data.get('token')
        session, err = self._resolve_token(token_str)
        if not session:
            self._json_error(err, 401)
            return

        action = str(data.get('action') or '').strip().lower()
        mnemonic = str(data.get('mnemonic') or '').strip().lower()
        if not mnemonic:
            self._json_error('No combat maneuver selected.')
            return

        server = TrainingRequestHandler.server_ref
        from server.core.scripting.lua_bindings.combat_maneuver_api import (
            learn_combat_maneuver_rank,
            unlearn_combat_maneuver_rank,
        )

        if action == 'learn':
            success, message = learn_combat_maneuver_rank(session, server, mnemonic)
        elif action == 'unlearn':
            success, message = unlearn_combat_maneuver_rank(session, server, mnemonic)
        else:
            self._json_error('Unknown combat maneuver action.')
            return

        if success and server._loop and message:
            async def _notify():
                await session.send_line(message)
                await session.send_prompt()
            asyncio.run_coroutine_threadsafe(_notify(), server._loop).result(timeout=5)

        self._json_response({
            'success': bool(success),
            'message': message,
            'state': _build_cman_state(session, server),
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
            SKILL_NAMES, calc_skill_bonus, get_train_limit, get_max_ranks,
            cost_for_rank_range, get_skill_cost, is_spell_circle_subject,
            spell_circle_id_for_subject, get_spell_rank_cap, get_total_spell_ranks,
            get_spell_circle_max_ranks, build_training_catalog, SPELL_RESEARCH_SKILL_ID
        )

        level   = session.level
        total_ptp = 0
        total_mtp = 0
        skill_changes = []
        circle_changes = []
        cap_errors = []
        current_spell_ranks = dict(getattr(session, 'spell_ranks', {}) or {})
        desired_spell_ranks = dict(current_spell_ranks)

        for skill_id_str, new_ranks in desired.items():
            skill_id  = int(skill_id_str)
            new_ranks = max(0, int(new_ranks))
            if is_spell_circle_subject(skill_id):
                circle_id = spell_circle_id_for_subject(skill_id)
                old_ranks = int(desired_spell_ranks.get(circle_id, 0) or 0)
                if new_ranks == old_ranks:
                    continue
                desired_spell_ranks[int(circle_id)] = new_ranks
                circle_changes.append((int(circle_id), old_ranks, new_ranks))
                continue
            raw       = (session.skills or {}).get(skill_id, {})
            old_ranks = int(raw.get('ranks', 0)) if isinstance(raw, dict) else 0
            if new_ranks == old_ranks:
                continue
            ptp_per, mtp_per = get_skill_cost(skill_id, prof_id)
            if ptp_per == 0 and mtp_per == 0:
                continue

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
            skill_changes.append((skill_id, old_ranks, new_ranks))

        if cap_errors:
            self._json_error('Rank cap exceeded:\n' + '\n'.join(cap_errors))
            return

        for skill_id, old_ranks, new_ranks in skill_changes:
            ptp_per, mtp_per = get_skill_cost(skill_id, prof_id)
            if new_ranks > old_ranks:
                limit = get_train_limit(skill_id, prof_id) or 1
                rp, rm = cost_for_rank_range(ptp_per, mtp_per, limit, level, old_ranks, new_ranks)
                total_ptp += rp
                total_mtp += rm
            else:
                delta = old_ranks - new_ranks
                total_ptp -= ptp_per * delta
                total_mtp -= mtp_per * delta

        old_total_spell_ranks = get_total_spell_ranks(session, server, prof_id)
        new_total_spell_ranks = sum(max(0, int(ranks or 0)) for ranks in desired_spell_ranks.values())
        spell_rank_cap = get_spell_rank_cap(prof_id, level)
        if new_total_spell_ranks > spell_rank_cap:
            self._json_error(
                'Spell rank cap exceeded:\nRequested {} total spell ranks but cap is {} at level {}.'.format(
                    new_total_spell_ranks, spell_rank_cap, level
                )
            )
            return

        spell_ptp_per, spell_mtp_per = get_skill_cost(SPELL_RESEARCH_SKILL_ID, prof_id)
        spell_limit = get_train_limit(SPELL_RESEARCH_SKILL_ID, prof_id) or 1
        if new_total_spell_ranks > old_total_spell_ranks:
            rp, rm = cost_for_rank_range(
                spell_ptp_per,
                spell_mtp_per,
                spell_limit,
                level,
                old_total_spell_ranks,
                new_total_spell_ranks,
            )
            total_ptp += rp
            total_mtp += rm
        elif new_total_spell_ranks < old_total_spell_ranks:
            delta = old_total_spell_ranks - new_total_spell_ranks
            total_ptp -= spell_ptp_per * delta
            total_mtp -= spell_mtp_per * delta

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
        for skill_id, old_ranks, new_ranks in skill_changes:
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

        if circle_changes:
            session.spell_ranks = desired_spell_ranks
            if server.db and session.character_id:
                server.db.save_character_spell_ranks(session.character_id, desired_spell_ranks)
                session.spellbook = server.db.load_character_spellbook(session.character_id)

            catalog, _ = build_training_catalog(session, server)
            for circle_id, old_ranks, new_ranks in circle_changes:
                name = (catalog.get(10000 + int(circle_id)) or {}).get('name', f'Circle {circle_id}')
                change_lines.append(
                    '{}: {} \u2192 {} ranks'.format(name, old_ranks, new_ranks)
                )

            total_spell_bonus = calc_skill_bonus(new_total_spell_ranks)
            if not session.skills:
                session.skills = {}
            session.skills[SPELL_RESEARCH_SKILL_ID] = {
                'ranks': new_total_spell_ranks,
                'bonus': total_spell_bonus,
            }
            if server.db and session.character_id:
                server.db.save_character_skill(
                    session.character_id,
                    SPELL_RESEARCH_SKILL_ID,
                    new_total_spell_ranks,
                    total_spell_bonus,
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
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',   'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, msg, status=400):
        self._json_response({'error': msg}, status)


# ── Skill tooltip data ─────────────────────────────────────────────────────────
# Plain Python dict serialized via json.dumps — no f-string brace issues.

_SKILL_INFO = {
    1:  {"d": "Wield a weapon in each hand simultaneously.",
         "m": "Off-hand AS uses the normal melee formula, then adds TWC bonus/3 and reduces the untrained -25 off-hand penalty by TWC bonus/2. TWC roundtime also uses main speed plus off-hand speed and weight."},
    2:  {"d": "Reduces the action penalty of heavier armor, letting you move and fight more freely inside it.",
         "m": "Every 2 ranks remove 1 point of armor action penalty, helping your AS, DS, and maneuver performance in heavier armor."},
    3:  {"d": "Proficiency with shields of all sizes.",
         "m": "Block DS uses Shield Use ranks + STR/4 + DEX/4, then adds shield size bonus and enchant. Shield size also changes evade penalties: small -22%, medium -30%, large -38%, tower -46%."},
    4:  {"d": "Specialized combat techniques including feints, parries, weapon-technique access, and other combat maneuvers.",
         "m": "Melee AS adds Combat Maneuvers ranks/2. Open aimed attacks use 25% of your CM bonus, and many maneuver checks and weapon-technique unlocks key directly from this skill."},
    5:  {"d": "Mastery of swords, daggers, and all bladed weapons.",
         "m": "Your Edged Weapons skill bonus is added directly to melee AS, and your edged ranks also feed parry DS when an edged weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, +4/rank to 20, +3/rank to 30, +2/rank to 40, then +1/rank."},
    6:  {"d": "Proficiency with maces, hammers, clubs, and other crushing weapons.",
         "m": "Your Blunt Weapons skill bonus is added directly to melee AS, and your blunt ranks also feed parry DS when a blunt weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."},
    7:  {"d": "Skill with greatswords, war mattocks, halberds, and other two-handed weapons.",
         "m": "Your Two-Handed Weapons skill bonus is added directly to melee AS, and your two-handed ranks also feed parry DS when a two-handed weapon is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."},
    8:  {"d": "Accuracy and power with bows, crossbows, and other ranged weapons.",
         "m": "Your Ranged Weapons skill bonus drives ranged AS for READY and FIRE. Aimed ranged shots also key off your stored AIM location and the normal aimed-shot checks."},
    9:  {"d": "Technique for hurling axes, daggers, javelins, and other projectiles with precision.",
         "m": "Your Thrown Weapons skill bonus drives thrown AS for HURL. Thrown attacks also use aimed-shot handling when you target a body part."},
    10: {"d": "Fighting with spears, tridents, pikes, and other pole weapons. Long reach is their hallmark.",
         "m": "Your Polearm Weapons skill bonus is added directly to melee AS, and your polearm ranks also feed parry DS when a polearm is in hand. Skill bonus follows the GS4 curve: +5/rank to 10, then +4, +3, +2, and +1 tiers."},
    11: {"d": "Unarmed combat covering punches, kicks, and grapples. Also governs brawling weapons.",
         "m": "UAF = (Brawling ranks x2) + CM/2 + STR bonus/2 + AGI bonus/2, plus UCS enchant bonuses. Brawling ranks also feed parry DS when you are using brawling attacks or bare-handed defense."},
    12: {"d": "The art of handling multiple opponents at once without being overwhelmed.",
         "m": "MSTRIKE currently gives 2 swings minimum, then adds 1 more swing per 25 MoC ranks, up to 5 total swings."},
    13: {"d": "General conditioning that improves stamina, maneuver defense, and physical endurance.",
         "m": "SMRv2 defense averages Dodging, CM, Perception, and Physical Fitness ranks. Physical Fitness also adds 25% of its skill bonus to CLIMB and 20% to SWIM checks."},
    14: {"d": "The ability to read attacks and move out of the way. Pure defensive value.",
         "m": "Evade DS starts from Dodging ranks + AGI bonus + INT bonus/4, then armor, shield size, and stance modify the final result."},
    15: {"d": "Knowledge of magical glyphs, runes, and symbols inscribed on scrolls and items.",
         "m": "Used directly by READ and INVOKE checks for scrolls and magical writing. More ranks improve your odds with higher-level or unfamiliar arcane material."},
    16: {"d": "Activating wands, scrolls, and enchanted objects without formal spell training.",
         "m": "Used for charged-item activation with wands, rods, and similar devices. More ranks improve reliability when the item's magic is outside your own circles."},
    17: {"d": "Accuracy when targeting creatures with bolt spells and directed magical attacks.",
         "m": "Each point of Spell Aiming bonus adds +1 bolt AS. Bolt AS = Spell Aiming bonus + stance (+30 offensive to -30 defensive) + any bolt/AS buffs."},
    18: {"d": "The capacity to draw ambient mana from the environment and store it for casting.",
         "m": "Max mana = base mana from your profession's mana stats + Harness Power ranks capped at level + your Harness Power skill bonus."},
    19: {"d": "Fine control over elemental mana flows. Essential for wizards and sorcerers.",
         "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."},
    20: {"d": "Fine control over spiritual mana. Essential for clerics, empaths, and paladins.",
         "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."},
    21: {"d": "Control over mental mana flows used by monks, bards, and mental lore specialists.",
         "m": "Mana regen uses +1 per 10 ranks for single-sphere users, or +1 per 10 ranks in the higher sphere and +1 per 20 in the lower sphere for two-sphere users."},
    22: {"d": "Scholarly pursuit and memorization of new spells beyond your base circle.",
         "m": "Each trained rank is one more spell rank known. Your profession's rank-per-level cap controls how many total spell ranks you can carry at your level."},
    23: {"d": "Wilderness craft covering tracking, foraging, and the art of skinning creatures for their hides.",
         "m": "TRACK reads real trails up to 900 seconds old, while Survival also supports FORAGE, FORAGE SENSE, and skinning quality."},
    24: {"d": "Detecting and safely neutralizing mechanical traps on chests, doors, and containers.",
         "m": "Disarm checks use your training, your stats, and your tools together. Better ranks and better disarm tools raise your odds on trapped boxes and containers."},
    25: {"d": "Coaxing open locks without the original key. The bread and butter of any rogue.",
         "m": "Lockpicking checks use your training, your stats, focus, and pick quality together. Better picks and more ranks raise your odds on tough locks."},
    26: {"d": "Moving unseen and melting into shadows. Drives your HIDE roll and your stealth-based ambush accuracy and weighting.",
         "m": "HIDE rolls open d100 + (3 x ranks) + Discipline bonus + profession bonus + room mods - armor penalty against the room's current hiding difficulty."},
    27: {"d": "Sharp awareness of your surroundings for spotting hidden creatures, traps, and passages.",
         "m": "Perception feeds stealth detection and is one of the equally weighted skills in SMRv2 defense, alongside Dodging, Combat Maneuvers, and Physical Fitness."},
    28: {"d": "Scaling walls, cliffs, ladders, and grates. Without training vertical travel is treacherous.",
         "m": "CLIMB uses open d100 + Climbing bonus + 25% of Physical Fitness bonus + DEX bonus + AGI/2 - encumbrance - armor. At 50 ranks, climbs are forced to succeed."},
    29: {"d": "Moving through water without drowning. Required for water rooms and some crossings.",
         "m": "SWIM uses open d100 + Swimming bonus + 20% of Physical Fitness bonus + STR bonus + CON bonus + DEX/2 - encumbrance - armor. At 50 ranks, swims are forced to succeed."},
    30: {"d": "Tending wounds with bandages and herbs to reduce injury severity after combat.",
         "m": "TEND chance is 40% + First Aid bonus/2 - 15 per wound rank, capped from 5% to 95%. Herb roundtime is reduced by 1 second per 20 First Aid bonus, to a 3 second minimum."},
    31: {"d": "The merchant's art covering haggling, appraisal, and knowing when the price is right.",
         "m": "Shop buy price is reduced by 0.2% per rank, capped at 15% off. More Trading means cheaper purchases anywhere this modifier is used."},
    32: {"d": "Lifting coin purses and small items from NPCs and other players without being noticed.",
         "m": "STEAL uses your Pickpocketing bonus, DEX bonus, Discipline bonus, and part of AGI, then applies hiding, rogue, hand-full, armor, and encumbrance modifiers."},
    33: {"d": "Knowledge of spiritual blessings covering warding spells, protective prayers, and holy shields.",
         "m": "Currently hooks into 304 Bless, 307 Benediction, 1604 Consecrate, 1611 Patron's Blessing, and 1625 Holy Weapon."},
    34: {"d": "Theological knowledge of the Arkati pantheon and their divine practices.",
         "m": "Currently hooks into 317 Divine Fury, 319 Soul Ward, 320 Ethereal Censer, 1614 Aura of the Arkati, and 1615 Repentance."},
    35: {"d": "The art of summoning spirits, elementals, and other entities to serve your will.",
         "m": "Currently hooks into Spirit Servant and other summon-style effects where summoning magic is implemented."},
    36: {"d": "Mastery of air-based elemental lore covering wind, lightning, and movement magic.",
         "m": "Currently hooks into 501 Sleep, 505 Hand of Tonis, 535 Haste, and 912 Call Wind."},
    37: {"d": "Mastery of earth-based elemental lore covering stone, metal, and endurance magic.",
         "m": "Currently hooks into 509 Strength, 514 Stone Fist, and 917 Earthen Fury."},
    38: {"d": "Mastery of fire-based elemental lore covering flame, heat, and destruction magic.",
         "m": "Currently hooks into 906 Minor Fire, 908 Major Fire, 915 Weapon Fire, and 519 Immolation."},
    39: {"d": "Mastery of water-based elemental lore covering ice, tides, and healing magic.",
         "m": "Currently hooks into 903 Minor Water and 512 Cold Snap."},
    40: {"d": "Mental lore focused on influencing and bending the will of others.",
         "m": "Currently hooks into Confusion-style control magic and other supported manipulation effects."},
    41: {"d": "Mental lore focused on mind-to-mind communication and reading surface thoughts.",
         "m": "Currently hooks into Mindward-style defense and other supported telepathy effects."},
    42: {"d": "Mental lore focused on transferring energy to drain foes and bolster allies.",
         "m": "Currently hooks into Powersink-style draining and other supported transference effects."},
    43: {"d": "The skill for aimed strikes and precision attacks, especially from hiding.",
         "m": "Hidden aimed attacks use 25% of your Ambush bonus toward aiming and add extra crit weighting. Open aiming uses 25% of Ambush bonus plus 25% of Combat Maneuvers bonus."},
    44: {"d": "Mental lore concerned with foresight, omens, and predictive insight.",
         "m": "Currently hooks into Foresight, Premonition, and other supported divination effects."},
    45: {"d": "Mental lore concerned with reshaping the body through force of will.",
         "m": "Currently hooks into Mind over Body and other supported transformation effects."},
    46: {"d": "Sorcerous lore focused on demonic entities, planar bargains, and summoning.",
         "m": "Currently hooks into Minor Summoning and other supported demonology or shadow-defense effects."},
    47: {"d": "Sorcerous lore focused on undeath, corpses, and gravebound power.",
         "m": "Currently hooks into Animate Dead, Grasp of the Grave, and other supported necromancy effects."},
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
.top-tabs{display:flex;gap:0.6rem;margin-bottom:1.35rem;}
.top-tab{font-family:'Cinzel',serif;font-size:0.8rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;background:var(--surface2);color:var(--parchment2);border:1px solid var(--border);padding:0.55rem 1rem;cursor:pointer;transition:all 0.15s;}
.top-tab:hover{border-color:var(--border-hi);color:var(--parchment);}
.top-tab.active{background:#231b10;color:var(--gold);border-color:var(--gold-dim);}
.tab-panel{display:block}
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
.wt-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0.8rem;margin-bottom:1rem;}
.wt-box{background:var(--surface);border:1px solid var(--border);padding:0.75rem 0.9rem;}
.wt-box-label{font-family:'Cinzel',serif;font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:0.35rem;}
.wt-box-value{font-family:'Cinzel',serif;font-size:1rem;color:var(--parchment);}
.wt-intro{padding:0.9rem 1rem;background:var(--surface);border:1px solid var(--border);margin-bottom:1rem;color:var(--parchment2);line-height:1.6;}
.wt-section{margin-bottom:1.25rem;}
.wt-section-title{font-family:'Cinzel',serif;font-size:0.82rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold-dim);border-bottom:1px solid var(--border);padding-bottom:0.35rem;margin-bottom:0.75rem;}
.wt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem;}
.wt-card{background:var(--surface);border:1px solid var(--border);padding:1rem;}
.wt-card.learned{border-color:var(--gold-dim);}
.wt-card.available{border-color:var(--green-dim);}
.wt-card.path{border-color:#5b4a2a;}
.wt-card.locked{opacity:0.92;}
.wt-card-head{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;margin-bottom:0.45rem;}
.wt-name{font-family:'Cinzel',serif;font-size:1rem;color:var(--gold);}
.wt-mnemonic{font-family:'Cinzel',serif;font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin-top:0.15rem;}
.wt-rank{font-family:'Cinzel',serif;font-size:0.8rem;color:var(--parchment2);text-align:right;}
.wt-tags{display:flex;gap:0.35rem;flex-wrap:wrap;margin-bottom:0.55rem;}
.wt-tag{font-family:'Cinzel',serif;font-size:0.65rem;letter-spacing:0.08em;text-transform:uppercase;padding:0.18rem 0.45rem;border:1px solid var(--border);color:var(--parchment2);}
.wt-tag.ok{border-color:var(--green-dim);color:var(--green);}
.wt-tag.bad{border-color:var(--red-dim);color:var(--red);}
.wt-desc{font-size:0.95rem;color:var(--parchment2);line-height:1.55;margin-bottom:0.65rem;}
.wt-meta{display:grid;grid-template-columns:1fr 1fr;gap:0.35rem 0.7rem;font-size:0.83rem;color:var(--muted);margin-bottom:0.75rem;}
.wt-meta div b{color:var(--gold-dim);font-style:normal;font-weight:600;}
.wt-note{font-size:0.83rem;color:var(--muted);border-top:1px solid var(--border);padding-top:0.55rem;margin-top:0.55rem;}
.wt-command{font-family:'Courier New',monospace;font-size:0.88rem;background:var(--surface2);border:1px solid var(--border);padding:0.55rem 0.65rem;color:var(--parchment);margin-top:0.7rem;}
.wt-empty{color:var(--muted);font-style:italic;padding:1rem;background:var(--surface);border:1px solid var(--border);}
.cm-intro{padding:0.9rem 1rem;background:var(--surface);border:1px solid var(--border);margin-bottom:1rem;color:var(--parchment2);line-height:1.6;}
.cm-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0.8rem;margin-bottom:1rem;}
.cm-head{display:grid;grid-template-columns:1.35fr 110px 100px 70px 80px 150px 96px;gap:0.5rem;padding:0.2rem 0.6rem 0.35rem;font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-family:'Cinzel',serif;border-bottom:1px solid var(--surface3);margin-bottom:0.15rem;}
.cm-row{display:grid;grid-template-columns:1.35fr 110px 100px 70px 80px 150px 96px;align-items:center;gap:0.5rem;padding:0.45rem 0.6rem;border-radius:2px;border-left:2px solid transparent;transition:background 0.1s;cursor:default;}
.cm-row:hover{background:var(--surface2);}
.cm-row.learned{border-left-color:var(--gold-dim);}
.cm-row.available{border-left-color:var(--green-dim);}
.cm-row.locked,.cm-row.profession_locked,.cm-row.special{opacity:0.93;}
.cm-row.guild{border-left-color:var(--blue);}
.cm-name-wrap{min-width:0;}
.cm-name{color:var(--parchment);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.cm-name.learned{color:var(--gold);font-weight:600;}
.cm-sub{font-size:0.74rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:0.12rem;}
.cm-meta{text-align:center;font-size:0.82rem;color:var(--parchment2);}
.cm-cost{font-family:'Cinzel',serif;text-align:center;color:var(--amber);}
.cm-rank{font-family:'Cinzel',serif;text-align:center;color:var(--parchment);}
.cm-status{font-size:0.8rem;color:var(--muted);line-height:1.35;}
.cm-status.available{color:var(--green);}
.cm-status.guild{color:var(--blue);}
.cm-status.locked,.cm-status.profession_locked,.cm-status.special{color:var(--amber);}
.cm-status.mastered{color:var(--gold);}
.cm-controls{display:flex;align-items:center;justify-content:flex-end;gap:0.3rem;}
.cm-empty{color:var(--muted);font-style:italic;padding:1rem;background:var(--surface);border:1px solid var(--border);}
@media (max-width:760px){
  .wt-summary{grid-template-columns:repeat(2,minmax(0,1fr));}
  .wt-meta{grid-template-columns:1fr;}
  .cm-summary{grid-template-columns:repeat(2,minmax(0,1fr));}
  .cm-head,.cm-row{grid-template-columns:1.3fr 90px 80px 64px 74px 120px 84px;font-size:0.74rem;}
  .cm-status{font-size:0.74rem;}
}
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
let char=null,pending={},activeTab='skills',weaponState=null,cmanState=null,cmanBusy=false;
SKILL_INFO_PLACEHOLDER

/* ── Skill bonus formula ── */
function bonus(r){
  if(r<=0)return 0;
  if(r<=10)return r*5;
  if(r<=20)return 50+((r-10)*4);
  if(r<=30)return 90+((r-20)*3);
  if(r<=40)return 120+((r-30)*2);
  return r+100;
}

/* ── Initial load ── */
async function load(){
  try{
    const r=await fetch('/api/character?token='+TOKEN);
    char=await r.json();
    if(char.error){mainErr(char.error);return;}
    try{render();}catch(e){mainErr('Training page render failed: '+(e&&e.message?e.message:String(e)));return;}
    initStatsModal();
    initConvModal();
  }catch(e){mainErr('Could not connect to game server. '+(e&&e.message?e.message:''));}
}

function mainErr(msg){
  const main=document.getElementById('main');
  if(!main)return;
  main.innerHTML='<div style="color:var(--red);padding:1.2rem 0.2rem;font-family:Cinzel,serif;">'+msg+'</div>';
}

window.addEventListener('error',e=>{
  const msg=(e&&e.message)?e.message:'Unknown training page error.';
  mainErr('Training page error: '+msg);
});

async function loadWeaponData(){
  try{
    const r=await fetch('/api/weapon?token='+TOKEN);
    weaponState=await r.json();
  }catch(e){
    weaponState={error:'Could not reach weapon technique service.'};
  }
}

async function loadCmanData(){
  try{
    const r=await fetch('/api/cman?token='+TOKEN);
    cmanState=await r.json();
  }catch(e){
    cmanState={error:'Could not reach combat maneuver service.'};
  }
}

async function switchTab(tab){
  activeTab=tab;
  if(tab==='weapon' && !weaponState){
    await loadWeaponData();
  }
  if(tab==='cman' && !cmanState){
    await loadCmanData();
  }
  try{render();}catch(e){mainErr('Training page render failed: '+(e&&e.message?e.message:String(e)));}
}

/* ════════════════════════════════════════════════════
   SKILL TRAINING
   ════════════════════════════════════════════════════ */
function render(){
  document.getElementById('char-badge').textContent=char.name+' \u00b7 Level '+char.level;
  refreshTP();
  const saveBtn=document.getElementById('save-btn');
  saveBtn.style.display=activeTab==='skills'?'inline-block':'none';
  const main=document.getElementById('main');main.innerHTML='';
  const tabs=document.createElement('div');tabs.className='top-tabs';
  tabs.innerHTML=
    '<button class="top-tab'+(activeTab==='skills'?' active':'')+'" onclick="switchTab(\'skills\')">Skills</button>'+
    '<button class="top-tab'+(activeTab==='weapon'?' active':'')+'" onclick="switchTab(\'weapon\')">Weapon Techniques</button>'+
    '<button class="top-tab'+(activeTab==='cman'?' active':'')+'" onclick="switchTab(\'cman\')">Combat Maneuvers</button>';
  main.appendChild(tabs);
  const content=document.createElement('div');content.className='tab-panel';content.id='tab-panel';
  main.appendChild(content);
  if(activeTab==='weapon'){renderWeaponTechniques(content);return;}
  if(activeTab==='cman'){renderCombatManeuvers(content);return;}
  renderSkills(content);
}

function renderSkills(main){
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

function renderWeaponTechniques(main){
  if(!weaponState){main.innerHTML='<div class="wt-empty">Loading weapon techniques...</div>';return;}
  if(weaponState.error){main.innerHTML='<div class="wt-empty">'+weaponState.error+'</div>';return;}
  const summary=document.createElement('div');summary.className='wt-summary';
  summary.innerHTML=
    '<div class="wt-box"><div class="wt-box-label">Current Weapon Path</div><div class="wt-box-value">'+((weaponState.current_categories||[]).join(', ')||'None')+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Ready Now</div><div class="wt-box-value">'+((weaponState.ready_now||[]).length||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Potential Unlocks</div><div class="wt-box-value">'+((weaponState.unlock_path||[]).length||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Stamina / RT</div><div class="wt-box-value">'+(weaponState.stamina||0)+' / '+(weaponState.roundtime||0)+'s</div></div>';
  main.appendChild(summary);

  const intro=document.createElement('div');intro.className='wt-intro';
  intro.innerHTML=
    'Only techniques relevant to your current character and readied weapon are shown here. '+
    'The command line on each card is the in-game syntax to use. '+
    'Assault techniques can be broken off with <b>STOP ASSAULT</b>.';
  main.appendChild(intro);

  renderWeaponSection(main,'Usable Right Now',weaponState.ready_now||[],false);
  renderWeaponSection(main,'Can Unlock On This Weapon Path',weaponState.unlock_path||[],true);
}

function renderWeaponSection(main,title,rows,isPath){
  const sec=document.createElement('div');sec.className='wt-section';
  sec.innerHTML='<div class="wt-section-title">'+title+'</div>';
  if(!rows.length){
    sec.innerHTML+='<div class="wt-empty">'+(isPath?'No additional techniques are on your current weapon path.':'No weapon techniques are usable right now with your current loadout.')+'</div>';
    main.appendChild(sec);
    return;
  }
  const grid=document.createElement('div');grid.className='wt-grid';
  for(const tech of rows){grid.appendChild(buildWeaponCard(tech,isPath));}
  sec.appendChild(grid);
  main.appendChild(sec);
}

function buildWeaponCard(tech,isPath){
  const card=document.createElement('div');
  card.className='wt-card '+(isPath?'path':tech.availability);
  const learnedText=tech.learned_rank>0?('Learned Rank '+tech.learned_rank+'/'+tech.max_rank):('Current Max '+tech.max_rank+'/5');
  const nextRank=(tech.learned_rank||0)+1;
  let nextText='';
  if(tech.rank_thresholds && tech.rank_thresholds.length>=nextRank){
    const nextThreshold=tech.rank_thresholds[nextRank-1];
    if(tech.learned_rank < 5){
      nextText='<div><b>Next unlock:</b> Rank '+nextRank+' at '+nextThreshold+' '+tech.weapon_skill_label+' ranks</div>';
    }
  }
  const tags=[
    '<span class="wt-tag">'+tech.category_label+'</span>',
    '<span class="wt-tag">'+String(tech.type||'').toUpperCase()+'</span>',
    '<span class="wt-tag ok">Profession OK</span>'
  ];
  if(isPath){
    tags.push('<span class="wt-tag">'+(tech.max_rank>0?'Unlock Path':'Needs More Training')+'</span>');
  }else{
    tags.push('<span class="wt-tag ok">Usable Now</span>');
  }
  if(tech.learned_rank>0){
    tags.push('<span class="wt-tag">Learned</span>');
  }
  card.innerHTML=
    '<div class="wt-card-head"><div><div class="wt-name">'+tech.name+'</div><div class="wt-mnemonic">'+tech.mnemonic+'</div></div><div class="wt-rank">'+learnedText+'</div></div>'+
    '<div class="wt-tags">'+tags.join('')+'</div>'+
    '<div class="wt-desc">'+tech.description+'</div>'+
    '<div class="wt-meta">'+
      '<div><b>Weapon Skill:</b> '+tech.weapon_skill_label+' ('+tech.skill_ranks+' ranks)</div>'+
      '<div><b>Minimum:</b> '+tech.min_ranks+' ranks</div>'+
      '<div><b>Stamina:</b> '+tech.stamina_cost+'</div>'+
      '<div><b>Cooldown:</b> '+tech.cooldown+'s</div>'+
      '<div><b>Roundtime:</b> '+tech.base_rt+'s'+(tech.rt_mod?(' ('+(tech.rt_mod>0?'+':'')+tech.rt_mod+' mod)'):'')+'</div>'+
      '<div><b>Gear:</b> '+(tech.gear_requirement_label||'Standard')+'</div>'+
      '<div><b>Thresholds:</b> '+(tech.rank_thresholds||[]).join(', ')+'</div>'+
      nextText+
      (tech.reaction_trigger?'<div><b>Reaction Trigger:</b> '+tech.reaction_trigger.replaceAll('_',' ')+'</div>':'')+
    '</div>'+
    (isPath&&tech.unlock_reason?'<div class="wt-note"><b>Not unlocked yet:</b> '+tech.unlock_reason+'</div>':'')+
    (tech.mechanics_notes?'<div class="wt-note"><b>Mechanics:</b> '+tech.mechanics_notes+'</div>':'')+
    '<div class="wt-command">'+tech.command_syntax+(tech.type==='assault'?'<br>STOP ASSAULT':'')+'</div>';
  return card;
}

function renderCombatManeuvers(main){
  if(!cmanState){main.innerHTML='<div class="cm-empty">Loading combat maneuvers...</div>';return;}
  if(cmanState.error){main.innerHTML='<div class="cm-empty">'+cmanState.error+'</div>';return;}

  const summary=document.createElement('div');summary.className='cm-summary';
  summary.innerHTML=
    '<div class="wt-box"><div class="wt-box-label">Free CMAN Points</div><div class="wt-box-value">'+(cmanState.free_points||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Spent / Total</div><div class="wt-box-value">'+(cmanState.spent_points||0)+' / '+(cmanState.total_points||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Directly Trained</div><div class="wt-box-value">'+(cmanState.trained_count||0)+'</div></div>'+
    '<div class="wt-box"><div class="wt-box-label">Available To Learn</div><div class="wt-box-value">'+(cmanState.available_count||0)+'</div></div>';
  main.appendChild(summary);

  const intro=document.createElement('div');intro.className='cm-intro';
  const passive=(cmanState.passive_summary||[]).length?(cmanState.passive_summary||[]).join(' • '):'No passive bonuses active from your current direct maneuver training.';
  intro.innerHTML=
    'Combat maneuver training spends points from your <b>Combat Maneuvers</b> skill ranks. '+
    'Guild maneuvers are shown here for reference but cannot be adjusted from this tab. '+
    '<br><span style="color:var(--muted)">Current passive effects: '+passive+'</span>';
  main.appendChild(intro);

  const groups={};
  for(const row of (cmanState.maneuvers||[])){
    if(row.availability==='profession_locked')continue;
    const key=row.category_label||'General';
    if(!groups[key])groups[key]=[];
    groups[key].push(row);
  }

  for(const [label,rows] of Object.entries(groups)){
    const sec=document.createElement('div');sec.className='cat';
    sec.innerHTML='<div class="cat-title">'+label+'</div><div class="cm-head"><span>Maneuver</span><span style="text-align:center">Type</span><span style="text-align:center">Target</span><span style="text-align:center">Cost</span><span style="text-align:center">Rank</span><span>Status</span><span></span></div>';
    for(const row of rows){sec.appendChild(buildCmanRow(row));}
    main.appendChild(sec);
  }
}

function buildCmanRow(row){
  const el=document.createElement('div');
  el.className='cm-row '+(row.availability||'locked')+((row.direct_rank||0)>0?' learned':'');
  const tooltipParts=[row.description||'',row.requirements?('Requirements: '+row.requirements):'',row.mechanics?('Mechanics: '+row.mechanics):''].filter(Boolean);
  if(tooltipParts.length)el.title=tooltipParts.join('\n\n');

  const costText=row.is_guild_skill?'Guild':(row.next_cost>0?row.next_cost:'\u2014');
  const statusClass=row.availability||'locked';
  const statusText=row.status_text||'\u2014';
  el.innerHTML=
    '<div class="cm-name-wrap"><div class="cm-name'+((row.effective_rank||0)>0?' learned':'')+'">'+row.name+'</div><div class="cm-sub">'+row.mnemonic+' \u00b7 '+(row.stamina||'0')+' stamina \u00b7 '+(row.roundtime||'n/a')+'</div></div>'+
    '<div class="cm-meta">'+(row.type_label||'\u2014')+'</div>'+
    '<div class="cm-meta">'+(row.targeting_label||'\u2014')+'</div>'+
    '<div class="cm-cost">'+costText+'</div>'+
    '<div class="cm-rank">'+(row.effective_rank||0)+' / '+(row.max_rank||0)+'</div>'+
    '<div class="cm-status '+statusClass+'">'+statusText+'</div>'+
    '<div class="cm-controls"></div>';

  const controls=el.querySelector('.cm-controls');
  const minus=document.createElement('button');
  minus.className='btn minus';
  minus.textContent='\u2212';
  minus.title='Unlearn rank';
  minus.disabled=cmanBusy||!row.can_unlearn;
  minus.onclick=()=>doCmanAction(row.mnemonic,'unlearn');

  const plus=document.createElement('button');
  plus.className='btn plus';
  plus.textContent='+';
  plus.title=row.is_guild_skill?'Guild-trained maneuver':'Learn next rank';
  plus.disabled=cmanBusy||!row.can_learn;
  plus.onclick=()=>doCmanAction(row.mnemonic,'learn');

  controls.appendChild(minus);
  controls.appendChild(plus);
  return el;
}

async function doCmanAction(mnemonic,action){
  if(cmanBusy)return;
  cmanBusy=true;
  try{render();}catch(e){}
  try{
    const res=await fetch('/api/cman_action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:TOKEN,mnemonic,action})});
    const result=await res.json();
    if(result.state)cmanState=result.state;
    if(!result.success){
      showSkillModal('Combat Maneuver', '<span style="color:var(--red)">'+(result.message||result.error||'Combat maneuver update failed.')+'</span>', true);
    }else if(result.message){
      showSkillModal('Combat Maneuver Updated', result.message, false);
    }
  }catch(e){
    showSkillModal('Combat Maneuver', '<span style="color:var(--red)">Could not reach combat maneuver service.</span>', true);
  }finally{
    cmanBusy=false;
    try{render();}catch(e){}
  }
}

function mkRow(id,sk){
  const cur=pending[id]!==undefined?pending[id]:sk.ranks;
  const changed=cur!==sk.ranks,empty=cur===0;
  const maxRanks=skillMaxRanks(id,sk);
  const atCap=maxRanks>0&&cur>=maxRanks;
  const row=document.createElement('div');
  row.className='sk-row'+(changed?' changed':'')+(!sk.trainable&&empty?' untrained':'');
  row.id='row-'+id;
  row.innerHTML=
    '<div class="sk-name'+(changed?' mod':empty&&!sk.trainable?' dim':'')+'\" id="nm-'+id+'">'+sk.name+'</div>'+
    '<div class="sk-ranks'+(changed?' mod':'')+'\" id="rk-'+id+'">'+cur+'</div>'+
    '<div class="sk-bonus" id="bn-'+id+'">'+(sk.show_bonus===false?'\u2014':('+'+bonus(cur)))+'</div>'+
    '<div class="sk-cost'+(nextCostText(id,sk,'ptp')!=='\u2014'?' act':'')+'\" id="cp-'+id+'">'+nextCostText(id,sk,'ptp')+'</div>'+
    '<div class="sk-cost'+(nextCostText(id,sk,'mtp')!=='\u2014'?' act':'')+'\" id="cm-'+id+'">'+nextCostText(id,sk,'mtp')+'</div>'+
    '<div class="sk-cost" id="cap-'+id+'" style="text-align:center;color:'+(atCap?'var(--amber)':'var(--muted)')+'">'+(maxRanks>0?cur+'/'+maxRanks:'\u2014')+'</div>'+
    '<div class="controls" id="ct-'+id+'"></div>';
  const ct=row.querySelector('#ct-'+id);
  if(sk.trainable){
    const m=document.createElement('button');m.className='btn minus';m.textContent='\u2212';m.title='Remove rank';m.onclick=()=>adj(id,-1);
    const inp=document.createElement('input');inp.type='number';inp.className='rk-input';inp.id='inp-'+id;inp.value=cur;inp.min=0;inp.max=maxRanks>0?maxRanks:9999;inp.onchange=()=>setRk(id,parseInt(inp.value)||0);inp.oninput=()=>setRk(id,parseInt(inp.value)||0);
    const p=document.createElement('button');p.className='btn plus';p.textContent='+';p.title='Add rank (cap: '+maxRanks+')';p.onclick=()=>adj(id,1);
    ct.appendChild(m);ct.appendChild(inp);ct.appendChild(p);
  }else{ct.innerHTML='<span style="color:var(--muted);font-size:0.8rem">N/A</span>';}
  ttAttach(row,id);
  return row;
}
function adj(id,d){const cur=pending[id]!==undefined?pending[id]:char.skills[id].ranks;setRk(id,Math.max(0,cur+d));}
function setRk(id,v){
  const sk=char.skills[id];v=Math.max(0,v);
  const maxRanks=skillMaxRanks(id,sk);
  if(maxRanks>0&&v>maxRanks){v=maxRanks;}
  if(v===sk.ranks)delete pending[id];else pending[id]=v;
  const inp=document.getElementById('inp-'+id);if(inp&&parseInt(inp.value)!==v)inp.value=v;
  const rkEl=document.getElementById('rk-'+id);if(rkEl){rkEl.textContent=v;rkEl.className='sk-ranks'+(v!==sk.ranks?' mod':'');}
  const bnEl=document.getElementById('bn-'+id);if(bnEl)bnEl.textContent=sk.show_bonus===false?'\u2014':('+'+bonus(v));
  const cpEl=document.getElementById('cp-'+id);if(cpEl)cpEl.textContent=nextCostText(id,sk,'ptp');
  const cmEl=document.getElementById('cm-'+id);if(cmEl)cmEl.textContent=nextCostText(id,sk,'mtp');
  const nmEl=document.getElementById('nm-'+id);if(nmEl)nmEl.className='sk-name'+(v!==sk.ranks?' mod':v===0&&!sk.trainable?' dim':'');
  const row=document.getElementById('row-'+id);if(row)row.classList.toggle('changed',v!==sk.ranks);
  const capEl=document.getElementById('cap-'+id);if(capEl){const atCap=maxRanks>0&&v>=maxRanks;capEl.textContent=v+'/'+maxRanks;capEl.style.color=atCap?'var(--amber)':'var(--muted)';}
  refreshSpellCircleDisplays();
  refreshTP();
}
function slotCost(base,limit,level,fromRank,toRank){
  if(limit<=0)limit=1;const prevCap=limit*(level-1);let t=0;
  for(let r=fromRank+1;r<=toRank;r++){const sp=r<=prevCap?1:Math.min(r-prevCap,2);t+=base*sp;}return t;
}
function desiredRanks(id){const sk=char.skills[id];return pending[id]!==undefined?pending[id]:sk.ranks;}
function totalDesiredSpellRanks(){
  let total=0;
  for(const [id, sk] of Object.entries(char.skills||{})){
    if(sk && sk.is_spell_circle) total+=desiredRanks(id);
  }
  return total;
}
function skillMaxRanks(id,sk){
  if(!sk || !sk.is_spell_circle) return sk&&sk.max_ranks>0?sk.max_ranks:0;
  const totalCap=char.spell_rank_cap||0;
  return Math.max(0,totalCap-(totalDesiredSpellRanks()-desiredRanks(id)));
}
function nextCostText(id, sk, kind){
  if(!sk) return '\u2014';
  const base=kind==='ptp'?(sk.base_ptp||0):(sk.base_mtp||0);
  if(!base) return '\u2014';
  if(sk.is_spell_circle){
    const totalCap=char.spell_rank_cap||0;
    const totalRanks=totalDesiredSpellRanks();
    if(totalCap>0 && totalRanks>=totalCap) return '\u2014';
    return String(slotCost(base,sk.limit||1,char.level,totalRanks,totalRanks+1));
  }
  const cur=desiredRanks(id);
  const maxRanks=skillMaxRanks(id,sk);
  if(maxRanks>0 && cur>=maxRanks) return '\u2014';
  return String(slotCost(base,sk.limit||1,char.level,cur,cur+1));
}
function refreshSpellCircleDisplays(){
  for(const [id, sk] of Object.entries(char.skills||{})){
    if(!sk || !sk.is_spell_circle) continue;
    const cur=desiredRanks(id);
    const maxRanks=skillMaxRanks(id,sk);
    const inp=document.getElementById('inp-'+id);if(inp)inp.max=maxRanks>0?maxRanks:9999;
    const cpEl=document.getElementById('cp-'+id);if(cpEl)cpEl.textContent=nextCostText(id,sk,'ptp');
    const cmEl=document.getElementById('cm-'+id);if(cmEl)cmEl.textContent=nextCostText(id,sk,'mtp');
    const capEl=document.getElementById('cap-'+id);if(capEl){const atCap=maxRanks>0&&cur>=maxRanks;capEl.textContent=cur+'/'+maxRanks;capEl.style.color=atCap?'var(--amber)':'var(--muted)';}
  }
}
function tpDelta(){
  let p=0,m=0;
  for(const[s,v]of Object.entries(pending)){
    const id=parseInt(s);const sk=char.skills[id];
    if(sk&&sk.is_spell_circle) continue;
    const lim=sk.limit||1;
    if(v>sk.ranks){p+=slotCost(sk.ptp,lim,char.level,sk.ranks,v);m+=slotCost(sk.mtp,lim,char.level,sk.ranks,v);}
    else{const d=sk.ranks-v;p-=sk.ptp*d;m-=sk.mtp*d;}
  }
  let oldSpell=0,newSpell=0,spellBaseP=0,spellBaseM=0,spellLimit=1;
  for(const sk of Object.values(char.skills||{})){
    if(!sk||!sk.is_spell_circle) continue;
    oldSpell+=sk.ranks||0;
    spellBaseP=sk.base_ptp||spellBaseP;
    spellBaseM=sk.base_mtp||spellBaseM;
    spellLimit=sk.limit||spellLimit;
  }
  newSpell=totalDesiredSpellRanks();
  if(newSpell>oldSpell){
    p+=slotCost(spellBaseP,spellLimit,char.level,oldSpell,newSpell);
    m+=slotCost(spellBaseM,spellLimit,char.level,oldSpell,newSpell);
  }else if(newSpell<oldSpell){
    const d=oldSpell-newSpell;
    p-=spellBaseP*d;
    m-=spellBaseM*d;
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
  const skills={};for(const[s,sk]of Object.entries(char.skills)){skills[s]=pending[s]!==undefined?pending[s]:sk.ranks;}
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
    for(const[s,v]of Object.entries(pending)){const id=parseInt(s);char.skills[id].ranks=v;char.skills[id].bonus=char.skills[id].show_bonus===false?0:bonus(v);}
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
