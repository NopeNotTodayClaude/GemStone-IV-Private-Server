------------------------------------------------------------------------
-- bleed_system.lua
-- GemStone IV Bleeding Tick System
--
-- Called from the game loop (via wound_bridge) each tick for characters
-- who have active (unbandaged) bleeding wounds.
--
-- Bleed rates (per tick, randomized):
--   rank 1 wound : 0 HP  (rank 1 doesn't bleed on its own)
--   rank 2 wound : 1-2 HP
--   rank 3 wound : 2-4 HP
--
-- Tick interval: every 8 seconds (matches status_effects tick_interval)
-- Fatal at 0 HP (triggers death system like normal).
------------------------------------------------------------------------

local WoundSystem = require("globals/wound_system")

local BleedSystem = {}

-- Damage range per wound rank (min, max)
local BLEED_RANGE = {
    [0] = { 0, 0 },
    [1] = { 0, 0 },
    [2] = { 1, 2 },
    [3] = { 2, 4 },
}

-- Messages shown to player when bleeding ticks
local BLEED_MSGS = {
    low  = {
        "A trickle of blood flows from your wound.",
        "You feel blood seeping from your injury.",
        "Your wound continues to bleed slowly.",
    },
    high = {
        "Blood pours from your wound!",
        "You are bleeding heavily!",
        "Your wounds bleed freely, sapping your strength!",
    },
}

local function rand_msg(tbl)
    return tbl[math.random(1, #tbl)]
end

-- ── Main tick function ────────────────────────────────────────────────
-- wounds:   Lua table mirror of session.wounds
-- Returns:  total_damage (int), messages (list of strings), wounds (updated)

function BleedSystem.tick(wounds)
    local total_damage = 0
    local messages     = {}
    local locations_bleeding = {}

    for _, loc in ipairs(WoundSystem.LOCATIONS) do
        local entry = wounds[loc]
        if entry and entry.is_bleeding and not entry.bandaged then
            local wr  = entry.wound_rank or 0
            local rng = BLEED_RANGE[wr] or BLEED_RANGE[0]
            if rng[2] > 0 then
                local dmg = math.random(rng[1], rng[2])
                total_damage = total_damage + dmg
                table.insert(locations_bleeding,
                    WoundSystem.LOCATION_DISPLAY[loc] or loc)
            end
        end
    end

    -- Build message based on severity
    if total_damage > 0 then
        if total_damage >= 3 then
            table.insert(messages, rand_msg(BLEED_MSGS.high))
        else
            table.insert(messages, rand_msg(BLEED_MSGS.low))
        end
        if #locations_bleeding > 1 then
            table.insert(messages,
                "  (" .. table.concat(locations_bleeding, ", ") .. ")")
        end
    end

    return total_damage, messages, wounds
end

-- ── Spontaneous stop ─────────────────────────────────────────────────
-- Small chance per tick that a minor wound stops bleeding on its own.
-- rank 2: 5% chance / tick; rank 3: never stops without TEND / herb.

function BleedSystem.check_natural_stop(wounds)
    local stopped = {}
    for _, loc in ipairs(WoundSystem.LOCATIONS) do
        local entry = wounds[loc]
        if entry and entry.is_bleeding and not entry.bandaged then
            local wr = entry.wound_rank or 0
            if wr <= 2 and math.random(1, 100) <= 5 then
                entry.is_bleeding = false
                table.insert(stopped, WoundSystem.LOCATION_DISPLAY[loc] or loc)
            end
        end
    end
    return stopped, wounds
end

-- ── Death bleed warning thresholds ───────────────────────────────────
-- Returns a warning string based on current HP and bleed rate,
-- or nil if no urgent warning needed.

function BleedSystem.death_warning(current_hp, max_hp, total_bleed_per_tick)
    if total_bleed_per_tick == 0 then return nil end
    local ticks_to_death = (total_bleed_per_tick > 0)
                           and math.floor(current_hp / total_bleed_per_tick)
                           or  999
    if ticks_to_death <= 3 then
        return "*** You are bleeding to death! ***"
    elseif ticks_to_death <= 8 then
        return "You are losing blood rapidly!"
    end
    return nil
end

return BleedSystem
