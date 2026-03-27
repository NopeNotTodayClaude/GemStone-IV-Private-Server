---------------------------------------------------
-- sheath.lua
-- Container behavior for sheaths and scabbards.
--
-- In GS4, sheaths are wearable containers that accept only specific
-- weapon nouns.  This script gates PUT attempts and handles the worn
-- sheath slot properly.
--
-- Supported item nouns (maps to sheath types):
--   dagger_sheath    → dagger, main gauche, dirk, stiletto, knife
--   small_scabbard   → short sword, backsword
--   scabbard         → longsword, broadsword, rapier, falchion, scimitar,
--                       saber, cutlass, wakizashi
--   large_scabbard   → claidhmore, greatsword, bastard sword, two-handed sword
--   axe_sheath       → hand axe, battle axe, hatchet
--   mace_sheath      → (typically maces don't sheath in GS4 – blocked)
--
-- The 'sheath_type' column is set in the items DB row (see migration).
-- Capacity is always 1 for sheaths.
---------------------------------------------------

local Sheath = {}

-- ── Weapon noun acceptance tables ────────────────────────────────────────────
-- Key = sheath_type tag on the item row.
-- Value = set of accepted weapon nouns (lowercase).
local ACCEPTS = {
    dagger_sheath = {
        ["dagger"]     = true,
        ["main gauche"]= true,
        ["dirk"]       = true,
        ["stiletto"]   = true,
        ["knife"]      = true,
        ["sgian dubh"] = true,
    },
    small_scabbard = {
        ["short sword"] = true,
        ["backsword"]   = true,
        ["wakizashi"]   = true,
    },
    scabbard = {
        ["longsword"]   = true,
        ["broadsword"]  = true,
        ["rapier"]      = true,
        ["falchion"]    = true,
        ["scimitar"]    = true,
        ["saber"]       = true,
        ["cutlass"]     = true,
        ["espee"]       = true,
        ["backsword"]   = true,
        ["short sword"] = true,   -- also fits if no small_scabbard available
    },
    large_scabbard = {
        ["claidhmore"]         = true,
        ["greatsword"]         = true,
        ["bastard sword"]      = true,
        ["two-handed sword"]   = true,
        ["two-handed falchion"]= true,
    },
    axe_sheath = {
        ["hand axe"]   = true,
        ["battle axe"] = true,
        ["hatchet"]    = true,
        ["tomahawk"]   = true,
    },
}

-- ─────────────────────────────────────────────────────────────────────────────
-- canAccept(sheath_item, weapon_item)
-- Returns true/false, and an error message string if false.
-- ─────────────────────────────────────────────────────────────────────────────
function Sheath.canAccept(sheath_item, weapon_item)
    local sheath_type = sheath_item:getTag("sheath_type")
    if not sheath_type then
        return false, "That doesn't seem to be a proper sheath."
    end

    local accepted = ACCEPTS[sheath_type]
    if not accepted then
        return false, "That sheath type is unknown."
    end

    -- Check if it's a weapon at all
    if weapon_item:getItemType() ~= "weapon" then
        return false, "That won't fit in a sheath."
    end

    -- Match on the weapon's noun (base name)
    local noun = weapon_item:getNoun():lower()
    if accepted[noun] then
        return true
    end

    -- Build a friendly error with accepted types
    local names = {}
    for k in pairs(accepted) do names[#names+1] = k end
    table.sort(names)
    return false, string.format(
        "The %s won't fit in there.  It accepts: %s.",
        noun, table.concat(names, ", ")
    )
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onPut(player, sheath_item, weapon_item)
-- Called when a player attempts to PUT weapon IN/INTO sheath.
-- Return true = handled (allow or deny); false = fall through to default.
-- ─────────────────────────────────────────────────────────────────────────────
function Sheath.onPut(player, sheath_item, weapon_item)
    -- Already full?
    if sheath_item:getContents() and #sheath_item:getContents() >= 1 then
        player:message("The "..sheath_item:getNoun().." already holds a weapon.")
        return true
    end

    local ok, err = Sheath.canAccept(sheath_item, weapon_item)
    if not ok then
        player:message(err)
        return true
    end

    -- Success – engine handles actual inventory move; we just narrate.
    player:message("You slide "..weapon_item:getName().." into "..sheath_item:getName()..".")
    player:roomMessage(
        player:getName().." slides "..weapon_item:getName()..
        " into "..sheath_item:getName()..".",
        player
    )
    return false  -- let engine complete the move
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onRemove(player, sheath_item, weapon_item)
-- Called when a player GETs/REMOVEs the weapon from the sheath.
-- ─────────────────────────────────────────────────────────────────────────────
function Sheath.onRemove(player, sheath_item, weapon_item)
    player:message("You draw "..weapon_item:getName().." from "..sheath_item:getName()..".")
    player:roomMessage(
        player:getName().." draws "..weapon_item:getName()..
        " from "..sheath_item:getName()..".",
        player
    )
    return false  -- let engine complete the move
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onWear(player, sheath_item)
-- ─────────────────────────────────────────────────────────────────────────────
function Sheath.onWear(player, sheath_item)
    local slot = sheath_item:getTag("worn_location") or "hip"
    player:message("You strap "..sheath_item:getName().." to your "..slot..".")
    player:roomMessage(
        player:getName().." straps "..sheath_item:getName().." to their "..slot..".",
        player
    )
    return false
end

-- ─────────────────────────────────────────────────────────────────────────────
-- onRemoveWorn(player, sheath_item)
-- ─────────────────────────────────────────────────────────────────────────────
function Sheath.onRemoveWorn(player, sheath_item)
    player:message("You remove "..sheath_item:getName().." from your hip.")
    player:roomMessage(
        player:getName().." removes "..sheath_item:getName()..".",
        player
    )
    return false
end

return Sheath
