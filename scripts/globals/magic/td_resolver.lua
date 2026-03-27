------------------------------------------------------------------------
-- scripts/globals/magic/td_resolver.lua
-- Target Defense (TD) calculation for GemStone IV warding spells.
-- Source: gswiki.play.net/Target_defense
--
-- Formula:
--   TD = (Level × 3) + Stat Bonus + Racial Bonus + Active Buff Bonuses
--
-- Stat used depends on the attacking circle's sphere:
--   Spiritual spells  → Wisdom
--   Elemental spells  → Aura
--   Mental spells     → Discipline
--   Sorcerer (hybrid) → average of Aura and Wisdom
--   Arcane            → average of Aura and Wisdom
--
-- Spells that add to one TD type bleed into others:
--   +X Spirit TD → +X/2 Elemental TD, +X*0.75 Sorcerer TD  (rounded)
--   +X Sorcerer TD → +X*0.75 Ele/Spi TD, +X/2 Mental TD   (rounded)
--
-- Racial TD bonuses are applied as flat additions per sphere.
------------------------------------------------------------------------

local DB           = require("globals/utils/db")
local SpellCircles = require("globals/magic/spell_circles")
local ActiveBuffs  = require("globals/magic/active_buffs")

local TD = {}

-- ── Racial TD bonuses ────────────────────────────────────────────────
-- Source: gswiki.play.net/Target_defense — "Natural TD bonuses" table
-- race_id → { spiritual=N, elemental=N, mental=N }
-- NOTE: race IDs must match the races table in the DB.
-- Checking SQL for race IDs: from character data race_id is present.
TD.racial_bonuses = {
    -- Aelotoi: all 0
    [1]  = { spiritual=0,   elemental=0,   mental=0  },
    -- Burghal Gnome: all 0
    [2]  = { spiritual=0,   elemental=0,   mental=0  },
    -- Dark Elf: -5 spi, -5 ele, 0 men
    [3]  = { spiritual=-5,  elemental=-5,  mental=0  },
    -- Dwarf: 0 spi, +30 ele, 0 men
    [4]  = { spiritual=0,   elemental=30,  mental=0  },
    -- Elf: -5 spi, -5 ele, 0 men
    [5]  = { spiritual=-5,  elemental=-5,  mental=0  },
    -- Erithian: all 0
    [6]  = { spiritual=0,   elemental=0,   mental=0  },
    -- Forest Gnome: all 0
    [7]  = { spiritual=0,   elemental=0,   mental=0  },
    -- Giantman: +5 spi, 0 ele, 0 men
    [8]  = { spiritual=5,   elemental=0,   mental=0  },
    -- Half-Elf: -5 spi, -5 ele, 0 men
    [9]  = { spiritual=-5,  elemental=-5,  mental=0  },
    -- Half-Krolvin: all 0
    [10] = { spiritual=0,   elemental=0,   mental=0  },
    -- Halfling: 0 spi, +40 ele, 0 men
    [11] = { spiritual=0,   elemental=40,  mental=0  },
    -- Human: all 0
    [12] = { spiritual=0,   elemental=0,   mental=0  },
    -- Sylvankind: -5 spi, -5 ele, 0 men
    [13] = { spiritual=-5,  elemental=-5,  mental=0  },
}

-- ── Stat bonus helper ─────────────────────────────────────────────────
local function stat_bonus(raw_stat)
    return math.floor((raw_stat - 50) / 5)
end

local function get_stat(char, key)
    return stat_bonus(char["stat_" .. key] or 50)
end

-- ── Active buff TD bonuses ─────────────────────────────────────────────
-- Reads character_active_buffs for td_* effects.
-- Returns { spiritual=N, elemental=N, mental=N, sorcerer=N }
-- applying the bleed-through rules from the wiki.
local function buff_td_bonuses(character_id)
    local buffs = ActiveBuffs.get_active(character_id)
    local spi_raw = 0
    local ele_raw = 0
    local men_raw = 0
    local sor_raw = 0

    for _, buff in ipairs(buffs) do
        local e = buff.effects or {}
        spi_raw = spi_raw + (e.td_spiritual or 0)
        ele_raw = ele_raw + (e.td_elemental or 0)
        men_raw = men_raw + (e.td_mental    or 0)
        sor_raw = sor_raw + (e.td_sorcerer  or 0)
    end

    -- Apply bleed-through per wiki:
    --   +X spirit → +X*0.5 elemental, +X*0.75 sorcerer
    --   +X elemental → +X*0.5 spirit, +X*0.75 sorcerer
    --   +X sorcerer → +X*0.75 ele and spi, +X*0.5 mental
    local result = {
        spiritual = spi_raw + math.floor(ele_raw * 0.5) + math.floor(sor_raw * 0.75),
        elemental = ele_raw + math.floor(spi_raw * 0.5) + math.floor(sor_raw * 0.75),
        mental    = men_raw + math.floor(sor_raw * 0.5),
        sorcerer  = sor_raw + math.floor(math.floor((spi_raw + ele_raw) / 2) * 0.75),
    }
    return result
end

-- ── Main TD calculation ───────────────────────────────────────────────
-- target:       character or creature db row (needs .level, stat fields, .race_id)
-- spell_number: the spell being cast (used to identify the sphere)
-- Returns: integer TD value
function TD.calculate(target, spell_number)
    local circle = SpellCircles.primary_for_spell(spell_number)
    local sphere = circle and circle.sphere or "spiritual"
    local level  = target.level or 1

    -- Base: level × 3
    local td = level * 3

    -- Stat bonus by sphere
    if sphere == "spiritual" then
        td = td + get_stat(target, "wisdom")
    elseif sphere == "elemental" then
        td = td + get_stat(target, "aura")
    elseif sphere == "mental" then
        td = td + get_stat(target, "discipline")
    elseif sphere == "hybrid_es" or sphere == "arcane" then
        -- Sorcerer / Arcane: average of Aura and Wisdom (round up)
        local a = get_stat(target, "aura")
        local w = get_stat(target, "wisdom")
        td = td + math.ceil((a + w) / 2)
    elseif sphere == "hybrid_em" then
        -- Bard: average Aura + Logic? Per wiki Bard uses Aura for CS/TD.
        td = td + get_stat(target, "aura")
    elseif sphere == "hybrid_sm" then
        -- Empath: uses Wisdom
        td = td + get_stat(target, "wisdom")
    end

    -- Racial TD bonus
    local race_id = target.race_id or 12
    local racial  = TD.racial_bonuses[race_id]
    if racial then
        if sphere == "spiritual" or sphere == "hybrid_sm" then
            td = td + (racial.spiritual or 0)
        elseif sphere == "elemental" or sphere == "hybrid_em" then
            td = td + (racial.elemental or 0)
        elseif sphere == "mental" then
            td = td + (racial.mental or 0)
        elseif sphere == "hybrid_es" or sphere == "arcane" then
            -- Sorcerer: average of spi/ele racial bonuses (wiki: apply average)
            td = td + math.floor(((racial.spiritual or 0) + (racial.elemental or 0)) / 2)
        end
    end

    -- Active buff TD bonuses (applies to player targets only; creatures skip)
    if target.id then
        local buffs = buff_td_bonuses(target.id)
        if sphere == "spiritual" or sphere == "hybrid_sm" then
            td = td + (buffs.spiritual or 0)
        elseif sphere == "elemental" or sphere == "hybrid_em" then
            td = td + (buffs.elemental or 0)
        elseif sphere == "mental" then
            td = td + (buffs.mental or 0)
        elseif sphere == "hybrid_es" or sphere == "arcane" then
            td = td + (buffs.sorcerer or 0)
        end
    end

    return td
end

-- ── CvA: Cast vs Armor modifier ──────────────────────────────────────
-- Source: gswiki.play.net/CvA
-- A small constant per armor ASG; heavier armor provides better CvA
-- (slightly easier to resist warding via armor).
-- ASG → CvA modifier (positive = helps caster, negative = helps defender)
TD.cva_table = {
    [1]  =  0,   -- Normal Clothing
    [2]  =  2,   -- Robes
    [5]  = -2,   -- Light Leather
    [6]  = -2,   -- Full Leather
    [7]  = -4,   -- Reinforced Leather
    [8]  = -6,   -- Double Leather
    [9]  = -7,   -- Leather Breastplate
    [10] = -7,   -- Cuirbouilli Leather
    [11] = -8,   -- Studded Leather
    [12] = -9,   -- Brigandine
    [13] = -12,  -- Chain Mail
    [14] = -13,  -- Double Chain
    [15] = -14,  -- Augmented Chain
    [16] = -15,  -- Chain Hauberk
    [17] = -17,  -- Metal Breastplate
    [18] = -18,  -- Augmented Breastplate
    [19] = -20,  -- Half Plate
    [20] = -25,  -- Full Plate
}

-- Returns the CvA value for a target's equipped torso armor.
-- Positive CvA means the armor makes warding HARDER to resist (favors caster).
-- Negative CvA means the armor makes warding EASIER to resist (favors defender).
function TD.get_cva(target_armor_asg)
    return TD.cva_table[target_armor_asg] or 0
end

return TD
