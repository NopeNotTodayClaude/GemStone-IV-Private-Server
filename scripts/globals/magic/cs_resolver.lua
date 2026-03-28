------------------------------------------------------------------------
-- scripts/globals/magic/cs_resolver.lua
-- Casting Strength (CS) calculation for GemStone IV warding spells.
-- Source: gswiki.play.net/Casting_strength
--
-- Formula:
--   CS = (Level × 3)
--      + round(Primary Circle Bonus)
--      + ceiling(Secondary Circle A Bonus)
--      + ceiling(Secondary Circle B Bonus)
--      + round(Stat Bonus)
--      + round(Active Spell Effects)
--
-- Primary Circle Bonus (ranks in the circle being cast):
--   Ranks up to level       = 1.0 per rank
--   Ranks 1-20 above level  = 0.75 per rank
--   Ranks 21-60 above level = 0.5 per rank
--   Ranks 61-100 above level= 0.25 per rank
--   Ranks 101+ above level  = 0.125 per rank
--
-- Secondary Circle Bonus (each other circle the caster has trained):
--   Ranks up to 2/3 level       = 0.333 per rank
--   Ranks between 2/3 and level = 0.111 per rank
--   Ranks above level           = 0.05 per rank
--
-- Stat used depends on the spell's circle (see spell_circles.lua cs_stat).
------------------------------------------------------------------------

local DB           = require("globals/utils/db")
local SpellCircles = require("globals/magic/spell_circles")
local ActiveBuffs  = require("globals/magic/active_buffs")
local GS4Math      = require("globals/utils/gs4_math")

local CS = {}

-- ── Primary circle bonus ─────────────────────────────────────────────
-- ranks_in_circle: total ranks trained in the circle being cast
-- char_level: caster's current level
local function primary_bonus(ranks_in_circle, char_level)
    local bonus = 0.0
    local r = ranks_in_circle
    -- Ranks up to level: 1.0 each
    local at_level = math.min(r, char_level)
    bonus = bonus + at_level * 1.0
    r = r - at_level
    if r <= 0 then return bonus end
    -- Ranks 1-20 above level: 0.75 each
    local tier1 = math.min(r, 20)
    bonus = bonus + tier1 * 0.75
    r = r - tier1
    if r <= 0 then return bonus end
    -- Ranks 21-60 above level: 0.5 each
    local tier2 = math.min(r, 40)
    bonus = bonus + tier2 * 0.5
    r = r - tier2
    if r <= 0 then return bonus end
    -- Ranks 61-100 above level: 0.25 each
    local tier3 = math.min(r, 40)
    bonus = bonus + tier3 * 0.25
    r = r - tier3
    if r <= 0 then return bonus end
    -- Ranks 101+ above level: 0.125 each
    bonus = bonus + r * 0.125
    return bonus
end

-- ── Secondary circle bonus ────────────────────────────────────────────
-- ranks_in_circle: ranks in a secondary circle
-- char_level: caster's current level
local function secondary_bonus(ranks_in_circle, char_level)
    local bonus = 0.0
    local r = ranks_in_circle
    local two_thirds = math.floor(char_level * 2 / 3)
    -- Ranks up to 2/3 level: 1/3 each
    local tier1 = math.min(r, two_thirds)
    bonus = bonus + tier1 * (1.0/3.0)
    r = r - tier1
    if r <= 0 then return bonus end
    -- Ranks between 2/3 level and level: 1/9 each
    local tier2_cap = char_level - two_thirds
    local tier2 = math.min(r, tier2_cap)
    bonus = bonus + tier2 * (1.0/9.0)
    r = r - tier2
    if r <= 0 then return bonus end
    -- Ranks above level: 1/20 each
    bonus = bonus + r * 0.05
    return bonus
end

-- ── Standard round / ceiling helpers ─────────────────────────────────
local function round_std(n)
    return math.floor(n + 0.5)
end

local function ceiling(n)
    return math.ceil(n)
end

-- ── Get stat bonus from a character row ──────────────────────────────
-- Returns the numeric stat bonus for the given stat key.
-- stat_key: "aura","wisdom","logic","discipline","influence","intuition"
local function stat_bonus(char, stat_key)
    local raw = char["stat_" .. stat_key] or 50
    return GS4Math.stat_bonus(raw)
end

-- ── Stat bonus for a specific circle ─────────────────────────────────
-- cs_stat values: aura | wisdom | logic | avg_aura_wis | avg_inf_log | avg_dis_log
local function circle_stat_bonus(char, cs_stat)
    if cs_stat == "aura" then
        return stat_bonus(char, "aura")
    elseif cs_stat == "wisdom" then
        return stat_bonus(char, "wisdom")
    elseif cs_stat == "logic" then
        return stat_bonus(char, "logic")
    elseif cs_stat == "avg_aura_wis" then
        local a = stat_bonus(char, "aura")
        local w = stat_bonus(char, "wisdom")
        return math.ceil((a + w) / 2)
    elseif cs_stat == "avg_inf_log" then
        local i = stat_bonus(char, "influence")
        local l = stat_bonus(char, "logic")
        return math.ceil((i + l) / 2)
    elseif cs_stat == "avg_dis_log" then
        local d = stat_bonus(char, "discipline")
        local l = stat_bonus(char, "logic")
        return math.ceil((d + l) / 2)
    end
    return 0
end

-- ── Load a character's spell ranks from DB ────────────────────────────
-- Returns { [circle_id] = ranks, ... }
function CS.load_spell_ranks(character_id)
    local rows = DB.query(
        "SELECT circle_id, ranks FROM character_spell_ranks WHERE character_id=?",
        { character_id }
    )
    local ranks = {}
    for _, row in ipairs(rows) do
        ranks[row.circle_id] = row.ranks or 0
    end
    return ranks
end

-- ── Active buff CS bonuses ────────────────────────────────────────────
-- Returns the total CS bonus from active buffs for a given sphere.
-- sphere: "elemental" | "spiritual" | "mental" | "hybrid_es" etc.
local function buff_cs_bonus(character_id, sphere)
    local buffs = ActiveBuffs.get_active(character_id)
    local total = 0.0
    for _, buff in ipairs(buffs) do
        local effects = buff.effects or {}
        -- "cs_all" applies to everything
        total = total + (effects.cs_all or 0)
        -- Sphere-specific: full bonus if matching, half if related hybrid
        local cs_ele = effects.cs_elemental or 0
        local cs_spi = effects.cs_spiritual or 0
        local cs_men = effects.cs_mental    or 0
        if sphere == "elemental" then
            total = total + cs_ele + cs_spi * 0.5
        elseif sphere == "spiritual" then
            total = total + cs_spi + cs_ele * 0.5
        elseif sphere == "mental" then
            total = total + cs_men
        elseif sphere == "hybrid_es" then
            total = total + (cs_ele + cs_spi) * 0.5
        elseif sphere == "hybrid_em" then
            total = total + cs_ele * 0.5 + cs_men * 0.5
        elseif sphere == "hybrid_sm" then
            total = total + cs_spi * 0.5 + cs_men * 0.5
        end
    end
    return total
end

-- ── Main CS calculation ───────────────────────────────────────────────
-- char:         character db row (must have .level, stat fields)
-- spell_number: the spell being cast (to determine primary circle)
-- spell_ranks:  table { [circle_id]=N } — all trained circles
-- Returns: integer CS value
function CS.calculate(char, spell_number, spell_ranks)
    local level        = char.level or 1
    local circle       = SpellCircles.primary_for_spell(spell_number)
    local profession   = SpellCircles.profession_circles[char.profession_id] or {}

    -- Base: level × 3
    local cs = level * 3

    -- Primary circle bonus
    local primary_ranks = 0
    if circle then
        primary_ranks = (spell_ranks and spell_ranks[circle.id]) or 0
    end

    if circle and SpellCircles.can_train(char.profession_id, circle.id) then
        -- Character can train this circle → use primary bonus formula
        cs = cs + round_std(primary_bonus(primary_ranks, level))
    else
        -- Circle not trainable by this profession (e.g. casting from item)
        -- No primary circle bonus per wiki
    end

    -- Secondary circle bonuses (all trained circles except the primary)
    local secondary_total = 0.0
    if spell_ranks then
        for cid, ranks in pairs(spell_ranks) do
            if (not circle) or cid ~= circle.id then
                secondary_total = secondary_total + secondary_bonus(ranks, level)
            end
        end
    end
    cs = cs + ceiling(secondary_total)

    -- Stat bonus for this circle
    if circle then
        cs = cs + round_std(circle_stat_bonus(char, circle.cs_stat))
    end

    -- Active spell buff bonuses
    if circle then
        local buff_bonus = buff_cs_bonus(char.id, circle.sphere)
        cs = cs + round_std(buff_bonus)
    end

    return cs
end

return CS
