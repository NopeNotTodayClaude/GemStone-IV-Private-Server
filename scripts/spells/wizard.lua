------------------------------------------------------------------------
-- scripts/spells/wizard.lua
-- Wizard Base (Wiz) spell circle — spells 901-950.
-- Circle id: 8 | Sphere: elemental | CS/TD stat: aura
-- Available to: Wizard only
-- Source: gswiki.play.net/Wizard_Base
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local ItemMagic   = require("globals/magic/item_magic")

local Wiz = {}

local CIRCLE_ID  = 8
local LUA_SCRIPT = "spells/wizard"

local SPELLS = {
    [901] = { name="Minor Shock",          mnemonic="MINORSHOCK",       spell_type="bolt",    mana_cost=1,
              description="element:lightning. Small bolt of electrical energy. The wizard's starter attack." },
    [902] = { name="Minor Elemental Edge", mnemonic="MINORELEEDGE",     spell_type="buff",    mana_cost=2,
              description="Imbues the caster's weapon with minor elemental energy for added damage." },
    [903] = { name="Minor Water",          mnemonic="MINORWATER",       spell_type="bolt",    mana_cost=3,
              description="element:ice. A bolt of frigid water. Effective against fire-based creatures." },
    [904] = { name="Minor Acid",           mnemonic="MINORACID",        spell_type="bolt",    mana_cost=4,
              description="element:acid. A spray of acidic water corroding armor and flesh." },
    [905] = { name="Prismatic Guard",      mnemonic="PRISMATICGUARD",   spell_type="buff",    mana_cost=5,
              description="Adds +10 DS (+1 per 4 ranks above 5). 2-hour duration." },
    [906] = { name="Minor Fire",           mnemonic="MINORFIRE",        spell_type="bolt",    mana_cost=6,
              description="element:fire. A small but directed bolt of flame." },
    [907] = { name="Major Cold",           mnemonic="MAJORCOLD",        spell_type="bolt",    mana_cost=7,
              description="element:ice. A powerful blast of freezing cold." },
    [908] = { name="Major Fire",           mnemonic="MAJORFIRE",        spell_type="bolt",    mana_cost=8,
              description="element:fire. A powerful fireball that deals significant damage." },
    [909] = { name="Tremors",              mnemonic="TREMORS",          spell_type="maneuver",mana_cost=9,
              description="SMR maneuver shaking the earth to unbalance and knock down all in the room." },
    [910] = { name="Major Shock",          mnemonic="MAJORSHOCK",       spell_type="bolt",    mana_cost=10,
              description="element:lightning. A powerful lightning bolt. Core wizard attack spell." },
    [911] = { name="Mass Blur",            mnemonic="MASSBLUR",         spell_type="buff",    mana_cost=11,
              description="Blurs all allies in the room, granting a DS bonus to the entire group." },
    [912] = { name="Call Wind",            mnemonic="CALLWIND",         spell_type="maneuver",mana_cost=12,
              description="Calls wind that can knock foes down and affect projectiles. Success strongly rank-based." },
    [913] = { name="Melgorehn's Aura",     mnemonic="MELGOREHN",        spell_type="buff",    mana_cost=13,
              description="+DS per rank above 13, +TD per 3 ranks above 13. The wizard's premier self-defense buff." },
    [914] = { name="Sandstorm",            mnemonic="SANDSTORM",        spell_type="maneuver",mana_cost=14,
              description="SMR maneuver unleashing a blinding, cutting sandstorm against all in the room." },
    [915] = { name="Weapon Fire",          mnemonic="WEAPONFIRE",       spell_type="buff",    mana_cost=15,
              description="Sets the target's weapon ablaze with elemental fire, adding fire flares." },
    [916] = { name="Invisibility",         mnemonic="INVISIBILITY",     spell_type="utility", mana_cost=16,
              description="Renders the caster invisible. Duration +30 sec per rank (substantial at high ranks)." },
    [917] = { name="Earthen Fury",         mnemonic="EARTHENFURY",      spell_type="bolt",    mana_cost=17,
              description="element:impact. Calls stone and earth against the target. Attack prowess scales with rank." },
    [918] = { name="Duplicate",            mnemonic="DUPLICATE",        spell_type="utility", mana_cost=18,
              description="Creates a duplicate of a magical item, making an imperfect copy." },
    [919] = { name="Wizard's Shield",      mnemonic="WIZARDSHIELD",     spell_type="buff",    mana_cost=19,
              description="A powerful elemental shield granting significant DS and TD." },
    [920] = { name="Call Familiar",        mnemonic="CALLFAMILIAR",     spell_type="summon",  mana_cost=20,
              description="Summons the wizard's familiar, a magical companion that aids in many ways." },
    [925] = { name="Enchant",              mnemonic="ENCHANT",          spell_type="utility", mana_cost=25,
              description="Enchants a weapon, increasing its magical bonus. Success improves with ranks." },
    [930] = { name="Familiar Gate",        mnemonic="FAMILIARGATE",     spell_type="utility", mana_cost=30,
              description="Opens a gate between the wizard and their familiar's location. Rank scales gate size." },
    [950] = { name="Core Tap",             mnemonic="CORETAP",          spell_type="utility", mana_cost=50,
              description="Taps directly into the mana core of the wizard's being for a massive mana surge." },
}

function Wiz.seed()
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

-- Generic bolt handler reused by all damage bolts
local function bolt_dmg(ctx, min_dmg, mult)
    if not ctx.result.hit then return end
    local dmg = math.max(min_dmg, math.floor((ctx.result.total or 101) - 100) * (mult or 1))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return dmg
end

local handlers = {}

handlers[901] = function(ctx)
    local dmg = bolt_dmg(ctx, 1, 1)
    if dmg then return string.format("A minor shock crackles through %s for %d damage!", tname(ctx), dmg) end
end
handlers[902] = function(ctx)
    local swings = 10 + (ctx.circle_ranks or 1) * 2
    DB.execute([[
        UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.elemental_edge',1,'$.edge_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, ctx.caster.id })
    return string.format("Minor elemental energy crackles along your weapon (%d swings).", swings)
end
handlers[903] = function(ctx)
    local dmg = bolt_dmg(ctx, 2, 1)
    if dmg then return string.format("A bolt of frigid water strikes %s for %d damage!", tname(ctx), dmg) end
end
handlers[904] = function(ctx)
    local dmg = bolt_dmg(ctx, 2, 1)
    if dmg then
        -- Acid also corrodes armor (small DS reduction)
        ActiveBuffs.apply(tid(ctx), 9910, nil, ctx.caster.id, 30, { ds_penalty=5, acid_corroded=true })
        return string.format("Acid sprays across %s for %d damage, corroding their armor!", tname(ctx), dmg)
    end
end
handlers[905] = function(ctx)
    local ds_bonus = 10 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 5) / 4)
    ActiveBuffs.apply(tid(ctx), 905, CIRCLE_ID, ctx.caster.id, 7200, { ds=ds_bonus })
    return string.format("A prismatic guard shimmers around %s (+%d DS).", tname(ctx), ds_bonus)
end
handlers[906] = function(ctx)
    local dmg = bolt_dmg(ctx, 3, 1)
    if dmg then return string.format("A bolt of fire ignites %s for %d damage!", tname(ctx), dmg) end
end
handlers[907] = function(ctx)
    local dmg = bolt_dmg(ctx, 5, 1)
    if dmg then
        ActiveBuffs.apply(tid(ctx), 9911, nil, ctx.caster.id, 5, { slowed=true })
        return string.format("Major cold BLASTS %s for %d damage and slows them!", tname(ctx), dmg)
    end
end
handlers[908] = function(ctx)
    local dmg = bolt_dmg(ctx, 5, 1)
    if dmg then
        ActiveBuffs.apply(tid(ctx), 9912, nil, ctx.caster.id, 5, { burning=true, burn_dmg=3 })
        return string.format("A fireball engulfs %s for %d damage and sets them ablaze!", tname(ctx), dmg)
    end
end
handlers[909] = function(ctx) -- Tremors
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE characters SET position='prone' WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
    end
    return "The earth SHAKES violently, knocking everyone to the ground!"
end
handlers[910] = function(ctx)
    local dmg = bolt_dmg(ctx, 8, 1)
    if dmg then return string.format("A major shock CRACKLES through %s for %d damage!", tname(ctx), dmg) end
end
handlers[911] = function(ctx) -- Mass Blur — group DS
    local room_id = ctx.caster.current_room_id
    if room_id then
        local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
        for _, a in ipairs(allies) do
            ActiveBuffs.apply(a.id, 911, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=15 })
        end
        return string.format("A blurring aura spreads over %d characters!", #allies)
    end
end
handlers[912] = function(ctx) -- Call Wind
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE characters SET position='prone' WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
    end
    return "Howling winds tear through the area, knocking all foes to the ground!"
end
handlers[913] = function(ctx) -- Melgorehn's Aura
    local ds_bonus = math.max(0, (ctx.circle_ranks or 0) - 13)
    local td_bonus = math.floor(math.max(0, (ctx.circle_ranks or 0) - 13) / 3)
    ActiveBuffs.apply(tid(ctx), 913, CIRCLE_ID, ctx.caster.id, 7200,
        { ds=ds_bonus, td_elemental=td_bonus })
    return string.format("Melgorehn's aura surrounds %s (+%d DS, +%d TD).", tname(ctx), ds_bonus, td_bonus)
end
handlers[914] = function(ctx) -- Sandstorm
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    if room_id then
        local targets = DB.query("SELECT id FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        for _, t in ipairs(targets) do
            ActiveBuffs.apply(t.id, 914, CIRCLE_ID, ctx.caster.id, 10, { blinded=true, as_penalty=20 })
        end
        return string.format("A blinding sandstorm rips through the area, blinding %d targets!", #targets)
    end
end
handlers[915] = function(ctx) -- Weapon Fire
    local swings = 20 + (ctx.circle_ranks or 1) * 2
    DB.execute([[
        UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.fire_flares',1,'$.fire_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, tid(ctx) })
    return string.format("The weapon of %s bursts into elemental flame (%d swings)!", tname(ctx), swings)
end
handlers[916] = function(ctx) -- Invisibility
    local d = 60 + (ctx.circle_ranks or 1) * 30
    ActiveBuffs.apply(ctx.caster.id, 916, CIRCLE_ID, ctx.caster.id, d, { invisible=true })
    return string.format("You fade from sight, invisible for %d seconds.", d)
end
handlers[917] = function(ctx) -- Earthen Fury
    local dmg = bolt_dmg(ctx, 10, 1)
    if dmg then return string.format("Stone and earth SLAM into %s for %d damage!", tname(ctx), dmg) end
end
handlers[918] = function(ctx)
    local held = ItemMagic.get_held_item(ctx.caster.id)
    if not held then
        return "You must hold the magical item you wish to duplicate."
    end
    local extra = held.extra or {}
    local is_magical = (tonumber(extra.charges) or 0) > 0
        or tonumber(extra.spell_number)
        or tonumber(extra.enchant_bonus)
        or tonumber(held.enchant_bonus or 0) > 0
    if not is_magical then
        return string.format("Your %s does not hold enough structured magic to duplicate.", held.short_name or held.name or "item")
    end
    local copy_extra = {}
    for key, value in pairs(extra) do
        copy_extra[key] = value
    end
    if tonumber(copy_extra.charges) and tonumber(copy_extra.charges) > 1 then
        copy_extra.charges = math.max(1, math.floor(copy_extra.charges / 2))
    end
    if tonumber(copy_extra.enchant_bonus) and tonumber(copy_extra.enchant_bonus) > 0 then
        copy_extra.enchant_bonus = math.max(0, copy_extra.enchant_bonus - 1)
    end
    ItemMagic.create_item(ctx.caster.id, held.item_id, copy_extra, nil)
    return string.format("A hazy duplicate of your %s peels away from the original.", held.short_name or held.name or "item")
end
handlers[919] = function(ctx) -- Wizard's Shield
    ActiveBuffs.apply(tid(ctx), 919, CIRCLE_ID, ctx.caster.id, 7200,
        { ds=25, td_elemental=15 })
    return string.format("A wizard's shield of pure elemental force surrounds %s.", tname(ctx))
end
handlers[920] = function(ctx)
    local duration = 300 + ((ctx.circle_ranks or 1) * 12)
    ActiveBuffs.apply(ctx.caster.id, 920, CIRCLE_ID, ctx.caster.id, duration, {
        familiar=true,
        see_hidden=true,
        perception_bonus=10 + math.floor((ctx.circle_ranks or 1) / 4),
        familiar_room_id=ctx.caster.current_room_id,
    })
    return "Your familiar materializes, watchful and ready to scout."
end
handlers[925] = function(ctx)
    local held = ItemMagic.get_held_item(ctx.caster.id)
    if not held then
        return "You must hold the item you wish to enchant."
    end
    if held.item_type ~= "weapon" and held.item_type ~= "shield" then
        return "This first enchantment pass only supports held weapons and shields."
    end
    local extra = held.extra or {}
    local current = tonumber(extra.enchant_bonus) or tonumber(held.enchant_bonus) or 0
    local cap = math.min(25, 4 + math.floor((ctx.circle_ranks or 1) / 6))
    if current >= cap then
        return string.format("Your %s is already at the limit of enchantment you can currently sustain.", held.short_name or held.name or "item")
    end
    extra.enchant_bonus = current + 1
    extra.enchant_spell = 925
    ItemMagic.save_extra(held.inv_id, extra)
    return string.format("Elemental runes sink into your %s, raising its enchant to +%d.", held.short_name or held.name or "item", current + 1)
end
handlers[930] = function(ctx)
    local buff = DB.queryOne([[
        SELECT effects_json
        FROM character_active_buffs
        WHERE character_id = ? AND spell_number = 920
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at DESC
        LIMIT 1
    ]], { ctx.caster.id })
    if not buff then
        return "You have no active familiar bond to open a gate through."
    end
    ActiveBuffs.apply(ctx.caster.id, 930, CIRCLE_ID, ctx.caster.id, 60, {
        familiar_gate=true,
        phased=true,
        rt_reduction=1,
    })
    return "A shimmering gate opens through your familiar bond, thinning the world around you."
end
handlers[950] = function(ctx) -- Core Tap
    local mana_gain = math.min(50, (ctx.circle_ranks or 1) * 2)
    local new_mana = math.min(ctx.caster.mana_max or 999,
        (ctx.caster.mana_current or 0) + mana_gain)
    DB.execute("UPDATE characters SET mana_current=? WHERE id=?", { new_mana, ctx.caster.id })
    return string.format("You tap your elemental core, surging %d mana!", mana_gain)
end

function Wiz.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Wiz] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Wiz
