------------------------------------------------------------------------
-- scripts/spells/arcane.lua
-- Arcane spell circle.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local Arc = {}

local CIRCLE_ID  = 15
local LUA_SCRIPT = "spells/arcane"

local SPELLS = {
    [1700] = { name="Arcane Blast",        mnemonic="ARCANEBLAST",      spell_type="warding", mana_cost=0,  description="A flexible arcane attack that can manifest as either a warding assault or a bolt." },
    [1701] = { name="Arcane Decoy",        mnemonic="ARCANEDECOY",      spell_type="buff",    mana_cost=1,  description="Creates a misleading arcane afterimage to distract attackers." },
    [1704] = { name="Stun Cloud",          mnemonic="STUNCLOUD",        spell_type="utility", mana_cost=4,  description="Fills the area with destabilizing vapors that can leave enemies stunned." },
    [1705] = { name="Martial Prowess",     mnemonic="MARTIALPROWESS",   spell_type="buff",    mana_cost=5,  description="Enhances the target's martial edge with arcane precision." },
    [1706] = { name="Flaming Aura",        mnemonic="FLAMINGAURA",      spell_type="buff",    mana_cost=6,  description="Wraps the target in a flickering aura of fire." },
    [1707] = { name="Minor Steam",         mnemonic="MINORSTEAM",       spell_type="utility", mana_cost=7,  description="Releases a short burst of scalding steam at the target." },
    [1708] = { name="Mystic Impedance",    mnemonic="MYSTICIMPEDANCE",  spell_type="buff",    mana_cost=8,  description="Disrupts hostile magical momentum around the target." },
    [1709] = { name="Minor Cold",          mnemonic="MINORCOLD",        spell_type="bolt",    mana_cost=9,  description="element:ice. A basic arcane burst of cold." },
    [1710] = { name="Major Acid",          mnemonic="MAJORACID",        spell_type="bolt",    mana_cost=10, description="element:acid. A stronger arcane assault of corrosive acid." },
    [1711] = { name="Mystic Focus",        mnemonic="MYSTICFOCUS",      spell_type="buff",    mana_cost=11, description="Deepens concentration, helping the target maintain magical control." },
    [1712] = { name="Spirit Guard",        mnemonic="SPIRITGUARD",      spell_type="buff",    mana_cost=12, description="Fortifies the target against hostile spiritual influence." },
    [1713] = { name="Death Cloud",         mnemonic="DEATHCLOUD",       spell_type="utility", mana_cost=13, description="Unleashes a dangerous cloud of corrupted arcane essence." },
    [1714] = { name="Quake",               mnemonic="QUAKE",            spell_type="maneuver",mana_cost=14, description="Shakes the battlefield with a violent tremor." },
    [1715] = { name="Firestorm",           mnemonic="FIRESTORM",        spell_type="utility", mana_cost=15, description="Rains destructive fire over the surrounding area." },
    [1716] = { name="Neutralize Curse",    mnemonic="NEUTRALIZECURSE",  spell_type="utility", mana_cost=16, description="Attempts to strip an item or person of an active curse." },
    [1718] = { name="V'tull's Fury",       mnemonic="VTULLSFURY",       spell_type="buff",    mana_cost=18, description="Empowers the target with violent, unstable arcane aggression." },
    [1720] = { name="Arcane Barrier",      mnemonic="ARCANEBARRIER",    spell_type="buff",    mana_cost=20, description="Projects a strong arcane barrier around the target." },
    [1750] = { name="Fash'lo'nae's Gift",  mnemonic="FASHLONAESGIFT",   spell_type="buff",    mana_cost=50, description="A rare arcane blessing that sharpens magical aptitude." },
}

function Arc.seed()
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

handlers[1701] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1701, CIRCLE_ID, ctx.caster.id, 180, { ds=15, arcane_decoy=true })
    return "A wavering arcane duplicate shimmers into place."
end

handlers[1705] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1705, CIRCLE_ID, ctx.caster.id, 180, { as_bonus=10, ds=5, martial_prowess=true })
    return "Arcane force hardens the edge of your martial instincts."
end

handlers[1706] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1706, CIRCLE_ID, ctx.caster.id, 180, { flaming_aura=true, ds=5 })
    return "A halo of living flame wreathes the target."
end

handlers[1708] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1708, CIRCLE_ID, ctx.caster.id, 180, { td_elemental=10, td_spiritual=10, mystic_impedance=true })
    return "A dense shell of arcane drag settles into place."
end

handlers[1711] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1711, CIRCLE_ID, ctx.caster.id, 240, { cs_all=10, mystic_focus=true })
    return "Your concentration narrows into an unwavering line."
end

handlers[1712] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1712, CIRCLE_ID, ctx.caster.id, 240, { td_spiritual=20, spirit_guard=true })
    return "A protective arcane ward settles over the spirit."
end

handlers[1716] = function(ctx)
    return "The target's lingering curse falters under focused arcane pressure."
end

handlers[1718] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1718, CIRCLE_ID, ctx.caster.id, 120, { as_bonus=15, ds=-5, vtulls_fury=true })
    return "A surge of savage arcane fury races through the target."
end

handlers[1720] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1720, CIRCLE_ID, ctx.caster.id, 300, { ds=25, td_elemental=10, td_spiritual=10, arcane_barrier=true })
    return "A solid pane of arcane force locks into place."
end

handlers[1750] = function(ctx)
    local target_id = ctx.target and ctx.target.id or ctx.caster.id
    ActiveBuffs.apply(target_id, 1750, CIRCLE_ID, ctx.caster.id, 300, { cs_all=15, td_mental=10, fashlonaes_gift=true })
    return "A brilliant wash of scholarly arcana settles over the target."
end

function Arc.on_cast(ctx)
    local fn = handlers[ctx.spell.spell_number]
    if fn then
        return fn(ctx)
    end
    return nil
end

return Arc
