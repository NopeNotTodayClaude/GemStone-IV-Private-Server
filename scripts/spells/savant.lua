------------------------------------------------------------------------
-- scripts/spells/savant.lua
-- Savant Base spell circle.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

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

handlers[1409] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1409, CIRCLE_ID, ctx.caster.id, 180, { ds=20, displace=true })
    return "Space ripples and your outline slips slightly out of alignment."
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
