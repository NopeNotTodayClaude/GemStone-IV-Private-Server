-- =============================================================================
-- scripts/weapon_techniques/techniques/brawling.lua
-- Handlers: Twin Hammerfists, Fury, Clash, Spin Kick
--
-- Each handler receives ctx = {player, target, tech, rank, is_creature, ...}
-- and returns a result table:
--   {ok, message, roundtime, stamina_spent, effects_applied, attack_results}
-- The Python bridge (weapon_api.py) reads result and applies effects.
-- =============================================================================

local SMR = require("globals/utils/smr")

local Brawling = {}

local function safe_int(v)  return tonumber(v) or 0  end
local function safe_str(v)  return tostring(v or "")  end

-- Format target name for messages (capitalize first letter)
local function fmt_target(name)
    name = safe_str(name)
    return name:sub(1,1):upper() .. name:sub(2)
end

-- Pronoun helpers (creature gender stored on entity)
local function pronoun_he(entity)
    local g = (entity.gender or ""):lower()
    if g == "female" then return "she"
    elseif g == "male" then return "he"
    else return "it" end
end
local function pronoun_him(entity)
    local g = (entity.gender or ""):lower()
    if g == "female" then return "her"
    elseif g == "male" then return "him"
    else return "it" end
end

-- Build SMR-ready entity snapshot from player session data
local function player_entity(player)
    local sr = player.skill_ranks or {}
    return {
        skill_ranks = {
            dodging          = safe_int(sr.dodging),
            combat_maneuvers = safe_int(sr.combat_maneuvers),
            perception       = safe_int(sr.perception),
            physical_fitness = safe_int(sr.physical_fitness),
            shield_use       = safe_int(sr.shield_use),
            brawling         = safe_int(sr.brawling),
        },
        stats = player.stats or {},
        race_id            = safe_int(player.race_id),
        level              = safe_int(player.level),
        stance             = player.stance or "neutral",
        smr_off_bonus      = safe_int(player.smr_off_bonus),
        smr_def_bonus      = safe_int(player.smr_def_bonus),
        encumbrance_penalty   = safe_int(player.encumbrance_penalty),
        armor_action_penalty  = safe_int(player.armor_action_penalty),
    }
end

local function creature_entity(creature)
    return {
        skill_ranks = creature.skill_ranks or {},
        stats       = creature.stats or {},
        race_id     = 0,
        level       = safe_int(creature.level),
        stance      = creature.stance or "neutral",
        smr_off_bonus = 0,
        smr_def_bonus = 0,
        encumbrance_penalty  = 0,
        armor_action_penalty = 0,
    }
end

-- ---------------------------------------------------------------------------
-- TWIN HAMMERFISTS  [twinhammer]  Setup | Brawling | Rank at 10/35/60/85/110
-- SMRv2 maneuver. Applies Vulnerable+(rank*5)s, Staggered=(margin/10)s.
-- Stun on margin > 50.
-- ---------------------------------------------------------------------------
function Brawling.twinhammer(ctx)
    local tech   = ctx.tech
    local rank   = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    -- Maneuver knowledge rank for both sides
    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).brawling),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = true,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    -- Stamina drain
    local stamina_cost = safe_int(tech.stamina_cost)

    if not roll.success then
        local target_name = safe_str(target and target.name or ctx.target_name)
        return {
            ok              = true,
            success         = false,
            stamina_spent   = stamina_cost,
            roundtime       = tech.base_rt or 2,
            smr_result      = roll,
            effects_applied = {},
            attack_results  = {},
            message         = string.format(
                "%s\n%s",
                roll.msg,
                tech.msg_fail:gsub("{Target}", fmt_target(target_name))
            ),
        }
    end

    -- Duration calculations (wiki-exact)
    local vulnerable_dur = 15 + (rank * 5)
    local stagger_dur    = math.max(0, math.floor(roll.margin / 10))
    local do_stun        = roll.margin >= (tech.stun_threshold or 50)
    local stun_dur       = do_stun and math.max(1, math.floor(roll.margin / 30)) or 0

    local target_name  = safe_str(target and target.name or ctx.target_name)
    local msg_template = do_stun and tech.msg_success_stun or tech.msg_success
    local hit_msg = msg_template
        :gsub("{target}", target_name)
        :gsub("{Target}", fmt_target(target_name))
        :gsub("{He}", pronoun_he(target):sub(1,1):upper()..pronoun_he(target):sub(2))
        :gsub("{he}", pronoun_he(target))
        :gsub("{It}", pronoun_he(target):sub(1,1):upper()..pronoun_he(target):sub(2))

    local effects = {
        {effect="vulnerable",  duration=vulnerable_dur, target="defender"},
        {effect="staggered",   duration=stagger_dur,    target="defender"},
    }
    if do_stun then
        table.insert(effects, {effect="stunned", duration=stun_dur, target="defender"})
    end

    return {
        ok              = true,
        success         = true,
        stamina_spent   = stamina_cost,
        roundtime       = tech.base_rt or 2,
        smr_result      = roll,
        effects_applied = effects,
        attack_results  = {{damage_type="crush", minor=true}},
        message         = string.format(
            "%s\n%s\n%s",
            tech.msg_attempt:gsub("{target}", target_name),
            roll.msg,
            hit_msg
        ),
    }
end

-- ---------------------------------------------------------------------------
-- FURY  [fury]  Assault | Brawling | Rank at 25/50/75/100/125
-- Multi-round brawling assault. Each round: parry mod (margin/5)% max 10%.
-- On success: Frenzy buff 120s.
-- ---------------------------------------------------------------------------
function Brawling.fury(ctx)
    local tech   = ctx.tech
    local rank   = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target

    local attacker     = player_entity(player)
    local defender     = creature_entity(target)
    local target_name  = safe_str(target and target.name or ctx.target_name)

    local moc_ranks  = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local num_rounds = SMR.moc_hits(moc_ranks)  -- assaults use MOC for hit count

    local all_results  = {}
    local any_success  = false
    local total_damage = 0

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).brawling),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = false,
    }

    local parry_mod_total = 0

    local round_msgs = {
        tech.msg_attempt:gsub("{target}", target_name)
    }

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        if roll.success then
            any_success = true
            -- Parry mod for THIS round: (margin/5)% capped at 10
            local parry_mod = math.min(tech.parry_mod_cap or 10,
                              math.floor(roll.margin / (tech.parry_mod_divisor or 5)))
            parry_mod_total = parry_mod_total + parry_mod
            table.insert(all_results, {
                round   = i,
                success = true,
                roll    = roll,
                damage  = {type="crush", minor=false},
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                tech.msg_hit:gsub("{target}", target_name)))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]", roll.msg))
        end
    end

    table.insert(round_msgs, (tech.msg_final:gsub("{target}", target_name)))

    local effects = {}
    if any_success then
        table.insert(effects, {effect="frenzy", duration=120, target="self"})
        if parry_mod_total > 0 then
            table.insert(effects, {effect="parry_bonus", magnitude=parry_mod_total, target="self", duration=30})
        end
    end

    return {
        ok              = true,
        success         = any_success,
        stamina_spent   = safe_int(tech.stamina_cost),
        roundtime       = tech.base_rt or 2,
        is_assault      = true,
        round_results   = all_results,
        effects_applied = effects,
        message         = table.concat(round_msgs, "\n"),
    }
end

-- ---------------------------------------------------------------------------
-- CLASH  [clash]  AoE | Brawling | Rank at 50/75/100/125/150
-- AoE brawl. Attacks (1+MOC_bonus) targets. Grants Evasiveness (5+rank)s.
-- ---------------------------------------------------------------------------
function Brawling.clash(ctx)
    local tech   = ctx.tech
    local rank   = safe_int(ctx.rank)
    local player = ctx.player
    local targets = ctx.targets or {}  -- Python fills this from room target list

    local attacker = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).brawling),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = true,
    }

    local round_msgs  = {tech.msg_attempt}
    local all_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender   = creature_entity(target)
        local roll       = SMR.roll(attacker, defender, smr_opts)
        local target_name = safe_str(target.name)
        if roll.success then
            any_success = true
            table.insert(all_results, {target=target_name, success=true, roll=roll,
                damage={type="crush", minor=false}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                tech.msg_hit:gsub("{target}", target_name)))
        else
            table.insert(all_results, {target=target_name, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  You miss %s!", roll.msg, target_name))
        end
    end

    -- Evasiveness = 5 + rank  (on the attacker)
    local evasiveness_dur = (tech.evasiveness_base or 5) + rank * (tech.evasiveness_per_rank or 1)
    local effects = {{effect="evasiveness", duration=evasiveness_dur, target="self"}}

    return {
        ok              = true,
        success         = any_success,
        stamina_spent   = safe_int(tech.stamina_cost),
        roundtime       = tech.base_rt or 3,
        is_aoe          = true,
        aoe_results     = all_results,
        effects_applied = effects,
        message         = table.concat(round_msgs, "\n"),
    }
end

-- ---------------------------------------------------------------------------
-- SPIN KICK  [spinkick]  Reaction | Brawling | Rank at 75/100/125/150/175
-- Trigger: recent_evade. Free, no stamina, RT=ATTACK-2.
-- +10 CER. Staggered = margin/8.
-- ---------------------------------------------------------------------------
function Brawling.spinkick(ctx)
    local tech   = ctx.tech
    local rank   = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target

    local attacker = player_entity(player)
    local defender = creature_entity(target)
    local target_name = safe_str(target and target.name or ctx.target_name)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).brawling),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
        off_bonus          = safe_int(tech.cer_bonus),  -- +10 CER
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    if not roll.success then
        return {
            ok              = true,
            success         = false,
            stamina_spent   = 0,
            roundtime       = 0,
            rt_from_attack  = true,
            rt_mod          = -2,
            smr_result      = roll,
            effects_applied = {},
            message         = string.format("%s\n%s", roll.msg,
                (tech.msg_fail or "Your spin kick finds only air!")
                    :gsub("{target}", target_name)),
        }
    end

    -- Staggered = margin / 8
    local stagger_dur = math.max(1, math.floor(roll.margin / (tech.stagger_divisor or 8)))

    local effects = {
        {effect="staggered", duration=stagger_dur, target="defender"},
    }

    return {
        ok              = true,
        success         = true,
        stamina_spent   = 0,
        roundtime       = 0,
        rt_from_attack  = true,
        rt_mod          = -2,
        smr_result      = roll,
        effects_applied = effects,
        attack_results  = {{damage_type="crush", minor=false}},
        message         = string.format("%s\n%s\n%s",
            tech.msg_attempt:gsub("{target}", target_name),
            roll.msg,
            tech.msg_hit:gsub("{target}", target_name)),
    }
end

return Brawling
