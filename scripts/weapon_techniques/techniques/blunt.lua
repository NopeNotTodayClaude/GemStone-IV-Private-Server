-- =============================================================================
-- scripts/weapon_techniques/techniques/blunt.lua
-- Handlers: Dizzying Swing, Clobber, Pummel, Pulverize
-- =============================================================================

local SMR = require("globals/utils/smr")
local Blunt = {}

local function safe_int(v) return tonumber(v) or 0 end
local function safe_str(v) return tostring(v or "") end
local function fmt(name)
    name = safe_str(name)
    return name:sub(1,1):upper() .. name:sub(2)
end

local function player_entity(p)
    local sr = p.skill_ranks or {}
    return {
        skill_ranks = {
            dodging=safe_int(sr.dodging), combat_maneuvers=safe_int(sr.combat_maneuvers),
            perception=safe_int(sr.perception), physical_fitness=safe_int(sr.physical_fitness),
            shield_use=safe_int(sr.shield_use), blunt_weapons=safe_int(sr.blunt_weapons),
        },
        stats=p.stats or {}, race_id=safe_int(p.race_id), level=safe_int(p.level),
        stance=p.stance or "neutral", smr_off_bonus=safe_int(p.smr_off_bonus),
        smr_def_bonus=safe_int(p.smr_def_bonus),
        encumbrance_penalty=safe_int(p.encumbrance_penalty),
        armor_action_penalty=safe_int(p.armor_action_penalty),
    }
end
local function creature_entity(c)
    return {skill_ranks=c.skill_ranks or {}, stats=c.stats or {},
            race_id=0, level=safe_int(c.level), stance=c.stance or "neutral",
            smr_off_bonus=0, smr_def_bonus=0, encumbrance_penalty=0, armor_action_penalty=0}
end

-- ---------------------------------------------------------------------------
-- DIZZYING SWING  Setup | Blunt | 10/35/60/85/110
-- SMRv2. Crush damage. Dazed=(15+rank*5)s. Staggered=(margin/10)s on success.
-- ---------------------------------------------------------------------------
function Blunt.dizzyingswing(ctx)
    local tech = ctx.tech
    local rank = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).blunt_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = true,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)
    local cost = safe_int(tech.stamina_cost)

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=cost,
            roundtime=tech.base_rt or 2, smr_result=roll, effects_applied={},
            message=string.format("%s\n%s", roll.msg,
                (tech.msg_fail or fmt(target_name).." avoids your swing!"):gsub("{Target}", fmt(target_name))),
        }
    end

    local daze_dur    = (tech.daze_base or 15) + rank * (tech.daze_per_rank or 5)
    local stagger_dur = math.max(0, math.floor(roll.margin / (tech.stagger_divisor or 10)))

    local effects = {
        {effect="dazed",     duration=daze_dur,    target="defender"},
        {effect="staggered", duration=stagger_dur, target="defender"},
    }

    return {
        ok=true, success=true, stamina_spent=cost,
        roundtime=tech.base_rt or 2, smr_result=roll, effects_applied=effects,
        attack_results={{damage_type="crush", minor=false}},
        message=string.format("%s\n%s\n%s",
            (tech.msg_attempt or "You swing at "..target_name.."!"):gsub("{target}", target_name),
            roll.msg,
            (tech.msg_hit or "Your blow staggers "..target_name.."!"):gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- CLOBBER  Reaction | Blunt | 25/50/75/100/125
-- Trigger: recent_parry. Weakened Armament applied BEFORE resolution.
-- Duration=(15+rank*5)s. Removes recent EBP.
-- ---------------------------------------------------------------------------
function Blunt.clobber(ctx)
    local tech = ctx.tech
    local rank = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    -- Weakened Armament applied BEFORE roll (lowers defender effective armor)
    local wa_dur = (tech.weakened_armament_base or 15) + rank * (tech.weakened_armament_per_rank or 5)
    -- This manifests as a defense reduction in SMR — we model as off_bonus to attacker
    -- (Python bridge also applies the actual Weakened Armament status)
    local wa_off_bonus = 10 + rank * 3  -- approximate WArmament -> SMR value

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).blunt_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
        off_bonus          = wa_off_bonus,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    local effects = {
        {effect="weakened_armament", duration=wa_dur, target="defender", pre_attack=true},
    }
    if tech.removes_recent_ebp then
        table.insert(effects, {effect="remove_recent_ebp", target="self"})
    end

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=0,
            roundtime=0, rt_from_attack=true, rt_mod=-2,
            smr_result=roll, effects_applied=effects,
            message=string.format("Capitalizing on %s's parry, you bring your weapon crashing down!\n%s\n%s misses!",
                target_name, roll.msg, tech.name),
        }
    end

    return {
        ok=true, success=true, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2,
        smr_result=roll, effects_applied=effects,
        attack_results={{damage_type="crush", minor=false}},
        message=string.format("%s\n%s\n%s",
            (tech.msg_attempt or "You clobber "..target_name.."!"):gsub("{target}", target_name),
            roll.msg,
            (tech.msg_hit or "The concussive blow staggers "..target_name.."!"):gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- PUMMEL  Assault | Blunt | 50/75/100/125/150
-- MOC-based multi-hit. Parry mod (margin/5)% max 10% per round.
-- On success: Forceful Blows 120s.
-- ---------------------------------------------------------------------------
function Blunt.pummel(ctx)
    local tech = ctx.tech
    local rank = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker  = player_entity(player)
    local defender  = creature_entity(target)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local num_rounds = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).blunt_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {(tech.msg_attempt or "You begin pummeling "..target_name.."!"):gsub("{target}", target_name)}
    local all_results = {}
    local any_success = false
    local total_parry_mod = 0

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        if roll.success then
            any_success = true
            local pm = math.min(tech.parry_mod_cap or 10,
                        math.floor(roll.margin / (tech.parry_mod_divisor or 5)))
            total_parry_mod = total_parry_mod + pm
            table.insert(all_results, {round=i, success=true, roll=roll, damage={type="crush"}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "You pummel "..target_name.."!"):gsub("{target}", target_name)))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]", roll.msg))
        end
    end

    table.insert(round_msgs, ((tech.msg_final or "Your pummel assault concludes!"):gsub("{target}", target_name)))

    local effects = {}
    if any_success then
        table.insert(effects, {effect="forceful_blows", duration=120, target="self"})
        if total_parry_mod > 0 then
            table.insert(effects, {effect="parry_bonus", magnitude=total_parry_mod, target="self", duration=30})
        end
    end

    return {
        ok=true, success=any_success, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 2, is_assault=true,
        round_results=all_results, effects_applied=effects,
        message=table.concat(round_msgs, "\n"),
    }
end

-- ---------------------------------------------------------------------------
-- PULVERIZE  AoE | Blunt | 75/100/125/150/175
-- AoE crush damage + Weakened Armament (15+rank*3)s on all targets.
-- ---------------------------------------------------------------------------
function Blunt.pulverize(ctx)
    local tech = ctx.tech
    local rank = safe_int(ctx.rank)
    local player = ctx.player
    local targets = ctx.targets or {}
    local target_name_single = safe_str(ctx.target_name)

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).blunt_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local wa_dur = (tech.weakened_armament_base or 15) + rank * (tech.weakened_armament_per_rank or 3)

    local round_msgs  = {tech.msg_attempt or "You swing in a wide pulverizing arc!"}
    local aoe_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender    = creature_entity(target)
        local roll        = SMR.roll(attacker, defender, smr_opts)
        local tname       = safe_str(target.name)
        if roll.success then
            any_success = true
            table.insert(aoe_results, {
                target=tname, success=true, roll=roll,
                damage={type="crush", minor=true},
                effects={{effect="weakened_armament", duration=wa_dur}},
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "Your blow weakens "..tname.."'s armor!"):gsub("{target}", tname)))
        else
            table.insert(aoe_results, {target=tname, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  You miss %s!", roll.msg, tname))
        end
    end

    return {
        ok=true, success=any_success, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 3, is_aoe=true,
        aoe_results=aoe_results, effects_applied={},
        message=table.concat(round_msgs, "\n"),
    }
end

return Blunt
