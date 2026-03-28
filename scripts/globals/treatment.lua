------------------------------------------------------------------------
-- treatment.lua
-- GemStone IV Treatment Dispatcher
--
-- Orchestrates herb application, TEND, and empath healing.
-- Called from wound_bridge.py; works with wound_system.lua + herbs.lua.
--
-- Public API:
--   Treatment.use_herb(wounds, herb_data, first_aid_bonus)
--     -> { ok, msg, wounds, changed_locs, scar_added }
--
--   Treatment.tend(wounds, location_input, first_aid_bonus)
--     -> { ok, msg, wounds, location }
--
--   Treatment.empath_heal(wounds, location_input)
--     -> { ok, msg, wounds, location }
--
--   Treatment.empath_heal_all(wounds)
--     -> { ok, msg, wounds, changed_locs }
------------------------------------------------------------------------

local WoundSystem = require("globals/wound_system")
local Herbs       = require("globals/herbs")

local Treatment = {}

-- ── 1. Herb use ──────────────────────────────────────────────────────
-- Applies a single bite of an herb.
-- wounds:          Lua table mirror of session.wounds
-- herb_data:       entry from Herbs.DATA
-- first_aid_bonus: int (FA skill bonus = ranks * 3)
-- location_hint:   optional specific location to target (player can't choose in GS4,
--                  but keep for empath/GM use)
--
-- Returns: result table

function Treatment.use_herb(wounds, herb_data, first_aid_bonus, location_hint)
    local result = {
        ok           = false,
        msg          = "",
        wounds       = wounds,
        changed_locs = {},
        scar_added   = false,
    }

    if not herb_data then
        result.msg = "You don't know how to use that."
        return result
    end

    local heal_type = herb_data.heal_type

    -- ── Blood / HP restore ──────────────────────────────────────────
    if heal_type == "blood" then
        result.ok  = true
        result.msg = herb_data.eat_msg or "The herb restores some of your health."
        result.hp_restore = herb_data.hp_restore or 0
        return result
    end

    -- ── Mana restore ────────────────────────────────────────────────
    if heal_type == "mana" then
        result.ok           = true
        result.msg          = herb_data.eat_msg or "Your mana is partially restored."
        result.mana_restore = herb_data.mana_restore or 0
        return result
    end

    -- ── Poison cure ─────────────────────────────────────────────────
    if heal_type == "poison" then
        result.ok          = true
        result.msg         = herb_data.eat_msg or "The poison begins to fade."
        result.cure_poison = true
        return result
    end

    -- ── Limb regeneration ───────────────────────────────────────────
    if heal_type == "limb_regen" then
        -- Find a severed limb (rank 3 wound in a limb location)
        local limb_locs = { "right_arm","left_arm","right_hand","left_hand",
                            "right_leg","left_leg" }
        local target_loc = nil

        if location_hint then
            local resolved = WoundSystem.resolve_location(location_hint)
            if resolved then
                local e = wounds[resolved]
                if e and (e.wound_rank or 0) >= 3 then
                    -- Check herb covers this group
                    if Herbs.can_treat(herb_data, resolved, 3, "limb_regen") then
                        target_loc = resolved
                    end
                end
            end
        end

        if not target_loc then
            for _, loc in ipairs(limb_locs) do
                local e = wounds[loc]
                if e and (e.wound_rank or 0) >= 3 then
                    if Herbs.can_treat(herb_data, loc, 3, "limb_regen") then
                        target_loc = loc
                        break
                    end
                end
            end
        end

        if not target_loc then
            result.msg = "You have no severed limb that this herb can treat."
            return result
        end

        -- Regenerate: fully remove wound + scar, no scarring
        wounds[target_loc] = { wound_rank=0, scar_rank=0, is_bleeding=false, bandaged=false }
        local display = WoundSystem.LOCATION_DISPLAY[target_loc] or target_loc
        result.ok           = true
        result.msg          = (herb_data.eat_msg or "The herb knits your severed limb back together.") ..
                              "  Your " .. display .. " has been restored!"
        result.changed_locs = { target_loc }
        return result
    end

    -- ── Eye regeneration ────────────────────────────────────────────
    if heal_type == "eye_regen" then
        local eye_locs = { "right_eye", "left_eye" }
        local target_loc = nil

        if location_hint then
            local resolved = WoundSystem.resolve_location(location_hint)
            if resolved and (resolved == "right_eye" or resolved == "left_eye") then
                local e = wounds[resolved]
                if e and (e.wound_rank or 0) >= 3 then
                    target_loc = resolved
                end
            end
        end

        if not target_loc then
            for _, loc in ipairs(eye_locs) do
                local e = wounds[loc]
                if e and (e.wound_rank or 0) >= 3 then
                    target_loc = loc
                    break
                end
            end
        end

        if not target_loc then
            result.msg = "You have no blinded eye that this herb can restore."
            return result
        end

        wounds[target_loc] = { wound_rank=0, scar_rank=0, is_bleeding=false, bandaged=false }
        local display = WoundSystem.LOCATION_DISPLAY[target_loc] or target_loc
        result.ok           = true
        result.msg          = (herb_data.eat_msg or "Your vision returns.") ..
                              "  Your " .. display .. " has been restored!"
        result.changed_locs = { target_loc }
        return result
    end

    -- ── Wound / Scar heal ────────────────────────────────────────────
    -- For wound/scar herbs: find the WORST matching wound we can treat.
    -- GS4 herbs auto-target the worst eligible wound automatically.

    local max_rank = herb_data.max_rank or 3
    local best_loc, best_rank = nil, 0

    -- Prefer wounds over scars; within same type, prefer higher rank
    local best_is_wound = false
    local resolved_hint = nil
    if location_hint and location_hint ~= "" then
        resolved_hint = WoundSystem.resolve_location(location_hint)
    end
    local candidate_locs = resolved_hint and { resolved_hint } or WoundSystem.LOCATIONS

    -- Candidate iterator
    for _, loc in ipairs(candidate_locs) do
        local e = wounds[loc]
        if e and Herbs.can_treat(herb_data, loc, (e.wound_rank or 0), heal_type) then
            local wr = e.wound_rank or 0
            local sr = e.scar_rank  or 0

            if heal_type == "wound" then
                if wr > 0 and wr <= max_rank then
                    if not best_is_wound or wr > best_rank then
                        best_loc      = loc
                        best_rank     = wr
                        best_is_wound = true
                    end
                end
            elseif heal_type == "scar" then
                -- For scar herbs: only treat scars (no active wounds at that location)
                if wr == 0 and sr > 0 and sr <= max_rank then
                    if sr > best_rank then
                        best_loc  = loc
                        best_rank = sr
                    end
                end
            end
        end
    end

    if not best_loc then
        if heal_type == "wound" then
            if resolved_hint then
                result.msg = "You have no wound there that this herb can treat."
            else
                result.msg = "You have no wounds that this herb can treat."
            end
        else
            if resolved_hint then
                result.msg = "You have no scar there that this herb can treat."
            else
                result.msg = "You have no scars that this herb can treat."
            end
        end
        result.ok = false
        return result
    end

    -- Apply heal via WoundSystem
    local entry = wounds[best_loc]
    local updated_entry, heal_msg = WoundSystem.heal_wound(
        entry, best_loc, 1, "herb"
    )

    if updated_entry then
        wounds[best_loc] = updated_entry
        local scar_added = (updated_entry.scar_rank or 0) >
                           (entry.scar_rank or 0)
        result.ok           = true
        result.msg          = (herb_data.eat_msg or "") ..
                              (heal_msg and ("  " .. heal_msg) or "")
        result.changed_locs = { best_loc }
        result.scar_added   = scar_added
    else
        result.msg = heal_msg or "The herb has no effect."
    end

    return result
end

-- ── 2. TEND (stop bleeding only) ────────────────────────────────────
-- GS4: TEND stops bleeding. It does NOT reduce wound rank.
-- Bandages are assumed available (no item required per GS4 rules).
--
-- location_input: raw player string, e.g. "right arm", "chest", "r leg"

function Treatment.tend(wounds, location_input, first_aid_bonus)
    local result = {
        ok       = false,
        msg      = "",
        wounds   = wounds,
        location = nil,
    }

    if not location_input or location_input == "" then
        -- Show all bleeding wounds
        local bleeding = {}
        for _, loc in ipairs(WoundSystem.LOCATIONS) do
            local e = wounds[loc]
            if e and e.is_bleeding and not e.bandaged then
                table.insert(bleeding, WoundSystem.LOCATION_DISPLAY[loc] or loc)
            end
        end
        if #bleeding == 0 then
            result.msg = "You have no bleeding wounds to tend."
        else
            result.msg = "Tend which wound?  Bleeding: " .. table.concat(bleeding, ", ") ..
                         ".  Syntax: TEND MY <area>  or  TEND <player> <area>"
        end
        return result
    end

    -- Resolve location
    local loc = WoundSystem.resolve_location(location_input)
    if not loc then
        result.msg = "'" .. location_input .. "' is not a valid wound location.  " ..
                     "Try: head, chest, right arm, left leg, nervous system, etc."
        return result
    end

    result.location = loc
    local entry = wounds[loc]

    local success, msg, updated = WoundSystem.tend_wound(entry, loc, first_aid_bonus)
    result.ok  = success
    result.msg = msg
    if updated and success then
        wounds[loc] = updated
    end

    return result
end

-- ── 3. Empath heal (single location) ────────────────────────────────
-- Reduces wound rank by 1 with no scarring (empath clears wounds cleanly).

function Treatment.empath_heal(wounds, location_input)
    local result = {
        ok       = false,
        msg      = "",
        wounds   = wounds,
        location = nil,
    }

    local loc = WoundSystem.resolve_location(location_input or "")
    if not loc then
        result.msg = "That is not a valid wound location."
        return result
    end

    result.location = loc
    local entry = wounds[loc]

    if not entry or ((entry.wound_rank or 0) == 0 and (entry.scar_rank or 0) == 0) then
        result.msg = "There is no wound or scar there to heal."
        return result
    end

    local updated, msg = WoundSystem.heal_wound(entry, loc, 1, "empath")
    wounds[loc]  = updated
    result.ok    = true
    result.msg   = msg
    return result
end

-- ── 4. Empath heal all (CURE/full heal flow) ────────────────────────
-- Iterates all wounds once, reducing each by 1 rank (no scars).
-- Empaths heal wounds priority order: highest rank first.

function Treatment.empath_heal_all(wounds)
    local result = {
        ok           = true,
        msg          = "",
        wounds       = wounds,
        changed_locs = {},
    }

    -- Sort locations by wound rank descending
    local to_heal = {}
    for _, loc in ipairs(WoundSystem.LOCATIONS) do
        local e = wounds[loc]
        if e then
            local wr = e.wound_rank or 0
            local sr = e.scar_rank  or 0
            if wr > 0 or sr > 0 then
                table.insert(to_heal, { loc=loc, rank=math.max(wr, sr) })
            end
        end
    end
    table.sort(to_heal, function(a, b) return a.rank > b.rank end)

    if #to_heal == 0 then
        result.msg = "This character has no wounds or scars to heal."
        result.ok  = false
        return result
    end

    local msgs = {}
    for _, item in ipairs(to_heal) do
        local entry   = wounds[item.loc]
        local updated, msg = WoundSystem.heal_wound(entry, item.loc, 1, "empath")
        wounds[item.loc] = updated
        table.insert(result.changed_locs, item.loc)
        if msg then table.insert(msgs, msg) end
    end

    result.msg = table.concat(msgs, "  ")
    return result
end

-- ── 5. TRANSFER (empath takes wounds) ───────────────────────────────
-- Copies wounds from target to empath, clears target wounds.
-- Returns { empath_wounds, target_wounds, msg }

function Treatment.transfer(empath_wounds, target_wounds, target_name)
    local transferred = {}

    for loc, entry in pairs(target_wounds) do
        local wr = entry.wound_rank or 0
        local sr = entry.scar_rank  or 0

        if wr > 0 or sr > 0 then
            -- Add to empath (stack up, cap at 3)
            local existing = empath_wounds[loc] or
                             { wound_rank=0, scar_rank=0, is_bleeding=false, bandaged=false }
            existing.wound_rank  = math.min(3, (existing.wound_rank or 0) + wr)
            existing.scar_rank   = math.min(3, (existing.scar_rank  or 0) + sr)
            existing.is_bleeding = existing.is_bleeding or entry.is_bleeding
            existing.bandaged    = false
            empath_wounds[loc] = existing

            -- Clear from target (empath takes wounds clean, no scar left)
            target_wounds[loc] = { wound_rank=0, scar_rank=0, is_bleeding=false, bandaged=false }
            table.insert(transferred, WoundSystem.LOCATION_DISPLAY[loc] or loc)
        end
    end

    local msg
    if #transferred > 0 then
        msg = "You take the wounds from " .. (target_name or "the target") ..
              " onto yourself: " .. table.concat(transferred, ", ") .. "."
    else
        msg = (target_name or "The target") .. " has no wounds to transfer."
    end

    return {
        ok             = #transferred > 0,
        msg            = msg,
        empath_wounds  = empath_wounds,
        target_wounds  = target_wounds,
        changed_locs   = transferred,
    }
end

return Treatment
