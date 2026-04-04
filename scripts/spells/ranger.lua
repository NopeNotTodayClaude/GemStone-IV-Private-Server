------------------------------------------------------------------------
-- scripts/spells/ranger.lua
-- Ranger Base (Ran) spell circle — spells 601-650.
-- Circle id: 6 | Sphere: spiritual | CS/TD stat: wisdom
-- Available to: Ranger only
-- Source: gswiki.play.net/Ranger_Base
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local SpellFx     = require("globals/magic/spell_formulas")

local Ran = {}

local CIRCLE_ID  = 6
local LUA_SCRIPT = "spells/ranger"

local SPELLS = {
    [601] = { name="Natural Colors",    mnemonic="NATURALCOLORS",  spell_type="buff",    mana_cost=1,
              description="Provides camouflage in natural terrains. Group version via EVOKE at 11 ranks." },
    [602] = { name="Resist Elements",   mnemonic="RESISTELEMENTS", spell_type="buff",    mana_cost=2,
              description="Reduces damage from elemental attacks (fire, ice, lightning, acid)." },
    [603] = { name="Wild Entropy",      mnemonic="WILDENTROPY",    spell_type="warding", mana_cost=3,
              description="Warding attack channeling the chaotic power of nature at the target." },
    [604] = { name="Nature's Bounty",   mnemonic="NATURESBOUNTY",  spell_type="buff",    mana_cost=4,
              description="Increases skinning and foraging bonus. Duration and bonus scale with ranks." },
    [605] = { name="Barkskin",          mnemonic="BARKSKIN",       spell_type="buff",    mana_cost=5,
              description="Coats the target in natural bark-like armor providing DS and padding." },
    [606] = { name="Phoen's Strength",  mnemonic="PHOENSSTRENGTH", spell_type="buff",    mana_cost=6,
              description="Grants strength and AS bonus channeled from Phoen, deity of the sun." },
    [607] = { name="Sounds",            mnemonic="SOUNDS",         spell_type="warding", mana_cost=7,
              description="Warding attack using disorienting natural sounds. DS penalty scales with ranks (to rank 70)." },
    [608] = { name="Camouflage",        mnemonic="CAMOUFLAGE",     spell_type="buff",    mana_cost=8,
              description="Advanced camouflage in any terrain. Grants Stalking and Hiding bonus." },
    [609] = { name="Sun Burst",         mnemonic="SUNBURST",       spell_type="bolt",    mana_cost=9,
              description="element:fire. A burst of concentrated sunlight. Effective against undead and creatures of darkness." },
    [610] = { name="Tangleweed",        mnemonic="TANGLEWEED",     spell_type="maneuver",mana_cost=10,
              description="SMR maneuver causing natural vines and tangles to root the target." },
    [611] = { name="Moonbeam",          mnemonic="MOONBEAM",       spell_type="maneuver",mana_cost=11,
              description="SMR maneuver using moonlight to disorient and potentially blind the target." },
    [612] = { name="Breeze",            mnemonic="BREEZE",         spell_type="utility", mana_cost=12,
              description="Summons a natural breeze that aids movement, clears gas/fog, and cools the environment." },
    [613] = { name="Self Control",      mnemonic="SELFCONTROL",    spell_type="buff",    mana_cost=13,
              description="+1 DS per 2 ranks above 13. Also grants aiming bonus. 2-hour duration." },
    [614] = { name="Imbue",             mnemonic="IMBUE",          spell_type="utility", mana_cost=14,
              description="Imbues a natural object with energy, creating a temporary wand or rod. Rank increases tier." },
    [615] = { name="Call Swarm",        mnemonic="CALLSWARM",      spell_type="maneuver",mana_cost=15,
              description="Calls a swarm of insects to harry the target. Success rate improves with ranks." },
    [616] = { name="Spike Thorn",       mnemonic="SPIKETHORN",     spell_type="bolt",    mana_cost=16,
              description="element:impact. Launches a barrage of natural spikes. Damage improves with ranks." },
    [617] = { name="Sneaking",          mnemonic="SNEAKING",       spell_type="buff",    mana_cost=17,
              description="Enhances Stalking & Hiding. Rank scaling improves stealth-related activities." },
    [618] = { name="Mobility",          mnemonic="MOBILITY",       spell_type="buff",    mana_cost=18,
              description="Adds phantom Dodge and CM ranks per spell known above 618. Bonus to stealing." },
    [619] = { name="Mass Calm",         mnemonic="MASSCALM",       spell_type="warding", mana_cost=19,
              description="Room-wide warding attack that attempts to calm all hostile creatures." },
    [620] = { name="Resist Nature",     mnemonic="RESISTNATURE",   spell_type="buff",    mana_cost=20,
              description="Resists nature-based attacks and hazards. Duration scales with ranks." },
    [625] = { name="Nature's Touch",    mnemonic="NATURESTOUCH",   spell_type="buff",    mana_cost=25,
              description="Adds +DS and +TD (Spiritual) per 2 ranks above 25, max +12 TD at 49 ranks." },
    [630] = { name="Animal Companion",  mnemonic="ANIMALCOMPANION",spell_type="summon",  mana_cost=30,
              description="Summons an animal companion to assist in combat and exploration." },
    [635] = { name="Nature's Fury",     mnemonic="NATURESFURY",    spell_type="bolt",    mana_cost=35,
              description="element:impact. Unleashes the full fury of nature in a devastating strike." },
    [640] = { name="Wall of Thorns",    mnemonic="WALLOFTHORNS",   spell_type="buff",    mana_cost=40,
              description="Creates a wall of thorns around the target room, damaging creatures that move through." },
    [650] = { name="Assume Aspect",     mnemonic="ASSUMEASPECT",   spell_type="utility", mana_cost=50,
              description="Allows the ranger to assume the aspect of an animal, gaining its traits temporarily." },
}

function Ran.seed()
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

local handlers = {}

local function ward_dmg(ctx, base, mult, opts)
    opts = opts or {}
    opts.base = base
    opts.margin_mult = mult
    opts.stat = opts.stat or "wisdom"
    opts.skill = opts.skill or "spell_research"
    opts.mana_control = opts.mana_control or "spirit"
    return SpellFx.warding_damage(ctx, opts)
end

local function bolt_dmg(ctx, base, mult, opts)
    opts = opts or {}
    opts.base = base
    opts.margin_mult = mult
    opts.stat = opts.stat or "wisdom"
    opts.mana_control = opts.mana_control or "spirit"
    return SpellFx.bolt_damage(ctx, opts)
end

handlers[601] = function(ctx)
    local sh_bonus = 15 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 601, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { stalking_hiding_bonus=sh_bonus, natural_camouflage=true })
    return string.format("%s blends into the natural surroundings.", tname(ctx))
end

handlers[602] = function(ctx)
    ActiveBuffs.apply(tid(ctx), 602, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { fire_resist=20, ice_resist=20, lightning_resist=20, acid_resist=20 })
    return string.format("Natural resistance shields %s from the elements.", tname(ctx))
end

handlers[603] = function(ctx)
    if not ctx.result.hit then return end
    local dmg = ward_dmg(ctx, 8, 1.00, { lore="summoning", lore_scale=0.04, stat="avg_wis_int" })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("Wild entropy tears through %s for %d damage!", tname(ctx), dmg)
end

handlers[604] = function(ctx)
    local bonus = 10 + math.floor((ctx.circle_ranks or 1) / 4)
    ActiveBuffs.apply(tid(ctx), 604, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { skinning_bonus=bonus, foraging_bonus=bonus })
    return string.format("Nature's bounty enhances %s's foraging and skinning.", tname(ctx))
end

handlers[605] = function(ctx)
    local ds_bonus = 10 + math.floor((ctx.circle_ranks or 1) / 5)
    ActiveBuffs.apply(tid(ctx), 605, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=ds_bonus, natural_padding=true })
    return string.format("Bark-like skin spreads across %s (+%d DS).", tname(ctx), ds_bonus)
end

handlers[606] = function(ctx)
    ActiveBuffs.apply(tid(ctx), 606, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { strength_bonus=10, as_bonus=10 })
    return string.format("Phoen's strength flows through %s!", tname(ctx))
end

handlers[607] = function(ctx)
    if not ctx.result.hit then return end
    local ds_penalty = math.min(30, math.floor((ctx.circle_ranks or 1) / 2))
    local sdur = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 607, CIRCLE_ID, ctx.caster.id, sdur, { ds_penalty=ds_penalty, confused=true })
    return string.format("Disorienting sounds swirl around %s (-%d DS)!", tname(ctx), ds_penalty)
end

handlers[608] = function(ctx)
    local sh_bonus = 25 + math.floor((ctx.circle_ranks or 1) / 2)
    ActiveBuffs.apply(tid(ctx), 608, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { stalking_hiding_bonus=sh_bonus, camouflage=true })
    return string.format("%s is concealed in natural camouflage.", tname(ctx))
end

handlers[609] = function(ctx) -- Sun Burst bolt
    if not ctx.result.hit then return end
    local dmg = bolt_dmg(ctx, 10, 1.10, { lore="summoning", lore_scale=0.03, stat="wisdom", flat_bonus=2 })
    local is_undead = ctx.target and (ctx.target.is_undead == 1 or ctx.target.is_undead == true)
    if is_undead then dmg = math.floor(dmg * 1.5) end
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("A burst of sunlight strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[610] = function(ctx) -- Tangleweed
    if not ctx.result.hit then return end
    local tdur = 5 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 10)
    ActiveBuffs.apply(tid(ctx), 610, CIRCLE_ID, ctx.caster.id, tdur, { rooted=true, immobilized=true })
    return string.format("Vines and tangleweed erupt around %s, rooting them in place!", tname(ctx))
end

handlers[611] = function(ctx) -- Moonbeam
    if not ctx.result.hit then return end
    local summoning = (ctx.lore_ranks and ctx.lore_ranks.summoning) or 0
    local mdur = math.min(60, 6 + math.floor(summoning / 25))
    ActiveBuffs.apply(tid(ctx), 611, CIRCLE_ID, ctx.caster.id, mdur, { immobilized=true, rooted=true, moonbeam_bound=true })
    return string.format("A pale moonbeam locks %s in place, pinning them in shimmering light!", tname(ctx))
end

handlers[612] = function(ctx) -- Breeze — clear gas, aid movement
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE rooms SET has_gas=0, has_fog=0 WHERE id=?", { room_id })
    end
    ActiveBuffs.apply(ctx.caster.id, 612, CIRCLE_ID, ctx.caster.id, 60, { movement_bonus=true })
    return "A refreshing breeze clears the air and eases your movement."
end

handlers[613] = function(ctx) -- Self Control
    local ds_bonus = math.floor(math.max(0, (ctx.circle_ranks or 0) - 13) / 2)
    ActiveBuffs.apply(tid(ctx), 613, CIRCLE_ID, ctx.caster.id, 7200,
        { ds=ds_bonus, ranged_aim_bonus=10 })
    return string.format("Self control focuses the combat awareness of %s (+%d DS).", tname(ctx), ds_bonus)
end

handlers[614] = function(ctx) -- Imbue
    return "You imbue a natural object with ranger energy, creating a temporary magical item."
end

handlers[615] = function(ctx) -- Call Swarm
    if not ctx.result.hit then return end
    local sdur = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 615, CIRCLE_ID, ctx.caster.id, sdur,
        { swarmed=true, as_penalty=10, stunned_chance=true })
    return string.format("A swarm of insects descends upon %s, harrying their every move!", tname(ctx))
end

handlers[616] = function(ctx) -- Spike Thorn bolt
    if not ctx.result.hit then return end
    local dmg = bolt_dmg(ctx, 11, 1.00, { lore="summoning", lore_scale=0.04, flat_bonus=math.floor((ctx.circle_ranks or 1) / 3) })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("A volley of thorns pierces %s for %d damage!", tname(ctx), dmg)
end

handlers[617] = function(ctx) -- Sneaking
    local sh_bonus = 20 + math.floor((ctx.circle_ranks or 1) / 2)
    ActiveBuffs.apply(tid(ctx), 617, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { stalking_hiding_bonus=sh_bonus, move_silently=true })
    return string.format("%s moves with supernatural silence.", tname(ctx))
end

handlers[618] = function(ctx) -- Mobility
    local spells_above = math.max(0, (ctx.circle_ranks or 0) - 18)
    ActiveBuffs.apply(tid(ctx), 618, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { phantom_dodge=spells_above, phantom_cm=spells_above, steal_bonus=10 })
    return string.format("Mobility enhances %s's evasion and agility.", tname(ctx))
end

handlers[619] = function(ctx) -- Mass Calm
    local room_id = ctx.caster.current_room_id
    local calmed = 0
    if room_id then
        local creatures = DB.query("SELECT id FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        for _, c in ipairs(creatures) do
            ActiveBuffs.apply(c.id, 619, CIRCLE_ID, ctx.caster.id, 30, { calmed=true })
            calmed = calmed + 1
        end
    end
    return string.format("A wave of natural calm washes over the area, calming %d creatures.", calmed)
end

handlers[620] = function(ctx) -- Resist Nature
    ActiveBuffs.apply(tid(ctx), 620, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { nature_resist=true, environmental_resist=20 })
    return string.format("%s is resistant to the hazards of the natural world.", tname(ctx))
end

handlers[625] = function(ctx) -- Nature's Touch
    local bonus = math.min(12, math.floor(math.max(0, (ctx.circle_ranks or 0) - 25) / 2))
    ActiveBuffs.apply(tid(ctx), 625, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=bonus, td_spiritual=bonus })
    return string.format("Nature's touch grants %s +%d DS and +%d TD.", tname(ctx), bonus, bonus)
end

handlers[630] = function(ctx) -- Animal Companion
    local transformation = (ctx.lore_ranks and ctx.lore_ranks.transformation) or 0
    local duration = 120 + ((ctx.circle_ranks or 1) * 12) + transformation * 2
    local companion_level = math.max(1, math.floor((ctx.circle_ranks or 1) / 5) + math.floor(transformation / 30))
    ActiveBuffs.apply(ctx.caster.id, 630, CIRCLE_ID, ctx.caster.id, duration, {
        animal_companion=true,
        companion_level=companion_level,
        perception_bonus=10 + math.floor(companion_level / 2),
        dodge_bonus=5 + math.floor(companion_level / 2),
    })
    return string.format("A wary animal companion pads into view and remains by your side for %d seconds.", duration)
end

handlers[635] = function(ctx) -- Nature's Fury bolt
    if not ctx.result.hit then return end
    local dmg = bolt_dmg(ctx, 18, 1.45, { lore="summoning", lore_scale=0.05, stat="avg_wis_int", flat_bonus=4 })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("The fury of nature UNLEASHES upon %s for %d damage!", tname(ctx), dmg)
end

handlers[640] = function(ctx) -- Wall of Thorns
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute([[
            UPDATE rooms SET thorn_wall=1, thorn_wall_expires=DATE_ADD(NOW(), INTERVAL ? SECOND)
            WHERE id=?
        ]], { dur(ctx), room_id })
    end
    return "A wall of thorns erupts around the area, threatening all who try to pass!"
end

handlers[650] = function(ctx) -- Assume Aspect
    local aspects = {"wolf","hawk","bear","stag","lynx"}
    local aspect = aspects[math.random(1,#aspects)]
    ActiveBuffs.apply(ctx.caster.id, 650, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { assumed_aspect=aspect, aspect_as_bonus=15, aspect_ds_bonus=10 })
    return string.format("You assume the aspect of a %s, gaining its natural power!", aspect)
end

function Ran.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Ran] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Ran
