------------------------------------------------------------------------
-- scripts/globals/magic/spell_hindrance.lua
-- Spell hindrance system for GemStone IV.
-- Source: gswiki.play.net/Spell_hindrance
--
-- Hindrance is a % chance armor prevents a spell from working.
-- Heavier armor interferes more, especially with elemental/mental circles.
-- Hindrance is reduced by training in Armor Use.
--
-- Formula:
--   Required Armor Use Bonus = (Base Hindrance × 20) - 10
--   Total Hindrance = Base Hindrance × (1 + (Required Bonus - Current Bonus) / 20)
--   Total Hindrance is capped at the armor's Max Hindrance.
--
-- Hindrance is nullified in natural sanctuaries and Major/Minor Sanctuary areas.
-- A 1% fumble chance exists for ALL attack spells regardless of hindrance.
------------------------------------------------------------------------

local ActiveBuffs = require("globals/magic/active_buffs")

local Hindrance = {}

-- ── Base hindrance table ──────────────────────────────────────────────
-- Source: gswiki.play.net/Spell_hindrance — "Chart of Armor Spell Hindrance Minimum Penalties"
-- Key = ASG (Armor Subcategory Group)
-- Values: { MnS, MjS, Cle, MnE, MjE, Ran, Sor, Wiz, Bar, Emp, MnM, MjM, Pal, max }
-- circle_id order: 1=MnS 2=MjS 3=Cle 4=MnE 5=MjE 6=Ran 7=Sor 8=Wiz 9=Bar 10=Emp 11=Pal 12=MnM 13=MjM
Hindrance.base = {
    -- ASG 1: Normal Clothing — no hindrance
    [1]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=0,  [6]=0, [7]=0,  [8]=0,  [9]=0,  [10]=0, [11]=0, [12]=0, [13]=0, max=0  },
    -- ASG 2: Robes — no hindrance
    [2]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=0,  [6]=0, [7]=0,  [8]=0,  [9]=0,  [10]=0, [11]=0, [12]=0, [13]=0, max=0  },
    -- ASG 5: Light Leather — no hindrance
    [5]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=0,  [6]=0, [7]=0,  [8]=0,  [9]=0,  [10]=0, [11]=0, [12]=0, [13]=0, max=0  },
    -- ASG 6: Full Leather — no hindrance
    [6]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=0,  [6]=0, [7]=0,  [8]=0,  [9]=0,  [10]=0, [11]=0, [12]=0, [13]=0, max=0  },
    -- ASG 7: Reinforced Leather
    [7]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=2,  [6]=0, [7]=1,  [8]=2,  [9]=0,  [10]=0, [11]=0, [12]=2, [13]=2, max=4  },
    -- ASG 8: Double Leather
    [8]  = { [1]=0, [2]=0, [3]=0, [4]=0,  [5]=4,  [6]=0, [7]=2,  [8]=4,  [9]=2,  [10]=0, [11]=0, [12]=4, [13]=4, max=6  },
    -- ASG 9: Leather Breastplate
    [9]  = { [1]=3, [2]=4, [3]=4, [4]=4,  [5]=6,  [6]=3, [7]=5,  [8]=6,  [9]=3,  [10]=4, [11]=2, [12]=4, [13]=6, max=16 },
    -- ASG 10: Cuirbouilli Leather
    [10] = { [1]=4, [2]=5, [3]=5, [4]=5,  [5]=7,  [6]=4, [7]=6,  [8]=7,  [9]=3,  [10]=5, [11]=3, [12]=5, [13]=7, max=20 },
    -- ASG 11: Studded Leather
    [11] = { [1]=5, [2]=6, [3]=6, [4]=6,  [5]=9,  [6]=5, [7]=8,  [8]=9,  [9]=3,  [10]=6, [11]=4, [12]=6, [13]=9, max=24 },
    -- ASG 12: Brigandine Armor
    [12] = { [1]=6, [2]=7, [3]=7, [4]=7,  [5]=12, [6]=6, [7]=11, [8]=12, [9]=7,  [10]=7, [11]=5, [12]=7, [13]=12, max=28 },
    -- ASG 13: Chain Mail
    [13] = { [1]=7, [2]=8, [3]=8, [4]=8,  [5]=16, [6]=7, [7]=16, [8]=16, [9]=8,  [10]=8, [11]=6, [12]=8, [13]=16, max=40 },
    -- ASG 14: Double Chain
    [14] = { [1]=8, [2]=9, [3]=9, [4]=9,  [5]=20, [6]=8, [7]=18, [8]=20, [9]=8,  [10]=9, [11]=7, [12]=9, [13]=20, max=45 },
    -- ASG 15: Augmented Chain
    [15] = { [1]=9, [2]=11,[3]=11,[4]=10, [5]=25, [6]=9, [7]=22, [8]=25, [9]=8,  [10]=11,[11]=8, [12]=10,[13]=25, max=55 },
    -- ASG 16: Chain Hauberk
    [16] = { [1]=11,[2]=14,[3]=14,[4]=12, [5]=30, [6]=11,[7]=26, [8]=30, [9]=15, [10]=15,[11]=9, [12]=15,[13]=30, max=60 },
    -- ASG 17: Metal Breastplate
    [17] = { [1]=16,[2]=25,[3]=25,[4]=16, [5]=35, [6]=21,[7]=29, [8]=35, [9]=21, [10]=25,[11]=10,[12]=21,[13]=35, max=90 },
    -- ASG 18: Augmented Breastplate
    [18] = { [1]=17,[2]=28,[3]=28,[4]=18, [5]=40, [6]=24,[7]=33, [8]=40, [9]=21, [10]=28,[11]=11,[12]=21,[13]=40, max=92 },
    -- ASG 19: Half Plate
    [19] = { [1]=18,[2]=32,[3]=32,[4]=20, [5]=45, [6]=27,[7]=39, [8]=45, [9]=21, [10]=32,[11]=12,[12]=21,[13]=45, max=94 },
    -- ASG 20: Full Plate
    [20] = { [1]=20,[2]=45,[3]=45,[4]=22, [5]=50, [6]=30,[7]=48, [8]=50, [9]=50, [10]=45,[11]=13,[12]=50,[13]=50, max=96 },
}

-- ── Armor Use skill bonus from ranks ──────────────────────────────────
-- Using standard GS4 skill bonus approximation.
local function armor_use_bonus(ranks)
    local bonus = 0
    local r = ranks
    local tiers = {{20,5},{20,3},{60,2}}
    for _, tier in ipairs(tiers) do
        if r <= 0 then break end
        local take = math.min(r, tier[1])
        bonus = bonus + take * tier[2]
        r = r - take
    end
    if r > 0 then bonus = bonus + r * 1 end
    return bonus
end

-- ── Get base hindrance for a circle in given armor ────────────────────
-- circle_id: 1-13 as per spell_circles
-- asg: Armor Subcategory Group (1-20)
-- Returns base hindrance percentage (integer)
local function get_base_hindrance(circle_id, asg)
    local armor_row = Hindrance.base[asg]
    if not armor_row then return 0 end
    return armor_row[circle_id] or 0
end

-- ── Calculate total hindrance for a cast attempt ─────────────────────
-- circle_id:     the spell circle being cast
-- asg:           Armor Subcategory Group of caster's torso armor
-- armor_use_ranks: caster's Armor Use skill ranks
-- character_id:  for active buff reduction lookup (nullable)
-- Returns: total_hindrance (integer %), is_sanctified (bool)
function Hindrance.calculate(circle_id, asg, armor_use_ranks, character_id)
    -- Robes and lighter: never any hindrance
    if not asg or asg <= 6 then return 0 end

    local armor_row = Hindrance.base[asg]
    if not armor_row then return 0 end

    local base = armor_row[circle_id] or 0
    if base == 0 then return 0 end
    local max_hind = armor_row.max or base

    -- Active buff reductions (e.g. Faith's Clarity 1612)
    local redux = 0
    if character_id then
        redux = ActiveBuffs.total_hindrance_redux(character_id)
    end
    local effective_base = math.max(0, base - redux)
    if effective_base == 0 then return 0 end

    -- Required Armor Use bonus to reach minimum hindrance
    local required_bonus = (effective_base * 20) - 10
    local current_bonus  = armor_use_bonus(armor_use_ranks or 0)

    local total
    if current_bonus >= required_bonus then
        -- Fully trained: minimum hindrance applies
        total = effective_base
    else
        -- Under-trained penalty
        total = math.floor(
            effective_base * (1 + (required_bonus - current_bonus) / 20)
        )
        -- Cap at armor's max hindrance
        total = math.min(total, max_hind)
    end

    return total
end

-- ── Roll hindrance: did the armor block the cast? ─────────────────────
-- Returns true if cast is BLOCKED, false if cast proceeds.
-- Also returns the hindrance % for messaging.
function Hindrance.roll(circle_id, asg, armor_use_ranks, character_id, in_sanctuary)
    -- Sanctuaries nullify hindrance entirely
    if in_sanctuary then return false, 0 end

    local pct = Hindrance.calculate(circle_id, asg, armor_use_ranks, character_id)
    if pct <= 0 then return false, 0 end

    local d100 = math.random(1, 100)
    local blocked = d100 <= pct
    return blocked, pct, d100
end

-- ── Arcane spell hindrance ────────────────────────────────────────────
-- Arcane spells use the hindrance of their "native" circle if they have one.
-- Spells without a native circle use Sorcerer Base (circle_id=7) hindrance.
-- native_circle_id: nil if no native circle
function Hindrance.arcane_circle(native_circle_id)
    return native_circle_id or 7  -- default to Sorcerer Base
end

return Hindrance
