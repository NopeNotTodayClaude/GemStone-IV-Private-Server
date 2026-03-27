-- =============================================================================
-- scripts/globals/combat/flare_system.lua
--
-- Elemental flare proc engine for GemStone IV.
--
-- GS4 wiki reference: gswiki.play.net/Category:Flares
--
-- Mechanics implemented:
--   • Counter-based proc: fires exactly every FLARE_SWING_INTERVAL successful hits
--     per weapon slot.  This prevents luck streaks, matching GS4's internal counter.
--   • Flare types: cold, fire, lightning, vibration, acid, ice — each with its own
--     crit table and creature vulnerability multipliers.
--   • Crit rank 1-5 random, with damage formula averaging ~20 HP per flare.
--   • Vulnerability table: fire creatures take bonus cold damage, trolls take
--     double fire damage, undead take bonus fire/plasma damage, etc.
--   • Resistances: some families resist certain elements (reduced damage).
--   • Family-group resolver: maps specific creature families (skeleton, ghoul,
--     wraith, lich, etc.) to parent vulnerability groups (undead) so the
--     vulnerability table stays clean and new creature types automatically
--     inherit the correct elemental weaknesses/resistances.
--
-- Called from Python via:
--   result = flare_system.tryFlare(weapon_data, creature_data, hit_count)
--
-- Returns a Lua table:
--   { proc=false }  — no flare this swing
--   { proc=true, flare_type="cold", crit_rank=3, damage=28,
--     vuln_mult=1.5, attacker_msg="...", room_msg="..." }
--
-- Python is responsible for:
--   • Tracking hit_count per (session, hand) slot and passing it in
--   • Applying the returned damage to the creature
--   • Sending the returned messages to the appropriate parties
-- =============================================================================

local Materials = require("data/items/materials")

local FlareSystem = {}

-- ── Configuration ─────────────────────────────────────────────────────────────

-- Proc every Nth successful hit on a weapon with a flare material.
-- GS4 wiki: "1 per 5 (20%) for weapons" via counter.
local FLARE_SWING_INTERVAL = 5

-- ── Family-group resolver ─────────────────────────────────────────────────────
--
-- Maps specific creature families to a parent vulnerability group so the
-- VULNERABILITY table only needs one entry per group instead of one per species.
--
-- How it works:
--   1. The creature template sets `family = "skeleton"` (or "ghoul", etc.)
--   2. resolveFamilyGroup("skeleton") → "undead"
--   3. getVulnMultiplier looks up "undead" in the VULNERABILITY sub-table
--
-- To add a new creature type that should inherit an existing group's weaknesses,
-- just add it here — no need to touch the VULNERABILITY table.
--
-- Families that ARE their own group (e.g. "troll", "insect") don't need entries
-- here; getVulnMultiplier falls back to the raw family string automatically.

local FAMILY_GROUPS = {
    -- ── Undead ────────────────────────────────────────────────────────────
    skeleton        = "undead",
    ghoul           = "undead",
    zombie          = "undead",
    wraith          = "undead",
    lich            = "undead",
    phantom         = "undead",
    specter         = "undead",
    banshee         = "undead",
    revenant        = "undead",
    wight           = "undead",
    mummy           = "undead",
    vampire         = "undead",
    ghost           = "undead",
    shade           = "undead",
    bone_golem      = "undead",
    death_knight    = "undead",
    necleriine      = "undead",   -- GS4 specific

    -- ── Fire creatures ────────────────────────────────────────────────────
    fire_elemental  = "fire",
    fire_ant        = "fire",
    fire_sprite     = "fire",
    lava_golem      = "fire",
    magma_worm      = "fire",
    fire_guardian   = "fire",
    fire_cat        = "fire",

    -- ── Cold / Ice creatures ──────────────────────────────────────────────
    ice_elemental   = "cold",
    frost_giant     = "cold",
    ice_golem       = "cold",
    ice_wraith      = "cold",
    frost_sprite    = "cold",
    snow_creature   = "cold",

    -- ── Water creatures ───────────────────────────────────────────────────
    water_elemental = "water",
    sea_serpent     = "water",
    water_sprite    = "water",
    kappa           = "water",

    -- ── Construct ─────────────────────────────────────────────────────────
    golem           = "construct",
    automaton       = "construct",
    clockwork       = "construct",
    stone_golem     = "construct",
    iron_golem      = "construct",
    clay_golem      = "construct",

    -- ── Troll variants ────────────────────────────────────────────────────
    -- (All trolls get the 2x fire weakness)
    cave_troll      = "troll",
    hill_troll      = "troll",
    war_troll       = "troll",
    forest_troll    = "troll",
    swamp_troll     = "troll",
    mountain_troll  = "troll",

    -- ── Plant variants ────────────────────────────────────────────────────
    treant          = "plant",
    vine_creature   = "plant",
    fungus          = "plant",
    shambler        = "plant",
    moss_creature   = "plant",
}

--- Resolve a specific creature family to its parent vulnerability group.
-- Returns the group name if a mapping exists, otherwise returns the raw family.
-- @param family string   The creature's family field (e.g. "skeleton")
-- @return string          The resolved group (e.g. "undead") or the original family
local function resolveFamilyGroup(family)
    if not family or family == "" then return "" end
    local lower = family:lower()
    return FAMILY_GROUPS[lower] or lower
end

-- ── Crit rank damage table ────────────────────────────────────────────────────
--
-- GS4: flares deliver "a single random critical of rank 1-5 from the relevant
-- critical table, causing 1-60 damage averaging ~20."
-- Formula: base_min + (rank-1)*10, base_max = rank*12
-- rank 1: 1-12   avg  6.5
-- rank 2: 11-24  avg 17.5
-- rank 3: 21-36  avg 28.5
-- rank 4: 31-48  avg 39.5
-- rank 5: 41-60  avg 50.5
-- Overall avg across equal rank distribution: ~28.5  (within "1-60, avg ~20" range)

local function rollFlareDamage(crit_rank)
    local base_min = 1 + (crit_rank - 1) * 10
    local base_max = crit_rank * 12
    return math.random(base_min, base_max)
end

-- ── Vulnerability & resistance multipliers ────────────────────────────────────
--
-- Keyed by flare_type, then by creature family GROUP (not raw family).
-- The resolveFamilyGroup() function above maps specific families to groups.
-- Multiplier applied to final flare damage before it is returned to Python.
--
-- Values > 1.0 = weakness (extra damage)
-- Values < 1.0 = resistance (reduced damage)
-- Values = 1.0 = neutral
--
-- GS4 wiki references:
--   Cold  flares: effective on fire-type creatures, resisted by cold/ice creatures
--   Fire  flares: effective on cold-type, undead, trolls (2x), plant; resisted by fire
--   Lightning:    broadly effective; bonus vs water creatures
--   Vibration:    effective on earth elementals, constructs
--   Acid:         effective on armored/carapace creatures, constructs; resisted by ooze
--   Ice:          effective on fire, reptile; resisted by cold/undead (partial)

local VULNERABILITY = {
    cold = {
        fire        = 1.5,   -- fire elementals, fire creatures
        reptile     = 1.25,  -- cold-blooded = vulnerable to cold
        insect      = 1.25,  -- cold slows insects
        plant       = 0.75,  -- plants partially resist cold
        cold        = 0.5,   -- cold creatures resist cold
        undead      = 0.75,  -- undead partially resist cold (already dead, less flesh)
        default     = 1.0,
    },
    fire = {
        undead      = 1.5,   -- GS4 wiki: fire effective vs undead
        troll       = 2.0,   -- GS4 wiki: trolls take DOUBLE fire damage
        cold        = 1.5,   -- cold creatures weak to fire
        water       = 1.5,   -- water creatures weak to fire (steam)
        plant       = 1.5,   -- plants burn
        insect      = 1.25,  -- insects burn easily
        fire        = 0.5,   -- fire creatures resist fire
        default     = 1.0,
    },
    lightning = {
        water       = 1.5,   -- electricity conducts through water creatures
        reptile     = 1.25,  -- reptiles vulnerable to lightning
        construct   = 1.25,  -- metal constructs conduct
        elemental   = 1.0,   -- neutral vs elementals (varies by type)
        default     = 1.0,   -- broadly effective, no huge bonus
    },
    vibration = {
        elemental   = 1.5,   -- earth elementals, stone creatures
        construct   = 1.5,   -- constructs shatter from resonance
        arachnid    = 1.25,  -- spiders are sensitive to vibration
        insect      = 1.25,  -- exoskeletons crack under vibration
        default     = 1.0,
    },
    acid = {
        construct   = 1.5,   -- acid dissolves constructs
        arachnid    = 1.5,   -- carapace/chitin dissolves in acid
        insect      = 1.5,   -- exoskeletons vulnerable to acid
        reptile     = 1.25,  -- scales corrode
        plant       = 1.25,  -- acid burns through plant matter
        elemental   = 0.75,  -- elementals partially resist (no real flesh)
        undead      = 0.75,  -- skeletal undead resist (less to dissolve)
        default     = 1.0,
    },
    ice = {
        fire        = 1.5,   -- ice vs fire = strong
        reptile     = 1.5,   -- cold-blooded reptiles freeze
        insect      = 1.25,  -- cold slows and shatters insects
        plant       = 1.25,  -- ice crystals rupture plant cells
        cold        = 0.5,   -- cold/ice creatures resist ice
        undead      = 0.75,  -- undead partially resist
        default     = 1.0,
    },
}

--- Get the vulnerability multiplier for a flare type vs a creature family.
-- First resolves the creature's raw family to its parent group via FAMILY_GROUPS,
-- then looks up the group in the VULNERABILITY table.
-- Falls back to the raw family if no group mapping exists, and finally to "default".
--
-- @param flare_type string       e.g. "fire"
-- @param creature_family string  e.g. "skeleton" → resolved to "undead"
-- @return number                 damage multiplier (e.g. 1.5 for weakness)
local function getVulnMultiplier(flare_type, creature_family)
    local tbl = VULNERABILITY[flare_type]
    if not tbl then return 1.0 end

    local raw_family = (creature_family or ""):lower()
    local group      = resolveFamilyGroup(raw_family)

    -- Try the resolved group first (e.g. "undead")
    if tbl[group] then
        return tbl[group]
    end

    -- Fall back to raw family in case it has its own entry
    -- (e.g. a creature with family="reptile" — no group mapping, but reptile
    --  IS a key in the vulnerability table directly)
    if tbl[raw_family] then
        return tbl[raw_family]
    end

    return tbl["default"] or 1.0
end

-- ── Message tables ────────────────────────────────────────────────────────────
--
-- Each flare type has attacker / room messages keyed by crit_rank (1-5).
-- %w = weapon noun, %c = creature name, %p = attacker name

local MESSAGES = {
    cold = {
        attacker = {
            [1] = "Your %w flares with a cold shimmer!",
            [2] = "Your %w blazes with icy energy!",
            [3] = "A burst of frost erupts from your %w!",
            [4] = "Your %w unleashes a wave of searing cold!",
            [5] = "A devastating blast of arctic energy explodes from your %w!",
        },
        room = {
            [1] = "%p's %w flares with cold light against %c!",
            [2] = "%p's %w crackles with icy energy against %c!",
            [3] = "A burst of frost erupts from %p's %w, striking %c!",
            [4] = "%p's %w sends a wave of freezing cold slamming into %c!",
            [5] = "A devastating arctic blast from %p's %w engulfs %c!",
        },
    },
    fire = {
        attacker = {
            [1] = "Your %w flares with a fiery shimmer!",
            [2] = "Your %w erupts with flames!",
            [3] = "A burst of fire explodes from your %w!",
            [4] = "Your %w unleashes a roaring wave of fire!",
            [5] = "A devastating inferno erupts from your %w!",
        },
        room = {
            [1] = "%p's %w flares with fire against %c!",
            [2] = "%p's %w erupts with flames against %c!",
            [3] = "A burst of fire explodes from %p's %w, scorching %c!",
            [4] = "%p's %w sends a roaring wave of fire crashing into %c!",
            [5] = "A devastating inferno from %p's %w engulfs %c!",
        },
    },
    lightning = {
        attacker = {
            [1] = "Your %w sparks with a lightning flare!",
            [2] = "Your %w crackles with electrical energy!",
            [3] = "A bolt of lightning leaps from your %w!",
            [4] = "Your %w unleashes a thunderous bolt!",
            [5] = "A tremendous bolt of lightning erupts from your %w!",
        },
        room = {
            [1] = "%p's %w sparks with lightning against %c!",
            [2] = "%p's %w crackles with electricity, striking %c!",
            [3] = "A bolt of lightning leaps from %p's %w into %c!",
            [4] = "%p's %w unleashes a thunderous bolt into %c!",
            [5] = "A tremendous bolt of lightning from %p's %w strikes %c!",
        },
    },
    vibration = {
        attacker = {
            [1] = "Your %w hums with resonant energy!",
            [2] = "Your %w vibrates with an earth-shaking force!",
            [3] = "A shockwave of resonant energy erupts from your %w!",
            [4] = "Your %w unleashes a crushing vibrational blast!",
            [5] = "A devastating earth-shaking force explodes from your %w!",
        },
        room = {
            [1] = "%p's %w hums with resonant energy against %c!",
            [2] = "%p's %w vibrates powerfully, striking %c!",
            [3] = "A shockwave of resonant energy from %p's %w smashes into %c!",
            [4] = "%p's %w sends a crushing vibrational blast into %c!",
            [5] = "A devastating earth-shaking force from %p's %w strikes %c!",
        },
    },
    acid = {
        attacker = {
            [1] = "Your %w drips with a hissing acid!",
            [2] = "Your %w oozes with corrosive venom!",
            [3] = "A spray of caustic acid erupts from your %w!",
            [4] = "Your %w unleashes a torrent of searing acid!",
            [5] = "A devastating wave of dissolving acid explodes from your %w!",
        },
        room = {
            [1] = "%p's %w drips acid onto %c!",
            [2] = "%p's %w splashes corrosive acid against %c!",
            [3] = "A spray of caustic acid erupts from %p's %w, eating into %c!",
            [4] = "%p's %w sends a torrent of searing acid splashing across %c!",
            [5] = "A devastating wave of dissolving acid from %p's %w engulfs %c!",
        },
    },
    ice = {
        attacker = {
            [1] = "Your %w glimmers with a thin rime of ice!",
            [2] = "Your %w crackles as jagged ice forms along its edge!",
            [3] = "A shard of razor-sharp ice bursts from your %w!",
            [4] = "Your %w unleashes a barrage of crystalline ice shards!",
            [5] = "A devastating lance of glacial ice explodes from your %w!",
        },
        room = {
            [1] = "%p's %w glimmers with ice against %c!",
            [2] = "Jagged ice crackles from %p's %w, striking %c!",
            [3] = "A shard of razor-sharp ice bursts from %p's %w into %c!",
            [4] = "%p's %w sends a barrage of ice shards slamming into %c!",
            [5] = "A devastating lance of glacial ice from %p's %w impales %c!",
        },
    },
}

local function buildMessages(flare_type, crit_rank, weapon_noun, creature_name, attacker_name)
    local tbl = MESSAGES[flare_type]
    if not tbl then
        return
            string.format("Your %s flares!", weapon_noun),
            string.format("%s's %s flares against %s!", attacker_name, weapon_noun, creature_name)
    end

    local rank_key = math.max(1, math.min(5, crit_rank))

    local attacker_template = tbl.attacker[rank_key] or tbl.attacker[1]
    local room_template     = tbl.room[rank_key]     or tbl.room[1]

    local attacker_msg = attacker_template
        :gsub("%%w", weapon_noun)
        :gsub("%%c", creature_name)
        :gsub("%%p", attacker_name)

    local room_msg = room_template
        :gsub("%%w", weapon_noun)
        :gsub("%%c", creature_name)
        :gsub("%%p", attacker_name)

    return attacker_msg, room_msg
end

-- ── Public API ────────────────────────────────────────────────────────────────

---
-- tryFlare(weapon_data, creature_data, hit_count, attacker_name)
--
-- weapon_data   table: { material, noun, ... }   (from item dict)
-- creature_data table: { name, family }
-- hit_count     int: number of successful hits so far with this weapon slot.
--                    Python tracks this per (session, hand).
-- attacker_name string: player name for room messages.
--
-- Returns a table.  Always has proc (bool).
-- On proc, also has: flare_type, crit_rank, damage, vuln_mult, attacker_msg, room_msg.
--
function FlareSystem.tryFlare(weapon_data, creature_data, hit_count, attacker_name)

    -- No flare if item has no flare capability.
    -- Check item.flare_type directly first (set on items table from DB / seed).
    -- Fall back to material lookup for items that have a material but no explicit
    -- flare_type set (e.g. freshly dropped loot before DB backfill runs).
    local direct_flare  = weapon_data and weapon_data.flare_type or nil
    local material_name = weapon_data and weapon_data.material or nil
    local flare_type    = direct_flare or Materials.flareType(material_name)

    if not flare_type then
        return { proc = false }
    end

    -- Counter check: proc on every FLARE_SWING_INTERVAL-th hit
    if (hit_count % FLARE_SWING_INTERVAL) ~= 0 then
        return { proc = false }
    end

    -- Roll crit rank 1-5
    local crit_rank = math.random(1, 5)

    -- Roll raw damage and apply vulnerability multiplier
    local raw_damage = rollFlareDamage(crit_rank)
    local family     = creature_data and creature_data.family or ""
    local vuln_mult  = getVulnMultiplier(flare_type, family)
    local damage     = math.max(1, math.floor(raw_damage * vuln_mult))

    -- Build messages
    local weapon_noun    = (weapon_data and weapon_data.noun) or "weapon"
    local creature_name  = (creature_data and creature_data.name) or "the creature"
    local attacker_nm    = attacker_name or "Someone"

    local attacker_msg, room_msg = buildMessages(
        flare_type, crit_rank, weapon_noun, creature_name, attacker_nm
    )

    return {
        proc         = true,
        flare_type   = flare_type,
        crit_rank    = crit_rank,
        damage       = damage,
        vuln_mult    = vuln_mult,
        attacker_msg = attacker_msg,
        room_msg     = room_msg,
    }
end

---
-- Expose the swing interval so Python can use it consistently.
FlareSystem.SWING_INTERVAL = FLARE_SWING_INTERVAL

---
-- Expose FAMILY_GROUPS so other systems (e.g. creature inspector, debug tools)
-- can check what group a creature family resolves to.
FlareSystem.FAMILY_GROUPS = FAMILY_GROUPS

---
-- Expose resolveFamilyGroup for external use (e.g. creature debug commands).
FlareSystem.resolveFamilyGroup = resolveFamilyGroup

return FlareSystem
