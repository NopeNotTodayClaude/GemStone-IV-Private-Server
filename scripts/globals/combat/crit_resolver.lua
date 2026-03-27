-- =============================================================================
-- scripts/globals/combat/crit_resolver.lua
--
-- Material-aware critical hit resolver for GemStone IV.
--
-- GS4 wiki reference: gswiki.play.net/Weighting
--
-- What this does:
--   The standard combat_engine.py crit flow is:
--     crit_rank_max = min(9, raw_damage // crit_divisor)
--     crit_rank_min = max(1, (crit_rank_max + 1) // 2)
--     crit_rank     = random(crit_rank_min, crit_rank_max)
--
--   razern has crit_weight = 2, which implements the GS4 CEP mechanic:
--   phantom damage points are added to raw_damage BEFORE the divisor is applied,
--   raising the effective crit rank floor without inflating HP damage.
--
--   This module returns the adjusted raw_damage for Python to use in the
--   standard crit formula.  Python's HP damage formula is unchanged —
--   only the crit rank derivation sees the phantom points.
--
-- Called from Python via:
--   result = crit_resolver.resolve(material_name, raw_damage, cap)
--
-- Returns:
--   { adjusted_raw_damage = N, crit_weight = N, material = "..." }
--
-- Python then runs its crit formula with adjusted_raw_damage for the
-- rank calculation, but uses the ORIGINAL raw_damage for HP damage.
-- =============================================================================

local Materials = require("data/items/materials")

local CritResolver = {}

---
-- resolve(material_name, raw_damage, rank_cap)
--
-- material_name  string: weapon's material (e.g. "razern")
-- raw_damage     int: damage from (endroll - 100) * weapon_df
-- rank_cap       int: max allowed rank (9 for most attacks, 5 for unarmed tier 1)
--
-- Returns a table:
--   adjusted_raw_damage  int: raw_damage + crit_weight phantom points
--   crit_weight          int: how many phantom points were added (0 for non-razern)
--   material             string: material name echoed back
--
function CritResolver.resolve(material_name, raw_damage, rank_cap)
    local crit_weight = Materials.critWeight(material_name)  -- 0 for all except razern (2)
    local adj = raw_damage + crit_weight

    return {
        adjusted_raw_damage = adj,
        crit_weight         = crit_weight,
        material            = material_name or "",
    }
end

---
-- quickCritWeight(material_name)
--
-- Convenience: just return the crit_weight integer for a material.
-- Used when Python only needs the number and not the full resolution.
--
function CritResolver.quickCritWeight(material_name)
    return Materials.critWeight(material_name)
end

return CritResolver
