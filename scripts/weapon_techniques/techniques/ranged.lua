-- =============================================================================
-- scripts/weapon_techniques/techniques/ranged.lua
-- Handlers: Reactive Shot, Pin Down, Barrage, Volley
-- =============================================================================

local SMR    = require("globals/utils/smr")
local Ranged = {}

local function safe_int(v) return tonumber(v) or 0 end
local function safe_str(v) return tostring(v or "") end

local function player_entity(p)
    local sr = p.skill_ranks or {}
    return {
        skill_ranks={
            dodging=safe_int(sr.dodging), combat_maneuvers=safe_int(sr.combat_maneuvers),
            perception=safe_int(sr.perception), physical_fitness=safe_int(sr.physical_fitness),
            shield_use=0,  -- ranged: no shield in off-hand
            ranged_weapons=safe_int(sr.ranged_weapons),
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
-- REACTIVE SHOT  Reaction | Ranged | 10/35/60/85/110
-- Trigger: recent_evade. Quick shot + Evasiveness (3+rank)s. No engagement penalty 1 round.
-- ---------------------------------------------------------------------------
function Ranged.reactiveshot(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).ranged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    local evasive_dur = (tech.evasiveness_base or 3) + rank * (tech.evasiveness_per_rank or 1)

    -- Evasiveness granted regardless of hit
    local effects = {
        {effect="evasiveness",           duration=evasive_dur, target="self"},
        {effect="avoid_engagement_bonus", duration=5,          target="self"},
    }

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=0,
            roundtime=0, rt_from_attack=true, rt_mod=-2,
            smr_result=roll, effects_applied=effects,
            message=string.format("%s\n%s\nYour hasty shot misses wide!", roll.msg,
                (tech.msg_attempt or "You snap a quick shot at "..target_name.."!"):gsub("{target}", target_name)),
        }
    end

    return {
        ok=true, success=true, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2,
        smr_result=roll, effects_applied=effects,
        attack_results={{damage_type="puncture", minor=false}},
        message=string.format("%s\n%s\n%s",
            (tech.msg_attempt or "You snap a quick shot at "..target_name.." and step back!"):gsub("{target}", target_name),
            roll.msg,
            (tech.msg_hit or "Your arrow finds "..target_name.."!"):gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- PIN DOWN  AoE | Ranged | 25/50/75/100/125
-- Hits (1+MOC_bonus) targets. Pinned = (10+rank*3)s each.
-- ---------------------------------------------------------------------------
function Ranged.pindown(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).ranged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local pinned_dur = (tech.pinned_base or 10) + rank * (tech.pinned_per_rank or 3)

    local round_msgs  = {tech.msg_attempt or "You loose a rapid volley of arrows to pin down multiple foes!"}
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
                damage={type="puncture", minor=false},
                effects={{effect="pinned", duration=pinned_dur}},
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "An arrow pins "..tname.." in place!"):gsub("{target}", tname)))
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
-- BARRAGE  Assault | Ranged | 50/75/100/125/150
-- Wiki-exact:
--   (1+MOC_bonus) shots per assault
--   Evade modified (margin/10)% max 10% per round
--   On success: attacker + party gain Enhance Dexterity power 10 for 2 minutes
-- ---------------------------------------------------------------------------
function Ranged.barrage(ctx)
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
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).ranged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {(tech.msg_attempt or "You rapidly nock and fire arrow after arrow at "..target_name.."!"):gsub("{target}", target_name)}
    local all_results = {}
    local any_success = false
    local total_evade_mod = 0

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        if roll.success then
            any_success = true
            -- Wiki: (SuccessMargin/10)% evade mod per round, max 10%
            local em = math.min(tech.evade_mod_cap or 10,
                       math.floor(roll.margin / (tech.evade_mod_divisor or 10)))
            total_evade_mod = total_evade_mod + em
            table.insert(all_results, {round=i, success=true, roll=roll, damage={type="puncture"}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "An arrow from your barrage finds "..target_name.."!"):gsub("{target}", target_name)))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]", roll.msg))
        end
    end

    table.insert(round_msgs, ((tech.msg_final or "You lower your bow as your barrage concludes!"):gsub("{target}", target_name)))

    local effects = {}
    if any_success then
        -- Wiki-exact: Enhance Dexterity power 10 for 2 min, party-wide
        table.insert(effects, {
            effect   = "enhance_dexterity",
            duration = tech.success_buff_duration or 120,
            magnitude = tech.success_buff_power or 10,
            target   = "self_and_party",
        })
        if total_evade_mod > 0 then
            table.insert(effects, {effect="evade_bonus", magnitude=total_evade_mod, target="self", duration=30})
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
-- VOLLEY  AoE | Ranged | 75/100/125/150/175
-- Wiki-exact:
--   Fires (Rank+1) shots into the sky; impacts next round
--   Arrows hit random enemies in room
-- ---------------------------------------------------------------------------
function Ranged.volley(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}   -- full room target list provided by Python

    local num_shots = rank + 1

    -- We build a deferred_aoe: Python reads this and schedules the impact 1 round later
    -- Each shot resolves independently at impact time against a random target
    local attacker = player_entity(player)

    -- Pre-compute one smr snapshot for Python to use at impact
    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).ranged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    return {
        ok=true, success=true, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 4,
        is_deferred_aoe   = true,
        deferred_delay    = tech.impact_delay_rounds or 1,
        num_shots         = num_shots,
        attacker_snapshot = {
            skill_ranks = player.skill_ranks,
            stats       = player.stats,
            race_id     = player.race_id,
            level       = player.level,
            stance      = player.stance,
            smr_opts    = smr_opts,
        },
        effects_applied = {},
        message = tech.msg_attempt or string.format(
            "You fire a volley of %d arrow%s high into the sky!",
            num_shots, num_shots == 1 and "" or "s"),
    }
end

return Ranged
