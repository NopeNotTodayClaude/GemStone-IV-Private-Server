-- =============================================================================
-- scripts/globals/utils/smr.lua
-- SMRv2  (Standard Maneuver Roll version 2)
-- GemStone IV canonical implementation
--
-- Usage from technique scripts:
--   local SMR = require("globals/utils/smr")
--   local result = SMR.roll(attacker, defender, opts)
--   -- result.total     = final d100 + bonuses
--   -- result.margin    = result.total - 100  (positive = success)
--   -- result.success   = bool
--   -- result.d100      = raw die
--   -- result.offense   = computed offense bonus
--   -- result.defense   = computed defense bonus
--   -- result.msg       = display string "[SMR result: X (Open d100: Y, Bonus: Z)]"
-- =============================================================================

local SMR = {}

-- ---------------------------------------------------------------------------
-- Constants
-- ---------------------------------------------------------------------------

-- Racial size modifiers to physical maneuver endroll (offense)
local RACIAL_SIZE_OFF = {
    [1]  =  10,   -- Giantman
    [2]  =  10,   -- Half-Krolvin
    [3]  =   5,   -- Human
    [4]  =   5,   -- Dwarf
    [5]  =   0,   -- Half-Elf
    [6]  =   0,   -- Dark Elf
    [7]  =   0,   -- Erithian
    [8]  =   0,   -- Sylvankind
    [9]  =   0,   -- Aelotoi  (also -5 to endroll but wiki lists them together)
    [10] =  -5,   -- Elf
    [11] =  -5,   -- Aelotoi (endroll)
    [12] = -10,   -- Forest Gnome
    [13] = -15,   -- Halfling
    [14] = -20,   -- Burghal Gnome
}

-- Bonus dodging ranks granted to certain races for SMRv2 DEFENSE
local RACIAL_DODGE_BONUS = {
    -- Aelotoi=9, DarkElf=6, Erithian=7, HalfElf=5, Sylvankind=8 -> +30
    [9]  = 30,
    [6]  = 30,
    [7]  = 30,
    [5]  = 30,
    [8]  = 30,
    -- Elf=10, ForestGnome=12, Halfling=13 -> +60
    [10] = 60,
    [12] = 60,
    [13] = 60,
    -- BurghalGnome=14 -> +80
    [14] = 80,
}

-- Maneuver knowledge offensive bonus by rank
local MK_OFF = { 2, 4, 8, 12, 20 }
-- Maneuver knowledge defensive bonus by rank
local MK_DEF = { 2, 4, 8, 12, 20 }

-- Stance DS modifiers (defender's stance lowers/raises their effective defense)
-- GS4 stance names: offensive, advance, forward, neutral, guarded, defensive
local STANCE_DEF_MOD = {
    offensive =  -20,
    advance   =  -10,
    forward   =    0,
    neutral   =    0,
    guarded   =   15,
    defensive =   25,
}

-- Stance AS modifiers for attacker (from wiki stance table)
local STANCE_OFF_MOD = {
    offensive =  20,
    advance   =  15,
    forward   =  10,
    neutral   =   0,
    guarded   = -10,
    defensive = -20,
}

-- ---------------------------------------------------------------------------
-- Internal helpers
-- ---------------------------------------------------------------------------

local function safe_int(v)
    return tonumber(v) or 0
end

-- Open d100: if roll >= 96, re-roll and add; if roll <= 5, re-roll and subtract
-- (simplified: just do a single open roll per GS4 convention for maneuvers)
local function open_d100()
    local roll = math.random(1, 100)
    if roll >= 96 then
        roll = roll + math.random(1, 100)
    elseif roll <= 5 then
        roll = roll - math.random(1, 100)
    end
    return roll
end

-- Skill bonus from ranks: GS4 canonical step formula
local function skill_bonus_from_ranks(ranks)
    ranks = safe_int(ranks)
    if ranks <= 0 then return 0 end
    local bonus = 0
    local steps = {
        {10,  5},   -- ranks  1-10:  +5 each
        {10,  4},   -- ranks 11-20:  +4 each
        {10,  3},   -- ranks 21-30:  +3 each
        {10,  2},   -- ranks 31-40:  +2 each
    }
    local remaining = ranks
    for _, s in ipairs(steps) do
        local take = math.min(remaining, s[1])
        bonus    = bonus + take * s[2]
        remaining = remaining - take
        if remaining <= 0 then return bonus end
    end
    -- Ranks 41+: +1 per rank
    bonus = bonus + remaining
    return bonus
end

-- ---------------------------------------------------------------------------
-- Compute SMRv2 DEFENSE bonus for a defender entity
-- entity fields expected (all optional, default 0):
--   .skill_ranks.dodging, .skill_ranks.combat_maneuvers,
--   .skill_ranks.perception, .skill_ranks.physical_fitness,
--   .skill_ranks.shield_use
--   .stats.agility, .stats.dexterity, .stats.intuition
--   .race_id, .stance, .level
--   .smr_def_bonus  (sum of any active spell/maneuver bonuses)
--   .encumbrance_penalty, .armor_action_penalty
-- ---------------------------------------------------------------------------
function SMR.compute_defense(entity, opts)
    opts = opts or {}
    local sr = entity.skill_ranks or {}
    local st = entity.stats or {}

    -- Racial dodge bonus
    local race_id     = safe_int(entity.race_id)
    local racial_dodge = safe_int(RACIAL_DODGE_BONUS[race_id])

    local dodge_ranks  = safe_int(sr.dodging)            + racial_dodge
    local cm_ranks     = safe_int(sr.combat_maneuvers)
    local perc_ranks   = safe_int(sr.perception)
    local pf_ranks     = safe_int(sr.physical_fitness)
    local shield_ranks = opts.include_shield and safe_int(sr.shield_use) or 0

    -- Primary skill pool: average of dodging, CM, perception, PF (and shield if applicable)
    -- GS4 wiki: all weighted equally
    local skill_count  = opts.include_shield and 5 or 4
    local skill_sum    = dodge_ranks + cm_ranks + perc_ranks + pf_ranks + shield_ranks
    local avg_ranks    = skill_sum / skill_count

    -- Convert to bonus
    local skill_def    = skill_bonus_from_ranks(avg_ranks)

    -- Stat contribution: Agility primary, Dex+Int secondary
    local agi = safe_int(st.agility)
    local dex = safe_int(st.dexterity)
    local itn = safe_int(st.intuition)
    local stat_def = math.floor(agi * 0.6 + (dex + itn) * 0.2)

    -- Stance
    local stance_str = entity.stance or "neutral"
    local stance_bonus = safe_int(STANCE_DEF_MOD[stance_str])

    -- Active spell/maneuver bonuses
    local spell_bonus = safe_int(entity.smr_def_bonus)

    -- Encumbrance + armor action penalty
    local enc_pen   = safe_int(entity.encumbrance_penalty)
    local armor_pen = safe_int(entity.armor_action_penalty)

    -- Maneuver knowledge defense bonus (passed in opts)
    local mk_rank = safe_int(opts.defender_mk_rank)  -- 0 = none
    local mk_bonus = mk_rank > 0 and safe_int(MK_DEF[mk_rank]) or 0

    local total = skill_def + stat_def + stance_bonus + spell_bonus + mk_bonus
                  - enc_pen - armor_pen

    return total
end

-- ---------------------------------------------------------------------------
-- Compute SMRv2 OFFENSE bonus for an attacker entity
-- entity fields expected:
--   .skill_ranks.combat_maneuvers, .skill_ranks.<weapon_skill>
--   .level, .race_id, .stance
--   .smr_off_bonus  (from Weapon Specialization, Bonding, Holy Weapon etc.)
--   .encumbrance_penalty, .armor_action_penalty
-- opts:
--   .weapon_skill_ranks  (override for weapon skill used)
--   .attacker_mk_rank    (0-5, maneuver knowledge rank)
--   .use_racial_size     (bool)
-- ---------------------------------------------------------------------------
function SMR.compute_offense(entity, opts)
    opts = opts or {}
    local sr = entity.skill_ranks or {}
    local st = entity.stats or {}

    -- Primary: Combat Maneuvers. Secondary: weapon skill
    -- Average (CM + weapon) / 2 per wiki
    local cm_ranks  = safe_int(sr.combat_maneuvers)
    local wpn_ranks = safe_int(opts.weapon_skill_ranks or sr.weapon_skill or 0)

    -- 1x training = baseline, 2x = +15% more effective
    -- "1x per level" means ranks = level is baseline
    local level    = math.max(1, safe_int(entity.level))
    local cm_eff   = cm_ranks
    local wpn_eff  = wpn_ranks
    -- Apply 2x diminishing return: ranks > level get 85% value each
    if cm_ranks > level then
        local over = cm_ranks - level
        cm_eff = level + math.floor(over * 0.85)
    end
    if wpn_ranks > level then
        local over = wpn_ranks - level
        wpn_eff = level + math.floor(over * 0.85)
    end

    local avg_ranks = (cm_eff + wpn_eff) / 2
    local skill_off = skill_bonus_from_ranks(avg_ranks)

    -- Minimum level of effectiveness (approx 70% vs same level):
    -- If computed bonus < (level * 3), use level * 3 instead
    local min_off = level * 3
    if skill_off < min_off then skill_off = min_off end

    -- Stance
    local stance_str = entity.stance or "neutral"
    local stance_bonus = safe_int(STANCE_OFF_MOD[stance_str])

    -- Racial size modifier (physical maneuvers only)
    local racial_bonus = 0
    if opts.use_racial_size then
        racial_bonus = safe_int(RACIAL_SIZE_OFF[safe_int(entity.race_id)])
    end

    -- Active bonuses (Weapon Specialization 2%/rank, Bonding, Holy Weapon)
    local wpn_bonus = safe_int(entity.smr_off_bonus)

    -- Maneuver knowledge offensive bonus
    local mk_rank  = safe_int(opts.attacker_mk_rank)
    local mk_bonus = mk_rank > 0 and safe_int(MK_OFF[mk_rank]) or 0

    -- Encumbrance + armor action penalty to offense
    local enc_pen   = safe_int(entity.encumbrance_penalty)
    local armor_pen = safe_int(entity.armor_action_penalty)

    local total = skill_off + stance_bonus + racial_bonus + wpn_bonus + mk_bonus
                  - enc_pen - armor_pen

    return total
end

-- ---------------------------------------------------------------------------
-- SMR.roll(attacker, defender, opts) -> result table
-- This is the main entry point for all weapon technique resolution.
--
-- opts fields:
--   .weapon_skill_ranks    (int)   attacker's relevant weapon skill ranks
--   .attacker_mk_rank      (int)   attacker's maneuver knowledge rank (0-5)
--   .defender_mk_rank      (int)   defender's maneuver knowledge rank (0-5)
--   .include_shield        (bool)  include shield_use in defender calc
--   .use_racial_size       (bool)  apply racial size to offense endroll
--   .off_bonus             (int)   any extra flat offense bonus (e.g. Overpower +10 CER)
--   .def_bonus             (int)   any extra flat defense bonus
--   .bypass_ebp            (bool)  if true, defender cannot evade/block/parry
-- ---------------------------------------------------------------------------
function SMR.roll(attacker, defender, opts)
    opts = opts or {}

    local off    = SMR.compute_offense(attacker, opts)
    local def    = SMR.compute_defense(defender, opts)
    local d100   = open_d100()

    -- Extra flat bonuses/penalties
    local extra_off = safe_int(opts.off_bonus)
    local extra_def = safe_int(opts.def_bonus)

    -- If bypass_ebp: defender can't use stance defense bonus at all
    if opts.bypass_ebp then
        local stance_str = defender.stance or "neutral"
        extra_def = extra_def - safe_int(STANCE_DEF_MOD[stance_str])
    end

    local total  = d100 + off - def + extra_off - extra_def
    local margin = total - 100
    local bonus  = off - def + extra_off - extra_def

    return {
        total   = total,
        margin  = margin,
        success = total > 100,
        d100    = d100,
        offense = off + extra_off,
        defense = def + extra_def,
        bonus   = bonus,
        msg     = string.format("[SMR result: %d (Open d100: %d, Bonus: %d)]",
                                total, d100, bonus),
    }
end

-- ---------------------------------------------------------------------------
-- Convenience: determine maneuver rank for a technique given weapon ranks
-- ---------------------------------------------------------------------------
function SMR.technique_rank(weapon_ranks, tech_def)
    local thresholds = {
        tech_def.rank5_ranks or 9999,
        tech_def.rank4_ranks or 9999,
        tech_def.rank3_ranks or 9999,
        tech_def.rank2_ranks or 9999,
        tech_def.min_skill_ranks or 10,
    }
    local values = {5, 4, 3, 2, 1}
    for i, thresh in ipairs(thresholds) do
        if weapon_ranks >= thresh then
            return values[i]
        end
    end
    return 0  -- not learned
end

-- ---------------------------------------------------------------------------
-- Compute number of assault/AoE hits based on MOC ranks
-- GS4: 1 base + 1 per 40 MOC ranks (simplified consistent with multi-strike)
-- ---------------------------------------------------------------------------
function SMR.moc_hits(moc_ranks)
    moc_ranks = safe_int(moc_ranks)
    return 1 + math.floor(moc_ranks / 40)
end

return SMR
