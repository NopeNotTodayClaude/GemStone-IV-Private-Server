"""
GemStone IV Inventory Commands - Proper GS4 Model (v2)
GET, DROP, GIVE, LOOT, SWAP, WEAR, REMOVE, PUT, STOW, OPEN, CLOSE,
INV, INSPECT, LOOK IN, YELL

GS4 Inventory Model:
  - Items are either: in your RIGHT/LEFT hand, WORN on a body slot, or INSIDE a worn container.
  - There is NO generic "carried" area. Every item must be somewhere specific.
  - Hand items persist to DB with slot='right_hand'/'left_hand' so they survive logout.
  - Multiple items CAN occupy the same slot (GS4 allows multiple worn items per location).
  - WEAR puts a held item on the correct body slot.
  - REMOVE takes a worn item off and puts it in your hand.
  - GET picks up from ground, or retrieves from a container (GET x FROM y).
  - PUT places a held item into a worn container.
  - STOW places a held item into your default container (backpack).
  - INSPECT shows item details.

Worn Locations (simplified):
  head, neck, torso, shoulders, shoulder_slung, back, waist, belt, arms,
  wrist, hands, finger, legs, feet, pin
"""

import logging
import random
from server.core.protocol.colors import colorize, TextPresets, item_name as fmt_item_name, roundtime_msg
from server.core.engine.skinning import (
    can_remove_corpse,
    get_skinning_sheath_nouns,
    get_skinning_tool_bonus,
)

log = logging.getLogger(__name__)

try:
    from server.core.engine.treasure import generate_treasure
except ImportError:
    generate_treasure = None


# Wear verbs by slot
WEAR_VERBS = {
    'torso': ('You put on ', '.'),
    'shoulder_slung': ('You sling ', ' over your shoulder.'),
    'shoulders': ('You drape ', ' over your shoulders.'),
    'back': ('You sling ', ' over your shoulder.'),
    'belt': ('You attach ', ' to your belt.'),
    'waist': ('You strap ', ' around your waist.'),
    'head': ('You put on ', '.'),
    'neck': ('You put on ', '.'),
    'finger': ('You slide ', ' onto your finger.'),
    'wrist': ('You clasp ', ' around your wrist.'),
    'arms': ('You strap on ', '.'),
    'hands': ('You put on ', '.'),
    'legs': ('You strap on ', '.'),
    'feet': ('You put on ', '.'),
    'pin': ('You attach ', '.'),
    'skinning_sheath': ('You strap ', ' to your belt.'),
}

# Remove verbs by slot
REMOVE_VERBS = {
    'torso': 'You remove ',
    'shoulder_slung': 'You unsling ',
    'shoulders': 'You remove ',
    'back': 'You remove ',
    'belt': 'You detach ',
    'waist': 'You unbuckle ',
    'head': 'You remove ',
    'neck': 'You remove ',
    'finger': 'You slide off ',
    'wrist': 'You unclasp ',
    'arms': 'You remove ',
    'hands': 'You remove ',
    'legs': 'You remove ',
    'feet': 'You remove ',
    'pin': 'You unpin ',
    'skinning_sheath': 'You unstrap ',
}

# Default worn location by item_type (fallback if DB worn_location is null)
ITEM_TYPE_SLOTS = {
    'armor': 'torso',
    'shield': 'shoulder_slung',
    'jewelry': 'neck',
    'ring': 'finger',
    'amulet': 'neck',
}

# Container default slots by noun
CONTAINER_SLOTS = {
    'backpack': 'back',
    'rucksack': 'back',
    'haversack': 'back',
    'pouch': 'belt',
    'sheath': 'belt',
    'sack': 'belt',
    'cloak': 'shoulders',
    'cape': 'shoulders',
    'satchel': 'shoulder_slung',
    'purse': 'belt',
    'bag': 'back',
}

TREASURE_CONTAINER_NOUNS = {'box', 'coffer', 'chest', 'strongbox', 'trunk', 'crate'}
LOCKED_ITEM_MARKER = " {L}"
SKINNING_SHEATH_SLOT = "skinning_sheath"


# =========================================================
# Session helpers
# =========================================================

def _ensure_hands(session):
    if not hasattr(session, 'right_hand'):
        session.right_hand = None
    if not hasattr(session, 'left_hand'):
        session.left_hand = None


def _item_display(item):
    """Formatted display name (colored)."""
    name = item.get('short_name') or item.get('name') or 'something'
    display = fmt_item_name(name)
    noun = (item.get('noun') or '').lower()
    if item.get('is_locked') and (noun in TREASURE_CONTAINER_NOUNS or item.get('item_type') == 'container'):
        display += colorize(LOCKED_ITEM_MARKER, TextPresets.SYSTEM)
    return display


def _item_full_name(item):
    """Capitalized display name for player output. No article prefix."""
    from server.core.world.material_data import pretty_item_name
    name = item.get('short_name') or item.get('name') or 'something'
    return pretty_item_name(name)


import re as _re
_ORDINAL_RE = _re.compile(
    r'^(?P<n>\d+)(?:st|nd|rd|th)\s+(?P<rest>.+)$', _re.I
)

def _parse_ordinal(target: str):
    """
    Parse '2nd gauche' -> (2, 'gauche').
    Parse 'gauche'    -> (None, 'gauche').
    """
    m = _ORDINAL_RE.match(target.strip())
    if m:
        return int(m.group('n')), m.group('rest').strip()
    return None, target.strip()


def _match_target(item, target):
    """Check if target string matches an item.
    Strips ordinal prefix first (e.g. '2nd gauche' -> 'gauche').
    Uses word-set matching: every word in the search must appear as a word
    in at least one of the item's name fields, regardless of order.
    e.g. 'midnight ora falchion' matches 'ora midnight falchion'
    """
    _, base = _parse_ordinal(target)
    base = base.lower().strip()
    if not base:
        return False

    # Normalize common compound-word aliases so "keyring" matches "key ring", etc.
    _ALIASES = {
        'keyring':   'key ring',
        'key-ring':  'key ring',
        'lockpick':  'lock pick',
    }
    base = _ALIASES.get(base, base)

    search_words = set(base.split())

    for field in ('short_name', 'name', 'noun'):
        val = (item.get(field) or '').lower()
        if not val:
            continue
        item_words = set(val.split())
        # Strip leading article from item words for matching
        item_words.discard('a')
        item_words.discard('an')
        item_words.discard('the')
        item_words.discard('some')
        if search_words.issubset(item_words):
            return True
    return False


def _find_in_hands(session, target):
    """Find item in hands by partial name. Supports ordinal prefixes.
    '1st gauche' returns the first matching item (right before left).
    '2nd gauche' returns the second matching item.
    Returns (item, hand_name) or (None, None).
    """
    target_l = target.lower()
    ordinal, base = _parse_ordinal(target_l)

    matches = []
    if session.right_hand and _match_target(session.right_hand, base):
        matches.append((session.right_hand, 'right'))
    if session.left_hand and _match_target(session.left_hand, base):
        matches.append((session.left_hand, 'left'))

    if not matches:
        return None, None
    if ordinal is None or ordinal == 1:
        return matches[0]
    idx = ordinal - 1
    if idx < len(matches):
        return matches[idx]
    return None, None


def _find_worn(session, target):
    """Find a worn item (has a slot, not a hand slot, not inside container)."""
    target = target.lower()
    for item in session.inventory:
        slot = item.get('slot')
        if slot and slot not in ('right_hand', 'left_hand') and not item.get('container_id'):
            if _match_target(item, target):
                return item
    return None


def _find_in_container(session, target, container):
    """Find an item inside a specific container. Supports ordinal prefixes.
    Searches both DB-backed inventory items (container_id match) and the
    container's inline contents list (treasure / temp items).
    """
    target_l = target.lower()
    ordinal, base = _parse_ordinal(target_l)
    matches = []

    cont_inv_id = container.get('inv_id')

    # Normalise cont_inv_id to int if possible
    if cont_inv_id is not None:
        try:
            cont_inv_id = int(cont_inv_id)
        except (TypeError, ValueError):
            pass

    if cont_inv_id is not None:
        # Fast path: match by container_id
        for item in session.inventory:
            cid = item.get('container_id')
            if cid is not None:
                try:
                    cid = int(cid)
                except (TypeError, ValueError):
                    pass
                if cid == cont_inv_id and _match_target(item, base):
                    matches.append(item)
    else:
        # cont_inv_id unknown (container not yet DB-persisted in this session).
        # Try to identify the container by matching item_id or name among
        # all items that have a container_id, then collect those whose
        # container_id matches the same parent.
        # Fallback: collect all items that have any container_id set and
        # whose container_id's parent item matches our container object.
        cont_item_id = container.get('item_id')
        # Find any inv_id that belongs to this container by item_id match
        resolved_cont_inv_id = None
        for item in session.inventory:
            if (item.get('item_id') == cont_item_id and
                    item.get('slot') and
                    item.get('slot') not in ('right_hand', 'left_hand') and
                    not item.get('container_id')):
                resolved_cont_inv_id = item.get('inv_id')
                if resolved_cont_inv_id is not None:
                    container['inv_id'] = resolved_cont_inv_id  # cache it
                    break
        if resolved_cont_inv_id is not None:
            try:
                resolved_cont_inv_id = int(resolved_cont_inv_id)
            except (TypeError, ValueError):
                pass
            for item in session.inventory:
                cid = item.get('container_id')
                if cid is not None:
                    try:
                        cid = int(cid)
                    except (TypeError, ValueError):
                        pass
                    if cid == resolved_cont_inv_id and _match_target(item, base):
                        matches.append(item)

    # Inline contents list (loot / treasure items not yet in DB)
    for item in container.get('contents', []):
        if _match_target(item, base):
            matches.append(item)

    if not matches:
        return None
    if ordinal is None or ordinal == 1:
        return matches[0]
    idx = ordinal - 1
    return matches[idx] if idx < len(matches) else None


def _find_container_by_name(session, target):
    """Find a worn/held container by partial name match."""
    target = target.lower()
    # Check hands
    if session.right_hand and session.right_hand.get('item_type') == 'container':
        if _match_target(session.right_hand, target):
            return session.right_hand
    if session.left_hand and session.left_hand.get('item_type') == 'container':
        if _match_target(session.left_hand, target):
            return session.left_hand
    # Check worn containers
    for item in session.inventory:
        if item.get('item_type') == 'container' and item.get('slot'):
            slot = item.get('slot')
            if slot not in ('right_hand', 'left_hand'):
                if _match_target(item, target):
                    return item
    return None


def _find_loose_item(session, target):
    """Find a loose item (no slot, no container_id) - legacy unplaced items."""
    target = target.lower()
    for item in session.inventory:
        if not item.get('slot') and not item.get('container_id'):
            if _match_target(item, target):
                return item
    return None


def _get_container_contents(session, container):
    """Get all items inside a container (type-safe int comparison)."""
    cont_inv_id = container.get('inv_id')
    if cont_inv_id is None:
        return []
    try:
        cont_inv_id = int(cont_inv_id)
    except (TypeError, ValueError):
        return []
    result = []
    for i in session.inventory:
        cid = i.get('container_id')
        if cid is None:
            continue
        try:
            cid = int(cid)
        except (TypeError, ValueError):
            continue
        if cid == cont_inv_id:
            result.append(i)
    return result


def _pick_up_to_hand(session, item):
    """Put an item into an empty hand. Returns hand name or None if both full."""
    if session.right_hand is None:
        session.right_hand = item
        return 'right'
    elif session.left_hand is None:
        session.left_hand = item
        return 'left'
    return None


def _clear_hand(session, hand_name, server=None):
    """Clear a hand slot in-memory and immediately null the DB slot record
    so the item can never be re-restored to the hand by _refresh_inventory."""
    item = None
    if hand_name == 'right':
        item = session.right_hand
        session.right_hand = None
    elif hand_name == 'left':
        item = session.left_hand
        session.left_hand = None
    # Immediately clear the DB slot so this item is never restored to a hand
    # by any subsequent _refresh_inventory call.
    if item and server:
        inv_id = item.get('inv_id')
        if inv_id and server.db:
            try:
                conn = server.db._get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE character_inventory SET slot = NULL WHERE id = %s",
                    (inv_id,)
                )
                conn.close()
            except Exception as _e:
                log.error("_clear_hand DB clear failed: %s", _e)


def _get_worn_slot(item):
    """Determine what body slot an item should be worn on."""
    # 1. Check DB worn_location
    db_loc = item.get('worn_location')
    if db_loc:
        return db_loc
    # 2. Check container noun mapping
    if item.get('item_type') == 'container':
        noun = (item.get('noun') or '').lower()
        if noun in CONTAINER_SLOTS:
            return CONTAINER_SLOTS[noun]
        return 'back'  # default for containers
    # 3. Fall back to item_type
    itype = (item.get('item_type') or '').lower()
    return ITEM_TYPE_SLOTS.get(itype, 'worn')


def _get_worn_items(session):
    """Get all worn items (have slot, not hand slots, not inside container)."""
    return [i for i in session.inventory
            if i.get('slot') and i.get('slot') not in ('right_hand', 'left_hand')
            and not i.get('container_id')]


def _get_worn_containers(session):
    """Get all worn containers."""
    return [i for i in session.inventory
            if i.get('item_type') == 'container'
            and i.get('slot') and i.get('slot') not in ('right_hand', 'left_hand')
            and not i.get('container_id')]


def _is_skinning_sheath(container):
    if not container or container.get('item_type') != 'container':
        return False
    slot = str(container.get('slot') or container.get('worn_location') or '').lower()
    sheath_type = str(container.get('sheath_type') or '').lower()
    return slot == SKINNING_SHEATH_SLOT or sheath_type == 'skinning_tool_sheath'


def _container_priority_key(container):
    noun = str(container.get('noun') or '').lower()
    slot = str(container.get('slot') or container.get('worn_location') or '').lower()
    if _is_skinning_sheath(container):
        return (99, 0, noun)
    if noun == 'backpack':
        return (0, 0, noun)
    if noun in ('cloak', 'cape') or slot == 'shoulders':
        return (1, 0, noun)
    return (2, 0, noun)


def _container_accepts_item(container, item, server, *, allow_special_sheath=False):
    if not container or container.get('item_type') != 'container':
        return False
    if _is_skinning_sheath(container):
        if not allow_special_sheath:
            return False
        if get_skinning_tool_bonus(item, server) is None:
            return False
        allowed_nouns = get_skinning_sheath_nouns(server)
        if allowed_nouns:
            noun = str(item.get('noun') or '').lower().strip()
            return noun in allowed_nouns
        return True
    return True


def _find_best_stow_container(session, server, item_dict, *, allow_special_sheath=False):
    candidates = []
    for cont in _get_worn_containers(session):
        if not _container_accepts_item(
            cont,
            item_dict,
            server,
            allow_special_sheath=allow_special_sheath,
        ):
            continue
        cont.setdefault('opened', True)
        cont_inv_id = cont.get('inv_id')
        if cont_inv_id is None:
            continue
        contents = _get_container_contents(session, cont)
        capacity = cont.get('container_capacity', 10) or 10
        free = capacity - len(contents)
        if free <= 0:
            continue
        candidates.append((_container_priority_key(cont), -free, cont))
    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1]))
    return candidates[0][2]


def _move_held_item_to_container(session, server, hand, container):
    _ensure_hands(session)
    item = session.right_hand if hand == 'right' else session.left_hand
    if not item:
        return False, None, "You aren't holding that."
    if not container:
        return False, None, "You don't have anywhere to stow that."
    if not _container_accepts_item(container, item, server, allow_special_sheath=True):
        return False, None, "That won't fit in there."
    contents = _get_container_contents(session, container)
    capacity = container.get('container_capacity', 10) or 10
    if len(contents) >= capacity:
        return False, None, "That container is full."

    _clear_hand(session, hand, server)

    if server.db and item.get('inv_id'):
        _db_update_container(server, item['inv_id'], container.get('inv_id'))
    elif server.db and session.character_id and item.get('item_id'):
        inv_id = server.db.add_item_to_inventory(session.character_id, item['item_id'])
        if inv_id:
            item['inv_id'] = inv_id
            _db_update_container(server, inv_id, container.get('inv_id'))

    item['slot'] = None
    item['container_id'] = container.get('inv_id')
    if item not in session.inventory:
        session.inventory.append(item)
    return True, item, None


def _move_inventory_item_to_hand(session, server, item, preferred_hand=None):
    _ensure_hands(session)
    hand = None
    if preferred_hand == 'right' and not session.right_hand:
        hand = 'right'
    elif preferred_hand == 'left' and not session.left_hand:
        hand = 'left'
    elif not session.right_hand:
        hand = 'right'
    elif not session.left_hand:
        hand = 'left'
    if not hand:
        return None

    hand_slot = 'right_hand' if hand == 'right' else 'left_hand'
    if server.db and item.get('inv_id'):
        _db_update_slot(server, item.get('inv_id'), hand_slot)
    elif server.db and session.character_id and item.get('item_id'):
        inv_id = server.db.add_item_to_inventory(session.character_id, item['item_id'], slot=hand_slot)
        if inv_id:
            item['inv_id'] = inv_id

    if item in session.inventory:
        session.inventory.remove(item)
    item['slot'] = hand_slot
    item['container_id'] = None
    if hand == 'right':
        session.right_hand = item
    else:
        session.left_hand = item
    return hand


def _db_update_slot(server, inv_id, slot):
    """Update an item's slot in the DB. THE ITEM STAYS IN DB."""
    if server.db and inv_id:
        try:
            server.db.set_inventory_slot(inv_id, slot)
        except Exception as e:
            log.error("Failed to update item slot: %s", e)


def _db_update_container(server, inv_id, container_inv_id):
    """Move an item into a container in DB."""
    if server.db and inv_id:
        try:
            conn = server.db._get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE character_inventory SET container_id = %s, slot = NULL WHERE id = %s",
                        (container_inv_id, inv_id))
            conn.close()
        except Exception as e:
            log.error("Failed to update item container: %s", e)


def _db_clear_container(server, inv_id):
    """Remove an item from its container (but keep in inventory)."""
    if server.db and inv_id:
        try:
            conn = server.db._get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE character_inventory SET container_id = NULL WHERE id = %s", (inv_id,))
            conn.close()
        except Exception as e:
            log.error("Failed to clear item container: %s", e)


def _db_save_item_state(server, inv_id, item_dict):
    """Persist runtime item properties (lock, trap, contents) to extra_data JSON.
    Called after adding a generated box/item to inventory so it survives logout."""
    EXTRA_KEYS = (
        'is_locked', 'lock_difficulty', 'opened',
        'trap_type', 'trapped', 'trap_difficulty', 'trap_checked',
        'trap_detected', 'trap_disarmed', 'trap_variant', 'trap_payload',
        'contents',
        'value', 'base_value', 'skin_quality', 'quality_label', 'base_skin_name',
        'charges', 'spell_number', 'spell_name', 'spell_type', 'spell_level',
    )
    extra = {k: item_dict[k] for k in EXTRA_KEYS if k in item_dict}
    if extra:
        try:
            server.db.save_item_extra_data(inv_id, extra)
        except Exception as e:
            log.error("Failed to save item state extra_data: %s", e)


def _refresh_inventory(server, session):
    """Reload inventory from DB, restore hand items, auto-open containers."""
    restore_inventory_state(server, session)


def _hand_restore_score(item):
    """Prefer sensible hand items over obvious corruption like treasure boxes."""
    item_type = (item.get('item_type') or '').lower()
    noun = (item.get('noun') or '').lower()
    short_name = (item.get('short_name') or item.get('name') or '').lower()
    score = 0

    if item_type == 'weapon':
        score += 100
    elif item_type == 'shield':
        score += 80
    elif item_type == 'container':
        score -= 20

    if noun in TREASURE_CONTAINER_NOUNS:
        score -= 40
    if any(word in short_name for word in ('box', 'coffer', 'chest', 'strongbox', 'trunk', 'crate')):
        score -= 20

    return score


def restore_inventory_state(server, session):
    """Load inventory from DB, restore hands safely, and purge impossible hand duplicates."""
    if not (server.db and session.character_id):
        return

    _ensure_hands(session)
    session.inventory = server.db.get_character_inventory(session.character_id)
    session.right_hand = None
    session.left_hand = None

    hand_candidates = {'right_hand': [], 'left_hand': []}
    for item in session.inventory:
        slot = item.get('slot')
        if slot in hand_candidates:
            hand_candidates[slot].append(item)

    keep_inv_ids = set()
    stale_inv_ids = []

    for slot, items in hand_candidates.items():
        if not items:
            continue

        winner = max(
            items,
            key=lambda row: (_hand_restore_score(row), -(row.get('inv_id') or 0))
        )
        if winner.get('inv_id'):
            keep_inv_ids.add(winner['inv_id'])
        if slot == 'right_hand':
            session.right_hand = winner
        else:
            session.left_hand = winner

        for item in items:
            if item is not winner and item.get('inv_id'):
                stale_inv_ids.append(item['inv_id'])

    session.inventory = [
        item for item in session.inventory
        if item.get('slot') not in ('right_hand', 'left_hand')
    ]

    for item in session.inventory:
        if item.get('item_type') == 'container' and item.get('slot'):
            item['opened'] = True

    _normalize_loose_inventory(server, session)

    for stale_id in stale_inv_ids:
        try:
            server.db.execute_update(
                "UPDATE character_inventory SET slot = NULL WHERE id = %s",
                (stale_id,)
            )
            log.warning("Purged stale hand-slot record inv_id=%s for %s", stale_id, session.character_name)
        except Exception as e:
            log.error("Failed to purge stale hand-slot record %s: %s", stale_id, e)


def _normalize_loose_inventory(server, session):
    """Repair legacy loose inventory rows into valid slots/containers when possible."""
    loose_items = [
        item for item in session.inventory
        if not item.get('slot') and not item.get('container_id')
    ]
    if not loose_items:
        return

    normalized = 0
    hand_moved = []

    for item in loose_items:
        noun = (item.get('noun') or '').lower()
        inv_id = item.get('inv_id')

        if item.get('item_type') == 'container' and noun in CONTAINER_SLOTS and noun not in TREASURE_CONTAINER_NOUNS:
            slot = _get_worn_slot(item)
            if slot:
                item['slot'] = slot
                _db_update_slot(server, inv_id, slot)
                normalized += 1
                continue

        cont = _find_best_stow_container(session, server, item, allow_special_sheath=False)
        if cont and cont.get('inv_id') is not None:
            item['container_id'] = cont.get('inv_id')
            _db_update_container(server, inv_id, cont.get('inv_id'))
            normalized += 1
            continue

        hand = _pick_up_to_hand(session, item)
        if hand:
            hand_slot = 'right_hand' if hand == 'right' else 'left_hand'
            item['slot'] = hand_slot
            _db_update_slot(server, inv_id, hand_slot)
            hand_moved.append(item)
            normalized += 1

    if hand_moved:
        session.inventory = [item for item in session.inventory if item not in hand_moved]

    if normalized:
        log.warning("Normalized %d loose inventory item(s) for %s", normalized, session.character_name)


# =========================================================
# Auto-stow helper (used by LOOT, SKIN, SEARCH)
# =========================================================

def auto_stow_item(session, server, item_dict, *, allow_hands=True, allow_special_sheath=False):
    """Try to auto-stow an item into a worn container, then hands.
    Returns (success, location_name, fail_msg).
    - success=True, location_name='backpack' or 'right hand'
    - success=False, location_name=None, fail_msg='No space...'
    """
    _ensure_hands(session)

    best_cont = _find_best_stow_container(
        session,
        server,
        item_dict,
        allow_special_sheath=allow_special_sheath,
    )
    if best_cont:
        item_id = item_dict.get('item_id') or item_dict.get('id')
        if server.db and session.character_id and item_id:
            inv_id = server.db.add_item_to_inventory(session.character_id, item_id)
            if inv_id:
                _db_update_container(server, inv_id, best_cont.get('inv_id'))
                # Persist box lock/trap/contents so they survive refresh
                _db_save_item_state(server, inv_id, item_dict)
                # Update in-memory directly â€” do NOT call _refresh_inventory here.
                # _refresh_inventory rebuilds hands from DB and will clobber any
                # hand item whose slot DB write hasn't landed yet (race condition
                # that causes items to be silently replaced by previously-looted boxes).
                item_dict['inv_id']       = inv_id
                item_dict['slot']         = None
                item_dict['container_id'] = best_cont.get('inv_id')
                session.inventory.append(item_dict)
                cont_name = best_cont.get('short_name') or best_cont.get('noun') or 'container'
                return True, cont_name, None

    if not allow_hands:
        item_name = item_dict.get('name') or item_dict.get('short_name') or 'something'
        return False, None, f"No container space remaining! {item_name} was left on the ground."

    # Try hands
    if not session.right_hand:
        item_id = item_dict.get('item_id') or item_dict.get('id')
        if server.db and session.character_id and item_id:
            inv_id = server.db.add_item_to_inventory(session.character_id, item_id, slot='right_hand')
            if inv_id:
                _db_save_item_state(server, inv_id, item_dict)
                item_dict['inv_id'] = inv_id
            else:
                log.error("auto_stow_item: DB insert returned None for item_id=%s", item_id)
        else:
            if not item_id:
                log.warning("auto_stow_item: item has no item_id - placing in hand without DB record")
        # Always place in hand in-memory regardless of DB success.
        # An item without inv_id won't survive login but won't cause phantom
        # slot records either â€” it simply won't be persisted.
        item_dict['slot'] = 'right_hand'
        item_dict.setdefault('container_id', None)
        session.right_hand = item_dict
        return True, 'right hand', None

    elif not session.left_hand:
        item_id = item_dict.get('item_id') or item_dict.get('id')
        if server.db and session.character_id and item_id:
            inv_id = server.db.add_item_to_inventory(session.character_id, item_id, slot='left_hand')
            if inv_id:
                _db_save_item_state(server, inv_id, item_dict)
                item_dict['inv_id'] = inv_id
            else:
                log.error("auto_stow_item: DB insert returned None for item_id=%s", item_id)
        else:
            if not item_id:
                log.warning("auto_stow_item: item has no item_id - placing in hand without DB record")
        item_dict['slot'] = 'left_hand'
        item_dict.setdefault('container_id', None)
        session.left_hand = item_dict
        return True, 'left hand', None

    item_name = item_dict.get('name') or item_dict.get('short_name') or 'something'
    return False, None, f"No space remaining! {item_name} was left on the ground."


# =========================================================
# INVENTORY / INV
# =========================================================

async def cmd_inventory(session, cmd, args, server):
    """INVENTORY / INV - GS4-style inventory display."""
    _ensure_hands(session)

    sub = args.strip().lower() if args else ''

    if sub == 'hands':
        await session.send_line('')
        rh = _item_display(session.right_hand) if session.right_hand else 'Empty'
        lh = _item_display(session.left_hand) if session.left_hand else 'Empty'
        await session.send_line('  Right hand: ' + rh)
        await session.send_line('  Left hand:  ' + lh)
        await session.send_line('')
        return

    await session.send_line('')

    # Hands
    rh = _item_full_name(session.right_hand) if session.right_hand else None
    lh = _item_full_name(session.left_hand) if session.left_hand else None

    if rh and lh:
        await session.send_line(f"You are holding {fmt_item_name(rh)} in your right hand and {fmt_item_name(lh)} in your left hand.")
    elif rh:
        await session.send_line(f"You are holding {fmt_item_name(rh)} in your right hand.")
    elif lh:
        await session.send_line(f"You are holding {fmt_item_name(lh)} in your left hand.")

    # Worn items (GS4 style: "You are wearing X, Y, and Z.")
    worn = _get_worn_items(session)
    if worn:
        names = [_item_full_name(i) for i in worn]
        if len(names) == 1:
            worn_str = fmt_item_name(names[0])
        elif len(names) == 2:
            worn_str = fmt_item_name(names[0]) + ' and ' + fmt_item_name(names[1])
        else:
            worn_str = ', '.join(fmt_item_name(n) for n in names[:-1]) + ', and ' + fmt_item_name(names[-1])
        await session.send_line(f"You are wearing {worn_str}.")
    else:
        await session.send_line("You aren't wearing anything unusual.")

    # FULL subcommand: show container contents
    if sub == 'full':
        await session.send_line('')
        containers = _get_worn_containers(session)
        total_items = len(worn)
        for cont in containers:
            contents = _get_container_contents(session, cont)
            total_items += len(contents)
            cname = _item_full_name(cont)
            if contents:
                await session.send_line(f"  In {fmt_item_name(cname)}:")
                for ci in contents:
                    await session.send_line('    ' + _item_display(ci))
            else:
                await session.send_line(f"  In {fmt_item_name(cname)}: (empty)")
        await session.send_line(f"  Total items: {total_items}")

    # Show loose items (unplaced) if any exist
    loose = [i for i in session.inventory
             if not i.get('slot') and not i.get('container_id')]
    if loose:
        await session.send_line('')
        await session.send_line(colorize('  Unplaced items (use GET then WEAR or STOW):', TextPresets.SYSTEM))
        for item in loose:
            await session.send_line('    ' + _item_display(item))

    await session.send_line('')


# =========================================================
# GET / TAKE
# =========================================================

async def cmd_get(session, cmd, args, server):
    """GET <item> [FROM <container>] - Pick up item from ground, container, or unplaced."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Get what?')
        return

    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    target = args.strip().lower()
    from_container = None

    if target.startswith('my '):
        target = target[3:]

    if ' from ' in target:
        parts = target.split(' from ', 1)
        target = parts[0].strip()
        from_container = parts[1].strip()
        if from_container.startswith('my '):
            from_container = from_container[3:]

    if from_container == 'locker':
        try:
            from server.core.commands.player.bank import maybe_handle_locker_get
            handled = await maybe_handle_locker_get(session, target, from_container, server)
            if handled:
                return
        except Exception as e:
            log.error("Locker GET hook failed: %s", e)

    if session.right_hand and session.left_hand:
        await session.send_line('Your hands are full!')
        return

    # GET FROM container
    if from_container:
        cont = _find_container_by_name(session, from_container)
        if not cont:
            await session.send_line("I could not find what you were referring to.")
            return
        if not cont.get('opened'):
            await session.send_line('That is closed.')
            return

        # _find_in_container handles both DB items and inline contents list
        found = _find_in_container(session, target, cont)

        if not found:
            await session.send_line("I could not find what you were referring to.")
            return

        hand = _pick_up_to_hand(session, found)
        if not hand:
            await session.send_line("Your hands are full!")
            return

        hand_slot = 'right_hand' if hand == 'right' else 'left_hand'

        # Determine whether this is an inline (temp) item or a DB-backed item
        is_inline = found in cont.get('contents', [])

        if is_inline:
            # Inline item (treasure drop not yet in DB) â€” add to DB now
            cont['contents'].remove(found)
            if found.get("item_type") == "coins":
                amount = found.get("coin_amount", found.get("value", 0))
                session.silver += amount
                await session.send_line(
                    f"You take {colorize(str(amount) + ' silver coins', TextPresets.ITEM_NAME)} "
                    f"from {_item_display(cont)}."
                )
                if server.db and session.character_id:
                    server.db.save_character_resources(
                        session.character_id,
                        session.health_current, session.mana_current,
                        session.spirit_current, session.stamina_current,
                        session.silver
                    )
                return
            if server.db and session.character_id and found.get("item_id"):
                inv_id = server.db.add_item_to_inventory(
                    session.character_id, found["item_id"], slot=hand_slot
                )
                found["inv_id"] = inv_id
            found["slot"]         = hand_slot
            found["container_id"] = None
            setattr(session, hand_slot, found)
        else:
            # DB-backed item â€” just update slot
            _db_update_slot(server, found.get('inv_id'), hand_slot)
            if found in session.inventory:
                session.inventory.remove(found)
            found['slot']         = hand_slot
            found['container_id'] = None
            setattr(session, hand_slot, found)

        await session.send_line(
            'You remove ' + _item_display(found) + ' from ' + _item_display(cont) + '.'
        )
        await server.world.broadcast_to_room(
            room.id,
            f"{session.character_name} removes {found.get('short_name') or 'something'} "
            f"from {cont.get('short_name') or 'a container'}.",
            exclude=session
        )
        return

    # GET from ground
    ground_items = server.world.get_ground_items(room.id) if hasattr(server, "world") else getattr(room, '_ground_items', [])
    found = None
    for item in ground_items:
        if _match_target(item, target):
            found = item
            break

    if found:
        hand = _pick_up_to_hand(session, found)
        if hand:
            if hasattr(server, "world"):
                server.world.remove_ground_item(room.id, found)
                ground_items = server.world.get_ground_items(room.id)
            else:
                ground_items.remove(found)
            hand_slot = 'right_hand' if hand == 'right' else 'left_hand'
            # Add to DB
            if server.db and session.character_id and found.get('item_id'):
                inv_id = server.db.add_item_to_inventory(session.character_id, found['item_id'], slot=hand_slot)
                found['inv_id'] = inv_id
                extra = {
                    key: value for key, value in dict(found).items()
                    if key not in {
                        'inv_id', 'item_id', 'name', 'short_name', 'noun', 'article',
                        'item_type', 'weight', 'value', 'slot', 'container_id',
                        'description',
                        'ground_id', 'room_id', 'dropped_source', 'created_at', 'expires_at',
                    }
                }
                if extra:
                    server.db.save_item_extra_data(inv_id, extra)
            found['slot'] = hand_slot
            found['container_id'] = None
            for key in ('ground_id', 'room_id', 'dropped_source', 'created_at', 'expires_at'):
                found.pop(key, None)
            await session.send_line('You pick up ' + _item_display(found) + '.')
            await server.world.broadcast_to_room(
                room.id,
                session.character_name + ' picks up ' + (found.get('short_name') or 'something') + '.',
                exclude=session
            )
        else:
            await session.send_line('Your hands are full!')
        return

    # GET from unplaced items (legacy)
    found = _find_loose_item(session, target)
    if found:
        hand = _pick_up_to_hand(session, found)
        if hand:
            hand_slot = 'right_hand' if hand == 'right' else 'left_hand'
            _db_update_slot(server, found.get('inv_id'), hand_slot)
            session.inventory.remove(found)
            found['slot'] = hand_slot
            await session.send_line('You pick up ' + _item_display(found) + '.')
        else:
            await session.send_line('Your hands are full!')
        return

    await session.send_line("I could not find what you were referring to.")


# =========================================================
# DROP
# =========================================================

async def cmd_drop(session, cmd, args, server):
    """DROP <item> - Drop held item to ground."""
    _ensure_hands(session)

    room = session.current_room
    if not room:
        await session.send_line("You can't do that right now.")
        return

    if not args:
        if session.right_hand:
            item = session.right_hand
            _clear_hand(session, 'right', server)
        elif session.left_hand:
            item = session.left_hand
            _clear_hand(session, 'left', server)
        else:
            await session.send_line("You aren't holding anything.")
            return
    else:
        item, hand = _find_in_hands(session, args.strip())
        if item:
            _clear_hand(session, hand, server)
        else:
            # Not in hands â€” check loose/unplaced items (no slot, no container_id)
            item = _find_loose_item(session, args.strip())
            if not item:
                await session.send_line("You don't seem to be holding that.")
                return
            # Remove from in-memory inventory
            if item in session.inventory:
                session.inventory.remove(item)
            # Remove from DB â€” purge all orphaned records for this item
            if server.db and item.get('inv_id'):
                server.db.remove_item_from_inventory(item['inv_id'])
            elif server.db and session.character_id and item.get('item_id'):
                try:
                    conn = server.db._get_conn()
                    cur  = conn.cursor()
                    cur.execute(
                        "DELETE FROM character_inventory "
                        "WHERE character_id = %s AND item_id = %s "
                        "AND slot IS NULL AND container_id IS NULL",
                        (session.character_id, item['item_id'])
                    )
                    conn.close()
                except Exception as _e:
                    log.error("cmd_drop loose item purge failed: %s", _e)
            if hasattr(server, "world"):
                server.world.add_ground_item(
                    room.id,
                    item,
                    dropped_by_character_id=session.character_id,
                    dropped_by_name=session.character_name,
                    source="drop",
                )
            await session.send_line('You drop ' + _item_display(item) + '.')
            await server.world.broadcast_to_room(
                room.id,
                session.character_name + ' drops ' + (item.get('short_name') or 'something') + '.',
                exclude=session
            )
            return

    if hasattr(server, "world"):
        server.world.add_ground_item(
            room.id,
            item,
            dropped_by_character_id=session.character_id,
            dropped_by_name=session.character_name,
            source="drop",
        )
    else:
        if not hasattr(room, '_ground_items'):
            room._ground_items = []
        room._ground_items.append(item)

    # Remove from DB
    if server.db and item.get('inv_id'):
        server.db.remove_item_from_inventory(item['inv_id'])
    elif server.db and session.character_id and item.get('item_id'):
        # inv_id wasn't set â€” sweep ALL records for this character+item_id
        # that have no container (slot=NULL or slot=hand) to avoid ghost "unplaced" entries.
        try:
            conn = server.db._get_conn()
            cur  = conn.cursor()
            cur.execute(
                "DELETE FROM character_inventory "
                "WHERE character_id = %s AND item_id = %s "
                "AND container_id IS NULL",
                (session.character_id, item['item_id'])
            )
            conn.close()
        except Exception as _e:
            log.error("cmd_drop orphan sweep failed: %s", _e)

    await session.send_line('You drop ' + _item_display(item) + '.')
    await server.world.broadcast_to_room(
        room.id,
        session.character_name + ' drops ' + (item.get('short_name') or 'something') + '.',
        exclude=session
    )


# =========================================================
# PUT
# =========================================================

async def cmd_put(session, cmd, args, server):
    """PUT <item> IN <container> - Put held item into a worn container."""
    _ensure_hands(session)

    if args and ' on ' in args.lower():
        try:
            from server.core.commands.player.crafting import handle_special_put
            handled = await handle_special_put(session, args, server)
            if handled:
                return
        except Exception as e:
            log.error("Crafting PUT hook failed: %s", e)

    if not args or ' in ' not in args.lower():
        await session.send_line('Usage: PUT <item> IN <container>')
        return

    parts = args.lower().split(' in ', 1)
    item_name = parts[0].strip()
    cont_name = parts[1].strip()

    if item_name.startswith('my '):
        item_name = item_name[3:]
    if cont_name.startswith('my '):
        cont_name = cont_name[3:]

    if cont_name == 'locker':
        try:
            from server.core.commands.player.bank import maybe_handle_locker_put
            handled = await maybe_handle_locker_put(session, item_name, cont_name, server)
            if handled:
                return
        except Exception as e:
            log.error("Locker PUT hook failed: %s", e)

    item, hand = _find_in_hands(session, item_name)
    if not item:
        await session.send_line("You aren't holding that.")
        return

    cont = _find_container_by_name(session, cont_name)
    if not cont:
        await session.send_line("I could not find what you were referring to.")
        return

    if not cont.get('opened'):
        await session.send_line('That is closed.')
        return

    if not _container_accepts_item(cont, item, server, allow_special_sheath=True):
        if _is_skinning_sheath(cont):
            await session.send_line("Only properly-sized skinning tools will fit in that sheath.")
        else:
            await session.send_line("That won't fit in there.")
        return

    # Capacity check
    contents = _get_container_contents(session, cont)
    capacity = cont.get('container_capacity', 10) or 10
    if len(contents) >= capacity:
        await session.send_line("That container is full.")
        return

    _clear_hand(session, hand, server)

    # Update DB: move item into container
    if server.db and item.get('inv_id'):
        _db_update_container(server, item['inv_id'], cont.get('inv_id'))
    elif server.db and session.character_id and item.get('item_id'):
        inv_id = server.db.add_item_to_inventory(session.character_id, item['item_id'])
        if inv_id:
            item['inv_id'] = inv_id
            _db_update_container(server, inv_id, cont.get('inv_id'))

    # Update in-memory directly â€” never call _refresh_inventory after a hand operation
    # as it rebuilds hands from DB and can restore stale slot records for old items.
    item['slot']         = None
    item['container_id'] = cont.get('inv_id')
    if item not in session.inventory:
        session.inventory.append(item)

    await session.send_line('You put ' + _item_display(item) + ' in ' + _item_display(cont) + '.')
    await server.world.broadcast_to_room(
        session.current_room.id if session.current_room else 0,
        f"{session.character_name} puts {item.get('short_name') or 'something'} in "
        f"{cont.get('short_name') or 'a container'}.",
        exclude=session
    )


# =========================================================
# GIVE
# =========================================================

async def cmd_give(session, cmd, args, server):
    """GIVE <item> TO <player|npc> - Give held item to another player or a quest NPC."""
    _ensure_hands(session)

    if not args or ' to ' not in args.lower():
        await session.send_line('Usage: GIVE <item> TO <player>')
        return

    parts = args.lower().split(' to ', 1)
    item_name = parts[0].strip()
    target_name = parts[1].strip()

    item, hand = _find_in_hands(session, item_name)
    if not item:
        await session.send_line("You aren't holding that.")
        return

    target = server.sessions.find_by_name(target_name)
    if target and target.current_room and target.current_room.id == session.current_room.id:
        _ensure_hands(target)
        if target.right_hand and target.left_hand:
            await session.send_line(target.character_name + "'s hands are full.")
            return

        _clear_hand(session, hand, server)

        target_hand = _pick_up_to_hand(target, item)

        # DB transfer
        if server.db and item.get('inv_id'):
            server.db.remove_item_from_inventory(item['inv_id'])
        if server.db and target.character_id and item.get('item_id'):
            t_hand_slot = 'right_hand' if target_hand == 'right' else 'left_hand'
            inv_id = server.db.add_item_to_inventory(target.character_id, item['item_id'], slot=t_hand_slot)
            item['inv_id'] = inv_id

        disp = _item_display(item)
        await session.send_line('You give ' + disp + ' to ' + target.character_name + '.')
        await target.send_line(session.character_name + ' gives you ' + disp + '.')
        return

    npc = None
    if hasattr(server, "npcs") and getattr(session, "current_room", None):
        npc = server.npcs.find_npc_in_room(session.current_room.id, target_name)
    if not npc:
        await session.send_line("You don't see them here.")
        return

    noun = str(item.get("noun") or item.get("short_name") or item.get("name") or "").strip().lower().replace(" ", "_")
    quest_engine = getattr(server, "guild", None)
    event_name = f"give_npc:{npc.template_id}:{noun}" if noun else ""
    quest_match = False
    if quest_engine and event_name and getattr(session, "character_id", None):
        for active in quest_engine.get_active_quests(session.character_id, general_only=True):
            current_stage = active.get("current_stage") or {}
            if (current_stage.get("objective_event") or "").lower() == event_name:
                quest_match = True
                break
    if not quest_match:
        await session.send_line(f"{npc.display_name} has no use for that right now.")
        return

    _clear_hand(session, hand, server)
    if server.db and item.get('inv_id'):
        server.db.remove_item_from_inventory(item['inv_id'])

    disp = _item_display(item)
    await session.send_line('You give ' + disp + ' to ' + npc.display_name + '.')
    await session.send_line(npc_speech(npc.display_name, f'accepts {disp} with a nod.'))
    await quest_engine.record_event(session, event_name)


# =========================================================
# SWAP
# =========================================================

async def cmd_swap(session, cmd, args, server):
    """SWAP - Swap items between hands."""
    _ensure_hands(session)

    if not session.right_hand and not session.left_hand:
        await session.send_line("You have nothing to swap.")
        return

    session.right_hand, session.left_hand = session.left_hand, session.right_hand

    # Update DB slots
    if session.right_hand and session.right_hand.get('inv_id'):
        _db_update_slot(server, session.right_hand['inv_id'], 'right_hand')
    if session.left_hand and session.left_hand.get('inv_id'):
        _db_update_slot(server, session.left_hand['inv_id'], 'left_hand')

    if session.right_hand and session.left_hand:
        await session.send_line(
            'You swap ' + _item_display(session.right_hand) + ' to your right hand and '
            + _item_display(session.left_hand) + ' to your left hand.')
    elif session.right_hand:
        await session.send_line('You swap ' + _item_display(session.right_hand) + ' to your right hand.')
    else:
        await session.send_line('You swap ' + _item_display(session.left_hand) + ' to your left hand.')


# =========================================================
# WEAR
# =========================================================

async def cmd_wear(session, cmd, args, server):
    """WEAR <item> - Wear or equip a held item."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Wear what?')
        return

    target = args.strip()
    if target.lower().startswith('my '):
        target = target[3:]

    item, hand = _find_in_hands(session, target)
    if not item:
        await session.send_line("You need to be holding that first.")
        return

    itype = (item.get('item_type') or '').lower()
    if itype == 'weapon':
        await session.send_line("You can't wear that. Weapons are wielded by holding them.")
        return

    # Determine slot
    slot = _get_worn_slot(item)

    # GS4 allows multiple items per slot. No blocking.
    # (Unique restriction only for armor on torso)
    if slot == 'torso' and itype == 'armor':
        for worn_item in _get_worn_items(session):
            if worn_item.get('slot') == 'torso' and worn_item.get('item_type') == 'armor':
                await session.send_line("You are already wearing armor.")
                return

    _clear_hand(session, hand, server)

    # Update DB: change slot from hand to worn slot
    if server.db and item.get('inv_id'):
        _db_update_slot(server, item['inv_id'], slot)
    elif server.db and session.character_id and item.get('item_id'):
        inv_id = server.db.add_item_to_inventory(session.character_id, item['item_id'], slot=slot)
        if inv_id:
            item['inv_id'] = inv_id

    # Update in-memory directly - no _refresh_inventory
    item['slot']         = slot
    item['container_id'] = None
    if item not in session.inventory:
        session.inventory.append(item)

    # Auto-open containers when worn
    if item.get('item_type') == 'container':
        item['opened'] = True

    disp = _item_display(item)
    prefix, suffix = WEAR_VERBS.get(slot, ('You put on ', '.'))
    await session.send_line(prefix + disp + suffix)

    await server.world.broadcast_to_room(
        session.current_room.id if session.current_room else 0,
        session.character_name + ' puts on ' + (item.get('short_name') or 'something') + '.',
        exclude=session
    )


# =========================================================
# REMOVE
# =========================================================

async def cmd_remove(session, cmd, args, server):
    """REMOVE <item> - Remove worn item to hand."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Remove what?')
        return

    if session.right_hand and session.left_hand:
        await session.send_line('Your hands are full!')
        return

    target = args.strip()
    if target.lower().startswith('my '):
        target = target[3:]

    item = _find_worn(session, target)
    if not item:
        await session.send_line("You aren't wearing that.")
        return

    old_slot = item.get('slot', '')

    # Move to hand
    hand = _pick_up_to_hand(session, item)
    hand_slot = 'right_hand' if hand == 'right' else 'left_hand'

    # Update DB
    _db_update_slot(server, item.get('inv_id'), hand_slot)
    session.inventory.remove(item)
    item['slot'] = hand_slot

    disp = _item_display(item)
    verb = REMOVE_VERBS.get(old_slot, 'You remove ')
    await session.send_line(verb + disp + '.')
    await server.world.broadcast_to_room(
        session.current_room.id if session.current_room else 0,
        f"{session.character_name} removes {item.get('short_name') or 'something'}.",
        exclude=session
    )


# =========================================================
# STOW
# =========================================================

async def cmd_stow(session, cmd, args, server):
    """STOW [item] - Stow held item into first available container."""
    _ensure_hands(session)

    if args and ' in ' in args.lower():
        await cmd_put(session, "put", args, server)
        return

    if not args:
        if session.right_hand:
            item = session.right_hand
            hand = 'right'
        elif session.left_hand:
            item = session.left_hand
            hand = 'left'
        else:
            await session.send_line("You have nothing to stow.")
            return
    else:
        item, hand = _find_in_hands(session, args.strip())
        if not item:
            await session.send_line("You aren't holding that.")
            return

    default_cont = _find_best_stow_container(session, server, item, allow_special_sheath=False)

    if not default_cont:
        await session.send_line("You don't have any containers to stow that in.")
        return

    # Auto-open
    if not default_cont.get('opened'):
        default_cont['opened'] = True

    # Capacity
    contents = _get_container_contents(session, default_cont)
    capacity = default_cont.get('container_capacity', 10) or 10
    if len(contents) >= capacity:
        await session.send_line("Your " + (default_cont.get('noun') or 'container') + " is full.")
        return

    _clear_hand(session, hand, server)

    # Update DB: move to container
    if server.db and item.get('inv_id'):
        _db_update_container(server, item['inv_id'], default_cont.get('inv_id'))
    elif server.db and session.character_id and item.get('item_id'):
        inv_id = server.db.add_item_to_inventory(session.character_id, item['item_id'])
        if inv_id:
            item['inv_id'] = inv_id
            _db_update_container(server, inv_id, default_cont.get('inv_id'))

    # Update in-memory directly - no _refresh_inventory
    item['slot']         = None
    item['container_id'] = default_cont.get('inv_id')
    if item not in session.inventory:
        session.inventory.append(item)

    await session.send_line('You put ' + _item_display(item) + ' in ' + _item_display(default_cont) + '.')
    await server.world.broadcast_to_room(
        session.current_room.id if session.current_room else 0,
        f"{session.character_name} stows {item.get('short_name') or 'something'} in "
        f"their {default_cont.get('noun') or 'container'}.",
        exclude=session
    )


# =========================================================
# OPEN
# =========================================================

async def cmd_open(session, cmd, args, server):
    """OPEN <container> - Open a container."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Open what?')
        return

    target = args.strip().lower()
    if target.startswith('my '):
        target = target[3:]

    try:
        from server.core.commands.player.bank import maybe_handle_locker_open
        handled = await maybe_handle_locker_open(session, target, server)
        if handled:
            return
    except Exception as e:
        log.error("Locker OPEN hook failed: %s", e)

    cont = _find_container_by_name(session, target)
    if cont:
        if cont.get('opened'):
            await session.send_line('That is already open.')
        elif cont.get('is_locked'):
            await session.send_line(
                colorize(
                    f"You cannot open {_item_display(cont)} - it is locked.  "
                    "You will need to pick the lock first.",
                    TextPresets.WARNING
                )
            )
        else:
            if cont.get("trapped") and not cont.get("trap_disarmed"):
                try:
                    from server.core.commands.player.lockpicking import _trigger_trap
                    trap = server.traps.get_trap_def(cont.get("trap_type")) if getattr(server, "traps", None) else None
                    await session.send_line(colorize(
                        f"You carefully start to open {_item_display(cont)}...",
                        TextPresets.WARNING
                    ))
                    if trap:
                        await _trigger_trap(session, server, cont, trap, source="open")
                    else:
                        await session.send_line(colorize("Something hidden in the latch snaps at you!", TextPresets.WARNING))
                    return
                except Exception as e:
                    log.error("OPEN trap trigger failed: %s", e, exc_info=True)
            cont['opened'] = True
            await session.send_line('You open ' + _item_display(cont) + '.')
        return

    await session.send_line("I could not find what you were referring to.")


# =========================================================
# CLOSE
# =========================================================

async def cmd_close(session, cmd, args, server):
    """CLOSE <container> - Close a container."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Close what?')
        return

    target = args.strip().lower()
    if target.startswith('my '):
        target = target[3:]

    try:
        from server.core.commands.player.bank import maybe_handle_locker_close
        handled = await maybe_handle_locker_close(session, target, server)
        if handled:
            return
    except Exception as e:
        log.error("Locker CLOSE hook failed: %s", e)

    cont = _find_container_by_name(session, target)
    if cont:
        if not cont.get('opened'):
            await session.send_line('That is already closed.')
        else:
            cont['opened'] = False
            await session.send_line('You close ' + _item_display(cont) + '.')
        return

    await session.send_line("I could not find what you were referring to.")


# =========================================================
# INSPECT HELPERS
# =========================================================

# ASG group name table (GS4 canon)
_ASG_GROUPS = {
    1: "cloth / unarmored", 2: "cloth / unarmored",
    3: "soft leather", 4: "soft leather",
    5: "hard leather", 6: "hard leather",
    7: "double leather", 8: "double leather",
    9: "metal breastplate", 10: "metal breastplate",
    11: "chain mail", 12: "chain mail",
    13: "double chain", 14: "double chain",
    15: "plate armor", 16: "plate armor",
    17: "heavy plate", 18: "heavy plate",
    19: "full plate", 20: "full plate",
}

def _item_stat_lines(item: dict) -> list:
    """
    Return a list of colored strings describing an item's stats.
    Used by both INSPECT and the shop ORDER/CONFIRM preview.
    All stats are shown - no hidden numbers.
    """
    from server.core.protocol.colors import colorize, TextPresets
    from math import ceil

    lines = []
    itype = (item.get('item_type') or '').lower()

    SYS  = TextPresets.SYSTEM       # bold blue  - labels
    VAL  = TextPresets.ITEM_NAME    # yellow     - values
    WARN = TextPresets.WARNING      # bright yellow - penalties
    OK   = TextPresets.HEALTH_FULL  # bright green  - bonuses

    def _kv(label, value, color=VAL):
        return f"  {colorize(label + ':', SYS)} {colorize(str(value), color)}"

    def _section(title):
        return colorize(f"  -- {title} {'-' * max(0, 38 - len(title))}", SYS)

    # â”€â”€ Weapon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if itype == 'weapon':
        cat  = (item.get('weapon_category') or item.get('weapon_type') or 'unknown').replace('_', ' ')
        df   = item.get('damage_factor') or 0.0
        spd  = item.get('weapon_speed') or 5
        dtype = (item.get('damage_type') or 'slash').replace(',', ' / ')
        eb   = item.get('enchant_bonus') or 0
        ab   = item.get('attack_bonus') or 0
        db   = item.get('damage_bonus') or 0
        wt   = item.get('weight') or 1.0
        lvl  = item.get('level_required') or (ceil(eb / 2) if eb else 0)
        mat  = item.get('material') or ''

        lines.append(_section('Weapon Stats'))
        lines.append(_kv('Type',        cat.title()))
        lines.append(_kv('Damage type', dtype))
        lines.append(_kv('Damage factor (DF)', f"{float(df):.3f}",
                         OK if df >= 0.40 else VAL))
        lines.append(_kv('Base roundtime',     f"{spd}s"))
        if eb:
            lines.append(_kv('Enchantment',    f"+{eb}", OK))
        if ab:
            lines.append(_kv('Attack bonus',   f"+{ab}", OK))
        if db:
            lines.append(_kv('Damage bonus',   f"+{db}", OK))
        if lvl:
            lines.append(_kv('Level required', str(lvl),
                              WARN if lvl > 0 else VAL))
        if mat:
            lines.append(_kv('Material', mat.title()))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))
        val = item.get('value') or 0
        lines.append(_kv('Base value', f"~{val} silver"))

    # â”€â”€ Armor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype == 'armor':
        asg  = item.get('armor_asg') or 1
        grp  = _ASG_GROUPS.get(int(asg), f"ASG {asg}")
        eb   = item.get('enchant_bonus') or 0
        ap   = item.get('action_penalty') or 0
        sh   = item.get('spell_hindrance') or 0
        db   = item.get('defense_bonus') or 0
        wt   = item.get('weight') or 1.0
        lvl  = item.get('level_required') or (ceil(eb / 2) if eb else 0)
        mat  = item.get('material') or ''

        lines.append(_section('Armor Stats'))
        lines.append(_kv('Armor type',       grp.title()))
        lines.append(_kv('ASG',              str(asg)))
        if eb:
            lines.append(_kv('Enchantment',  f"+{eb}", OK))
        if db:
            lines.append(_kv('Defense bonus',f"+{db}", OK))
        if ap:
            lines.append(_kv('Action penalty',f"{ap}%", WARN))
        if sh:
            lines.append(_kv('Spell hindrance', f"{sh}%", WARN))
        if lvl:
            lines.append(_kv('Level required', str(lvl), WARN))
        if mat:
            lines.append(_kv('Material', mat.title()))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))
        val = item.get('value') or 0
        lines.append(_kv('Base value', f"~{val} silver"))

    # â”€â”€ Shield â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype == 'shield':
        size = (item.get('shield_size') or 'small').title()
        ds   = item.get('shield_ds') or 0
        evp  = item.get('shield_evade_penalty') or 0
        eb   = item.get('enchant_bonus') or 0
        wt   = item.get('weight') or 1.0
        lvl  = item.get('level_required') or (ceil(eb / 2) if eb else 0)
        mat  = item.get('material') or ''

        lines.append(_section('Shield Stats'))
        lines.append(_kv('Size',            size))
        lines.append(_kv('Shield DS',       f"+{ds}", OK if ds > 0 else VAL))
        if evp:
            lines.append(_kv('Evade penalty', f"{evp}%", WARN))
        if eb:
            lines.append(_kv('Enchantment', f"+{eb}", OK))
        if lvl:
            lines.append(_kv('Level required', str(lvl), WARN))
        if mat:
            lines.append(_kv('Material', mat.title()))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))
        val = item.get('value') or 0
        lines.append(_kv('Base value', f"~{val} silver"))

    # â”€â”€ Container â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype == 'container':
        cap  = item.get('container_capacity') or 0
        wt   = item.get('weight') or 1.0
        loc  = (item.get('worn_location') or '').replace('_', ' ')

        lines.append(_section('Container Stats'))
        if cap:
            lines.append(_kv('Capacity', f"{cap} items", OK))
        else:
            lines.append(_kv('Capacity', 'unlimited / unknown'))
        if loc:
            lines.append(_kv('Worn on', loc.title()))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs (empty)"))
        val = item.get('value') or 0
        lines.append(_kv('Base value', f"~{val} silver"))

    # â”€â”€ Gem â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype == 'gem':
        val = item.get('value') or 0
        fam = (item.get('gem_family') or '').title()
        lines.append(_section('Gem'))
        if fam:
            lines.append(_kv('Family', fam))
        lines.append(_kv('Appraised value', f"~{val} silver", OK))

    # â”€â”€ Herb / Consumable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype in ('herb', 'consumable'):
        ht   = (item.get('herb_heal_type') or item.get('heal_type') or '').replace('_', ' ')
        ha   = item.get('herb_heal_amount') or item.get('heal_amount') or 0
        hr   = item.get('herb_roundtime') or 0
        rank = item.get('heal_rank') or 0
        wt   = item.get('weight') or 1.0

        lines.append(_section('Herb / Consumable Stats'))
        if ht:
            lines.append(_kv('Heals', ht.title(), OK))
        if ha:
            lines.append(_kv('Heal amount', f"+{ha}", OK))
        if rank:
            lines.append(_kv('Heal rank', str(rank)))
        if hr:
            lines.append(_kv('Use roundtime', f"{hr}s"))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))

    # â”€â”€ Lockpick â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elif itype == 'misc' and (item.get('lockpick_modifier') or 0) != 0:
        lpm  = float(item.get('lockpick_modifier') or 0)
        wt   = item.get('weight') or 1.0
        lines.append(_section('Lockpick Stats'))
        lines.append(_kv('Pick modifier', f"{lpm:+.2f}", OK if lpm > 0 else WARN))
        lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))
        val = item.get('value') or 0
        lines.append(_kv('Base value', f"~{val} silver"))

    # â”€â”€ Misc / Jewelry â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    else:
        wt  = item.get('weight') or 1.0
        val = item.get('value') or 0
        eb  = item.get('enchant_bonus') or 0
        loc = (item.get('worn_location') or '').replace('_', ' ')
        if eb or loc or val:
            lines.append(_section('Item Info'))
            if loc:
                lines.append(_kv('Worn on', loc.title()))
            if eb:
                lines.append(_kv('Enchantment', f"+{eb}", OK))
            lines.append(_kv('Weight', f"{float(wt):.1f} lbs"))
            if val:
                lines.append(_kv('Base value', f"~{val} silver"))

    return lines


# =========================================================
# INSPECT
# =========================================================

async def cmd_inspect(session, cmd, args, server):
    """INSPECT <item> - Examine an item in detail."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Inspect what?')
        return

    target = args.strip()
    if target.lower().startswith('my '):
        target = target[3:]

    try:
        from server.core.commands.player.bank import maybe_handle_locker_inspect
        handled = await maybe_handle_locker_inspect(session, target, server)
        if handled:
            return
    except Exception as e:
        log.error("Locker INSPECT hook failed: %s", e)

    # Search: hands first, then worn, then containers, then loose
    item, _ = _find_in_hands(session, target)
    if not item:
        item = _find_worn(session, target)
    if not item:
        # Search inside all worn containers
        for cont in _get_worn_containers(session):
            item = _find_in_container(session, target, cont)
            if item:
                break
    if not item:
        item = _find_loose_item(session, target)

    if not item:
        await session.send_line("I could not find what you were referring to.")
        return

    await session.send_line('')
    full_name = _item_full_name(item)
    await session.send_line(f"You carefully inspect {fmt_item_name(full_name)}.")
    await session.send_line('')

    desc = item.get('description') or item.get('examine_text') or ''

    # Dye vial - show color, usage instructions, and price hint
    if item.get('item_type') == 'dye':
        from server.core.protocol.colors import colorize, TextPresets
        dye_color = (item.get('color') or '').strip()
        await session.send_line(desc)
        await session.send_line('')
        await session.send_line(colorize('  -- Dye Vial ----------------------------------', TextPresets.SYSTEM))
        if dye_color:
            await session.send_line(f"  Color  : {colorize(dye_color, TextPresets.ITEM_NAME)}")
        await session.send_line( "  Usage  : DYE <worn item> " + (dye_color or '<color>'))
        await session.send_line( "           DYE HAIR " + (dye_color or '<color>'))
        await session.send_line( "           DYE <item> REMOVE   (strips dye, no vial needed)")
        await session.send_line( "  Notes  : One vial per application.  Overwrites existing color.")
        await session.send_line("           Works on anything you wear - clothing, armor, accessories.")
        await session.send_line(colorize('  ---------------------------------------------', TextPresets.SYSTEM))
        await session.send_line('')
        return

    # Order slip â€” show full order details instead of generic stats
    if item.get("is_order_slip") or item.get("noun") == "order slip":
        from server.core.protocol.colors import colorize, TextPresets
        # Pull details from session's active/ready order lists
        inv_id = item.get("inv_id")
        order = None
        for lst in (getattr(session, "_active_orders", []), getattr(session, "_ready_orders", [])):
            order = next((o for o in lst if o.get("slip_inv_id") == inv_id), None)
            if order:
                break
        if order:
            oitem   = order["item"]
            mat     = oitem.get("material", "")
            color   = oitem.get("color", "")
            bonus   = oitem.get("enchant_bonus", 0)
            paid    = order.get("price_paid", 0)
            shop    = order.get("shop_name", "Unknown")
            ready   = order.get("ready", False)
            status  = colorize("READY - return to shop and type REDEEM", TextPresets.ITEM_NAME) \
                      if ready else colorize("In progress...", TextPresets.SYSTEM)
            await session.send_line(colorize("  \u2500\u2500 Custom Order Details \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500", TextPresets.SYSTEM))
            await session.send_line(f"  Item   : {colorize(oitem.get('name','unknown'), TextPresets.ITEM_NAME)}")
            if mat:
                bonus_str = f" (+{bonus})" if bonus else ""
                await session.send_line(f"  Material: {mat}{bonus_str}")
            if color:
                await session.send_line(f"  Color  : {color}")
            await session.send_line(f"  Paid   : {paid:,} silver")
            await session.send_line(f"  Shop   : {shop}")
            await session.send_line(f"  Status : {status}")
            await session.send_line(colorize("  " + "\u2500" * 42, TextPresets.SYSTEM))
        else:
            await session.send_line("  This slip contains details of a custom order.")
            await session.send_line("  Return to the shop that issued it and type REDEEM when ready.")
        await session.send_line('')
        return
    if desc:
        await session.send_line(f"  {desc}")
        await session.send_line('')

    for stat_line in _item_stat_lines(item):
        await session.send_line(stat_line)

    # Lore
    lore = item.get('lore_text')
    if lore:
        await session.send_line('')
        await session.send_line(f"  {lore}")

    await session.send_line('')


# =========================================================
# LOOK IN (container)
# =========================================================

async def cmd_look_in(session, cmd, args, server):
    """LOOK IN <container> - Look inside a container."""
    _ensure_hands(session)

    if not args:
        await session.send_line('Look in what?')
        return

    target = args.strip().lower()
    if target.startswith('my '):
        target = target[3:]

    try:
        from server.core.commands.player.bank import maybe_handle_locker_look_in
        handled = await maybe_handle_locker_look_in(session, target, server)
        if handled:
            return
    except Exception as e:
        log.error("Locker LOOK IN hook failed: %s", e)

    cont = _find_container_by_name(session, target)
    if not cont:
        await session.send_line("I could not find what you were referring to.")
        return

    if cont.get("destroyed"):
        await session.send_line("That has been destroyed.")
        return

    if not cont.get('opened'):
        if cont.get("is_locked"):
            await session.send_line('That is locked.')
        else:
            await session.send_line('That is closed.')
        return

    # Gather items: inline contents list + DB-backed inventory items
    inline   = cont.get("contents", [])
    db_items = _get_container_contents(session, cont)
    all_items = inline + db_items

    disp = _item_display(cont)
    if all_items:
        await session.send_line(f'In {disp} you see:')
        for ci in all_items:
            await session.send_line('  ' + colorize(ci['name'], TextPresets.ITEM_NAME))
    else:
        await session.send_line(f'In {disp} you see nothing.')


# =========================================================
# LOOT
# =========================================================

async def cmd_loot(session, cmd, args, server):
    """LOOT - Search a dead creature for treasure. Auto-stows items."""
    _ensure_hands(session)
    room = session.current_room
    room_id = room.id if room else 0
    dead = server.creatures.get_dead_creatures_in_room(room_id)

    if not dead:
        await session.send_line('There is nothing here to loot.')
        return

    creature = dead[0]
    found_anything = False
    left_on_ground = []
    can_still_skin = bool(getattr(creature, 'skin', None) and not getattr(creature, 'skinned', False))
    was_already_searched = bool(getattr(creature, 'searched', False))

    await session.send_line('You search ' + creature.full_name + '...')
    await server.world.broadcast_to_room(
        room.id,
        f"{session.character_name} searches {creature.full_name}...",
        exclude=session
    )

    if was_already_searched:
        msg = '  You find nothing more of value.'
        if can_still_skin:
            msg += '  You could still try to skin it.'
        await session.send_line(msg)
    elif generate_treasure and server.db:
        creature.searched = True
        loot = generate_treasure(server.db, creature, server=server)

        if loot['coins'] > 0:
            session.silver += loot['coins']
            found_anything = True
            await session.send_line('  You find ' + colorize(str(loot['coins']) + ' silver coins', TextPresets.ITEM_NAME) + '!')
            await server.world.broadcast_to_room(
                room.id,
                f"  {session.character_name} finds {loot['coins']} silver coins!",
                exclude=session
            )

        for item in loot.get('items', []):
            item_id = item.get('item_id') or item.get('id')
            if not item_id:
                item_id = server.db.get_or_create_item(
                    name=item.get('name', 'something'),
                    short_name=item.get('short_name', 'something'),
                    noun=item.get('noun', 'item'),
                    item_type=item.get('item_type', 'misc'),
                    value=item.get('value', 0),
                    description=item.get('description', '')
                )
            item['item_id'] = item_id
            found_anything = True
            display = item.get('name') or item.get('short_name') or 'something'

            success, location, fail_msg = auto_stow_item(session, server, item)
            if success:
                if item.get('item_type') == 'container' and item.get('inv_id'):
                    _db_save_item_state(server, item['inv_id'], item)
                await session.send_line('  You find ' + fmt_item_name(display) + ' and put it in your ' + location + '.')
                await server.world.broadcast_to_room(
                    room.id,
                    f"  {session.character_name} finds {display} and puts it in their {location}.",
                    exclude=session
                )
            else:
                if hasattr(server, "world"):
                    server.world.add_ground_item(
                        room.id,
                        item,
                        dropped_by_character_id=session.character_id,
                        dropped_by_name=session.character_name,
                        source="loot",
                    )
                else:
                    if not hasattr(room, '_ground_items'):
                        room._ground_items = []
                    room._ground_items.append(item)
                left_on_ground.append(display)
                await session.send_line('  You find ' + fmt_item_name(display) + '!')
                await server.world.broadcast_to_room(
                    room.id,
                    f"  {session.character_name} finds {display} and leaves it on the ground.",
                    exclude=session
                )
    else:
        creature.searched = True
        treasure = creature.treasure
        if treasure.get('coins'):
            coins = random.randint(1, creature.level * 20 + 10)
            session.silver += coins
            found_anything = True
            await session.send_line('  You find ' + colorize(str(coins) + ' silver coins', TextPresets.ITEM_NAME) + '!')
            await server.world.broadcast_to_room(
                room.id,
                f"  {session.character_name} finds {coins} silver coins!",
                exclude=session
            )

    if not found_anything:
        await session.send_line('  You find nothing of value.')
        await server.world.broadcast_to_room(
            room.id,
            f"  {session.character_name} searches {creature.full_name} but finds nothing of value.",
            exclude=session
        )

    if can_still_skin and not was_already_searched:
        await session.send_line('  You could still try to skin it.')

    if left_on_ground:
        for iname in left_on_ground:
            await session.send_line(colorize('  No space remaining! ' + iname + ' was left on the ground.', TextPresets.WARNING))

    if server.db and session.character_id:
        server.db.save_character_resources(
            session.character_id,
            session.health_current, session.mana_current,
            session.spirit_current, session.stamina_current,
            session.silver
        )

    if can_remove_corpse(creature):
        server.creatures.remove_creature(creature)
    session.set_roundtime(3)
    await session.send_line(roundtime_msg(3))
# =========================================================
# YELL
# =========================================================

async def cmd_yell(session, cmd, args, server):
    """YELL <message> - Yell for adjacent rooms to hear."""
    if not args:
        await session.send_line('You let out a loud yell!')
        text = session.character_name + ' lets out a loud yell!'
    else:
        await session.send_line('You yell, "' + args + '"')
        text = session.character_name + ' yells, "' + args + '"'

    room = session.current_room
    if not room:
        return

    await server.world.broadcast_to_room(room.id, text, exclude=session)

    opposites = {
        'north': 'south', 'south': 'north',
        'east': 'west', 'west': 'east',
        'northeast': 'southwest', 'southwest': 'northeast',
        'northwest': 'southeast', 'southeast': 'northwest',
        'up': 'below', 'down': 'above',
    }

    for direction, adj_room_id in room.exits.items():
        if direction.startswith('go_'):
            continue
        rev = opposites.get(direction, direction)
        if args:
            muffled = 'You hear someone yell from the ' + rev + ', "' + args + '"'
        else:
            muffled = 'You hear someone yell from the ' + rev + '.'
        await server.world.broadcast_to_room(adj_room_id, muffled)


# =========================================================
# GET ALL  (drain open coffer in hand into backpack)
# =========================================================

async def cmd_get_all(session, cmd, args, server):
    """
    GET ALL              - Drain an open coffer/chest/box held in either hand.
    GET ALL FROM <box>   - Same but specifies which box if holding two containers.

    Rules:
      - ONLY works on containers currently held in your hands.
      - Does NOT pick up from the ground.
      - Does NOT fall through to generic GET behavior.
      1. All coins go directly to your silver (pocket).
      2. All other items are stowed into your largest worn container (backpack first).
      3. Items that won't fit stay in the box.
      4. Once emptied, the box is closed and stowed into your pack.
    """
    _ensure_hands(session)

    # -- Find the target box - HANDS ONLY -------------------------------------
    box      = None
    box_slot = None

    if args:
        # GET ALL FROM <box> - match against held containers only
        stripped = args.strip().lower()
        if stripped.startswith("from "):
            stripped = stripped[5:].strip()

        for slot in ("right_hand", "left_hand"):
            item = getattr(session, slot, None)
            if item and item.get("item_type") == "container":
                if _match_target(item, stripped):
                    box      = item
                    box_slot = slot
                    break

        if not box:
            await session.send_line(
                "You aren't holding a container by that name.  "
                "GET ALL only works on boxes and coffers in your hands."
            )
            return
    else:
        # No args - look for an open container in hand only
        for slot in ("right_hand", "left_hand"):
            item = getattr(session, slot, None)
            if item and item.get("item_type") == "container" and item.get("opened"):
                box      = item
                box_slot = slot
                break

        if not box:
            await session.send_line(
                "You aren't holding an open container.  "
                "Hold a coffer or box first, then use GET ALL."
            )
            return

    if not box.get("opened"):
        # QOL: auto-open the box for GET ALL
        if box.get("is_locked"):
            await session.send_line(
                f"{fmt_item_name(box.get('short_name', 'the box'))} is locked!"
            )
            return
        box["opened"] = True
        await session.send_line(
            f"You open {fmt_item_name(box.get('short_name', 'the box'))}."
        )

    if box.get("destroyed"):
        await session.send_line("That has been destroyed.")
        return

    # -- Find largest worn container to stow into -----------------------------
    def _largest_container(session, exclude=None):
        """Return the worn container with the most free space (backpack preferred)."""
        containers = _get_worn_containers(session)
        best      = None
        best_free = 0
        for cont in containers:
            if cont is exclude:
                continue
            cap      = cont.get("container_capacity", 10) or 10
            inv_id   = cont.get("inv_id")
            in_cont  = [i for i in session.inventory if i.get("container_id") == inv_id]
            # Also count inline contents
            in_cont_inline = len(cont.get("contents", []))
            used     = len(in_cont) + in_cont_inline
            free     = cap - used
            if free > best_free:
                is_bp = (cont.get("noun") or "").lower() == "backpack"
                if is_bp:
                    # Backpack always wins if it has space
                    return cont, free
                best      = cont
                best_free = free
        return best, best_free

    dest, dest_free = _largest_container(session, exclude=box)
    dest_name = (dest.get("short_name") or dest.get("noun") or "your pack") if dest else None

    disp_box = fmt_item_name(box.get("short_name") or "the box")
    await session.send_line(f"You empty {disp_box}...")

    contents       = list(box.get("contents", []))    # inline items
    coins_collected = 0
    stowed         = []
    couldnt_stow   = []

    # -- 1. Coins first --------------------------------------------------------
    remaining_contents = []
    for item in contents:
        if item.get("item_type") == "coins":
            amount = item.get("coin_amount") or item.get("value") or 0
            if amount:
                coins_collected += amount
        else:
            remaining_contents.append(item)

    if coins_collected:
        session.silver += coins_collected
        await session.send_line(
            f"  You pocket {colorize(str(coins_collected) + ' silver coins', TextPresets.ITEM_NAME)}."
        )
        if server.db and session.character_id:
            server.db.save_character_resources(
                session.character_id,
                session.health_current, session.mana_current,
                session.spirit_current,
                getattr(session, "stamina_current", 100),
                session.silver
            )

    # -- 2. Stow everything else ----------------------------------------------
    for item in remaining_contents:
        iname = colorize(item.get("name") or "something", TextPresets.ITEM_NAME)

        if dest and dest_free > 0:
            # Resolve item_id - dynamic treasure items (scrolls, wands, etc.)
            # are stored inline without a real item_id.  Mint one now so they
            # survive as proper DB-backed inventory rows.
            item_id = item.get("item_id") or item.get("id")
            if not item_id and server.db:
                item_id = server.db.get_or_create_item(
                    name        = item.get("name", "something"),
                    short_name  = item.get("short_name") or item.get("name", "something"),
                    noun        = item.get("noun", "item"),
                    item_type   = item.get("item_type", "misc"),
                    article     = item.get("article", "a"),
                    value       = item.get("value", 0),
                    description = item.get("description", ""),
                )
                if item_id:
                    item["item_id"] = item_id

            if server.db and session.character_id and item_id:
                inv_id = server.db.add_item_to_inventory(
                    session.character_id, item_id
                )
                if inv_id:
                    _db_update_container(server, inv_id, dest.get("inv_id"))
                    item["inv_id"]       = inv_id
                    item["container_id"] = dest.get("inv_id")
                    item["slot"]         = None
                    session.inventory.append(item)
                    dest_free -= 1
                    stowed.append((item.get("name", "something"), dest_name))
                    await session.send_line(
                        f"  You put {iname} in your {dest_name}."
                    )
                    continue

            # No DB record possible - still track in session.inventory so
            # inv full can display it (container_id links it to dest).
            item["container_id"] = dest.get("inv_id")
            item["slot"]         = None
            item.setdefault("inv_id", None)
            if item not in session.inventory:
                session.inventory.append(item)
            dest_free -= 1
            stowed.append((item.get("name", "something"), dest_name))
            await session.send_line(f"  You put {iname} in your {dest_name}.")
        else:
            # Can't stow - stays in box
            couldnt_stow.append(item)
            await session.send_line(
                colorize(f"  No room - {item.get('name', 'something')} stays in the box.", TextPresets.WARNING)
            )

    # Update the box's inline contents to only what couldn't be stowed
    box["contents"] = couldnt_stow

    # -- 3. Handle the now-empty (or partially empty) box ----------------------
    if not couldnt_stow:
        box["opened"] = False

        # Remove box from hand
        if box_slot and getattr(session, box_slot, None) is box:
            setattr(session, box_slot, None)

        if dest and dest_free > 0:
            # Stow the empty box into the pack too
            box_item_id = box.get("item_id") or box.get("id")
            stored_box  = False
            if server.db and session.character_id and box_item_id:
                inv_id = server.db.add_item_to_inventory(
                    session.character_id, box_item_id
                )
                if inv_id:
                    _db_update_container(server, inv_id, dest.get("inv_id"))
                    box["inv_id"]       = inv_id
                    box["container_id"] = dest.get("inv_id")
                    box["slot"]         = None
                    session.inventory.append(box)
                    stored_box = True

            if stored_box:
                await session.send_line(
                    f"  {disp_box} is empty -- you close it and put it in your {dest_name}."
                )
            else:
                await session.send_line(
                    f"  {disp_box} is empty and closed."
                )
        else:
            # Pack is full - keep box where it was, just close it
            await session.send_line(
                f"  {disp_box} is empty.  You close it."
            )
    else:
        items_left = len(couldnt_stow)
        await session.send_line(
            colorize(
                f"  {items_left} item{'s' if items_left > 1 else ''} could not be stowed - {disp_box} remains open.",
                TextPresets.WARNING
            )
        )

    # Broadcast to room
    if session.current_room and (stowed or coins_collected):
        src = box.get('short_name', 'a box')
        await server.world.broadcast_to_room(
            session.current_room.id,
            f"{session.character_name} empties {src} into their pack.",
            exclude=session
        )

