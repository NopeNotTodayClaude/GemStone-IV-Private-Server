-- =============================================================================
-- scripts/globals/ucs.lua
-- Unarmed Combat System configuration.
-- Keeps shared UCS tuning in Lua so punch/kick/grapple math is not hardcoded
-- across Python call sites.
--
-- GSWiki notes used for the current baseline:
--   - UAF/UDF ratio is capped at 2.000
--   - MM is driven by stance and situational positioning
--   - UDF is primarily overall defense; when a creature has no authored UDF,
--     the fallback should be based on melee defense plus a level bonus instead
--     of using raw melee DS alone.
-- =============================================================================

local UCS = {}

-- Hard cap on the computed UAF / UDF ratio.
UCS.ratio_cap = 2.0

-- Tier-1 "decent positioning" multiplier modifier by stance.
-- Average MM in offensive is 100; the other stances are intentionally lower.
UCS.stance_mm = {
    offensive = 100,
    advance   = 90,
    forward   = 80,
    neutral   = 70,
    guarded   = 55,
    defensive = 40,
}

-- Creature / NPC fallback UDF when the authored template leaves Creature.udf=0.
-- UDF should scale from overall defense, not raw melee DS alone.
UCS.fallback_udf = {
    minimum = 1,
    melee_ds_multiplier = 1.0,
    level_bonus_multiplier = 2.0,
    flat_bonus = 0,
}

return UCS
