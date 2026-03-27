------------------------------------------------------------------------
-- scripts/spells/major_elemental.lua
-- Major Elemental (MjE) spell circle — spells 501-550.
-- Circle id: 5 | Sphere: elemental | CS/TD stat: aura
-- Available to: Wizard only
-- Source: gswiki.play.net/Major_Elemental
-- Enhancement spells last 2 hours unless otherwise stated.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")
local ItemMagic   = require("globals/magic/item_magic")

local MjE = {}

local CIRCLE_ID  = 5
local LUA_SCRIPT = "spells/major_elemental"
local BUFF_SECS  = 7200  -- 2-hour default for MjE defensive buffs

local SPELLS = {
    [501] = { name="Sleep",                mnemonic="SLEEP",            spell_type="warding", mana_cost=1,
              description="Warding attack that puts the target to sleep. Duration scales with warding margin." },
    [502] = { name="Chromatic Circle",     mnemonic="CHROMATICCIRCLE",  spell_type="warding", mana_cost=2,
              description="Warding attack using a rotating circle of elemental colors. Random element type each cast." },
    [503] = { name="Thurfel's Ward",       mnemonic="THURFELWARD",      spell_type="buff",    mana_cost=3,
              description="Adds +10 DS (+1 per 4 ranks above 3). 2-hour duration." },
    [504] = { name="Slow",                 mnemonic="SLOW",             spell_type="warding", mana_cost=4,
              description="Warding attack that slows the target, increasing their roundtimes significantly." },
    [505] = { name="Hand of Tonis",        mnemonic="HANDOFTONIS",      spell_type="warding", mana_cost=5,
              description="Warding attack from the air deity Tonis, striking with concussive force." },
    [506] = { name="Celerity",             mnemonic="CELERITY",         spell_type="buff",    mana_cost=6,
              description="Reduces the caster's roundtime by 1 second for most actions. 2-hour duration." },
    [507] = { name="Elemental Deflection", mnemonic="ELEDEFLECTION",    spell_type="buff",    mana_cost=7,
              description="Adds +10 DS (+1 per 2 ranks above 7). 2-hour duration." },
    [508] = { name="Elemental Bias",       mnemonic="ELEBIAS",          spell_type="buff",    mana_cost=8,
              description="Biases elemental energy to reduce incoming bolt damage. TD bonus vs bolt spells." },
    [509] = { name="Strength",             mnemonic="STRENGTH",         spell_type="buff",    mana_cost=9,
              description="Grants a Strength bonus, improving AS and carry capacity for the duration." },
    [510] = { name="Hurl Boulder",         mnemonic="HURLBOULDER",      spell_type="bolt",    mana_cost=10,
              description="element:impact. Hurls a massive stone at the target for crushing damage." },
    [511] = { name="Floating Disk",        mnemonic="FLOATINGDISK",     spell_type="utility", mana_cost=11,
              description="Creates a floating disk that carries items, reducing encumbrance." },
    [512] = { name="Cold Snap",            mnemonic="COLDSNAP",         spell_type="warding", mana_cost=12,
              description="element:ice. Warding/bolt hybrid that snaps the target with intense cold." },
    [513] = { name="Elemental Focus",      mnemonic="ELEFOCUS",         spell_type="buff",    mana_cost=13,
              description="Adds +1 Bolt AS per 2 ranks above 13. 2-hour duration." },
    [514] = { name="Stone Fist",           mnemonic="STONEFIST",        spell_type="bolt",    mana_cost=14,
              description="element:impact. A fist of compressed stone strikes the target." },
    [515] = { name="Rapid Fire",           mnemonic="RAPIDFIRE",        spell_type="utility", mana_cost=15,
              description="Reduces the cooldown between bolt spell casts. Active for a limited number of casts." },
    [516] = { name="Mana Leech",           mnemonic="MANALEECH",        spell_type="utility", mana_cost=16,
              description="Drains mana from the target. Max drained per cast equals MjE ranks." },
    [517] = { name="Charge Item",          mnemonic="CHARGEITEM",       spell_type="utility", mana_cost=17,
              description="Recharges magical items (wands, rods). Success chance improves with ranks." },
    [518] = { name="Cone of Elements",     mnemonic="CONEOFELEMENTS",   spell_type="bolt",    mana_cost=18,
              description="element:fire. A cone of elemental energy that can hit multiple targets in front of the caster." },
    [519] = { name="Immolation",           mnemonic="IMMOLATION",       spell_type="bolt",    mana_cost=19,
              description="element:fire. Sets the target on fire for ongoing burn damage. Very destructive." },
    [520] = { name="Mage Armor",           mnemonic="MAGEARMOR",        spell_type="buff",    mana_cost=20,
              description="Creates magical armor equivalent to brigandine with no spell hindrance. Padding increases every 15 ranks." },
    [525] = { name="Meteor Swarm",         mnemonic="METEORSWARM",      spell_type="bolt",    mana_cost=25,
              description="element:impact. Calls meteors down on a target. Room AoE at very high ranks." },
    [530] = { name="Elemental Disjunction",mnemonic="ELEDISJUNCTION",   spell_type="warding", mana_cost=30,
              description="Warding attack that dispels multiple elemental buffs. Min buffs removed scales with ranks." },
    [535] = { name="Haste",                mnemonic="HASTE",            spell_type="buff",    mana_cost=35,
              description="Reduces all roundtimes by up to 60%. -1% RT reduction per 5 ranks. 2-hour duration." },
    [540] = { name="Temporal Reversion",   mnemonic="TEMPORALREVERSION",spell_type="buff",    mana_cost=40,
              description="If the caster would be killed, temporal energy reverts them to a less injured state. Single-use trigger." },
    [550] = { name="Time Stop",            mnemonic="TIMESTOP",         spell_type="utility", mana_cost=50,
              description="Briefly stops time, allowing the caster to act without roundtime for a short period." },
}

function MjE.seed()
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

local handlers = {}

handlers[501] = function(ctx) -- Sleep
    if not ctx.result.hit then return end
    local sdur = 5 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 10)
    ActiveBuffs.apply(tid(ctx), 501, CIRCLE_ID, ctx.caster.id, sdur, { asleep=true, immobilized=true })
    DB.execute("UPDATE characters SET position='sleeping' WHERE id=?", { tid(ctx) })
    return string.format("%s slumps into an unnatural slumber!", tname(ctx))
end

handlers[502] = function(ctx) -- Chromatic Circle
    if not ctx.result.hit then return end
    local elements = {"fire","ice","lightning","acid","impact"}
    local elem = elements[math.random(1,#elements)]
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A %s chromatic strike hits %s for %d damage!", elem, tname(ctx), dmg)
end

handlers[503] = function(ctx) -- Thurfel's Ward
    local ds_bonus = 10 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 3) / 4)
    ActiveBuffs.apply(tid(ctx), 503, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { ds=ds_bonus })
    return string.format("Thurfel's ward surrounds %s (+%d DS).", tname(ctx), ds_bonus)
end

handlers[504] = function(ctx) -- Slow
    if not ctx.result.hit then return end
    local sdur = 15 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5)
    ActiveBuffs.apply(tid(ctx), 504, CIRCLE_ID, ctx.caster.id, sdur, { slowed=true, rt_penalty=2 })
    return string.format("Time seems to crawl around %s!", tname(ctx))
end

handlers[505] = function(ctx) -- Hand of Tonis
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    DB.execute("UPDATE characters SET health_current=MAX(0,health_current-?), position='prone' WHERE id=?",
        { dmg, tid(ctx) })
    return string.format("A concussive fist of air slams %s to the ground for %d damage!", tname(ctx), dmg)
end

handlers[506] = function(ctx) -- Celerity
    ActiveBuffs.apply(tid(ctx), 506, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { rt_reduction=1 })
    return "Your movements quicken with elemental celerity."
end

handlers[507] = function(ctx) -- Elemental Deflection
    local ds_bonus = 10 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 7) / 2)
    ActiveBuffs.apply(tid(ctx), 507, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { ds=ds_bonus })
    return string.format("Elemental deflection surrounds %s (+%d DS).", tname(ctx), ds_bonus)
end

handlers[508] = function(ctx) -- Elemental Bias
    ActiveBuffs.apply(tid(ctx), 508, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { td_elemental=20, bolt_resist=15 })
    return string.format("Elemental energy shifts around %s, biasing against incoming bolts.", tname(ctx))
end

handlers[509] = function(ctx) -- Strength
    ActiveBuffs.apply(tid(ctx), 509, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { strength_bonus=10, as_bonus=5 })
    return string.format("The strength of %s swells with elemental power.", tname(ctx))
end

handlers[510] = function(ctx) -- Hurl Boulder
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100) * 2)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=?, position='prone' WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A massive boulder smashes into %s for %d damage!", tname(ctx), dmg)
end

handlers[511] = function(ctx) -- Floating Disk
    ActiveBuffs.apply(tid(ctx), 511, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { floating_disk=true, carry_bonus=50 })
    return "A shimmering disk of force materializes to carry your burdens."
end

handlers[512] = function(ctx) -- Cold Snap
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    local sdur = 3 + math.floor(dmg / 10)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    ActiveBuffs.apply(tid(ctx), 512, CIRCLE_ID, ctx.caster.id, sdur, { slowed=true })
    return string.format("A snap of intense cold strikes %s for %d damage and slows them!", tname(ctx), dmg)
end

handlers[513] = function(ctx) -- Elemental Focus
    local bolt_as = math.floor(math.max(0, (ctx.circle_ranks or 0) - 13) / 2)
    ActiveBuffs.apply(tid(ctx), 513, CIRCLE_ID, ctx.caster.id, BUFF_SECS, { bolt_as_bonus=bolt_as })
    return string.format("Your elemental focus sharpens (+%d Bolt AS).", bolt_as)
end

handlers[514] = function(ctx) -- Stone Fist
    if not ctx.result.hit then return end
    local dmg = math.max(8, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A stone fist SLAMS into %s for %d damage!", tname(ctx), dmg)
end

handlers[515] = function(ctx) -- Rapid Fire
    ActiveBuffs.apply(tid(ctx), 515, CIRCLE_ID, ctx.caster.id, 60, { rapid_fire=true, bolt_rt_reduction=1 })
    return "Your spellcasting accelerates into rapid-fire mode."
end

handlers[516] = function(ctx) -- Mana Leech
    if not ctx.target then return end
    local max_leech = math.min(ctx.circle_ranks or 1, ctx.target.mana_current or 0)
    local amount = math.random(1, math.max(1, max_leech))
    local new_target_mana = math.max(0, (ctx.target.mana_current or 0) - amount)
    local new_caster_mana = math.min(ctx.caster.mana_max or 99, (ctx.caster.mana_current or 0) + amount)
    DB.execute("UPDATE characters SET mana_current=? WHERE id=?", { new_target_mana, ctx.target.id })
    DB.execute("UPDATE characters SET mana_current=? WHERE id=?", { new_caster_mana, ctx.caster.id })
    return string.format("You leech %d mana from %s.", amount, tname(ctx))
end

handlers[517] = function(ctx)
    local item = ItemMagic.get_item_by_types(ctx.caster.id, { "wand", "rod" })
    if not item then
        return "You must be carrying a wand or rod before you can channel fresh power into it."
    end
    if not (item.spell_number or item.extra.spell_number) then
        return string.format("Your %s contains no recognizable spell matrix to recharge.", item.short_name or item.name or "item")
    end

    local charges = tonumber(item.charges) or 0
    local amount = 1 + math.floor((tonumber(ctx.circle_ranks) or 1) / 15)
    local new_charges = math.min(10, charges + amount)
    item.extra.charges = new_charges
    ItemMagic.save_extra(item.inv_id, item.extra)

    return string.format("Elemental power surges into your %s, restoring it to %d charge%s.",
        item.short_name or item.name or "item",
        new_charges,
        new_charges == 1 and "" or "s")
end

handlers[518] = function(ctx) -- Cone of Elements
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    local hit_count = 0
    if room_id then
        local targets = DB.query(
            "SELECT id, health_current FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
        for i, t in ipairs(targets) do
            if i <= 3 then -- cone hits up to 3
                DB.execute("UPDATE characters SET health_current=? WHERE id=?",
                    { math.max(0, (t.health_current or 0) - dmg), t.id })
                hit_count = hit_count + 1
            end
        end
    end
    return string.format("A cone of elemental fire scorches %d targets!", hit_count)
end

handlers[519] = function(ctx) -- Immolation
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100))
    local burn_dur = 5 + math.floor((ctx.circle_ranks or 1) / 5)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    ActiveBuffs.apply(tid(ctx), 519, CIRCLE_ID, ctx.caster.id, burn_dur, { burning=true, burn_dmg=5 })
    return string.format("%s bursts into flames, taking %d damage and continuing to burn!", tname(ctx), dmg)
end

handlers[520] = function(ctx) -- Mage Armor
    -- Grants ASG 12 (brigandine equivalent) with no hindrance
    ActiveBuffs.apply(tid(ctx), 520, CIRCLE_ID, ctx.caster.id, BUFF_SECS,
        { mage_armor=true, armor_asg_override=12, hindrance_redux=100 })
    return string.format("Shimmering plates of magical force assemble around %s.", tname(ctx))
end

handlers[525] = function(ctx) -- Meteor Swarm
    if not ctx.result.hit then return end
    local dmg = math.max(15, math.floor((ctx.result.total or 101) - 100) * 3)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A swarm of meteors crashes down upon %s for %d damage!", tname(ctx), dmg)
end

handlers[530] = function(ctx) -- Elemental Disjunction
    if not ctx.result.hit then return end
    local n_rem = 2 + math.floor((ctx.circle_ranks or 1) / 10)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND circle_id IN (4,5,8,9)
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid(ctx), n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format("Elemental disjunction tears away %d buff(s) from %s!", #buffs, tname(ctx))
end

handlers[535] = function(ctx) -- Haste
    local rt_redux = math.min(60, math.floor((ctx.circle_ranks or 1) / 5))
    ActiveBuffs.apply(tid(ctx), 535, CIRCLE_ID, ctx.caster.id, BUFF_SECS,
        { rt_reduction_pct=rt_redux })
    return string.format("Time bends around %s, reducing roundtimes by %d%%.", tname(ctx), rt_redux)
end

handlers[540] = function(ctx) -- Temporal Reversion
    ActiveBuffs.apply(tid(ctx), 540, CIRCLE_ID, ctx.caster.id, BUFF_SECS,
        { temporal_reversion=true, reversion_hp_pct=50 })
    return "A loop of temporal energy forms around you, ready to revert death."
end

handlers[550] = function(ctx) -- Time Stop
    ActiveBuffs.apply(ctx.caster.id, 550, CIRCLE_ID, ctx.caster.id, 15,
        { time_stopped=true, rt_reduction_pct=100 })
    return "Time halts around you as you step outside its flow!"
end

function MjE.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[MjE] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return MjE
