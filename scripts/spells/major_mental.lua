------------------------------------------------------------------------
-- scripts/spells/major_mental.lua
-- Major Mental (MjM) spell circle.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local MjM = {}

local CIRCLE_ID  = 13
local LUA_SCRIPT = "spells/major_mental"

local SPELLS = {
    [1315] = {
        name="Comprehend Languages",
        mnemonic="COMPREHENDLANGUAGES",
        spell_type="utility",
        mana_cost=15,
        description="Lets the caster understand and speak languages they do not normally know.",
    },
    [1319] = {
        name="Clarity of Thought",
        mnemonic="CLARITYOFTHOUGHT",
        spell_type="buff",
        mana_cost=19,
        description="Grants a brief burst of enhanced mental casting strength for the next mental spell.",
    },
}

function MjM.seed()
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

handlers[1315] = function(ctx)
    return "Arcane insight settles over your thoughts, and unfamiliar speech becomes understandable."
end

handlers[1319] = function(ctx)
    ActiveBuffs.apply(ctx.caster.id, 1319, CIRCLE_ID, ctx.caster.id, 120, { cs_mental=30, clarity_of_thought=true })
    return "Your thoughts sharpen into a crystal-clear focus."
end

function MjM.on_cast(ctx)
    local fn = handlers[ctx.spell.spell_number]
    if fn then
        return fn(ctx)
    end
    return nil
end

return MjM
