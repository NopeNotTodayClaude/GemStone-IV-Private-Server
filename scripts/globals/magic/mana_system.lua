------------------------------------------------------------------------
-- scripts/globals/magic/mana_system.lua
-- Mana pool calculation and regeneration for GemStone IV.
-- Source: gswiki.play.net/Mana, /Harness_Power
--
-- Formula summary (from wiki):
--
-- BASE MANA (single mana stat):
--   BaseMana = floor(StatBonus / 2)
--
-- BASE MANA (two mana stats):
--   BaseMana = floor((StatBonus1 + StatBonus2) / 4)
--
-- HARNESS POWER BONUS (HP ranks capped at level):
--   HP_Bonus = HP_ranks_capped_at_level + HP_skill_bonus
--
-- TOTAL MAX MANA = BaseMana + HP_Bonus
--
-- REGENERATION:
--   Off-node: 15% of max_mana per pulse
--   On-node:  25% of max_mana per pulse
--   Bonus regen (single sphere MC):  floor(MC_ranks / 10)
--   Bonus regen (two sphere MC):
--     floor(MC_higher / 10) + floor(MC_lower / 20)
--
-- MANA COST: Each spell costs mana equal to its spell rank by default.
--   Attempting to cast without sufficient mana causes nervous system injury.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local GS4Math     = require("globals/utils/gs4_math")
local Professions = require("data/professions")

local Mana = {}

-- ── Stat bonus helper ─────────────────────────────────────────────────
-- Returns the numeric stat bonus for a named stat from a character row.
-- Stat bonus is the "bonus" column in INFO, not the raw stat value.
-- Stat indices match professions.lua: 0=STR 1=CON 2=DEX 3=AGI 4=DIS
--                                      5=AUR 6=LOG 7=INT 8=WIS 9=INF
local STAT_BONUS_TABLE = {
    -- bonus = floor((stat - 50) / 10) for stats above 50 (simplified)
    -- actual GS4 uses a published table; this mirrors that table's output
    -- for typical values. The real bonus is stored in the character row.
}

local function get_char_stat_bonus(char, stat_name)
    -- stat_name: "aura","wisdom","logic","discipline","influence","intuition"
    local raw = char["stat_" .. stat_name] or 50
    return GS4Math.stat_bonus(raw)
end

-- ── Mana stat bonus for a profession ─────────────────────────────────
-- Returns the total mana-relevant stat bonus for base mana calc.
-- Uses the professions.lua mana_stats definition.
-- mana_stats maps profession_id → { stat_idx1, stat_idx2 } or { stat_idx }
-- stat index: 5=AUR, 8=WIS, 6=LOG, 9=INF, 4=DIS
local STAT_IDX_TO_NAME = {
    [4]="discipline", [5]="aura", [6]="logic",
    [7]="intuition",  [8]="wisdom", [9]="influence"
}

function Mana.calc_base_mana(char, profession_id)
    local mana_stats = Professions.mana_stats[profession_id]
    if not mana_stats then return 0 end

    -- Wiki: single-stat professions use level-0 stat bonus (INFO START).
    -- We use current stat as approximation (proper INFO START requires separate col).
    if #mana_stats == 1 then
        local stat_name = STAT_IDX_TO_NAME[mana_stats[1]] or "wisdom"
        local bonus = get_char_stat_bonus(char, stat_name)
        return math.floor(bonus / 2)
    else
        local name1 = STAT_IDX_TO_NAME[mana_stats[1]] or "aura"
        local name2 = STAT_IDX_TO_NAME[mana_stats[2]] or "wisdom"
        local b1 = get_char_stat_bonus(char, name1)
        local b2 = get_char_stat_bonus(char, name2)
        return math.floor((b1 + b2) / 4)
    end
end

-- ── Harness Power bonus ───────────────────────────────────────────────
function Mana.calc_harness_power_bonus(char, hp_ranks)
    local level = char.level or 1
    local capped_ranks = math.min(hp_ranks, level)
    local hp_skill_bonus = GS4Math.skill_bonus_from_ranks(hp_ranks)
    return capped_ranks + hp_skill_bonus
end

-- ── Total max mana ────────────────────────────────────────────────────
function Mana.calc_max_mana(char, profession_id, hp_ranks)
    local base = Mana.calc_base_mana(char, profession_id)
    local hp   = Mana.calc_harness_power_bonus(char, hp_ranks or 0)
    return math.max(0, base + hp)
end

-- ── Mana regeneration ─────────────────────────────────────────────────
-- Returns mana regenerated per pulse.
-- on_node: true if in a mana node room.
-- mc_ranks: table { emc=N, smc=N, mmc=N } — only sphere-relevant ones count.
-- mana_spheres: which mana control skills apply for this profession.
--   professions with single sphere: only that MC counts.
--   professions with two spheres: both count (higher/lower formula).
function Mana.calc_regen(max_mana, on_node, mc_ranks, profession_id)
    local pct   = on_node and 0.25 or 0.15
    local base  = math.floor(max_mana * pct)

    -- Determine which MC skills are relevant for this profession.
    -- Source: gswiki.play.net/Mana — professions with single sphere of power
    -- get +1 per 10 ranks; two-sphere professions use the higher/lower formula.
    local MC_SPHERES = {
        [1]  = {"emc","smc"},   -- Warrior  (both contribute but low impact)
        [2]  = {"emc","smc"},   -- Rogue
        [3]  = {"emc"},         -- Wizard   (Elemental only)
        [4]  = {"smc"},         -- Cleric   (Spiritual only)
        [5]  = {"smc","mmc"},   -- Empath   (Spiritual, Mental)
        [6]  = {"emc","smc"},   -- Sorcerer (Elemental, Spiritual)
        [7]  = {"smc"},         -- Ranger   (Spiritual only)
        [8]  = {"emc","mmc"},   -- Bard     (Elemental, Mental)
        [9]  = {"smc"},         -- Paladin  (Spiritual only)
        [10] = {"smc","mmc"},   -- Monk     (Spiritual, Mental)
    }

    local spheres = MC_SPHERES[profession_id] or {}
    local bonus_regen = 0

    if #spheres == 1 then
        -- Single sphere: +1 per 10 ranks
        local key = spheres[1]
        local r = (mc_ranks and mc_ranks[key]) or 0
        bonus_regen = math.floor(r / 10)
    elseif #spheres == 2 then
        -- Two spheres: higher/lower formula
        local r1 = (mc_ranks and mc_ranks[spheres[1]]) or 0
        local r2 = (mc_ranks and mc_ranks[spheres[2]]) or 0
        local higher = math.max(r1, r2)
        local lower  = math.min(r1, r2)
        bonus_regen = math.floor(higher / 10) + math.floor(lower / 20)
    end

    return base + bonus_regen
end

-- ── Deduct mana; returns true if successful, false + injury flag ──────
-- Does NOT write to DB — caller must update mana_current.
-- Returns: success(bool), injury(bool)
function Mana.deduct(current_mana, cost)
    if current_mana >= cost then
        return true, false
    end
    -- Insufficient mana → cast fails and caster suffers nerve injury
    return false, true
end

-- ── Mana sharing formula (SEND verb) ─────────────────────────────────
-- Source: gswiki.play.net/Mana — Sharing section
-- sender_skill_bonus, receiver_skill_bonus: numeric bonus in matching MC skill
-- sent: amount the sender wants to send
-- Returns actual mana received (after 95% cap and skill scaling).
function Mana.calc_sharing(sent, sender_skill_bonus, receiver_skill_bonus)
    if sender_skill_bonus <= 0 or receiver_skill_bonus <= 0 then
        return sent  -- no skill → no loss (wiki: "no mana will be lost")
    end
    local received = math.floor(
        sent * 0.95
             * (sender_skill_bonus   / 100)
             * (receiver_skill_bonus / 100)
    )
    return math.max(0, received)
end

-- ── DB helpers ───────────────────────────────────────────────────────
-- Load a character's mana-relevant skill ranks from DB.
-- Returns { hp=N, emc=N, smc=N, mmc=N }
function Mana.load_mc_ranks(character_id)
    local SKILL_IDS = { hp=18, emc=19, smc=20, mmc=21 }
    local result = { hp=0, emc=0, smc=0, mmc=0 }
    for key, sid in pairs(SKILL_IDS) do
        local row = DB.queryOne(
            "SELECT ranks FROM character_skills WHERE character_id=? AND skill_id=?",
            { character_id, sid }
        )
        if row then result[key] = row.ranks or 0 end
    end
    return result
end

-- Update mana_current in the DB (called after any mana change).
function Mana.save_mana(character_id, new_mana)
    DB.execute(
        "UPDATE characters SET mana_current=? WHERE id=?",
        { new_mana, character_id }
    )
end

return Mana
