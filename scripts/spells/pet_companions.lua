-- scripts/spells/pet_companions.lua
-- Custom companion-only spells executed through the real Lua spell engine.

local DB = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local PetCompanions = {}

local CIRCLE_ID = 15
local SPELL_COMFORTING_GLOW = 5001
local SPELL_SCALEGUARD_WARD = 5002
local SPELL_STATIC_LASH = 5003
local SPELL_STATIC_TEMPEST = 5004

local function target_id(ctx)
    return ctx.target and ctx.target.id or ctx.caster.id
end

function PetCompanions.seed()
    local spells = {
        {
            SPELL_COMFORTING_GLOW,
            "Comforting Glow",
            "CGLOW",
            "buff",
            "A companion-only restorative aura that quietly bolsters the owner's health recovery.",
        },
        {
            SPELL_SCALEGUARD_WARD,
            "Scaleguard Ward",
            "SGWARD",
            "buff",
            "A companion-only sapphire ward that absorbs a limited amount of incoming damage and stiffens the owner's defenses.",
        },
        {
            SPELL_STATIC_LASH,
            "Static Lash",
            "SLASH",
            "utility",
            "A companion-only arc of crackling force used to harry the owner's current foe.",
        },
        {
            SPELL_STATIC_TEMPEST,
            "Static Tempest",
            "STEMPEST",
            "utility",
            "A companion-only room-wide storm of crackling force that lashes every hostile foe near the owner.",
        },
    }

    for _, spell in ipairs(spells) do
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
            spell[1],
            spell[2],
            spell[3],
            CIRCLE_ID,
            spell[4],
            0,
            spell[5],
            "spells/pet_companions",
        })
    end
end

local handlers = {}

handlers[SPELL_COMFORTING_GLOW] = function(ctx)
    local spell_data = (ctx.target and ctx.target.pet_spell_data) or {}
    local duration = tonumber(spell_data.duration_seconds) or 60
    local heal_pct = tonumber(spell_data.heal_pct) or 0.01
    local owner_pet_id = tonumber(spell_data.owner_pet_id) or 0
    local pet_name = tostring(spell_data.pet_name or ctx.caster.pet_name or "your companion")

    ActiveBuffs.apply(target_id(ctx), SPELL_COMFORTING_GLOW, CIRCLE_ID, ctx.caster.id, duration, {
        floofer_glow = true,
        pet_regen_pct = heal_pct,
        pet_regen_owner_id = owner_pet_id,
        pet_regen_source = pet_name,
    })

    -- Silent by design: the pet status icon communicates the effect instead of chat spam.
    return ""
end

handlers[SPELL_SCALEGUARD_WARD] = function(ctx)
    local spell_data = (ctx.target and ctx.target.pet_spell_data) or {}
    local duration = tonumber(spell_data.duration_seconds) or 25
    local absorb_amount = tonumber(spell_data.absorb_amount) or 8
    local ds_bonus = tonumber(spell_data.ds_bonus) or 0

    ActiveBuffs.apply(target_id(ctx), SPELL_SCALEGUARD_WARD, CIRCLE_ID, ctx.caster.id, duration, {
        damage_redirect = absorb_amount,
        ds = ds_bonus,
        scaleguard_ward = true,
        scaleguard_pet_name = tostring(spell_data.pet_name or ctx.caster.pet_name or "your companion"),
    })

    return ""
end

handlers[SPELL_STATIC_LASH] = function(ctx)
    local spell_data = (ctx.target and ctx.target.pet_spell_data) or {}
    local pet_name = tostring(spell_data.pet_name or ctx.caster.pet_name or "your companion")
    local target_name = tostring((ctx.target and ctx.target.name) or "your foe")
    local min_dmg = tonumber(spell_data.min_damage) or 6
    local max_dmg = tonumber(spell_data.max_damage) or 11
    local dmg = min_dmg + math.random(0, math.max(0, max_dmg - min_dmg))
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("%s lashes out with a crackling arc of force at %s for %d damage!", pet_name, target_name, dmg)
end

handlers[SPELL_STATIC_TEMPEST] = function(ctx)
    local spell_data = (ctx.target and ctx.target.pet_spell_data) or {}
    local pet_name = tostring(spell_data.pet_name or ctx.caster.pet_name or "your companion")
    local min_dmg = tonumber(spell_data.min_damage) or 22
    local max_dmg = tonumber(spell_data.max_damage) or 36
    local dmg = min_dmg + math.random(0, math.max(0, max_dmg - min_dmg))
    ctx.result.room_damage = (ctx.result.room_damage or 0) + dmg
    return string.format("%s arches its back and detonates a room-wide storm of crackling force for %d damage!", pet_name, dmg)
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
