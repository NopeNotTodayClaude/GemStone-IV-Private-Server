-- =============================================================================
-- scripts/weapon_techniques/engine.lua
-- Core dispatcher: WEAPON verb routing, validation, technique invocation.
-- Called from Python via lua_engine.call_hook(engine_table, "onWeaponVerb", ...)
--
-- Python calls:
--   engine.onWeaponVerb(player, args_table)    -> result table
--   engine.onAutoGrant(player, skill_name, new_ranks) -> list of granted names
--   engine.onCreatureTechnique(creature, target, mnemonic) -> result table
-- =============================================================================

local DEFS   = require("weapon_techniques/definitions")
local SMR    = require("globals/utils/smr")

local BRAWL  = require("weapon_techniques/techniques/brawling")
local BLUNT  = require("weapon_techniques/techniques/blunt")
local EDGED  = require("weapon_techniques/techniques/edged")
local POLE   = require("weapon_techniques/techniques/polearm")
local RANGED = require("weapon_techniques/techniques/ranged")
local TWOHD  = require("weapon_techniques/techniques/twohanded")

local Engine = {}

-- ---------------------------------------------------------------------------
-- Technique dispatch table  mnemonic -> handler function
-- ---------------------------------------------------------------------------
local HANDLERS = {
    -- Brawling
    twinhammer   = BRAWL.twinhammer,
    fury         = BRAWL.fury,
    clash        = BRAWL.clash,
    spinkick     = BRAWL.spinkick,
    -- Blunt
    dizzyingswing = BLUNT.dizzyingswing,
    clobber       = BLUNT.clobber,
    pummel        = BLUNT.pummel,
    pulverize     = BLUNT.pulverize,
    -- Edged
    cripple       = EDGED.cripple,
    riposte       = EDGED.riposte,
    flurry        = EDGED.flurry,
    wblade        = EDGED.wblade,
    -- Polearm
    charge        = POLE.charge,
    gthrusts      = POLE.gthrusts,
    cyclone       = POLE.cyclone,
    radialsweep   = POLE.radialsweep,
    -- Ranged
    reactiveshot  = RANGED.reactiveshot,
    pindown       = RANGED.pindown,
    barrage       = RANGED.barrage,
    volley        = RANGED.volley,
    -- Two-Handed
    overpower     = TWOHD.overpower,
    thrash        = TWOHD.thrash,
    reversestrike = TWOHD.reversestrike,
    whirlwind     = TWOHD.whirlwind,
}

-- Category -> weapon skill name map (matches skill_ranks keys on player)
local CAT_TO_SKILL = {
    brawling  = "brawling",
    blunt     = "blunt_weapons",
    edged     = "edged_weapons",
    polearm   = "polearm_weapons",
    ranged    = "ranged_weapons",
    twohanded = "two_handed_weapons",
}

-- ---------------------------------------------------------------------------
-- Internal helpers
-- ---------------------------------------------------------------------------

local function safe_int(v)
    return tonumber(v) or 0
end

local function player_stamina(player)
    local get_stat = player and player.getStat
    if player and player.stamina ~= nil then
        return safe_int(player.stamina)
    end
    if type(get_stat) == "function" then
        return safe_int(get_stat(player, "stamina"))
    end
    return 0
end

local function player_skill_ranks(player, skill_name)
    local sr = player.skill_ranks or {}
    return safe_int(sr[skill_name] or sr[skill_name:gsub("_weapons",""):gsub("_"," ")] or 0)
end

local function player_technique_rank(player, mnemonic)
    -- Python bridge stores learned techniques on player.weapon_techniques dict
    local wt = player.weapon_techniques or {}
    return safe_int(wt[mnemonic] or 0)
end

-- Compute current rank from weapon ranks (for auto-grant / rank updates)
local function compute_rank(weapon_ranks, tech)
    return SMR.technique_rank(weapon_ranks, {
        min_skill_ranks = tech.rank_thresholds and tech.rank_thresholds[1] or tech.min_ranks or 10,
        rank2_ranks     = tech.rank_thresholds and tech.rank_thresholds[2] or 35,
        rank3_ranks     = tech.rank_thresholds and tech.rank_thresholds[3] or 60,
        rank4_ranks     = tech.rank_thresholds and tech.rank_thresholds[4] or 85,
        rank5_ranks     = tech.rank_thresholds and tech.rank_thresholds[5] or 110,
    })
end

-- Check reaction trigger availability
local function has_trigger(player, trigger_name)
    if not trigger_name then return true end  -- non-reaction types
    local triggers = player.reaction_triggers or {}
    if trigger_name == "recent_evade_block_parry" then
        return (triggers.recent_evade or triggers.recent_block or triggers.recent_parry)
    end
    return triggers[trigger_name] == true
end

-- Consume a reaction trigger (called after use, success or failure)
local function consume_trigger(player, trigger_name)
    if not trigger_name then return end
    local triggers = player.reaction_triggers or {}
    if trigger_name == "recent_evade_block_parry" then
        triggers.recent_evade  = nil
        triggers.recent_block  = nil
        triggers.recent_parry  = nil
    else
        triggers[trigger_name] = nil
    end
    player.reaction_triggers = triggers
end

-- ---------------------------------------------------------------------------
-- WEAPON LIST  ->  returns formatted list string for the player
-- ---------------------------------------------------------------------------
local TYPE_ORDER = {"setup","assault","reaction","aoe","concentration"}

local function build_list(player, filter_cat, filter_type)
    local lines = {}
    local wt    = player.weapon_techniques or {}

    -- Header
    if filter_cat then
        table.insert(lines, string.format("Weapon Techniques - %s:", filter_cat:upper()))
    elseif filter_type then
        table.insert(lines, string.format("Weapon Techniques - %s type:", filter_type:upper()))
    else
        table.insert(lines, "Weapon Techniques:")
    end

    local shown = 0
    local cats = filter_cat and {filter_cat} or {"brawling","blunt","edged","polearm","ranged","twohanded"}

    for _, cat in ipairs(cats) do
        local mnemonics = DEFS._by_category[cat] or {}
        if filter_type then
            local filtered = {}
            for _, m in ipairs(mnemonics) do
                if DEFS[m] and DEFS[m].type == filter_type then
                    table.insert(filtered, m)
                end
            end
            mnemonics = filtered
        end
        if #mnemonics > 0 then
            local label = cat:gsub("^%l", string.upper):gsub("_", " ")
            table.insert(lines, "  " .. label .. ":")
            for _, mnemonic in ipairs(mnemonics) do
                local tech  = DEFS[mnemonic]
                local rank  = safe_int(wt[mnemonic] or 0)
                local skill = CAT_TO_SKILL[cat] or cat
                local wpn_r = player_skill_ranks(player, skill)
                local max_rank = compute_rank(wpn_r, tech)

                local status
                if rank == 0 then
                    local needed = tech.rank_thresholds and tech.rank_thresholds[1] or 10
                    if wpn_r >= needed then
                        status = "Available (not yet granted)"
                    else
                        status = string.format("Requires %d %s ranks", needed, skill:gsub("_"," "))
                    end
                else
                    status = string.format("Rank %d/%d", rank, math.max(rank, max_rank))
                end

                table.insert(lines, string.format(
                    "    [%s] %-20s (%s) - %s",
                    mnemonic, tech.name, tech.type, status
                ))
                shown = shown + 1
            end
        end
    end

    if shown == 0 then
        table.insert(lines, "  No techniques found for that filter.")
    end
    table.insert(lines, "Use WEAPON HELP <mnemonic> for details.")
    return table.concat(lines, "\n")
end

-- ---------------------------------------------------------------------------
-- WEAPON HELP <mnemonic>
-- ---------------------------------------------------------------------------
local function build_help(mnemonic)
    local tech = DEFS[mnemonic]
    if not tech then
        return string.format("Unknown technique '%s'. Use WEAPON LIST to see available techniques.", mnemonic)
    end
    local lines = {}
    table.insert(lines, string.format("=== %s [%s] ===", tech.name, mnemonic))
    table.insert(lines, string.format("Category : %s", tech.category:gsub("^%l",string.upper)))
    table.insert(lines, string.format("Type     : %s", tech.type:gsub("^%l",string.upper)))
    table.insert(lines, string.format("Skill    : %s", (CAT_TO_SKILL[tech.category] or tech.category):gsub("_"," ")))
    if tech.stamina_cost and tech.stamina_cost > 0 then
        table.insert(lines, string.format("Stamina  : %d", tech.stamina_cost))
    else
        table.insert(lines, "Stamina  : None (Reaction)")
    end
    if tech.cooldown and tech.cooldown > 0 then
        table.insert(lines, string.format("Cooldown : %ds", tech.cooldown))
    end
    if tech.reaction_trigger then
        local trigger_nice = tech.reaction_trigger:gsub("_"," "):gsub("^%l",string.upper)
        table.insert(lines, string.format("Trigger  : Requires %s", trigger_nice))
    end

    local ranks_str = {}
    local thresholds = tech.rank_thresholds or {tech.min_ranks,35,60,85,110}
    for i, v in ipairs(thresholds) do
        table.insert(ranks_str, string.format("Rank %d: %d ranks", i, v))
    end
    table.insert(lines, "Ranks    : " .. table.concat(ranks_str, " | "))
    table.insert(lines, "Available: " .. table.concat(tech.available_to or {}, ", "))
    table.insert(lines, "")
    table.insert(lines, tech.description or "")
    table.insert(lines, "")
    if tech.mechanics_notes then
        table.insert(lines, "Mechanics: " .. tech.mechanics_notes)
    end
    return table.concat(lines, "\n")
end

-- ---------------------------------------------------------------------------
-- MAIN: onWeaponVerb(player, args_table)
-- args_table.subcmd = "list"|"help"|"info"|<mnemonic>
-- args_table.arg    = secondary argument (target, limb, filter word)
-- ---------------------------------------------------------------------------
function Engine.onWeaponVerb(player, args)
    args = args or {}
    local subcmd = (args.subcmd or ""):lower()
    local arg    = (args.arg    or ""):lower()
    local target_name = args.target

    -- WEAPON LIST [category|type]
    if subcmd == "list" then
        local cat  = nil
        local typ  = nil
        if arg ~= "" then
            if DEFS._by_category[arg] then cat = arg
            elseif arg == "setup" or arg == "assault" or arg == "reaction"
                or arg == "aoe" or arg == "concentration" then typ = arg
            end
        end
        return {ok=true, message=build_list(player, cat, typ)}
    end

    -- WEAPON HELP <mnemonic>
    if subcmd == "help" or subcmd == "info" then
        if arg == "" then
            return {ok=false, message="Usage: WEAPON HELP <mnemonic>  e.g. WEAPON HELP cripple"}
        end
        return {ok=true, message=build_help(arg)}
    end

    -- WEAPON <mnemonic> [target] [limb]
    local mnemonic = subcmd
    if mnemonic == "" then
        return {ok=false, message="Usage: WEAPON <mnemonic> <target>  or  WEAPON LIST  or  WEAPON HELP <mnemonic>"}
    end

    local tech = DEFS[mnemonic]
    if not tech then
        return {ok=false, message=string.format("'%s' is not a valid weapon technique mnemonic. Use WEAPON LIST to see available techniques.", mnemonic)}
    end

    -- Check profession eligibility
    local prof = (player.profession_name or ""):lower()
    if not DEFS.can_use(mnemonic, prof) then
        return {ok=false, message=string.format("The %s technique is not available to your profession.", tech.name)}
    end

    -- Check if player has this technique
    local player_rank = player_technique_rank(player, mnemonic)
    if player_rank == 0 then
        local skill = CAT_TO_SKILL[tech.category] or tech.category
        local needed = tech.rank_thresholds and tech.rank_thresholds[1] or 10
        local have   = player_skill_ranks(player, skill)
        if have >= needed then
            return {ok=false, message=string.format("You have not yet been granted %s. (Your skills have been updated — this should auto-grant. Report a bug if this persists.)", tech.name)}
        end
        return {ok=false, message=string.format("%s requires %d ranks of %s. You have %d.", tech.name, needed, skill:gsub("_"," "), have)}
    end

    -- Check reaction trigger
    if tech.type == "reaction" then
        if not has_trigger(player, tech.reaction_trigger) then
            local trigger_nice = (tech.reaction_trigger or ""):gsub("_"," ")
            return {ok=false, message=string.format("%s requires a %s to activate.", tech.name, trigger_nice)}
        end
        -- Consume trigger before resolving (regardless of outcome)
        consume_trigger(player, tech.reaction_trigger)
    end

    -- Check cooldown
    local now = os.time()
    local cooldowns = player.technique_cooldowns or {}
    if tech.cooldown and tech.cooldown > 0 then
        local expires = cooldowns[mnemonic] or 0
        if now < expires then
            local remaining = expires - now
            return {ok=false, message=string.format("%s is on cooldown for %d more second%s.", tech.name, remaining, remaining == 1 and "" or "s")}
        end
    end

    -- Check stamina (non-reaction)
    if tech.type ~= "reaction" then
        local cost = safe_int(tech.stamina_cost)
        if cost > 0 then
            local stam = player_stamina(player)
            if stam < cost then
                return {ok=false, message=string.format("You need %d stamina to use %s but only have %d.", cost, tech.name, stam)}
            end
        end
    end

    -- Require a target for offensive techniques
    -- (AoE types may auto-target room; reaction may auto-target last attacker)
    if not target_name or target_name == "" then
        if tech.type == "aoe" then
            target_name = "__room__"  -- signal to Python bridge to gather room targets
        else
            return {ok=false, message=string.format("Use: WEAPON %s <target>", mnemonic)}
        end
    end

    -- Set cooldown
    if tech.cooldown and tech.cooldown > 0 then
        cooldowns[mnemonic] = now + tech.cooldown
        player.technique_cooldowns = cooldowns
    end

    -- Dispatch to technique handler
    local handler = HANDLERS[mnemonic]
    if not handler then
        return {ok=false, message=string.format("Technique '%s' has no handler implemented. Please report this bug.", mnemonic)}
    end

    local ctx = {
        player       = player,
        target_name  = target_name,
        mnemonic     = mnemonic,
        tech         = tech,
        rank         = player_rank,
        limb         = args.limb or "",
        extra_arg    = arg,
    }

    local ok, result = pcall(handler, ctx)
    if not ok then
        return {ok=false, message="Internal technique error: " .. tostring(result)}
    end

    return result
end

-- ---------------------------------------------------------------------------
-- onAutoGrant(player, skill_name, new_ranks)
-- Called by Python training system after weapon skill rank increase.
-- Returns list of {mnemonic, name, new_rank} for techniques newly granted or upgraded.
-- ---------------------------------------------------------------------------
function Engine.onAutoGrant(player, skill_name, new_ranks)
    new_ranks = safe_int(new_ranks)
    local granted = {}
    local wt = player.weapon_techniques or {}

    -- Find all techniques for this weapon skill
    local skill_to_cat = {
        brawling         = "brawling",
        blunt_weapons    = "blunt",
        edged_weapons    = "edged",
        polearm_weapons  = "polearm",
        ranged_weapons   = "ranged",
        two_handed_weapons = "twohanded",
    }

    local cat = skill_to_cat[skill_name]
    if not cat then return granted end

    local mnemonics = DEFS._by_category[cat] or {}
    for _, mnemonic in ipairs(mnemonics) do
        local tech = DEFS[mnemonic]
        if tech then
            local new_rank = compute_rank(new_ranks, tech)
            local cur_rank = safe_int(wt[mnemonic] or 0)

            if new_rank > cur_rank then
                table.insert(granted, {
                    mnemonic  = mnemonic,
                    name      = tech.name,
                    new_rank  = new_rank,
                    old_rank  = cur_rank,
                    is_new    = cur_rank == 0,
                })
            end
        end
    end

    return granted
end

-- ---------------------------------------------------------------------------
-- onCreatureTechnique(creature, target, mnemonic, creature_rank)
-- Called by the combat engine for creatures using weapon techniques.
-- ---------------------------------------------------------------------------
function Engine.onCreatureTechnique(creature, target, mnemonic, creature_rank)
    local tech = DEFS[mnemonic]
    if not tech then
        return {ok=false, message="Unknown technique: " .. tostring(mnemonic)}
    end

    creature_rank = safe_int(creature_rank) or 1

    local handler = HANDLERS[mnemonic]
    if not handler then
        return {ok=false, message="No handler for: " .. mnemonic}
    end

    -- Build a pseudo-player-like context from the creature
    local ctx = {
        player      = creature,   -- creature acts as attacker entity
        target_name = "__direct__",
        target      = target,
        mnemonic    = mnemonic,
        tech        = tech,
        rank        = creature_rank,
        is_creature = true,
        limb        = "",
    }

    local ok, result = pcall(handler, ctx)
    if not ok then
        return {ok=false, message="Creature technique error: " .. tostring(result)}
    end

    return result
end

return Engine
