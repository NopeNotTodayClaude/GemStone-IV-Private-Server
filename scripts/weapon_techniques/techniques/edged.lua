-- =============================================================================
-- scripts/weapon_techniques/techniques/edged.lua
-- Handlers: Cripple, Riposte, Flurry, Whirling Blade
-- =============================================================================

local SMR   = require("globals/utils/smr")
local Edged = {}

local function safe_int(v) return tonumber(v) or 0 end
local function safe_str(v) return tostring(v or "") end
local function fmt(name) name=safe_str(name); return name:sub(1,1):upper()..name:sub(2) end

local function player_entity(p)
    local sr = p.skill_ranks or {}
    return {
        skill_ranks={
            dodging=safe_int(sr.dodging), combat_maneuvers=safe_int(sr.combat_maneuvers),
            perception=safe_int(sr.perception), physical_fitness=safe_int(sr.physical_fitness),
            shield_use=safe_int(sr.shield_use), edged_weapons=safe_int(sr.edged_weapons),
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
    return {skill_ranks=c.skill_ranks or {}, stats=c.stats or {},
            race_id=0, level=safe_int(c.level), stance=c.stance or "neutral",
            smr_off_bonus=0,smr_def_bonus=0,encumbrance_penalty=0,armor_action_penalty=0}
end

-- ---------------------------------------------------------------------------
-- CRIPPLE  Setup | Edged | 10/35/60/85/110
-- Wiki-exact:
--   Minor slash damage
--   Crippled = (15 + Rank*5)s
--   If leg targeted: Rooted = (10 + Rank*2)s
-- ---------------------------------------------------------------------------
function Edged.cripple(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    -- Limb target: passed from Python as ctx.limb
    local limb = (ctx.limb or ""):lower()
    if limb == "" then limb = "right arm" end  -- default limb if unspecified

    -- Validate limb
    local valid = {["right arm"]=true,["left arm"]=true,["right leg"]=true,
                   ["left leg"]=true,["right hand"]=true,["left hand"]=true}
    if not valid[limb] then
        limb = "right arm"
    end
    local is_leg = (limb == "right leg" or limb == "left leg")

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).edged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = true,
    }

    local roll  = SMR.roll(attacker, defender, smr_opts)
    local cost  = safe_int(tech.stamina_cost)

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=cost,
            roundtime=tech.base_rt or 2, smr_result=roll, effects_applied={},
            message=string.format("%s\n%s\n%s", roll.msg,
                (tech.msg_attempt or "You slash at "..target_name.."'s "..limb.."!")
                    :gsub("{target}", target_name):gsub("{limb}", limb),
                (tech.msg_fail or fmt(target_name).." avoids your crippling slash!")
                    :gsub("{Target}", fmt(target_name)):gsub("{target}", target_name)),
        }
    end

    -- Wiki-exact durations
    local crippled_dur = (tech.crippled_base or 15) + rank * (tech.crippled_per_rank or 5)
    local rooted_dur   = is_leg and ((tech.rooted_base or 10) + rank * (tech.rooted_per_rank or 2)) or 0

    local effects = {
        {effect="crippled", duration=crippled_dur, target="defender", limb=limb},
    }
    if is_leg and rooted_dur > 0 then
        table.insert(effects, {effect="rooted", duration=rooted_dur, target="defender"})
    end

    local hit_msg = is_leg
        and (tech.msg_hit_leg or "Your slash severs the tendons in "..target_name.."'s "..limb.."!")
        or  (tech.msg_hit     or "Your blade cuts deep into "..target_name.."'s "..limb.."!")
    hit_msg = hit_msg:gsub("{target}", target_name):gsub("{limb}", limb)

    return {
        ok=true, success=true, stamina_spent=cost,
        roundtime=tech.base_rt or 2, smr_result=roll,
        effects_applied=effects,
        attack_results={{damage_type="slash", minor=true, limb=limb}},
        message=string.format("%s\n%s\n%s",
            roll.msg,
            (tech.msg_attempt or "You slash at "..target_name.."'s "..limb.."!")
                :gsub("{target}", target_name):gsub("{limb}", limb),
            hit_msg),
    }
end

-- ---------------------------------------------------------------------------
-- RIPOSTE  Reaction | Edged | 25/50/75/100/125
-- Wiki-exact:
--   Trigger: recent_parry
--   Weakened Armament applied BEFORE attack resolution for (15+Rank*5)s
--   Removes recent EBP from attacker
--   RT = ATTACK - 2
-- ---------------------------------------------------------------------------
function Edged.riposte(ctx)
    local tech  = ctx.tech
    local rank  = safe_int(ctx.rank)
    local player = ctx.player
    local target = ctx.target
    local target_name = safe_str(target and target.name or ctx.target_name)

    local attacker = player_entity(player)
    local defender = creature_entity(target)

    -- Weakened Armament duration
    local wa_dur = (tech.weakened_armament_base or 15) + rank * (tech.weakened_armament_per_rank or 5)

    -- WA applied before roll: model as offensive bonus
    local wa_off_bonus = 10 + rank * 3

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).edged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
        off_bonus          = wa_off_bonus,
    }

    local roll = SMR.roll(attacker, defender, smr_opts)

    -- Effects are applied regardless of hit outcome (WA is pre-attack)
    local effects = {
        {effect="weakened_armament", duration=wa_dur, target="defender", pre_attack=true},
        {effect="remove_recent_ebp", target="self"},
    }

    if not roll.success then
        return {
            ok=true, success=false, stamina_spent=0,
            roundtime=0, rt_from_attack=true, rt_mod=-2,
            smr_result=roll, effects_applied=effects,
            message=string.format(
                "You seize %s's parry and drive your blade forward!\n%s\n%s recovers and your riposte misses!",
                target_name, roll.msg, fmt(target_name)),
        }
    end

    return {
        ok=true, success=true, stamina_spent=0,
        roundtime=0, rt_from_attack=true, rt_mod=-2,
        smr_result=roll, effects_applied=effects,
        attack_results={{damage_type="slash", minor=false}},
        message=string.format("%s\n%s\n%s",
            (tech.msg_attempt or "You seize "..target_name.."'s parry and drive your blade forward!")
                :gsub("{target}", target_name),
            roll.msg,
            (tech.msg_hit or "Your riposte slips past "..target_name.."'s guard!")
                :gsub("{target}", target_name)),
    }
end

-- ---------------------------------------------------------------------------
-- FLURRY  Assault | Edged | 50/75/100/125/150
-- Wiki-exact:
--   (1+MOC_bonus) attacks
--   Parry modified (SuccessMargin/5)% max 10% per round
--   On success: Slashing Strikes 2 minutes
-- ---------------------------------------------------------------------------
function Edged.flurry(ctx)
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
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).edged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {(tech.msg_attempt or "You launch into a rapid flurry of slashes at "..target_name.."!"):gsub("{target}", target_name)}
    local all_results = {}
    local any_success = false
    local total_parry = 0

    for i = 1, num_rounds do
        local roll = SMR.roll(attacker, defender, smr_opts)
        if roll.success then
            any_success = true
            -- Wiki: (SuccessMargin / 5)% max 10%
            local pm = math.min(tech.parry_mod_cap or 10,
                        math.floor(roll.margin / (tech.parry_mod_divisor or 5)))
            total_parry = total_parry + pm
            table.insert(all_results, {round=i, success=true, roll=roll, damage={type="slash"}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "You carve a slash across "..target_name.."!"):gsub("{target}", target_name)))
        else
            table.insert(all_results, {round=i, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  [miss]", roll.msg))
        end
    end

    table.insert(round_msgs, (tech.msg_final or "With a final flourish you step back from "..target_name.."!"):gsub("{target}", target_name))

    local effects = {}
    if any_success then
        -- Wiki: Slashing Strikes 2 minutes on success
        table.insert(effects, {effect="slashing_strikes", duration=tech.success_buff_duration or 120, target="self"})
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
-- WHIRLING BLADE  AoE | Edged | 75/100/125/150/175
-- Wiki-exact:
--   (1+MOC_bonus) targets
--   Evasiveness = (5+Rank)s on attacker
-- ---------------------------------------------------------------------------
function Edged.wblade(ctx)
    local tech    = ctx.tech
    local rank    = safe_int(ctx.rank)
    local player  = ctx.player
    local targets = ctx.targets or {}

    local attacker  = player_entity(player)
    local moc_ranks = safe_int((player.skill_ranks or {}).multi_opponent_combat or 0)
    local max_targets = SMR.moc_hits(moc_ranks)

    local smr_opts = {
        weapon_skill_ranks = safe_int((player.skill_ranks or {}).edged_weapons),
        attacker_mk_rank   = rank,
        defender_mk_rank   = 0,
        use_racial_size    = false,
        include_shield     = false,
    }

    local round_msgs  = {tech.msg_attempt or "You spin your blade in a brilliant whirling arc!"}
    local aoe_results = {}
    local any_success = false

    for i, target in ipairs(targets) do
        if i > max_targets then break end
        local defender    = creature_entity(target)
        local roll        = SMR.roll(attacker, defender, smr_opts)
        local tname       = safe_str(target.name)
        if roll.success then
            any_success = true
            table.insert(aoe_results, {target=tname, success=true, roll=roll, damage={type="slash"}})
            table.insert(round_msgs, string.format("%s  %s", roll.msg,
                (tech.msg_hit or "Your whirling blade slashes across "..tname.."!"):gsub("{target}", tname)))
        else
            table.insert(aoe_results, {target=tname, success=false, roll=roll})
            table.insert(round_msgs, string.format("%s  You miss %s!", roll.msg, tname))
        end
    end

    -- Wiki-exact: Evasiveness = 5 + Rank seconds
    local evasiveness_dur = (tech.evasiveness_base or 5) + rank * (tech.evasiveness_per_rank or 1)
    local effects = {
        {effect="evasiveness", duration=evasiveness_dur, target="self"},
    }

    return {
        ok=true, success=any_success, stamina_spent=safe_int(tech.stamina_cost),
        roundtime=tech.base_rt or 3, is_aoe=true,
        aoe_results=aoe_results, effects_applied=effects,
        message=table.concat(round_msgs, "\n"),
    }
end

return Edged
