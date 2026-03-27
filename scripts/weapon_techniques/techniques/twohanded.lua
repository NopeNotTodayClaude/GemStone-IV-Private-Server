-- =============================================================================
-- scripts/weapon_techniques/techniques/twohanded.lua
-- Handlers: Overpower, Thrash, Reverse Strike, Whirlwind
-- =============================================================================

local SMR      = require("globals/utils/smr")
local TwoHanded = {}

local function safe_int(v) return tonumber(v) or 0 end
local function safe_str(v) return tostring(v or "") end
local function fmt(n) n=safe_str(n); return n:sub(1,1):upper()..n:sub(2) end

local function player_entity(p)
    local sr = p.skill_ranks or {}
    return {
        skill_ranks={
            dodging=safe_int(sr.dodging), combat_maneuvers=safe_int(sr.combat_maneuvers),
            perception=safe_int(sr.perception), physical_fitness=safe_int(sr.physical_fitness),
            shield_use=0,  -- two-handers: no shield
            two_handed_weapons=safe_int(sr.two_handed_weapons),
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
-- OVERPOWER  Reaction | Two-Handed | 10/35/60/85/110
-- Wiki-exact:
--   Trigger: recent_evade OR recent_block OR recent_parry
--   +10 CER critical weighting for one swing
--   Attack CANNOT be evaded, blocked, or parried
--   RT = ATTACK - 2
-- ---------------------------------------------------------------------------
function TwoHanded.overpower(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).two_handed_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
        off_bonus          = safe_int(tech.cer_bonus),   -- +10 CER
        bypass_ebp         = tech.bypass_ebp,            -- true
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=0,
            roundtime=0, rt_from_attack=true, rt_mod=-2,
            smr_result=roll, effects_applied={},
            -- Even on fail: cannot be evaded/blocked/parried means the ATTACK
            -- still goes through the standard attack roll; fail here means
            -- the maneuver setup failed before the attack fires
            message=string.format("%s\n%s\n%s manages to avoid your overpower attempt!",
                tech.msg_attempt:gsub("{target}", target_name),
                roll.msg, fmt(target_name)),
        }
    end

    return {
        ok=true, success=true, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2,
        smr_result=roll, effects_applied={},
        attack_results={{
            damage_type = "weapon",
            cer_bonus   = safe_int(tech.cer_bonus),
            bypass_ebp  = true,   -- Python bridge enforces this in attack roll
        }},
        message=string.format("%s\n%s\n%s",
            tech.msg_attempt:gsub("{target}", target_name),
            roll.msg,
            tech.msg_hit:gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- THRASH  Assault | Two-Handed | 25/50/75/100/125
-- Wiki-exact:
--   (1+MOC_bonus) attacks
--   Parry modified (SuccessMargin/10)% max 10% per round
--   On success: Forceful Blows 2 minutes
-- ---------------------------------------------------------------------------
function TwoHanded.thrash(ctx)
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
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).two_handed_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {(tech.msg_attempt or "You rush "..target_name..", raising your weapon high!"):gsub("{target}", target_name)}
    local all_results = {}
    local any_success = false
    local total_parry = 0

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        if roll.success then
            any_success = true
            -- Wiki: (SuccessMargin/10)% max 10%
            local pm = math.min(tech.parry_mod_cap or 10,
                        math.floor(roll.margin / (tech.parry_mod_divisor or 10)))
            total_parry = total_parry + pm
            table.insert(all_results, {round=i, success=true, roll=roll, damage={type="weapon"}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "You bring your weapon around to batter "..target_name.."!"):gsub("{target}", target_name)))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]", roll.msg))
        end
    end

    table.insert(round_msgs, (tech.msg_final or "With a final, explosive breath, you pull your weapon back to a ready position."):gsub("{target}", target_name))

    local effects = {}
    if any_success then
        table.insert(effects, {effect="forceful_blows", duration=tech.success_buff_duration or 120, target="self"})
        if total_parry > 0 then
            table.insert(effects, {effect="parry_bonus", magnitude=total_parry, target="self", duration=30})
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
-- REVERSE STRIKE  Reaction | Two-Handed | 50/75/100/125/150
-- Wiki-exact:
--   Trigger: recent_parry
--   Bypasses target stance DS bonus
--   Disoriented = (8+Rank*3)s on hit
--   RT = ATTACK - 2
-- ---------------------------------------------------------------------------
function TwoHanded.reversestrike(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).two_handed_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
        bypass_ebp         = tech.bypass_stance_ds,  -- bypasses stance DS bonus
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=0,
            roundtime=0, rt_from_attack=true, rt_mod=-2,
            smr_result=roll, effects_applied={},
            message=string.format("%s\n%s\n%s recovers before your reverse strike lands!",
                (tech.msg_attempt or "You feint then snap your weapon back at "..target_name.."!"):gsub("{target}", target_name),
                roll.msg, fmt(target_name)),
        }
    end

    -- Wiki-exact: Disoriented = 8 + (Rank*3)
    local disoriented_dur = (tech.disoriented_base or 8) + rank * (tech.disoriented_per_rank or 3)

    local effects = {
        {effect="disoriented", duration=disoriented_dur, target="defender"},
    }

    return {
        ok=true, success=true, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2,
        smr_result=roll, effects_applied=effects,
        attack_results={{damage_type="weapon", bypass_stance_ds=true}},
        message=string.format("%s\n%s\n%s",
            (tech.msg_attempt or "You feint then snap your weapon back at "..target_name.."!"):gsub("{target}", target_name),
            roll.msg,
            (tech.msg_hit or "Your unexpected reverse strike catches "..target_name.." completely off guard!"):gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- WHIRLWIND  AoE | Two-Handed | 75/100/125/150/175
-- Wiki-exact:
--   (1+MOC_bonus) targets, full weapon damage each
--   Evasiveness = (5+Rank)s
--   High margin may force target to higher stance
-- ---------------------------------------------------------------------------
function TwoHanded.whirlwind(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).two_handed_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = true,
        include_shield     = false,
    }

    local round_msgs  = {tech.msg_attempt or "You spin in a powerful whirlwind attack!"}
    local aoe_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender = creature_entity(target)
        local roll     = SMR.roll(attacker, defender, smr_opts)
        local tname    = safe_str(target.name)
        if roll.success then
            any_success = true
            local force_stance = roll.margin >= (tech.force_stance_threshold or 100)
            table.insert(aoe_results, {
                target=tname, success=true, roll=roll,
                damage={type="weapon", full=true},
                force_target_stance=force_stance,
            })
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "Your spinning weapon crashes into "..tname.."!"):gsub("{target}", tname)))
        else
            table.insert(aoe_results, {target=tname, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  You miss %s!", roll.msg, tname))
        end
    end

    -- Wiki-exact: Evasiveness = 5 + Rank seconds
    local evasive_dur = (tech.evasiveness_base or 5) + rank * (tech.evasiveness_per_rank or 1)
    local effects = {
        {effect="evasiveness", duration=evasive_dur, target="self"},
    }

    return {
        ok=true, success=any_success, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 3, is_aoe=true,
        aoe_results=aoe_results, effects_applied=effects,
        message=table.concat(round_msgs, "\n"),
    }
end

return TwoHanded
