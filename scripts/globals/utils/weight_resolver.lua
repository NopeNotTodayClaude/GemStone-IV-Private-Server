-- =============================================================================
-- scripts/globals/utils/weight_resolver.lua
--
-- Effective item weight calculator for GemStone IV.
--
-- The items table stores BASE weight (the weight of the object in a neutral
-- material — typically steel or iron).  Each material has a weight_modifier
-- that scales that base weight.  A kelyn weapon at 0.7x weighs 30% less;
-- an imflass shield at 0.6x is 40% lighter; a gornar piece at 1.1x is heavier.
--
-- This module is the single source of truth for effective weight.
-- encumbrance.py and any other Python code calls material_combat.py, which
-- calls this module via the Lua engine.
--
-- Usage from Python (via material_combat.py):
--   eff_weight = weight_resolver.effectiveWeight(item_data)
--   total      = weight_resolver.totalInventoryWeight(item_list)
--
-- item_data is a dict/table with at minimum:
--   { weight = N, material = "kelyn" }
-- =============================================================================

local Materials = require("data/items/materials")

local WeightResolver = {}

---
-- effectiveWeight(item_data)
--
-- Returns the effective weight of a single item after applying its material's
-- weight_modifier.  If the material is unknown or unset, modifier = 1.0.
--
-- item_data  table: { weight=N, material="..." }
--
function WeightResolver.effectiveWeight(item_data)
    if not item_data then return 0.0 end

    local base_weight = tonumber(item_data.weight) or 0.0
    if base_weight <= 0 then return 0.0 end

    local modifier = Materials.weightModifier(item_data.material)
    return base_weight * modifier
end

---
-- totalInventoryWeight(item_list)
--
-- Sum effective weights across a list of items.
-- Skips items that have container_id set (stowed inside containers, GS4 rule).
-- Intended for verifying encumbrance from the Lua side; Python's
-- encumbrance.py is the canonical caller but this is available for scripting.
--
-- item_list  array of item tables, each with { weight, material, container_id? }
--
function WeightResolver.totalInventoryWeight(item_list)
    local total = 0.0
    if not item_list then return total end
    for _, item in ipairs(item_list) do
        if not item.container_id then
            total = total + WeightResolver.effectiveWeight(item)
        end
    end
    return total
end

return WeightResolver
