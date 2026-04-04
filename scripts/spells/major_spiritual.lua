------------------------------------------------------------------------
-- scripts/spells/major_spiritual.lua
-- Major Spiritual (MjS) spell circle — spells 201-240.
-- Circle id: 2 | Sphere: spiritual | CS/TD stat: wisdom
-- Available to: Cleric, Empath
-- Source: gswiki.play.net/Major_Spiritual
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local ItemMagic   = require("globals/magic/item_magic")
local SpellFx     = require("globals/magic/spell_formulas")

local MjS = {}

local CIRCLE_ID  = 2
local LUA_SCRIPT = "spells/major_spiritual"

local SPELLS = {
    [201] = { name="Calm",                 mnemonic="CALM",             spell_type="warding", mana_cost=1,
              description="Warding attack that calms (pacifies) the target, preventing them from attacking." },
    [202] = { name="Spirit Shield",        mnemonic="SPIRITSHIELD",     spell_type="buff",    mana_cost=2,
              description="Adds +10 DS (+1 per 3 ranks above 2). Stackable self/group." },
    [203] = { name="Manna",                mnemonic="MANNA",            spell_type="utility", mana_cost=3,
              description="Creates manna bread that restores mana when eaten. Rank scaling increases restoration." },
    [204] = { name="Unpresence",           mnemonic="UNPRESENCE",       spell_type="utility", mana_cost=4,
              description="Reduces the caster's magical presence, making them harder to detect by magical means." },
    [205] = { name="Light",                mnemonic="LIGHT",            spell_type="utility", mana_cost=5,
              description="Creates a light source that illuminates dark areas. Duration scales with circle ranks." },
    [206] = { name="Tend Lore",            mnemonic="TENDLORE",         spell_type="utility", mana_cost=6,
              description="Improves First Aid skill for tending wounds and injuries. Duration scales with ranks." },
    [207] = { name="Purify Air",           mnemonic="PURIFYAIR",        spell_type="buff",    mana_cost=7,
              description="Protects against gas and environmental hazards. Can counteract some poison clouds." },
    [208] = { name="Living Spell",         mnemonic="LIVINGSPELL",      spell_type="utility", mana_cost=8,
              description="Infuses a spell into an object, allowing non-casters to trigger it later." },
    [209] = { name="Untrammel",            mnemonic="UNTRAMMEL",        spell_type="utility", mana_cost=9,
              description="Removes web, roots, and immobilization effects from the target." },
    [210] = { name="Silence",              mnemonic="SILENCE",          spell_type="warding", mana_cost=10,
              description="Warding attack that prevents the target from casting spells by silencing their voice." },
    [211] = { name="Bravery",              mnemonic="BRAVERY",          spell_type="buff",    mana_cost=11,
              description="Grants bonus AS and immunity to fear effects. Non-stackable combat buff." },
    [212] = { name="Interference",         mnemonic="INTERFERENCE",     spell_type="warding", mana_cost=12,
              description="Warding attack that interferes with the target's spellcasting, increasing hindrance." },
    [213] = { name="Minor Sanctuary",      mnemonic="MINORSANCTUARY",   spell_type="utility", mana_cost=13,
              description="Creates a temporary sanctuary in the current room. Fixed duration, no PvP combat." },
    [214] = { name="Bind",                 mnemonic="BIND",             spell_type="warding", mana_cost=14,
              description="Warding attack that binds the target in place, preventing all movement." },
    [215] = { name="Heroism",              mnemonic="HEROISM",          spell_type="buff",    mana_cost=15,
              description="Grants +AS, +DS, and enhanced combat statistics. Group-capable offensive buff." },
    [216] = { name="Frenzy",               mnemonic="FRENZY",           spell_type="warding", mana_cost=16,
              description="Warding attack that causes the target to attack randomly, including allies." },
    [217] = { name="Mass Interference",    mnemonic="MASSINTERFERENCE", spell_type="warding", mana_cost=17,
              description="Room-wide warding attack that interferes with all hostile spellcasters." },
    [218] = { name="Spirit Servant",       mnemonic="SPIRITSERVANT",    spell_type="summon",  mana_cost=18,
              description="Summons a spirit servant to carry items, scout ahead, preserve remains, and perform simple tasks." },
    [219] = { name="Spell Shield",         mnemonic="SPELLSHIELD",      spell_type="buff",    mana_cost=19,
              description="Grants significant TD and resistance to warding spells." },
    [220] = { name="Major Sanctuary",      mnemonic="MAJORSANCTUARY",   spell_type="utility", mana_cost=20,
              description="Creates a powerful sanctuary. +30 sec per rank. Persists much longer than minor version." },
    [225] = { name="Transference",         mnemonic="TRANSFERENCE",     spell_type="utility", mana_cost=25,
              description="Spiritually transfers the caster to the target's room. Mana cost decreases with skill." },
    [230] = { name="Spiritual Abolition",  mnemonic="SPIRITUALABOLITION",spell_type="warding", mana_cost=30,
              description="Warding attack that dispels multiple active spiritual buffs. Number removed scales with ranks." },
    [240] = { name="Spirit Slayer",        mnemonic="SPIRITSLAYER",     spell_type="buff",    mana_cost=40,
              description="Grants massive AS and CS bonus against undead and spiritual creatures. Fixed duration." },
}

function MjS.seed()
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

handlers[201] = function(ctx) -- Calm
    if not ctx.result.hit then return end
    ActiveBuffs.apply(tid(ctx), 201, CIRCLE_ID, ctx.caster.id, 30, { calmed=true })
    return string.format("A wave of calming energy washes over %s.", tname(ctx))
end

handlers[202] = function(ctx) -- Spirit Shield
    local ds_bon = 10 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 2) / 3)
    ActiveBuffs.apply(tid(ctx), 202, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bon })
    return string.format("A shimmering spiritual shield surrounds %s.", tname(ctx))
end

handlers[203] = function(ctx)
    local blessings = (ctx.lore_ranks and ctx.lore_ranks.blessings) or 0
    local mana_restore = SpellFx.support_heal_amount(ctx, {
        base = 6,
        stat = "wisdom",
        skill = "spell_research",
        mana_control = "spirit",
        lore = "blessings",
        circle_scale = 0.20,
        stat_scale = 0.12,
        skill_scale = 0.04,
        lore_scale = 0.03,
        min = 6,
    })
    local max_mana_bonus = math.min(50, math.floor(blessings / 10) * 5)
    local item = DB.queryOne("SELECT id FROM items WHERE short_name = ? LIMIT 1", { "manna bread" })
    if not item then
        return "The blessing forms briefly, but there is no proper vessel prepared for manna."
    end
    ItemMagic.create_item(ctx.caster.id, item.id, {
        mana_restore = mana_restore,
        manna_max_bonus = max_mana_bonus,
        manna_fresh = true,
        blessed_food = true,
    }, nil)
    return "A small loaf of manna bread materializes for later use."
end

handlers[204] = function(ctx) -- Unpresence
    ActiveBuffs.apply(tid(ctx), 204, CIRCLE_ID, ctx.caster.id, dur(ctx), { magical_presence=false })
    return string.format("The magical aura of %s becomes difficult to detect.", tname(ctx))
end

handlers[205] = function(ctx) -- Light
    local duration = 1200 + ((ctx.circle_ranks or 1) * 60)
    ActiveBuffs.apply(tid(ctx), 205, CIRCLE_ID, ctx.caster.id, duration, { light_source=true })
    return "A warm light radiates from your hand, illuminating the area."
end

handlers[206] = function(ctx) -- Tend Lore
    local blessings = (ctx.lore_ranks and ctx.lore_ranks.blessings) or 0
    local extra = 0
    local threshold = 2
    while blessings >= threshold do
        extra = extra + 1
        threshold = threshold + (extra + 2)
    end
    local bonus = 20 + extra
    ActiveBuffs.apply(tid(ctx), 206, CIRCLE_ID, ctx.caster.id, 60,
        { first_aid_bonus=bonus, tend_rt_reduction_pct=25 })
    return string.format("The healing knowledge of %s is spiritually enhanced (+%d First Aid).", tname(ctx), bonus)
end

handlers[207] = function(ctx) -- Purify Air
    ActiveBuffs.apply(tid(ctx), 207, CIRCLE_ID, ctx.caster.id, dur(ctx), { gas_immune=true, poison_resist=true })
    return string.format("A purifying aura surrounds %s, cleansing the air nearby.", tname(ctx))
end

handlers[208] = function(ctx)
    local held = ItemMagic.get_held_item(ctx.caster.id)
    if not held then
        return "You need to hold an item before you can house a living spell within it."
    end
    local spell_number, spell_name, spell_level = 202, "Spirit Shield", 2
    if (ctx.circle_ranks or 1) >= 15 then
        spell_number, spell_name, spell_level = 215, "Heroism", 15
    end
    held.extra.living_spell = true
    held.extra.charges = 1
    held.extra.spell_number = spell_number
    held.extra.spell_name = spell_name
    held.extra.spell_type = "buff"
    held.extra.spell_level = spell_level
    ItemMagic.save_extra(held.inv_id, held.extra)
    return string.format("A living spell settles into your %s, ready to awaken once.", held.short_name or held.name or "item")
end

handlers[209] = function(ctx) -- Untrammel
    local id = tid(ctx)
    DB.execute("UPDATE characters SET position='standing' WHERE id=? AND position IN ('webbed','rooted','prone')", { id })
    ActiveBuffs.remove_spell(id, 118) -- web
    ActiveBuffs.remove_spell(id, 9904) -- root
    return string.format("The bonds trapping %s dissolve away.", tname(ctx))
end

handlers[210] = function(ctx) -- Silence
    if not ctx.result.hit then return end
    local margin = math.max(0, (ctx.result.total or 101) - 100)
    local sdur = 5 + math.floor(margin / 10)
    ActiveBuffs.apply(tid(ctx), 210, CIRCLE_ID, ctx.caster.id, sdur, { silenced=true })
    return string.format("A spiritual silence descends upon %s, blocking their voice!", tname(ctx))
end

handlers[211] = function(ctx) -- Bravery
    ActiveBuffs.apply(tid(ctx), 211, CIRCLE_ID, ctx.caster.id, dur(ctx), { as_bonus=15, fear_immune=true })
    return string.format("A surge of spiritual bravery steels the heart of %s.", tname(ctx))
end

handlers[212] = function(ctx) -- Interference
    local sdur = 60
    ActiveBuffs.apply(tid(ctx), 212, CIRCLE_ID, ctx.caster.id, sdur,
        { as_penalty=20, ds_penalty=20, td_spiritual=-20, td_elemental=-20, td_mental=-20 })
    return string.format("Spiritual static crackles around %s, interfering with every action!", tname(ctx))
end

handlers[213] = function(ctx) -- Minor Sanctuary
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE rooms SET is_sanctuary=1, sanctuary_expires=DATE_ADD(NOW(), INTERVAL 600 SECOND) WHERE id=?", { room_id })
    end
    return "The air shimmers as a minor sanctuary forms around you."
end

handlers[214] = function(ctx) -- Bind
    if not ctx.result.hit then return end
    local margin = math.max(0, (ctx.result.total or 101) - 100)
    local bdur = 5 + math.floor(margin / 5)
    ActiveBuffs.apply(tid(ctx), 214, CIRCLE_ID, ctx.caster.id, bdur, { bound=true, immobilized=true })
    DB.execute("UPDATE characters SET position='bound' WHERE id=?", { tid(ctx) })
    return string.format("Spiritual bonds coil around %s, binding them in place!", tname(ctx))
end

handlers[215] = function(ctx) -- Heroism
    ActiveBuffs.apply(tid(ctx), 215, CIRCLE_ID, ctx.caster.id, dur(ctx), { as_bonus=20, ds=20, heroism=true })
    return string.format("Heroic resolve blazes through %s!", tname(ctx))
end

handlers[216] = function(ctx) -- Frenzy
    if not ctx.result.hit then return end
    local fdur = 10 + math.floor((ctx.circle_ranks or 1) / 2)
    ActiveBuffs.apply(tid(ctx), 216, CIRCLE_ID, ctx.caster.id, fdur, { frenzied=true })
    return string.format("%s is overwhelmed by a maddened frenzy!", tname(ctx))
end

handlers[217] = function(ctx) -- Mass Interference — hits all hostiles in room
    local room_id = ctx.caster.current_room_id
    if room_id then
        -- Mark all non-allied characters in the room as interference-debuffed
        local rows = DB.query("SELECT id FROM characters WHERE current_room_id=? AND id != ?",
            { room_id, ctx.caster.id })
        for _, row in ipairs(rows) do
            ActiveBuffs.apply(row.id, 217, CIRCLE_ID, ctx.caster.id, 10, { hindrance_penalty=20 })
        end
    end
    return "Spiritual static floods the area, disrupting all spellcasters!"
end

handlers[218] = function(ctx)
    local summoning = (ctx.lore_ranks and ctx.lore_ranks.summoning) or 0
    local preservation = 300 + (math.min(summoning, 100) * 15) + (math.max(0, summoning - 100) * 10)
    ActiveBuffs.apply(ctx.caster.id, 218, CIRCLE_ID, ctx.caster.id, nil, {
        spirit_servant=true,
        summon_key="spirit_servant",
        hand_capacity=2,
        spirit_servant_hands=2,
        preservation_seconds=preservation,
        see_hidden=true,
    })
    return string.format(
        "A translucent spirit servant materializes at your side, its ghostly hands ready for labor and its preserving touch lasting %d seconds.",
        preservation
    )
end

handlers[219] = function(ctx) -- Spell Shield
    ActiveBuffs.apply(tid(ctx), 219, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { td_spiritual=25, td_elemental=15, td_mental=15 })
    return string.format("A shimmering magical shield envelops %s.", tname(ctx))
end

handlers[220] = function(ctx) -- Major Sanctuary
    local sdur = 30 * math.max(1, ctx.circle_ranks or 1)
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute([[
            UPDATE rooms SET is_sanctuary=1,
            sanctuary_expires=DATE_ADD(NOW(), INTERVAL ? SECOND) WHERE id=?
        ]], { sdur, room_id })
    end
    return string.format("A powerful sanctuary takes hold, lasting %d seconds.", sdur)
end

handlers[225] = function(ctx) -- Transference
    if not ctx.target or not ctx.target.current_room_id then
        return "You need a same-realm player target to transfer yourself to."
    end
    local spirit_mc = (ctx.mana_control and ctx.mana_control.spirit) or 0
    local travel_cost = math.max(5, 25 - math.floor((ctx.circle_ranks or 1) / 3) - math.floor(spirit_mc / 20))
    if (ctx.caster.mana_current or 0) < travel_cost then
        return string.format("You need %d mana to transfer to %s.", travel_cost, tname(ctx))
    end
    DB.execute("UPDATE characters SET mana_current=GREATEST(0,mana_current-?), current_room_id=? WHERE id=?",
        { travel_cost, ctx.target.current_room_id, ctx.caster.id })
    return string.format("Spiritual transference carries you instantly to %s.", tname(ctx))
end

handlers[230] = function(ctx) -- Spiritual Abolition
    if not ctx.result.hit then return end
    local n_rem = 1 + math.floor((ctx.circle_ranks or 1) / 5)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND circle_id IN (1,2,3,6,11)
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid(ctx), n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format("Spiritual abolition tears away %d effect(s) from %s!", #buffs, tname(ctx))
end

handlers[240] = function(ctx) -- Spirit Slayer — fixed 600s, massive AS/CS vs undead
    ActiveBuffs.apply(tid(ctx), 240, CIRCLE_ID, ctx.caster.id, 600,
        { as_bonus=50, cs_spiritual=50, undead_only=true })
    return "Your spiritual power blazes with deadly intensity against the undead!"
end

function MjS.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[MjS] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return MjS
