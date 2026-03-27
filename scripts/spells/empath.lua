------------------------------------------------------------------------
-- scripts/spells/empath.lua
-- Empath Base (Emp) spell circle — spells 1101-1150.
-- Circle id: 10 | Sphere: hybrid_sm (spiritual/mental) | CS/TD stat: wisdom
-- Available to: Empath only
-- Source: gswiki.play.net/Empath_Base
--
-- Healing spells: heal more serious wounds after +5 ranks (e.g. 1102
-- obtainable at rank 2, heals major wounds at rank 7).
-- Healing RT reduces with additional Emp Base training (capped at level).
-- Many spells require no physical gesture — can cast with missing limbs.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local Emp = {}

local CIRCLE_ID  = 10
local LUA_SCRIPT = "spells/empath"

local SPELLS = {
    [1101] = { name="Harm/Heal",          mnemonic="HEAL",            spell_type="healing", mana_cost=4,
               description="Dual-purpose spell. CAST = Harm (attack on hostile). CHANNEL = Heal (restore HP)." },
    [1102] = { name="Limb Repair",        mnemonic="LIMBREPAIR",      spell_type="healing", mana_cost=6,
               description="Heals limb wounds. Heals more serious wounds after 7 ranks." },
    [1103] = { name="System Repair",      mnemonic="SYSTEMREPAIR",    spell_type="healing", mana_cost=8,
               description="Heals torso and system wounds. More serious wounds healed after 8 ranks." },
    [1104] = { name="Head Repair",        mnemonic="HEADREPAIR",      spell_type="healing", mana_cost=9,
               description="Heals head wounds. More serious wounds healed after 9 ranks." },
    [1105] = { name="Organ Repair",       mnemonic="ORGANREPAIR",     spell_type="healing", mana_cost=10,
               description="Heals organ damage. More serious organ damage healed after 10 ranks." },
    [1106] = { name="Bone Shatter",       mnemonic="BONESHATTER",     spell_type="warding", mana_cost=11,
               description="Warding attack that shatters bones, dealing internal damage and crippling limbs." },
    [1107] = { name="Adrenal Surge",      mnemonic="ADRENALSURGE",    spell_type="utility", mana_cost=12,
               description="Provides a temporary surge of adrenaline, reducing roundtimes briefly." },
    [1108] = { name="Empathy",            mnemonic="EMPATHY",         spell_type="warding", mana_cost=13,
               description="Warding attack linking caster and target empathically, redirecting some damage." },
    [1109] = { name="Empathic Focus",     mnemonic="EMPATHICFOCUS",   spell_type="buff",    mana_cost=14,
               description="+DS per 2 ranks above 9, capped at level. The empath's key defensive buff." },
    [1110] = { name="Empathic Assault",   mnemonic="EMPATHICASSAULT", spell_type="warding", mana_cost=15,
               description="Warding attack using empathic force, sharing the empath's pain with the target." },
    [1111] = { name="Limb Scar Repair",   mnemonic="LIMBSCARREPAIR",  spell_type="healing", mana_cost=11,
               description="Heals limb scars. Heals more serious scars after 15 ranks." },
    [1112] = { name="System Scar Repair", mnemonic="SYSTEMSCARREPAIR",spell_type="healing", mana_cost=12,
               description="Heals system/torso scars." },
    [1113] = { name="Head Scar Repair",   mnemonic="HEADSCARREPAIR",  spell_type="healing", mana_cost=13,
               description="Heals head scars." },
    [1114] = { name="Organ Scar Repair",  mnemonic="ORGANSCARREPAIR", spell_type="healing", mana_cost=14,
               description="Heals organ scars." },
    [1115] = { name="Wither",             mnemonic="WITHER",          spell_type="warding", mana_cost=15,
               description="Warding attack that withers the target's physical attributes, reducing their effectiveness." },
    [1116] = { name="Rapid Healing",      mnemonic="RAPIDHEALING",    spell_type="healing", mana_cost=16,
               description="Rapidly heals a significant amount of HP from a single target." },
    [1117] = { name="Empathic Link",      mnemonic="EMPATHICLINK",    spell_type="warding", mana_cost=17,
               description="Warding attack creating a link through which damage to the empath injures the target." },
    [1118] = { name="Herb Production",    mnemonic="HERBPRODUCTION",  spell_type="utility", mana_cost=18,
               description="Creates healing herbs from ambient spiritual energy. Type depends on rank." },
    [1119] = { name="Strength of Will",   mnemonic="STRENGTHOFWILL",  spell_type="buff",    mana_cost=19,
               description="+DS and +TD per 3 ranks above 19, max +25 at 58 ranks. Powerful defensive buff." },
    [1120] = { name="Sympathy",           mnemonic="SYMPATHY",        spell_type="warding", mana_cost=20,
               description="Warding attack creating sympathetic suffering — what the target feels, the empath shares and amplifies back." },
    [1125] = { name="Troll's Blood",      mnemonic="TROLLSBLOOD",     spell_type="healing", mana_cost=25,
               description="Grants rapid HP regeneration per pulse, like a troll's healing factor." },
    [1130] = { name="Intensity",          mnemonic="INTENSITY",       spell_type="buff",    mana_cost=30,
               description="+AS and +DS per 2 ranks above 30, capped at level. Offensive and defensive." },
    [1135] = { name="Bloodsmith",         mnemonic="BLOODSMITH",      spell_type="utility", mana_cost=35,
               description="Advanced blood empathy allowing wound transfer with greater efficiency." },
    [1140] = { name="Solace",             mnemonic="SOLACE",          spell_type="healing", mana_cost=40,
               description="Provides deep solace healing, restoring both HP and addressing trauma." },
    [1150] = { name="Regeneration",       mnemonic="REGENERATION",    spell_type="healing", mana_cost=50,
               description="Grants full regeneration, restoring HP and healing wounds over time." },
}

function Emp.seed()
    for num, sp in pairs(SPELLS) do
        DB.execute([[
            INSERT INTO spells (spell_number,name,mnemonic,circle_id,spell_type,mana_cost,description,lua_script)
            VALUES (?,?,?,?,?,?,?,?)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name),mnemonic=VALUES(mnemonic),spell_type=VALUES(spell_type),
                mana_cost=VALUES(mana_cost),description=VALUES(description),lua_script=VALUES(lua_script)
        ]], { num, sp.name, sp.mnemonic, CIRCLE_ID, sp.spell_type, sp.mana_cost, sp.description, LUA_SCRIPT })
    end
end

local function tid(ctx) return ctx.target and ctx.target.id or ctx.caster.id end
local function tname(ctx)
    if ctx.target and ctx.target.id ~= ctx.caster.id then return ctx.target.name or "your target" end
    return "you"
end
local function dur(ctx, ov) return ov or (60 * math.max(1, ctx.circle_ranks or 1)) end

-- Healing rank thresholds (each healing spell adds +5 more healing per tier)
local function heal_amount(ctx, base_ranks)
    local ranks  = ctx.circle_ranks or 1
    local tier   = math.floor(math.max(0, ranks - base_ranks) / 5)
    local base   = 20 + tier * 15
    return base
end

local handlers = {}

handlers[1101] = function(ctx) -- Harm/Heal
    local verb = ctx.verb or "cast"
    if verb == "channel" then
        -- Heal mode
        local hp = heal_amount(ctx, 1)
        local new_hp = math.min(ctx.target.health_max or 999,
            (ctx.target.health_current or 0) + hp)
        DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
        return string.format("Empathic healing flows into %s, restoring %d health.", tname(ctx), hp)
    else
        -- Harm mode (warding attack)
        if not ctx.result.hit then return end
        local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
        local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
        DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
        return string.format("Empathic harm sears through %s for %d damage!", tname(ctx), dmg)
    end
end

local function make_healer(ranks, wtype)
    return function(ctx)
        local hp = heal_amount(ctx, ranks)
        local new_hp = math.min(ctx.target.health_max or 999,
            (ctx.target.health_current or 0) + hp)
        DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
        return string.format("Empathic %s repair restores %d health to %s.", wtype, hp, tname(ctx))
    end
end

handlers[1102] = make_healer(2,  "limb")
handlers[1103] = make_healer(3,  "system")
handlers[1104] = make_healer(4,  "head")
handlers[1105] = make_healer(5,  "organ")
handlers[1111] = make_healer(11, "limb scar")
handlers[1112] = make_healer(12, "system scar")
handlers[1113] = make_healer(13, "head scar")
handlers[1114] = make_healer(14, "organ scar")

handlers[1106] = function(ctx) -- Bone Shatter
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100) * 2)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    local limbs = {"right_arm","left_arm","right_leg","left_leg"}
    ActiveBuffs.apply(tid(ctx), 1106, CIRCLE_ID, ctx.caster.id, 15,
        { broken_limb=limbs[math.random(1,4)], as_penalty=15 })
    return string.format("Bones SHATTER within %s for %d damage!", tname(ctx), dmg)
end

handlers[1107] = function(ctx) -- Adrenal Surge
    ActiveBuffs.apply(tid(ctx), 1107, CIRCLE_ID, ctx.caster.id, 30, { rt_reduction=2, adrenal=true })
    return string.format("%s surges with adrenaline, acting faster!", tname(ctx))
end

handlers[1108] = function(ctx) -- Empathy
    if not ctx.result.hit then return end
    local redirect = math.floor(math.max(0, (ctx.result.total or 101) - 100) / 2)
    ActiveBuffs.apply(tid(ctx), 1108, CIRCLE_ID, ctx.caster.id, 15, { empathy_linked=true, damage_redirect=redirect })
    return string.format("An empathic link forms between you and %s.", tname(ctx))
end

handlers[1109] = function(ctx) -- Empathic Focus
    local ds_bonus = math.min(ctx.caster.level or 1,
        math.floor(math.max(0, (ctx.circle_ranks or 0) - 9) / 2))
    ActiveBuffs.apply(tid(ctx), 1109, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("Empathic focus sharpens %s's defenses (+%d DS).", tname(ctx), ds_bonus)
end

handlers[1110] = function(ctx) -- Empathic Assault
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Empathic force assaults %s for %d damage!", tname(ctx), dmg)
end

handlers[1115] = function(ctx) -- Wither
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 1115, CIRCLE_ID, ctx.caster.id, 20,
        { withered=true, as_penalty=20, strength_penalty=10 })
    return string.format("%s withers under empathic assault!", tname(ctx))
end

handlers[1116] = function(ctx) -- Rapid Healing
    local hp = 30 + (ctx.circle_ranks or 1) * 3
    local new_hp = math.min(ctx.target.health_max or 999, (ctx.target.health_current or 0) + hp)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Rapid healing floods through %s, restoring %d health!", tname(ctx), hp)
end

handlers[1117] = function(ctx) -- Empathic Link
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 1117, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { empathic_link=true, reverse_damage_pct=30 })
    return string.format("An empathic link binds %s — your pain becomes theirs!", tname(ctx))
end

handlers[1118] = function(ctx) -- Herb Production
    local ranks = ctx.circle_ranks or 1
    local herb_id = ranks >= 35 and 607 or ranks >= 20 and 603 or 601 -- haphip/torban/acantha
    DB.execute([[
        INSERT INTO character_inventory (character_id, item_id, slot, quantity)
        VALUES (?,?, NULL, 1)
    ]], { ctx.caster.id, herb_id })
    return "Empathic energy condenses into a healing herb."
end

handlers[1119] = function(ctx) -- Strength of Will
    local bonus = math.min(25, math.floor(math.max(0, (ctx.circle_ranks or 0) - 19) / 3))
    ActiveBuffs.apply(tid(ctx), 1119, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=bonus, td_spiritual=bonus })
    return string.format("Strength of will fortifies %s (+%d DS/TD).", tname(ctx), bonus)
end

handlers[1120] = function(ctx) -- Sympathy
    if not ctx.result.hit then return end
    local sdur = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 1120, CIRCLE_ID, ctx.caster.id, sdur, { sympathy=true, pain_echo=true })
    return string.format("Sympathy links you and %s — suffering is shared and amplified!", tname(ctx))
end

handlers[1125] = function(ctx) -- Troll's Blood
    local regen = 5 + math.floor((ctx.circle_ranks or 1) / 5)
    ActiveBuffs.apply(tid(ctx), 1125, CIRCLE_ID, ctx.caster.id, dur(ctx), { regen_bonus=regen })
    return string.format("Troll's blood courses through %s, granting rapid regeneration!", tname(ctx))
end

handlers[1130] = function(ctx) -- Intensity
    local bonus = math.min(ctx.caster.level or 1,
        math.floor(math.max(0, (ctx.circle_ranks or 0) - 30) / 2))
    ActiveBuffs.apply(tid(ctx), 1130, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=bonus, ds=bonus })
    return string.format("Intensity blazes within %s (+%d AS/DS).", tname(ctx), bonus)
end

handlers[1135] = function(ctx) -- Bloodsmith
    return "Advanced bloodsmithing allows you to transfer wounds with greater efficiency."
end

handlers[1140] = function(ctx) -- Solace
    local hp = 50 + (ctx.circle_ranks or 1) * 2
    local new_hp = math.min(ctx.target.health_max or 999, (ctx.target.health_current or 0) + hp)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Deep solace washes over %s, restoring %d health.", tname(ctx), hp)
end

handlers[1150] = function(ctx) -- Regeneration
    local regen = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 1150, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { regen_bonus=regen, wound_regen=true })
    return string.format("Full regeneration suffuses %s, healing wounds over time.", tname(ctx))
end

function Emp.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Emp] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Emp
