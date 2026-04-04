------------------------------------------------------------------------
-- scripts/globals/magic/spell_formulas.lua
-- Shared GS4-style spell effect helpers so circle scripts stop hand-rolling
-- toy damage/heal math on top of the real CS/TD/bolt resolution layer.
------------------------------------------------------------------------

local Math = require("globals/utils/gs4_math")

local Fx = {}

local function n(v, default)
    local num = tonumber(v)
    if num == nil then
        return default or 0
    end
    return num
end

function Fx.level(ctx)
    return math.max(1, n(ctx and ctx.caster and ctx.caster.level, 1))
end

function Fx.circle_ranks(ctx)
    return math.max(0, n(ctx and ctx.circle_ranks, 0))
end

function Fx.margin(ctx)
    return math.max(0, math.floor(n(ctx and ctx.result and ctx.result.total, 100) - 100))
end

function Fx.lore(ctx, name)
    if not name or name == "" then
        return 0
    end
    return math.max(0, n(ctx and ctx.lore_ranks and ctx.lore_ranks[name], 0))
end

function Fx.mana_control(ctx, sphere)
    if not sphere or sphere == "" then
        return 0
    end
    return math.max(0, n(ctx and ctx.mana_control and ctx.mana_control[sphere], 0))
end

function Fx.skill_rank(ctx, name)
    if not name or name == "" then
        return 0
    end
    return math.max(0, n(ctx and ctx.skill_ranks and ctx.skill_ranks[name], 0))
end

function Fx.skill_bonus(ctx, name)
    if not name or name == "" then
        return 0
    end
    local bonuses = ctx and ctx.skill_bonuses or {}
    local direct = bonuses and bonuses[name]
    if direct ~= nil then
        return n(direct, 0)
    end
    return Math.skill_bonus_from_ranks(Fx.skill_rank(ctx, name))
end

local function raw_stat(ctx, name)
    return n(ctx and ctx.caster and ctx.caster["stat_" .. name], 50)
end

function Fx.stat_bonus(ctx, name)
    if name == "avg_aura_wis" then
        return math.floor((Fx.stat_bonus(ctx, "aura") + Fx.stat_bonus(ctx, "wisdom")) / 2)
    end
    if name == "avg_wis_int" then
        return math.floor((Fx.stat_bonus(ctx, "wisdom") + Fx.stat_bonus(ctx, "intuition")) / 2)
    end
    if name == "avg_aura_int" then
        return math.floor((Fx.stat_bonus(ctx, "aura") + Fx.stat_bonus(ctx, "intuition")) / 2)
    end
    return Math.stat_bonus(raw_stat(ctx, name or "wisdom"))
end

function Fx.hp_after_heal(target, amount)
    local current = n(target and target.health_current, 0)
    local maximum = n(target and target.health_max, current)
    return math.min(maximum, current + math.max(0, math.floor(amount)))
end

function Fx.hp_after_damage(target, amount)
    local current = n(target and target.health_current, 0)
    return math.max(0, current - math.max(0, math.floor(amount)))
end

function Fx.warding_damage(ctx, opts)
    opts = opts or {}
    local margin = Fx.margin(ctx)
    local level = Fx.level(ctx)
    local circle = Fx.circle_ranks(ctx)
    local stat_bonus = Fx.stat_bonus(ctx, opts.stat or "wisdom")
    local skill_bonus = Fx.skill_bonus(ctx, opts.skill or "spell_research")
    local lore = Fx.lore(ctx, opts.lore)
    local mana_control = Fx.mana_control(ctx, opts.mana_control)
    local base = n(opts.base, 1)
    local damage =
        base +
        math.floor(margin * n(opts.margin_mult, 1.0)) +
        math.floor(level * n(opts.level_scale, 0.35)) +
        math.floor(circle * n(opts.circle_scale, 0.45)) +
        math.floor(stat_bonus * n(opts.stat_scale, 0.35)) +
        math.floor(skill_bonus * n(opts.skill_scale, 0.10)) +
        math.floor(lore * n(opts.lore_scale, 0.05)) +
        math.floor(mana_control * n(opts.mc_scale, 0.04)) +
        math.floor(n(opts.flat_bonus, 0))
    return math.max(n(opts.min, base), math.floor(damage))
end

function Fx.bolt_damage(ctx, opts)
    opts = opts or {}
    local margin = Fx.margin(ctx)
    local level = Fx.level(ctx)
    local circle = Fx.circle_ranks(ctx)
    local stat_bonus = Fx.stat_bonus(ctx, opts.stat or "aura")
    local aiming_bonus = Fx.skill_bonus(ctx, "spell_aiming")
    local lore = Fx.lore(ctx, opts.lore)
    local mana_control = Fx.mana_control(ctx, opts.mana_control or "elemental")
    local base = n(opts.base, 1)
    local damage =
        base +
        math.floor(margin * n(opts.margin_mult, 1.0)) +
        math.floor(level * n(opts.level_scale, 0.30)) +
        math.floor(circle * n(opts.circle_scale, 0.35)) +
        math.floor(stat_bonus * n(opts.stat_scale, 0.25)) +
        math.floor(aiming_bonus * n(opts.aiming_scale, 0.12)) +
        math.floor(lore * n(opts.lore_scale, 0.05)) +
        math.floor(mana_control * n(opts.mc_scale, 0.03)) +
        math.floor(n(opts.flat_bonus, 0))
    return math.max(n(opts.min, base), math.floor(damage))
end

function Fx.empath_heal_amount(ctx, opts)
    opts = opts or {}
    local level = Fx.level(ctx)
    local circle = Fx.circle_ranks(ctx)
    local first_aid_bonus = Fx.skill_bonus(ctx, "first_aid")
    local first_aid_ranks = Fx.skill_rank(ctx, "first_aid")
    local wisdom = Fx.stat_bonus(ctx, "wisdom")
    local intuition = Fx.stat_bonus(ctx, "intuition")
    local transference = Fx.lore(ctx, "transference")
    local manipulation = Fx.lore(ctx, "manipulation")
    local amount =
        n(opts.base, 10) +
        math.floor(level * n(opts.level_scale, 0.50)) +
        math.floor(circle * n(opts.circle_scale, 0.70)) +
        math.floor(first_aid_bonus * n(opts.first_aid_scale, 0.20)) +
        math.floor(first_aid_ranks * n(opts.first_aid_rank_scale, 0.15)) +
        math.floor(wisdom * n(opts.wisdom_scale, 0.35)) +
        math.floor(intuition * n(opts.intuition_scale, 0.20)) +
        math.floor(transference * n(opts.transference_scale, 0.05)) +
        math.floor(manipulation * n(opts.manipulation_scale, 0.04))
    return math.max(n(opts.min, 1), math.floor(amount))
end

function Fx.support_heal_amount(ctx, opts)
    opts = opts or {}
    local level = Fx.level(ctx)
    local circle = Fx.circle_ranks(ctx)
    local stat_bonus = Fx.stat_bonus(ctx, opts.stat or "wisdom")
    local skill_bonus = Fx.skill_bonus(ctx, opts.skill or "spell_research")
    local lore = Fx.lore(ctx, opts.lore)
    local mana_control = Fx.mana_control(ctx, opts.mana_control or "spirit")
    local amount =
        n(opts.base, 8) +
        math.floor(level * n(opts.level_scale, 0.40)) +
        math.floor(circle * n(opts.circle_scale, 0.50)) +
        math.floor(stat_bonus * n(opts.stat_scale, 0.30)) +
        math.floor(skill_bonus * n(opts.skill_scale, 0.10)) +
        math.floor(lore * n(opts.lore_scale, 0.04)) +
        math.floor(mana_control * n(opts.mc_scale, 0.03)) +
        math.floor(n(opts.flat_bonus, 0))
    return math.max(n(opts.min, 1), math.floor(amount))
end

function Fx.heal_summary(target, amount)
    local new_hp = Fx.hp_after_heal(target, amount)
    local max_hp = n(target and target.health_max, new_hp)
    return new_hp, max_hp
end

return Fx
