------------------------------------------------------------------------
-- scripts/spells/savant.lua
-- Savant Base spell circle.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local SpellFx     = require("globals/magic/spell_formulas")

local Sav = {}

local CIRCLE_ID  = 14
local LUA_SCRIPT = "spells/savant"

local SPELLS = {
    [1408] = {
        name="Astral Spear",
        mnemonic="ASTRALSPEAR",
        spell_type="bolt",
        mana_cost=8,
        description="element:impact. Hurls a focused spear of astral energy at the target.",
    },
    [1409] = {
        name="Displace",
        mnemonic="DISPLACE",
        spell_type="buff",
        mana_cost=9,
        description="Bends space around the caster, making hostile attacks less accurate.",
    },
    [1414] = {
        name="Mana Burst",
        mnemonic="MANABURST",
        spell_type="warding",
        mana_cost=14,
        description="A burst of mental force damages the target with repeated pulses of energy.",
    },
    [1417] = {
        name="Astral Vault",
        mnemonic="ASTRALVAULT",
        spell_type="utility",
        mana_cost=17,
        description="Stores an item in an extradimensional vault for later retrieval.",
    },
    [1435] = {
        name="Convoke",
        mnemonic="CONVOKE",
        spell_type="utility",
        mana_cost=35,
        description="Projects the savant's voice and attention across the astral pathways.",
    },
}

function Sav.seed()
    for num, sp in pairs(SPELLS) do
        DB.execute([[
            INSERT INTO spells
                (spell_number, name, mnemonic, circle_id, spell_type, mana_cost, description, lua_script)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name), mnemonic=VALUES(mnemonic),
                spell_type=VALUES(spell_type), mana_cost=VALUES(mana_cost),
                description=VALUES(description), lua_script=VALUES(lua_script)
        ]], { num, sp.name, sp.mnemonic, CIRCLE_ID, sp.spell_type, sp.mana_cost, sp.description, LUA_SCRIPT })
    end
end

local handlers = {}

handlers[1408] = function(ctx)
    if not ctx.result.hit or not ctx.target then
        return "The astral spear misses its mark."
    end
    local dmg = SpellFx.bolt_damage(ctx, {
        base = 9,
        min = 9,
        margin_mult = 1.25,
        stat = "avg_aura_wis",
        mana_control = "mental",
        level_scale = 0.30,
        circle_scale = 0.40,
        stat_scale = 0.28,
        aiming_scale = 0.10,
    })
    local new_hp = SpellFx.hp_after_damage(ctx.target, dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, ctx.target.id })
    return string.format("An astral spear punches through %s for %d damage!", ctx.target.name or "your target", dmg)
end

handlers[1409] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1409, CIRCLE_ID, ctx.caster.id, 180, { ds=20, displace=true })
    return "Space ripples and your outline slips slightly out of alignment."
end

handlers[1414] = function(ctx)
    if not ctx.result.hit or not ctx.target then
        return "The mana burst dissipates harmlessly."
    end
    local pulses = 2 + math.floor((ctx.circle_ranks or 1) / 20)
    local per_pulse = SpellFx.warding_damage(ctx, {
        base = 4,
        min = 4,
        margin_mult = 0.35,
        stat = "avg_aura_wis",
        skill = "spell_research",
        mana_control = "mental",
        level_scale = 0.20,
        circle_scale = 0.20,
        stat_scale = 0.20,
        skill_scale = 0.06,
    })
    local total = pulses * per_pulse
    local new_hp = SpellFx.hp_after_damage(ctx.target, total)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, ctx.target.id })
    DB.execute("UPDATE characters SET mana_current=GREATEST(0, mana_current-?) WHERE id=?", { pulses, ctx.target.id })
    return string.format("A mana burst hammers %s with %d astral pulses for %d damage!", ctx.target.name or "your target", pulses, total)
end

handlers[1417] = function(ctx)
    return "An astral vault flickers open for a moment, ready to receive an item."
end

handlers[1435] = function(ctx)
    return "Your thoughts push outward across the astral conduits."
end

function Sav.on_cast(ctx)
    local fn = handlers[ctx.spell.spell_number]
    if fn then
        return fn(ctx)
    end
    return nil
end

return Sav
