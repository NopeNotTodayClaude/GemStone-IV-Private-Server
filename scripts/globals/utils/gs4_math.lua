------------------------------------------------------------------------
-- scripts/globals/utils/gs4_math.lua
-- Shared canonical GemStone IV math helpers.
------------------------------------------------------------------------

local Math = {}

local function safe_int(v)
    return tonumber(v) or 0
end

-- GS4 stat bonus conversion.
-- Example: 50 -> 0, 60 -> +5, 100 -> +25.
function Math.stat_bonus(raw_stat)
    return math.floor((safe_int(raw_stat) - 50) / 2)
end

-- GS4 skill bonus conversion.
-- Ranks 1-10: +5 each
-- Ranks 11-20: +4 each
-- Ranks 21-30: +3 each
-- Ranks 31-40: +2 each
-- Ranks 41+: +1 each
function Math.skill_bonus_from_ranks(ranks)
    ranks = safe_int(ranks)
    if ranks <= 0 then return 0 end

    local bonus = 0
    local remaining = ranks
    local tiers = {
        { 10, 5 },
        { 10, 4 },
        { 10, 3 },
        { 10, 2 },
    }

    for _, tier in ipairs(tiers) do
        local take = math.min(remaining, tier[1])
        bonus = bonus + take * tier[2]
        remaining = remaining - take
        if remaining <= 0 then
            return bonus
        end
    end

    return bonus + remaining
end

return Math
