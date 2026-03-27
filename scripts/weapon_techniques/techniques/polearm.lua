-- =============================================================================
-- scripts/weapon_techniques/techniques/polearm.lua
-- Handlers: Charge, Guardant Thrusts, Cyclone, Radial Sweep
-- =============================================================================

local SMR    = require("globals/utils/smr")
local Polearm = {}

local function safe_int(v) return tonumber(v) or 0 end
local function safe_str(v) return tostring(v or "") end
local function fmt(n) n=safe_str(n); return n:sub(1,1):upper()..n:sub(2) end

local function player_entity(p)
    local sr = p.skill_ranks or {}
    return {
        skill_ranks={
            dodging=safe_int(sr.dodging), combat_maneuvers=safe_int(sr.combat_maneuvers),
            perception=safe_int(sr.perception), physical_fitness=safe_int(sr.physical_fitness),
            shield_use=safe_int(sr.shield_use), polearm_weapons=safe_int(sr.polearm_weapons),
        },
        stats=p.stats or {}, race_id=safe_int(p.race_id), level=safe_int(p.level),
        stance=p.stance or "neutral", smr_off_bonus=safe_int(p.smr_off_bonus),
        smr_def_bonus=safe_int(p.smr_def_bonus),
        encumbrance_penalty=safe_int(p.encumbrance_penalty),
        armor_action_penalty=safe_int(p.armor_action_penalty),
    }
end
local function creature_entity(c)
    if not c then return {skill_ranks={},stats={},race_id=0,level=1,stance="neutral",
        smr_off_bonus=0,smr_def_bonus=0,encumbrance_penalty=0,armor_action_penalty=0} end
    return {skill_ranks=c.skill_ranks or {},stats=c.stats or {},race_id=0,
            level=safe_int(c.level),stance=c.stance or "neutral",
            smr_off_bonus=0,smr_def_bonus=0,encumbrance_penalty=0,armor_action_penalty=0}
end

-- ---------------------------------------------------------------------------
-- CHARGE  Setup | Polearm | 10/35/60/85/110
-- Wiki-exact:
--   Moderate weapon + unbalance damage
--   Can force target to higher stance
--   Vulnerable = (15+Rank*5)s
--   Staggered  = margin/6 s
-- ---------------------------------------------------------------------------
function Polearm.charge(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).polearm_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,  -- size matters for charge
        include_shield     = true,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)
    local cost = safe_int(tech.stamina_cost)

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=cost,
            roundtime=tech.base_rt or 4, smr_result=roll, effects_applied={},
            message=string.format("%s\n%s\n%s sidesteps your charge!",
                tech.msg_attempt:gsub("{target}", target_name), roll.msg, fmt(target_name)),
        }
    end

    local vulnerable_dur = (tech.vulnerable_base or 15) + rank * (tech.vulnerable_per_rank or 5)
    local stagger_dur    = math.max(0, math.floor(roll.margin / (tech.stagger_divisor or 6)))

    local effects = {
        {effect="vulnerable", duration=vulnerable_dur, target="defender"},
        {effect="staggered",  duration=stagger_dur,    target="defender"},
    }

    -- Force stance if high margin (wiki: can force target to higher stance)
    local force_stance = tech.can_force_stance and roll.margin >= 40

    local hit_msg = roll.margin >= 80
        and (tech.msg_success_major or fmt(target_name).." flips through the air!")
        or  (tech.msg_success_minor or fmt(target_name).." loses "..("their").." footing!")
    hit_msg = hit_msg:gsub("{Target}", fmt(target_name)):gsub("{target}", target_name)

    return {
        ok=true, success=true, stamina_spent=cost,
        roundtime=tech.base_rt or 4, smr_result=roll,
        effects_applied=effects,
        attack_results={{damage_type="weapon", moderate=true}, {damage_type="unbalance", moderate=true}},
        force_target_stance = force_stance,
        message=string.format("%s\n%s\n%s",
            tech.msg_attempt:gsub("{target}", target_name), roll.msg, hit_msg),
    }
end

-- ---------------------------------------------------------------------------
-- GUARDANT THRUSTS  Assault | Polearm | 25/50/75/100/125
-- Each round: attack once + +5 DS (stacks up to Rank times).
-- On completion: Fortified Stance 30s.
-- ---------------------------------------------------------------------------
function Polearm.gthrusts(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker  = player_entity(player)
    local defender  = creature_entity(target)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local num_rounds = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).polearm_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {(tech.msg_attempt or "You advance on "..target_name.." with measured thrusts!"):gsub("{target}", target_name)}
    local all_results = {}
    local any_success = false
    local ds_stack    = 0

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        -- Per round: +5 DS bonus to attacker (stacks up to Rank)
        if ds_stack < rank then
            ds_stack = ds_stack + (tech.ds_bonus_per_round or 5)
        end
        if roll.success then
            any_success = true
            table.insert(all_results, {round=i, success=true, roll=roll, damage={type="puncture"}})
            table.insert(round_msgs, string.format("%s  %s  [DS +%d]", roll.msg,
                (tech.msg_hit or "You drive your weapon into "..target_name.."!"):gsub("{target}", target_name),
                math.min(ds_stack, rank * (tech.ds_bonus_per_round or 5))))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]  [DS +%d]", roll.msg,
                math.min(ds_stack, rank * (tech.ds_bonus_per_round or 5))))
        end
    end

    table.insert(round_msgs, (tech.msg_final or "With a final thrust you settle into a guarded stance!"):gsub("{target}", target_name))

    local effects = {
        -- Fortified Stance on completion (whether success or not)
        {effect="fortified_stance", duration=tech.completion_buff_duration or 30, target="self"},
        -- Per-round DS bonus applied cumulatively
        {effect="ds_bonus", magnitude=math.min(ds_stack, rank * (tech.ds_bonus_per_round or 5)), target="self", duration=15},
    }

    return {
        ok=true, success=any_success, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 2, is_assault=true,
        round_results=all_results, effects_applied=effects,
        message=table.concat(round_msgs, "\n"),
    }
end

-- ---------------------------------------------------------------------------
-- CYCLONE  AoE | Polearm | 50/75/100/125/150
-- AoE unbalance damage. Staggered=(margin/8)s each. Forces stance on high margin.
-- ---------------------------------------------------------------------------
function Polearm.cyclone(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).polearm_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = false,
    }

    local round_msgs  = {tech.msg_attempt or "You spin your polearm in a wide cyclone arc!"}
    local aoe_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender = creature_entity(target)
        local roll     = SMR.roll(attacker, defender, smr_opts)
        local tname    = safe_str(target.name)
        if roll.success then
            any_success = true
            local stagger_dur    = math.max(0, math.floor(roll.margin / (tech.stagger_divisor or 8)))
            local force_stance   = roll.margin >= (tech.force_stance_threshold or 80)
            table.insert(aoe_results, {
                target=tname, success=true, roll=roll,
                damage={type="unbalance"},
                effects={{effect="staggered", duration=stagger_dur}},
                force_target_stance=force_stance,
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "Your sweeping polearm crashes into "..tname.."!"):gsub("{target}", tname)))
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

-- ---------------------------------------------------------------------------
-- RADIAL SWEEP  Reaction | Polearm | 75/100/125/150/175
-- Trigger: recent_evade. AoE vs all room enemies. Targets legs.
-- Rooted = (8+Rank*2)s on each hit.
-- ---------------------------------------------------------------------------
function Polearm.radialsweep(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).polearm_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = false,
    }

    local rooted_dur = (tech.rooted_base or 8) + rank * (tech.rooted_per_rank or 2)

    local round_msgs  = {tech.msg_attempt or "You spin low, sweeping your polearm at the legs of your foes!"}
    local aoe_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender = creature_entity(target)
        local roll     = SMR.roll(attacker, defender, smr_opts)
        local tname    = safe_str(target.name)
        if roll.success then
            any_success = true
            table.insert(aoe_results, {
                target=tname, success=true, roll=roll,
                damage={type="unbalance", minor=true},
                effects={{effect="rooted", duration=rooted_dur}},
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "Your sweeping polearm tangles "..tname.."'s legs!"):gsub("{target}", tname)))
        else
            table.insert(aoe_results, {target=tname, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  You miss %s!", roll.msg, tname))
        end
    end

    return {
        ok=true, success=any_success, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2, is_aoe=true,
        aoe_results=aoe_results, effects_applied={},
        message=table.concat(round_msgs, "\n"),
    }
end

return Polearm
