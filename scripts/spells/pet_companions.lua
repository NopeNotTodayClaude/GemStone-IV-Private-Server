-- scripts/spells/pet_companions.lua
-- Custom companion-only spells executed through the real Lua spell engine.

local DB = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local PetCompanions = {}

local CIRCLE_ID = 15
local SPELL_NUMBER = 5001

local function target_id(ctx)
    return ctx.target and ctx.target.id or ctx.caster.id
end

function PetCompanions.seed()
    DB.execute([[
        INSERT INTO spells
            (spell_number, name, mnemonic, circle_id, spell_type, mana_cost, description, lua_script)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            mnemonic=VALUES(mnemonic),
            circle_id=VALUES(circle_id),
            spell_type=VALUES(spell_type),
            mana_cost=VALUES(mana_cost),
            description=VALUES(description),
            lua_script=VALUES(lua_script)
    ]], {
        SPELL_NUMBER,
        "Comforting Glow",
        "CGLOW",
        CIRCLE_ID,
        "buff",
        0,
        "A companion-only restorative aura that quietly bolsters the owner's health recovery.",
        "spells/pet_companions",
    })
end

local handlers = {}

handlers[SPELL_NUMBER] = function(ctx)
    local spell_data = (ctx.target and ctx.target.pet_spell_data) or {}
    local duration = tonumber(spell_data.duration_seconds) or 60
    local heal_pct = tonumber(spell_data.heal_pct) or 0.01
    local owner_pet_id = tonumber(spell_data.owner_pet_id) or 0
    local pet_name = tostring(spell_data.pet_name or ctx.caster.pet_name or "your companion")

    ActiveBuffs.apply(target_id(ctx), SPELL_NUMBER, CIRCLE_ID, ctx.caster.id, duration, {
        floofer_glow = true,
        pet_regen_pct = heal_pct,
        pet_regen_owner_id = owner_pet_id,
        pet_regen_source = pet_name,
    })

    -- Silent by design: the pet status icon communicates the effect instead of chat spam.
    return ""
end

function PetCompanions.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if not h then
        return
    end
    local ok, msg = pcall(h, ctx)
    if not ok then
        print(string.format("[PetCompanions] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        return
    end
    if type(msg) == "string" and msg ~= "" and (not ctx.result.message or ctx.result.message == "") then
        ctx.result.message = msg
    end
end

return PetCompanions
