------------------------------------------------------------------------
-- scripts/globals/magic/active_buffs.lua
-- Active spell effect tracking for GemStone IV.
-- Reads/writes the character_active_buffs table.
--
-- effects_json schema (flat keys):
--   ds              — Defense Strength bonus
--   td_spiritual    — Target Defense bonus (spiritual sphere)
--   td_elemental    — Target Defense bonus (elemental sphere)
--   td_mental       — Target Defense bonus (mental sphere)
--   td_sorcerer     — Target Defense bonus (sorcerer/hybrid sphere)
--   cs_all          — Casting Strength bonus (all spheres)
--   cs_elemental    — Casting Strength bonus (elemental sphere)
--   cs_spiritual    — Casting Strength bonus (spiritual sphere)
--   cs_mental       — Casting Strength bonus (mental sphere)
--   as_bonus        — Attack Strength bonus
--   hindrance_redux — Percentage points of spell hindrance reduction
--   regen_bonus     — Flat mana regen bonus per pulse
--   max_mana_bonus  — Temporary max mana increase
------------------------------------------------------------------------

local DB   = require("globals/utils/db")
local JSON = require("globals/utils/json")

local ActiveBuffs = {}

-- ── Load all currently-active buffs for a character ──────────────────
-- Returns an array of buff tables with .spell_number, .effects, .expires_at
function ActiveBuffs.get_active(character_id)
    local rows = DB.query([[
        SELECT id, spell_number, circle_id, caster_id, effects_json, expires_at
        FROM character_active_buffs
        WHERE character_id = ?
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC
    ]], { character_id })

    local result = {}
    for _, row in ipairs(rows) do
        local effects = {}
        if row.effects_json and row.effects_json ~= "" then
            local ok, parsed = pcall(JSON.decode, row.effects_json)
            if ok and type(parsed) == "table" then
                effects = parsed
            end
        end
        result[#result+1] = {
            id           = row.id,
            spell_number = row.spell_number,
            circle_id    = row.circle_id,
            caster_id    = row.caster_id,
            effects      = effects,
            expires_at   = row.expires_at,
        }
    end
    return result
end

-- ── Apply a new buff to a character ──────────────────────────────────
-- spell_number: e.g. 101, 406, 913
-- circle_id:    optional; used for dispel targeting
-- caster_id:    character_id of caster, or nil if item/environment
-- duration_sec: seconds until expiry; nil = permanent
-- effects:      table of effect keys to values { ds=20, td_spiritual=10, … }
-- If the same spell is already active, it refreshes (overwrites).
function ActiveBuffs.apply(character_id, spell_number, circle_id,
                            caster_id, duration_sec, effects)
    -- Remove existing instance of this spell first (refresh behavior)
    ActiveBuffs.remove_spell(character_id, spell_number)

    local expires_at = nil
    if duration_sec then
        -- Store as UTC datetime string; Python side handles actual clock.
        expires_at = string.format(
            "DATE_ADD(NOW(), INTERVAL %d SECOND)", duration_sec
        )
    end

    local effects_json = JSON.encode(effects or {})

    if expires_at then
        DB.execute([[
            INSERT INTO character_active_buffs
                (character_id, spell_number, circle_id, caster_id, effects_json, expires_at)
            VALUES (?, ?, ?, ?, ?, ]] .. expires_at .. [[)
        ]], { character_id, spell_number, circle_id, caster_id, effects_json })
    else
        DB.execute([[
            INSERT INTO character_active_buffs
                (character_id, spell_number, circle_id, caster_id, effects_json, expires_at)
            VALUES (?, ?, ?, ?, ?, NULL)
        ]], { character_id, spell_number, circle_id, caster_id, effects_json })
    end
end

-- ── Remove a specific spell buff from a character ─────────────────────
function ActiveBuffs.remove_spell(character_id, spell_number)
    DB.execute([[
        DELETE FROM character_active_buffs
        WHERE character_id=? AND spell_number=?
    ]], { character_id, spell_number })
end

-- ── Remove all buffs on a character (death, DISPEL all, etc.) ────────
function ActiveBuffs.remove_all(character_id)
    DB.execute(
        "DELETE FROM character_active_buffs WHERE character_id=?",
        { character_id }
    )
end

-- ── Purge expired buffs (call periodically from server tick) ──────────
function ActiveBuffs.purge_expired()
    DB.execute(
        "DELETE FROM character_active_buffs WHERE expires_at IS NOT NULL AND expires_at <= NOW()",
        {}
    )
end

-- ── Check if a specific spell is active on a character ───────────────
function ActiveBuffs.is_active(character_id, spell_number)
    local row = DB.queryOne([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND spell_number=?
          AND (expires_at IS NULL OR expires_at > NOW())
    ]], { character_id, spell_number })
    return row ~= nil
end

-- ── Get total DS bonus from all active buffs ──────────────────────────
function ActiveBuffs.total_ds_bonus(character_id)
    local buffs = ActiveBuffs.get_active(character_id)
    local total = 0
    for _, buff in ipairs(buffs) do
        total = total + (buff.effects.ds or 0)
    end
    return total
end

-- ── Get total regen bonus from active buffs ───────────────────────────
function ActiveBuffs.total_regen_bonus(character_id)
    local buffs = ActiveBuffs.get_active(character_id)
    local total = 0
    for _, buff in ipairs(buffs) do
        total = total + (buff.effects.regen_bonus or 0)
    end
    return total
end

-- ── Get total hindrance reduction from active buffs ───────────────────
function ActiveBuffs.total_hindrance_redux(character_id)
    local buffs = ActiveBuffs.get_active(character_id)
    local total = 0
    for _, buff in ipairs(buffs) do
        total = total + (buff.effects.hindrance_redux or 0)
    end
    return total
end

function ActiveBuffs.total_hindrance_penalty(character_id)
    local buffs = ActiveBuffs.get_active(character_id)
    local total = 0
    for _, buff in ipairs(buffs) do
        total = total + (buff.effects.hindrance_penalty or 0)
    end
    return total
end

return ActiveBuffs
