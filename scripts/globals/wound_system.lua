------------------------------------------------------------------------
-- wound_system.lua
-- GemStone IV Wound & Scar System
--
-- Canonical 14-location, 3-rank wound model matching live GS4.
-- Loaded once by LuaEngine; Python calls functions via wound_bridge.py.
--
-- Data model per character (stored in DB + session.wounds Python dict):
--   session.wounds = {
--     [location] = {
--       wound_rank  = 0-3,   -- 0 = no wound
--       scar_rank   = 0-3,   -- 0 = no scar
--       is_bleeding = bool,
--       bandaged    = bool,
--     }
--   }
--
-- Wound rank -> GS4 crit_rank mapping:
--   crit 1-2 : no wound assigned
--   crit 3-4 : wound rank 1 (minor)
--   crit 5-6 : wound rank 2 (moderate, bleeds)
--   crit 7+  : wound rank 3 (severe)
------------------------------------------------------------------------

local WoundSystem = {}

-- ── 1. Canonical locations ───────────────────────────────────────────

WoundSystem.LOCATIONS = {
    "head", "neck", "chest", "abdomen", "back",
    "right_eye", "left_eye",
    "right_arm", "left_arm",
    "right_hand", "left_hand",
    "right_leg", "left_leg",
    "nervous_system",
}

-- Set for fast membership tests
WoundSystem.LOCATION_SET = {}
for _, loc in ipairs(WoundSystem.LOCATIONS) do
    WoundSystem.LOCATION_SET[loc] = true
end

-- Display names (for messaging)
WoundSystem.LOCATION_DISPLAY = {
    head          = "head",
    neck          = "neck",
    chest         = "chest",
    abdomen       = "abdomen",
    back          = "back",
    right_eye     = "right eye",
    left_eye      = "left eye",
    right_arm     = "right arm",
    left_arm      = "left arm",
    right_hand    = "right hand",
    left_hand     = "left hand",
    right_leg     = "right leg",
    left_leg      = "left leg",
    nervous_system = "nervous system",
}

-- ── 2. Wound rank descriptions (per location, per rank) ──────────────
-- Format: WOUND_DESC[location][rank]

WoundSystem.WOUND_DESC = {
    head = {
        [1] = "minor bruises about the head",
        [2] = "minor lacerations about the head and a possible mild concussion",
        [3] = "severe head trauma and bleeding from the ears",
    },
    neck = {
        [1] = "minor bruises on your neck",
        [2] = "moderate bleeding from your neck",
        [3] = "snapped bones and serious bleeding from the neck",
    },
    chest = {
        [1] = "minor cuts and bruises on your chest",
        [2] = "fractured ribs and bleeding across your chest",
        [3] = "crushed ribs and severe internal bleeding in your chest",
    },
    abdomen = {
        [1] = "minor bruising across your abdomen",
        [2] = "lacerations and bleeding across your abdomen",
        [3] = "severe internal injuries and bleeding in your abdomen",
    },
    back = {
        [1] = "minor bruising along your back",
        [2] = "deep lacerations across your back",
        [3] = "severe spinal trauma and bleeding along your back",
    },
    right_eye = {
        [1] = "a bruised right eye",
        [2] = "a swollen, partially blinded right eye",
        [3] = "a completely blinded right eye",
    },
    left_eye = {
        [1] = "a bruised left eye",
        [2] = "a swollen, partially blinded left eye",
        [3] = "a completely blinded left eye",
    },
    right_arm = {
        [1] = "minor cuts and bruises on your right arm",
        [2] = "a fractured and bleeding right arm",
        [3] = "a completely severed right arm",
    },
    left_arm = {
        [1] = "minor cuts and bruises on your left arm",
        [2] = "a fractured and bleeding left arm",
        [3] = "a completely severed left arm",
    },
    right_hand = {
        [1] = "minor cuts on your right hand",
        [2] = "fractured bones and bleeding in your right hand",
        [3] = "a completely severed right hand",
    },
    left_hand = {
        [1] = "minor cuts on your left hand",
        [2] = "fractured bones and bleeding in your left hand",
        [3] = "a completely severed left hand",
    },
    right_leg = {
        [1] = "minor cuts and bruises on your right leg",
        [2] = "a fractured and bleeding right leg",
        [3] = "a completely severed right leg",
    },
    left_leg = {
        [1] = "minor cuts and bruises on your left leg",
        [2] = "a fractured and bleeding left leg",
        [3] = "a completely severed left leg",
    },
    nervous_system = {
        [1] = "a strange case of muscle twitching",
        [2] = "sporadic convulsions throughout your body",
        [3] = "uncontrollable convulsions wracking your entire body",
    },
}

-- Scar descriptions (per location, per rank)
WoundSystem.SCAR_DESC = {
    head = {
        [1] = "a small scar on your head",
        [2] = "a noticeable scar across your head",
        [3] = "old mutilation wounds about your head",
    },
    neck = {
        [1] = "a faint scar on your neck",
        [2] = "a deep scar across your neck",
        [3] = "severe scarring along your neck",
    },
    chest = {
        [1] = "a small scar on your chest",
        [2] = "a noticeable scar across your chest",
        [3] = "severe scarring across your chest",
    },
    abdomen = {
        [1] = "a small scar on your abdomen",
        [2] = "a noticeable scar across your abdomen",
        [3] = "severe scarring across your abdomen",
    },
    back = {
        [1] = "a small scar on your back",
        [2] = "a noticeable scar across your back",
        [3] = "severe scarring along your back",
    },
    right_eye = {
        [1] = "a small scar near your right eye",
        [2] = "a disfiguring scar near your right eye",
        [3] = "severe scarring around your right eye socket",
    },
    left_eye = {
        [1] = "a small scar near your left eye",
        [2] = "a disfiguring scar near your left eye",
        [3] = "severe scarring around your left eye socket",
    },
    right_arm = {
        [1] = "a small scar on your right arm",
        [2] = "a deep scar along your right arm",
        [3] = "severe scarring along your right arm",
    },
    left_arm = {
        [1] = "a small scar on your left arm",
        [2] = "a deep scar along your left arm",
        [3] = "severe scarring along your left arm",
    },
    right_hand = {
        [1] = "a small scar on your right hand",
        [2] = "a deep scar across your right hand",
        [3] = "severe scarring across your right hand",
    },
    left_hand = {
        [1] = "a small scar on your left hand",
        [2] = "a deep scar across your left hand",
        [3] = "severe scarring across your left hand",
    },
    right_leg = {
        [1] = "a small scar on your right leg",
        [2] = "a deep scar along your right leg",
        [3] = "severe scarring along your right leg",
    },
    left_leg = {
        [1] = "a small scar on your left leg",
        [2] = "a deep scar along your left leg",
        [3] = "severe scarring along your left leg",
    },
    nervous_system = {
        [1] = "residual muscle twitching from old nerve damage",
        [2] = "occasional tremors from old nerve damage",
        [3] = "chronic convulsive episodes from severe nerve scarring",
    },
}

-- ── 3. Crit rank -> wound rank mapping ──────────────────────────────

-- GS4: crits 1-2 no wound, 3-4 minor, 5-6 moderate, 7+ severe
WoundSystem.CRIT_TO_WOUND_RANK = {
    [1] = 0, [2] = 0,
    [3] = 1, [4] = 1,
    [5] = 2, [6] = 2,
    [7] = 3, [8] = 3, [9] = 3,
}

-- Does this crit rank cause bleeding?
-- GS4: rank 2 wounds bleed; that means crit 5+
WoundSystem.CRIT_CAUSES_BLEED = {
    [1] = false, [2] = false, [3] = false, [4] = false,
    [5] = true,  [6] = true,  [7] = true,  [8] = true, [9] = true,
}

-- ── 4. Ability penalty checks ────────────────────────────────────────
-- Returns true if the wound state BLOCKS the ability.
-- wounds_table = Python dict converted to Lua table:
--   { head = {wound_rank=N, scar_rank=N, ...}, ... }

-- Locations that block casting when rank >= 2
local CAST_BLOCK_LOCS = {
    head=true, neck=true, abdomen=true, back=true, nervous_system=true,
    right_eye=true, left_eye=true,
    right_hand=true, left_hand=true,   -- rank 3 only for hands/arms
    right_arm=true, left_arm=true,
}

-- Effective rank: wound takes priority, then scar
local function eff_rank(entry)
    if not entry then return 0 end
    local wr = entry.wound_rank or 0
    local sr = entry.scar_rank  or 0
    return (wr > sr) and wr or sr
end

function WoundSystem.blocks_cast(wounds_table)
    for loc, entry in pairs(wounds_table) do
        local r = eff_rank(entry)
        if r >= 2 and CAST_BLOCK_LOCS[loc] then
            -- Arms/hands only block at rank 3
            if (loc == "right_hand" or loc == "left_hand" or
                loc == "right_arm"  or loc == "left_arm") then
                if r >= 3 then return true, loc end
            else
                return true, loc
            end
        end
    end
    return false
end

function WoundSystem.blocks_search(wounds_table)
    -- Same locations as cast block
    return WoundSystem.blocks_cast(wounds_table)
end

function WoundSystem.blocks_sneak(wounds_table)
    for loc, entry in pairs(wounds_table) do
        local r = eff_rank(entry)
        if r >= 2 and (loc == "right_leg" or loc == "left_leg") then
            return true, loc
        end
    end
    return false
end

function WoundSystem.blocks_ranged(wounds_table)
    for loc, entry in pairs(wounds_table) do
        local r = eff_rank(entry)
        if r >= 2 then
            if loc == "right_arm" or loc == "left_arm" or
               loc == "right_hand" or loc == "left_hand" then
                return true, loc
            end
        end
    end
    return false
end

-- AS/DS penalty from active wounds + scars
-- GS4: rank 1 = -5, rank 2 = -15, rank 3 = -30 per wounded location
local WOUND_AS_DS_PENALTY = { [0]=0, [1]=5, [2]=15, [3]=30 }

function WoundSystem.as_penalty(wounds_table)
    local total = 0
    for _, entry in pairs(wounds_table) do
        local r = eff_rank(entry)
        total = total + (WOUND_AS_DS_PENALTY[r] or 0)
    end
    return total
end

function WoundSystem.ds_penalty(wounds_table)
    return WoundSystem.as_penalty(wounds_table)
end

-- ── 5. Apply wound from crit ─────────────────────────────────────────
-- wounds_table: current wounds (Lua table from Python dict)
-- location:     string, one of LOCATIONS
-- crit_rank:    int 1-9
-- Returns: new_wound_rank, did_bleed, message_to_player

function WoundSystem.apply_wound(wounds_table, location, crit_rank)
    local new_rank = WoundSystem.CRIT_TO_WOUND_RANK[crit_rank] or 0
    if new_rank == 0 then
        return 0, false, nil
    end

    local entry = wounds_table[location] or {
        wound_rank=0, scar_rank=0, is_bleeding=false, bandaged=false
    }

    -- Wounds stack up, never down from combat
    local old_rank = entry.wound_rank or 0
    local final_rank = (new_rank > old_rank) and new_rank or old_rank
    local did_bleed = WoundSystem.CRIT_CAUSES_BLEED[crit_rank] or false

    if did_bleed then
        entry.is_bleeding = true
        entry.bandaged    = false   -- fresh bleeding clears bandage
    end

    entry.wound_rank = final_rank

    -- Build message
    local display  = WoundSystem.LOCATION_DISPLAY[location] or location
    local desc     = (WoundSystem.WOUND_DESC[location] or {})[final_rank]
    local msg = nil
    if desc then
        msg = "You have " .. desc .. "."
    end

    return final_rank, did_bleed, msg, entry
end

-- ── 6. Heal wound (herb / empath) ────────────────────────────────────
-- method: "herb" | "empath" | "spell"
-- reduce_by: how many ranks to reduce (usually 1 or fully clear)
-- empath heal = no scar; herb heal = converts wound to scar
-- Returns: updated entry, message

function WoundSystem.heal_wound(entry, location, reduce_by, method)
    if not entry then return nil, "No wound at that location." end
    local wr = entry.wound_rank or 0
    local sr = entry.scar_rank  or 0

    if wr == 0 and sr == 0 then
        return entry, "There is no wound or scar there to heal."
    end

    local display = WoundSystem.LOCATION_DISPLAY[location] or location
    local msg

    if wr > 0 then
        -- Heal the wound
        local new_wr = math.max(0, wr - (reduce_by or 1))

        if method == "empath" then
            -- Empath heals cleanly: wound removed, NO scar added
            entry.wound_rank = new_wr
            entry.is_bleeding = (new_wr > 1)   -- rank 1 stops bleeding
            msg = "The empath heals your " .. display .. "."
        else
            -- Herb / non-empath: wound reduced, leaves scar one rank lower
            local scar_added = math.max(0, new_wr)
            entry.wound_rank  = new_wr
            entry.scar_rank   = math.max(sr, scar_added > 0 and scar_added or (wr > 0 and 1 or 0))
            if new_wr == 0 then
                entry.is_bleeding = false
                entry.bandaged    = false
            else
                entry.is_bleeding = (new_wr > 1)
            end
            local scar_desc = (WoundSystem.SCAR_DESC[location] or {})[entry.scar_rank]
            msg = "You feel the herb working on your " .. display .. "."
            if scar_desc then
                msg = msg .. "  It leaves behind " .. scar_desc .. "."
            end
        end
    else
        -- Only a scar remains
        local new_sr = math.max(0, sr - (reduce_by or 1))
        entry.scar_rank = new_sr
        if new_sr == 0 then
            msg = "Your scar on your " .. display .. " has been fully removed."
        else
            local scar_desc = (WoundSystem.SCAR_DESC[location] or {})[new_sr]
            msg = "Your scar on your " .. display .. " has faded."
            if scar_desc then msg = msg .. "  It is now " .. scar_desc .. "." end
        end
    end

    return entry, msg
end

-- ── 7. Stop bleed (TEND) ─────────────────────────────────────────────
-- TEND does NOT heal wounds. It only stops bleeding.
-- first_aid_bonus: int (ranks * 3)
-- Returns: success bool, message

function WoundSystem.tend_wound(entry, location, first_aid_bonus)
    if not entry then
        return false, "You have no wound there to tend."
    end
    if not entry.is_bleeding then
        if (entry.wound_rank or 0) > 0 then
            return false, "That wound is not bleeding."
        end
        return false, "You have no wound there."
    end
    if entry.bandaged then
        return false, "That wound is already bandaged."
    end

    -- Success chance: base 40% + FA bonus, capped 95%
    -- Rank 3 wounds are harder to tend (require more FA)
    local wr = entry.wound_rank or 0
    local difficulty = wr * 15    -- rank 3 = -45 to base
    local chance = math.min(95, math.max(5, 40 + (first_aid_bonus or 0) // 2 - difficulty))
    local roll = math.random(1, 100)

    local display = WoundSystem.LOCATION_DISPLAY[location] or location

    if roll <= chance then
        entry.is_bleeding = false
        entry.bandaged    = true
        local msg = "You carefully tend your " .. display ..
                    ".  The bleeding has been stopped."
        if wr >= 2 then
            msg = msg .. "  The wound still requires healing."
        end
        return true, msg, entry
    else
        return false,
            "You fumble with the bandages but fail to properly tend your " .. display .. ".",
            entry
    end
end

-- ── 8. Bleed tick damage ─────────────────────────────────────────────
-- Called each game tick; returns total HP lost from all bleeding wounds.
-- Rank 2 wound: 1-2 HP/tick; rank 3: 2-4 HP/tick

local BLEED_DAMAGE = { [1]=0, [2]=2, [3]=4 }

function WoundSystem.bleed_tick(wounds_table)
    local total_dmg = 0
    local bleeding_locs = {}

    for loc, entry in pairs(wounds_table) do
        if entry.is_bleeding and not entry.bandaged then
            local wr = entry.wound_rank or 0
            local base = BLEED_DAMAGE[wr] or 0
            if base > 0 then
                -- Slight randomness: 1 to base
                local dmg = math.random(1, base)
                total_dmg = total_dmg + dmg
                table.insert(bleeding_locs, WoundSystem.LOCATION_DISPLAY[loc] or loc)
            end
        end
    end

    return total_dmg, bleeding_locs
end

-- ── 9. Build HEALTH display string ───────────────────────────────────
-- Returns a list of lines for the HEALTH command wound section.

function WoundSystem.health_display(wounds_table)
    local lines = {}

    -- Collect active wounds
    local has_wounds = false
    for _, loc in ipairs(WoundSystem.LOCATIONS) do
        local entry = wounds_table[loc]
        if entry then
            local wr = entry.wound_rank or 0
            local sr = entry.scar_rank  or 0
            if wr > 0 then
                has_wounds = true
                local desc   = (WoundSystem.WOUND_DESC[loc] or {})[wr] or "wounded"
                local bleed  = (entry.is_bleeding and not entry.bandaged) and "  [BLEEDING]" or
                               (entry.bandaged and "  [bandaged]" or "")
                local scar_note = (sr > 0) and ("  [scar rank " .. sr .. "]") or ""
                table.insert(lines, {
                    type     = "wound",
                    location = WoundSystem.LOCATION_DISPLAY[loc] or loc,
                    rank     = wr,
                    desc     = desc,
                    suffix   = bleed .. scar_note,
                })
            elseif sr > 0 then
                has_wounds = true
                local desc = (WoundSystem.SCAR_DESC[loc] or {})[sr] or "scarred"
                table.insert(lines, {
                    type     = "scar",
                    location = WoundSystem.LOCATION_DISPLAY[loc] or loc,
                    rank     = sr,
                    desc     = desc,
                    suffix   = "",
                })
            end
        end
    end

    if not has_wounds then
        table.insert(lines, { type="none", desc="None" })
    end

    return lines
end

-- ── 10. Utility ──────────────────────────────────────────────────────

-- Resolve player input to canonical location name
-- e.g. "right arm" -> "right_arm", "head" -> "head"
local INPUT_ALIASES = {
    ["r arm"]       = "right_arm",
    ["l arm"]       = "left_arm",
    ["r leg"]       = "right_leg",
    ["l leg"]       = "left_leg",
    ["r hand"]      = "right_hand",
    ["l hand"]      = "left_hand",
    ["r eye"]       = "right_eye",
    ["l eye"]       = "left_eye",
    ["right arm"]   = "right_arm",
    ["left arm"]    = "left_arm",
    ["right leg"]   = "right_leg",
    ["left leg"]    = "left_leg",
    ["right hand"]  = "right_hand",
    ["left hand"]   = "left_hand",
    ["right eye"]   = "right_eye",
    ["left eye"]    = "left_eye",
    ["nerves"]      = "nervous_system",
    ["nerve"]       = "nervous_system",
    ["nervous"]     = "nervous_system",
    ["spine"]       = "nervous_system",
    ["stomach"]     = "abdomen",
    ["belly"]       = "abdomen",
    ["torso"]       = "chest",
    ["arm"]         = "right_arm",   -- default to right
    ["leg"]         = "right_leg",
    ["hand"]        = "right_hand",
    ["eye"]         = "right_eye",
}

function WoundSystem.resolve_location(input)
    local s = input:lower():gsub("%s+", " "):match("^%s*(.-)%s*$")
    -- Direct match
    if WoundSystem.LOCATION_SET[s] then return s end
    -- Alias match
    if INPUT_ALIASES[s] then return INPUT_ALIASES[s] end
    -- Underscore variant
    local underscored = s:gsub(" ", "_")
    if WoundSystem.LOCATION_SET[underscored] then return underscored end
    return nil
end

-- Check if character has any active wounds or scars
function WoundSystem.has_any(wounds_table)
    for _, entry in pairs(wounds_table) do
        if (entry.wound_rank or 0) > 0 or (entry.scar_rank or 0) > 0 then
            return true
        end
    end
    return false
end

-- Check if character is bleeding from any location
function WoundSystem.is_bleeding(wounds_table)
    for _, entry in pairs(wounds_table) do
        if entry.is_bleeding and not entry.bandaged then
            return true
        end
    end
    return false
end

return WoundSystem
