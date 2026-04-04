------------------------------------------------------------------------
-- scripts/spells/sorcerer.lua
-- Sorcerer Base (Sor) spell circle — spells 701-740.
-- Circle id: 7 | Sphere: hybrid_es (elemental/spiritual) | CS/TD stat: avg_aura_wis
-- Available to: Sorcerer only
-- Source: gswiki.play.net/Sorcerer_Base
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local ItemMagic   = require("globals/magic/item_magic")
local SpellFx     = require("globals/magic/spell_formulas")

local Sor = {}

local CIRCLE_ID  = 7
local LUA_SCRIPT = "spells/sorcerer"

local SPELLS = {
    [701] = { name="Blood Burst",         mnemonic="BLOODBURST",      spell_type="warding", mana_cost=1,
              description="Warding attack that causes internal hemorrhaging. Ignores most armor protection." },
    [702] = { name="Mana Disruption",     mnemonic="MANADISRUPTION",  spell_type="warding", mana_cost=2,
              description="Warding attack that disrupts the target's mana, draining it and causing nerve damage." },
    [703] = { name="Corrupt Essence",     mnemonic="CORRUPTESSENCE",  spell_type="warding", mana_cost=3,
              description="Warding attack corrupting the target's life essence, dealing spiritual damage." },
    [704] = { name="Phase",               mnemonic="PHASE",           spell_type="utility", mana_cost=4,
              description="Briefly phases the caster out of normal space, allowing them to pass through some obstacles." },
    [705] = { name="Disintegrate",        mnemonic="DISINTEGRATE",    spell_type="bolt",    mana_cost=5,
              description="element:void. Attempts to disintegrate the target utterly." },
    [706] = { name="Tenebrous Tether",    mnemonic="TENEBROUSTETHER", spell_type="warding", mana_cost=6,
              description="Warding attack that anchors the target in place with shadowy tendrils." },
    [707] = { name="Eye Spy",             mnemonic="EYESPY",          spell_type="utility", mana_cost=7,
              description="Creates a remote viewing eye allowing the sorcerer to see a distant location." },
    [708] = { name="Limb Disruption",     mnemonic="LIMBDISRUPTION",  spell_type="warding", mana_cost=8,
              description="Warding attack targeting a specific limb to disrupt or damage it." },
    [709] = { name="Grasp of the Grave",  mnemonic="GRASPOFTHEGRAVE", spell_type="maneuver",mana_cost=9,
              description="SMR maneuver using undead hands from below to grip and hold the target." },
    [710] = { name="Energy Maelstrom",    mnemonic="ENERGYMAELSTROM", spell_type="bolt",    mana_cost=10,
              description="element:void. A maelstrom of pure energy that damages all in a radius." },
    [711] = { name="Pain",                mnemonic="PAIN",            spell_type="warding", mana_cost=11,
              description="Warding attack that inflicts excruciating pain, heavily penalizing all combat activity." },
    [712] = { name="Cloak of Shadows",    mnemonic="CLOAKOFSHADOWS",  spell_type="buff",    mana_cost=12,
              description="+DS per rank above 12 (capped at level). +TD per 10 ranks. Scales with training." },
    [713] = { name="Balefire",            mnemonic="BALEFIRE",        spell_type="bolt",    mana_cost=13,
              description="element:fire. Dark spiritual fire that burns through magical and physical defenses." },
    [714] = { name="Scroll Infusion",     mnemonic="SCROLLINFUSION",  spell_type="utility", mana_cost=14,
              description="Infuses a scroll with the current prepared spell, allowing later use." },
    [715] = { name="Curse",               mnemonic="CURSE",           spell_type="warding", mana_cost=15,
              description="Warding attack that curses the target, causing ongoing ill fortune and penalties." },
    [716] = { name="Pestilence",          mnemonic="PESTILENCE",      spell_type="warding", mana_cost=16,
              description="Warding attack unleashing a magical plague on the target, with a chance to spread." },
    [717] = { name="Evil Eye",            mnemonic="EVILEYE",         spell_type="warding", mana_cost=17,
              description="Warding attack using the sorcerer's malefic gaze. Multiple negative effects on success." },
    [718] = { name="Torment",             mnemonic="TORMENT",         spell_type="warding", mana_cost=18,
              description="Sustained warding attack inflicting ongoing torment damage each pulse." },
    [719] = { name="Dark Catalyst",       mnemonic="DARKCATALYST",    spell_type="warding", mana_cost=19,
              description="Warding attack that catalyzes dark energies within the target for massive damage." },
    [720] = { name="Implosion",           mnemonic="IMPLOSION",       spell_type="bolt",    mana_cost=20,
              description="element:void. Forces the target to implode inward. Extremely powerful. Rank scales success." },
    [725] = { name="Minor Summoning",     mnemonic="MINORSUMMONING",  spell_type="summon",  mana_cost=25,
              description="Summons a minor demonic entity to assist the sorcerer. Duration +20 sec per rank." },
    [730] = { name="Animate Dead",        mnemonic="ANIMATEDEAD",     spell_type="utility", mana_cost=30,
              description="Animates a corpse as an undead servant to fight for the sorcerer." },
    [735] = { name="Ensorcell",           mnemonic="ENSORCELL",       spell_type="utility", mana_cost=35,
              description="Permanently ensorcells a weapon, making it more effective and receptive to flares." },
    [740] = { name="Planar Shift",        mnemonic="PLANARSHIFT",     spell_type="utility", mana_cost=40,
              description="Shifts the sorcerer or a target to a different plane of existence temporarily." },
}

function Sor.seed()
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
local function sor_dmg(ctx, base, mult, opts)
    if not ctx.result.hit then return end
    opts = opts or {}
    local dmg = SpellFx.warding_damage(ctx, {
        base = base,
        min = opts.min or base,
        margin_mult = mult or 1.0,
        stat = "avg_aura_wis",
        skill = "spell_research",
        lore = opts.lore or "necromancy",
        mana_control = "spirit",
        level_scale = opts.level_scale or 0.40,
        circle_scale = opts.circle_scale or 0.45,
        stat_scale = opts.stat_scale or 0.35,
        skill_scale = opts.skill_scale or 0.10,
        lore_scale = opts.lore_scale or 0.06,
        flat_bonus = opts.flat_bonus or 0,
    })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return dmg
end

local handlers = {}

handlers[701] = function(ctx) -- Blood Burst
    local dmg = sor_dmg(ctx, 12, 1.40, { lore = "necromancy", min = 12 })
    if not dmg then return end
    ActiveBuffs.apply(tid(ctx), 9905, nil, ctx.caster.id, 5, { bleeding=true, bleed_dmg=3 })
    return string.format("Internal vessels rupture within %s for %d damage!", tname(ctx), dmg)
end

handlers[702] = function(ctx) -- Mana Disruption
    if not ctx.result.hit then return end
    local drained = math.min(ctx.target.mana_current or 0, math.random(5, 15))
    DB.execute("UPDATE characters SET mana_current=MAX(0,mana_current-?) WHERE id=?",
        { drained, tid(ctx) })
    return string.format("%s's mana is disrupted, draining %d mana!", tname(ctx), drained)
end

handlers[703] = function(ctx) -- Corrupt Essence
    local dmg = sor_dmg(ctx, 7, 1.05, { lore = "demonology", min = 7 })
    if not dmg then return end
    ActiveBuffs.apply(tid(ctx), 703, CIRCLE_ID, ctx.caster.id, 10, { corrupted=true, td_spiritual=-10 })
    return string.format("Dark essence corrupts %s for %d damage and weakens their spirit!", tname(ctx), dmg)
end

handlers[704] = function(ctx) -- Phase
    local d = 10 + (ctx.circle_ranks or 1) * 6
    ActiveBuffs.apply(ctx.caster.id, 704, CIRCLE_ID, ctx.caster.id, d, { phased=true, incorporeal=true })
    return "You phase out of normal space, becoming partially incorporeal."
end

handlers[705] = function(ctx) -- Disintegrate bolt
    if not ctx.result.hit then return end
    local dmg = SpellFx.bolt_damage(ctx, {
        base = 20,
        min = 20,
        margin_mult = 1.80,
        lore = "necromancy",
        stat = "avg_aura_wis",
        mana_control = "spirit",
        level_scale = 0.32,
        circle_scale = 0.42,
        stat_scale = 0.28,
        aiming_scale = 0.10,
        lore_scale = 0.06,
    })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("Void energy tears %s apart for %d damage!", tname(ctx), dmg)
end

handlers[706] = function(ctx) -- Tenebrous Tether
    if not ctx.result.hit then return end
    local tdur = 5 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 10)
    ActiveBuffs.apply(tid(ctx), 706, CIRCLE_ID, ctx.caster.id, tdur, { tethered=true, immobilized=true })
    return string.format("Shadowy tendrils coil around %s, anchoring them!", tname(ctx))
end

handlers[707] = function(ctx)
    local room_id = ctx.caster.current_room_id
    local seen = {}
    local others = DB.query([[
        SELECT name, level
        FROM characters
        WHERE current_room_id = ? AND id != ?
        ORDER BY level DESC, name ASC
        LIMIT 5
    ]], { room_id, ctx.caster.id })
    for _, row in ipairs(others) do
        seen[#seen + 1] = string.format("%s (level %d)", row.name or "someone", tonumber(row.level) or 0)
    end
    ActiveBuffs.apply(ctx.caster.id, 707, CIRCLE_ID, ctx.caster.id, dur(ctx), {
        eye_spy=true,
        see_hidden=true,
        see_invisible=true,
    })
    if #seen == 0 then
        return "A shadowy eye manifests, confirming that nothing else in the room currently draws its attention."
    end
    return "A shadowy eye manifests and surveys the area: " .. table.concat(seen, ", ") .. "."
end

handlers[708] = function(ctx) -- Limb Disruption
    if not ctx.result.hit then return end
    local limbs = {"right_arm","left_arm","right_leg","left_leg"}
    local limb = limbs[math.random(1, #limbs)]
    ActiveBuffs.apply(tid(ctx), 708, CIRCLE_ID, ctx.caster.id, 15,
        { disrupted_limb=limb, limb_penalty=true })
    return string.format("Dark energy disrupts the %s of %s!", limb:gsub("_"," "), tname(ctx))
end

handlers[709] = function(ctx) -- Grasp of the Grave
    if not ctx.result.hit then return end
    local necromancy = (ctx.lore_ranks and ctx.lore_ranks.necromancy) or 0
    local gdur = 5 + math.floor((ctx.circle_ranks or 1) / 5) + math.floor(necromancy / 20)
    ActiveBuffs.apply(tid(ctx), 709, CIRCLE_ID, ctx.caster.id, gdur,
        { grabbed_from_below=true, immobilized=true })
    DB.execute("UPDATE characters SET position='prone' WHERE id=?", { tid(ctx) })
    return string.format("Decomposed hands erupt from the ground to seize %s!", tname(ctx))
end

handlers[710] = function(ctx) -- Energy Maelstrom bolt AoE
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    local hit_count = 0
    if room_id then
        local targets = DB.query(
            "SELECT id, health_current FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100))
        for _, t in ipairs(targets) do
            -- Player HP reduced via DB (room-wide spell; creature HP applied by Python via result.room_damage)
            DB.execute("UPDATE characters SET health_current=? WHERE id=?",
                { math.max(0, (t.health_current or 0) - dmg), t.id })
            hit_count = hit_count + 1
        end
        ctx.result.room_damage = dmg
    end
    return string.format("An energy maelstrom rips through the area striking %d targets!", hit_count)
end

handlers[711] = function(ctx) -- Pain
    if not ctx.result.hit then return end
    local pdur = 10 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5)
    ActiveBuffs.apply(tid(ctx), 711, CIRCLE_ID, ctx.caster.id, pdur,
        { in_pain=true, as_penalty=30, ds_penalty=30 })
    return string.format("Searing pain wracks %s's body!", tname(ctx))
end

handlers[712] = function(ctx) -- Cloak of Shadows
    local demonology = (ctx.lore_ranks and ctx.lore_ranks.demonology) or 0
    local necromancy = (ctx.lore_ranks and ctx.lore_ranks.necromancy) or 0
    local ds_bonus = math.min((ctx.caster.level or 1) + math.floor(necromancy / 30), math.max(0, (ctx.circle_ranks or 0) - 12) + math.floor(necromancy / 20))
    local td_bonus = math.min(math.floor((ctx.caster.level or 1) / 3) + math.floor(demonology / 30), math.floor(math.max(0, (ctx.circle_ranks or 0) - 12) / 10) + math.floor(demonology / 25))
    local mana_cost = 12 + math.floor(ds_bonus / 3)
    ActiveBuffs.apply(tid(ctx), 712, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=ds_bonus, td_sorcerer=td_bonus })
    return string.format("A cloak of shadows envelops %s (+%d DS, +%d TD).", tname(ctx), ds_bonus, td_bonus)
end

handlers[713] = function(ctx) -- Balefire bolt
    local dmg = SpellFx.bolt_damage(ctx, {
        base = 10,
        min = 10,
        margin_mult = 1.15,
        lore = "demonology",
        stat = "avg_aura_wis",
        mana_control = "spirit",
        level_scale = 0.30,
        circle_scale = 0.40,
        stat_scale = 0.28,
        aiming_scale = 0.10,
        lore_scale = 0.06,
    })
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("Balefire scorches %s for %d damage, burning through their defenses!", tname(ctx), dmg)
end

handlers[714] = function(ctx)
    local scroll = ItemMagic.get_item_by_types(ctx.caster.id, { "scroll" })
    if not scroll then
        return "You must be holding a scroll before you can infuse it."
    end
    local spell_number, spell_name, spell_level = 703, "Corrupt Essence", 3
    local ranks = tonumber(ctx.circle_ranks) or 1
    if ranks >= 18 then
        spell_number, spell_name, spell_level = 717, "Evil Eye", 17
    elseif ranks >= 10 then
        spell_number, spell_name, spell_level = 711, "Pain", 11
    end
    scroll.extra.spells = {
        {
            number = spell_number,
            name = spell_name,
            level = spell_level,
            charges = 1 + math.floor(ranks / 20),
        }
    }
    scroll.extra.scroll_infusion = true
    scroll.extra.spell_number = nil
    scroll.extra.spell_name = nil
    scroll.extra.spell_type = nil
    scroll.extra.spell_level = nil
    scroll.extra.charges = nil
    ItemMagic.save_extra(scroll.inv_id, scroll.extra)
    return string.format("You lace your %s with %s.", scroll.short_name or scroll.name or "scroll", spell_name)
end

handlers[715] = function(ctx) -- Curse
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 715, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { cursed=true, as_penalty=20, ds_penalty=20, luck_penalty=true })
    DB.execute("UPDATE characters SET is_cursed=1 WHERE id=?", { tid(ctx) })
    return string.format("A dark curse settles upon %s!", tname(ctx))
end

handlers[716] = function(ctx) -- Pestilence
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 716, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { plagued=true, hp_drain_per_pulse=3 })
    DB.execute("UPDATE characters SET is_diseased=1 WHERE id=?", { tid(ctx) })
    return string.format("A magical plague takes hold within %s!", tname(ctx))
end

handlers[717] = function(ctx) -- Evil Eye
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 717, CIRCLE_ID, ctx.caster.id, 20,
        { evil_eyed=true, as_penalty=15, stunned_chance=true, fear_effect=true })
    return string.format("The malefic gaze of the evil eye falls upon %s!", tname(ctx))
end

handlers[718] = function(ctx) -- Torment
    if not ctx.result.hit then return end
    local d = 5 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 718, CIRCLE_ID, ctx.caster.id, d, { tormented=true, hp_drain_per_pulse=5 })
    return string.format("Sorcerous torment grips %s, draining their life force!", tname(ctx))
end

handlers[719] = function(ctx) -- Dark Catalyst
    if not ctx.result.hit then return end
    local dmg = math.max(20, math.floor((ctx.result.total or 101) - 100) * 4)
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("Dark energies catalyze within %s in a devastating explosion for %d damage!", tname(ctx), dmg)
end

handlers[720] = function(ctx) -- Implosion
    if not ctx.result.hit then return end
    local dmg = math.max(25, math.floor((ctx.result.total or 101) - 100) * 5)
    ctx.result.damage = (ctx.result.damage or 0) + dmg
    return string.format("%s IMPLODES for %d catastrophic damage!", tname(ctx), dmg)
end

handlers[725] = function(ctx) -- Minor Summoning
    local demonology = (ctx.lore_ranks and ctx.lore_ranks.demonology) or 0
    local sdur = 60 + (ctx.circle_ranks or 1) * 20 + demonology * 2
    ActiveBuffs.apply(ctx.caster.id, 725, CIRCLE_ID, ctx.caster.id, sdur,
        { demonic_servant=true, servant_level=math.floor((ctx.circle_ranks or 1) / 5) + math.floor(demonology / 30) })
    return "A minor demonic entity materializes to serve you."
end

handlers[730] = function(ctx) -- Animate Dead
    local necromancy = (ctx.lore_ranks and ctx.lore_ranks.necromancy) or 0
    local undead_level = math.max(1, math.floor((ctx.circle_ranks or 1) / 6) + math.floor(necromancy / 25))
    local duration = 90 + ((ctx.circle_ranks or 1) * 15) + necromancy * 2
    ActiveBuffs.apply(ctx.caster.id, 730, CIRCLE_ID, ctx.caster.id, duration,
        {
            undead_servant=true,
            servant_level=undead_level,
            see_hidden=true,
            fear_resist=10 + math.floor(undead_level / 2),
        })
    return string.format("Dark power surges through a nearby corpse, animating it as your servant for %d seconds.", duration)
end

handlers[735] = function(ctx) -- Ensorcell
    local held = ItemMagic.get_held_item(ctx.caster.id)
    if not held then
        return "You must be holding a weapon or shield to ensorcell it."
    end
    local noun = (held.noun or "").lower()
    local item_type = (held.item_type or "").lower()
    if item_type ~= "weapon" and item_type ~= "shield" and noun == "" then
        return "That item offers no stable surface for an ensorcelling matrix."
    end
    local necromancy = (ctx.lore_ranks and ctx.lore_ranks.necromancy) or 0
    local tier = math.min(5, (held.extra.ensorcell_tier or 0) + 1)
    held.extra.ensorcelled = true
    held.extra.ensorcell_tier = tier
    held.extra.flare_type = held.extra.flare_type or "void"
    held.extra.attack_bonus = math.max(0, tonumber(held.extra.attack_bonus or 0) or 0) + math.floor(necromancy / 60)
    ItemMagic.save_extra(held.inv_id, held.extra)
    return string.format("Dark power sinks into your %s, raising its ensorcell tier to %d.", held.short_name or held.name or "item", tier)
end

handlers[740] = function(ctx) -- Planar Shift
    ActiveBuffs.apply(ctx.caster.id, 740, CIRCLE_ID, ctx.caster.id, 30,
        { planar_shifted=true, incorporeal=true, immune_to_physical=true })
    return "Reality warps as you shift partially out of this plane of existence."
end

function Sor.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Sor] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Sor
