------------------------------------------------------------------------
-- scripts/spells/bard.lua
-- Bard Base (Bar) spell circle — spells 1001-1040.
-- Circle id: 9 | Sphere: hybrid_em (elemental/mental) | CS/TD stat: aura
-- Available to: Bard only
-- Source: gswiki.play.net/Bard_Base
--
-- Bard spells are SUNG (SING verb) not CAST.
-- Continuous songs cost mana on renewal (renew cycle formula is in
-- spell_engine — Bard Base is handled identically to cast spells here;
-- the SING/RENEW verb distinction lives in the command layer).
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local Bar = {}

local CIRCLE_ID  = 9
local LUA_SCRIPT = "spells/bard"

local SPELLS = {
    [1001] = { name="Holding Song",               mnemonic="HOLDINGSONG",         spell_type="warding", mana_cost=1,
               description="Warding attack song that holds the target in place. +1 target per 5 ranks." },
    [1002] = { name="Vibration Chant",             mnemonic="VIBRATIONCHANT",      spell_type="bolt",    mana_cost=2,
               description="element:impact. Shattering sonic vibration directed at a target." },
    [1003] = { name="Fortitude Song",              mnemonic="FORTITUDESONG",       spell_type="buff",    mana_cost=3,
               description="Continuous song granting +DS to the bard and nearby allies." },
    [1004] = { name="Purification Song",           mnemonic="PURIFICATIONSONG",    spell_type="utility", mana_cost=4,
               description="Continuous song that cures disease and poison for all in the area." },
    [1005] = { name="Lullabye",                    mnemonic="LULLABYE",            spell_type="warding", mana_cost=5,
               description="Warding attack song that puts the target to sleep with a soothing melody." },
    [1006] = { name="Song of Luck",                mnemonic="SONGOFLUCK",          spell_type="buff",    mana_cost=6,
               description="Continuous luck song improving all chance-based rolls for those who hear it." },
    [1007] = { name="Kai's Triumph Song",          mnemonic="KAISTRIUMPHSONG",     spell_type="buff",    mana_cost=7,
               description="Continuous song granting +AS to the bard and melee allies who can hear it." },
    [1008] = { name="Stunning Shout",              mnemonic="STUNNINGSHOUT",       spell_type="warding", mana_cost=8,
               description="Warding attack shout that may stun the target with sonic force." },
    [1009] = { name="Sonic Shield Song",           mnemonic="SONICSHIELDSONG",     spell_type="utility", mana_cost=9,
               description="Song that creates a sonic shield usable as a defensive barrier by the bard." },
    [1010] = { name="Song of Valor",               mnemonic="SONGOFVALOR",         spell_type="buff",    mana_cost=10,
               description="Continuous song inspiring valor, granting +DS and resistance to fear." },
    [1011] = { name="Song of Peace",               mnemonic="SONGOFPEACE",         spell_type="utility", mana_cost=11,
               description="Continuous song attempting to pacify hostile creatures. Room-wide calm." },
    [1012] = { name="Sonic Weapon Song",           mnemonic="SONICWEAPONSONG",     spell_type="buff",    mana_cost=12,
               description="Continuous song imbuing all allies' weapons with sonic energy." },
    [1013] = { name="Song of Unravelling",         mnemonic="SONGUNRAVELLING",     spell_type="warding", mana_cost=13,
               description="Warding attack song that unravels magical buffs from the target." },
    [1014] = { name="Sonic Armor",                 mnemonic="SONICARMOR",          spell_type="buff",    mana_cost=14,
               description="Creates sonic armor around the bard providing equivalent to chain protection." },
    [1015] = { name="Song of Depression",          mnemonic="SONGOFDEPRESSION",    spell_type="warding", mana_cost=15,
               description="Warding attack song inflicting despair, reducing the target's AS and CS significantly." },
    [1016] = { name="Song of Rage",                mnemonic="SONGOFRAGE",          spell_type="warding", mana_cost=16,
               description="Warding attack song driving the target into a murderous rage against random targets." },
    [1017] = { name="Song of Noise",               mnemonic="SONGOFNOISE",         spell_type="utility", mana_cost=17,
               description="Creates a cacophony of noise in the area preventing stealth and masking sounds." },
    [1018] = { name="Song of Power",               mnemonic="SONGOFPOWER",         spell_type="buff",    mana_cost=18,
               description="Continuous song amplifying magical power, granting CS bonus to spellcasters." },
    [1019] = { name="Song of Mirrors",             mnemonic="SONGOFMIRRORS",       spell_type="buff",    mana_cost=19,
               description="Creates sonic mirrors around the bard, deflecting some bolt attacks." },
    [1020] = { name="Traveler's Song",             mnemonic="TRAVELERSONG",        spell_type="utility", mana_cost=20,
               description="Song that aids travel, reducing movement roundtimes and improving navigation." },
    [1025] = { name="Singing Sword Song",          mnemonic="SINGINGSWORDSONG",    spell_type="buff",    mana_cost=25,
               description="Continuous song causing the bard's weapon to vibrate with sonic power." },
    [1030] = { name="Song of Sonic Disruption",    mnemonic="SONGSONICDISR",       spell_type="bolt",    mana_cost=30,
               description="element:impact. Devastating sonic bolt disrupting the target's very molecules." },
    [1035] = { name="Song of Tonis",               mnemonic="SONGOFTONIS",         spell_type="buff",    mana_cost=35,
               description="Song invoking Tonis, deity of wind, granting speed and DS bonuses." },
    [1040] = { name="Troubadour's Rally",          mnemonic="TROUBADOURSRALLY",    spell_type="utility", mana_cost=40,
               description="Rallying song restoring morale, removing fear effects and granting temporary HP." },
}

function Bar.seed()
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

-- Room-wide ally buff helper
local function buff_room(ctx, spell_num, effects)
    local room_id = ctx.caster.current_room_id
    if not room_id then return 0 end
    local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
    for _, a in ipairs(allies) do
        ActiveBuffs.apply(a.id, spell_num, CIRCLE_ID, ctx.caster.id, dur(ctx), effects)
    end
    return #allies
end

local handlers = {}

handlers[1001] = function(ctx) -- Holding Song
    if not ctx.result.hit then return end
    local hdur = 5 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 10)
    ActiveBuffs.apply(tid(ctx), 1001, CIRCLE_ID, ctx.caster.id, hdur, { held=true, immobilized=true })
    return string.format("A melodic holding song wraps around %s, rooting them!", tname(ctx))
end

handlers[1002] = function(ctx) -- Vibration Chant bolt
    if not ctx.result.hit then return end
    local dmg = math.max(3, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Shattering vibrations rip through %s for %d damage!", tname(ctx), dmg)
end

handlers[1003] = function(ctx) -- Fortitude Song
    local n = buff_room(ctx, 1003, { ds=10 })
    return string.format("Your fortitude song bolsters %d characters (+10 DS each).", n)
end

handlers[1004] = function(ctx) -- Purification Song
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE characters SET is_diseased=0, is_poisoned=0 WHERE current_room_id=?", { room_id })
    end
    return "Your purification song cleanses disease and poison from the area."
end

handlers[1005] = function(ctx) -- Lullabye
    if not ctx.result.hit then return end
    local sdur = 10 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 8)
    ActiveBuffs.apply(tid(ctx), 1005, CIRCLE_ID, ctx.caster.id, sdur, { asleep=true, immobilized=true })
    DB.execute("UPDATE characters SET position='sleeping' WHERE id=?", { tid(ctx) })
    return string.format("Your soothing lullabye sends %s into a deep slumber!", tname(ctx))
end

handlers[1006] = function(ctx) -- Song of Luck
    local n = buff_room(ctx, 1006, { luck_bonus=10 })
    return string.format("Your luck song brightens fortune for %d nearby characters.", n)
end

handlers[1007] = function(ctx) -- Kai's Triumph Song
    local as_bonus = 10 + math.floor((ctx.circle_ranks or 1) / 5)
    local n = buff_room(ctx, 1007, { as_bonus=as_bonus })
    return string.format("Kai's triumph song empowers %d allies (+%d AS)!", n, as_bonus)
end

handlers[1008] = function(ctx) -- Stunning Shout
    if not ctx.result.hit then return end
    local sdur = 3 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 15)
    ActiveBuffs.apply(tid(ctx), 1008, CIRCLE_ID, ctx.caster.id, sdur, { stunned=true })
    return string.format("Your shout STUNS %s with sonic force!", tname(ctx))
end

handlers[1009] = function(ctx) -- Sonic Shield Song
    ActiveBuffs.apply(ctx.caster.id, 1009, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { sonic_shield=true, ds=10 })
    return "A sonic shield forms around you from your own song."
end

handlers[1010] = function(ctx) -- Song of Valor
    local n = buff_room(ctx, 1010, { ds=15, fear_immune=true })
    return string.format("Your valor song fills %d hearts with courage and resolve!", n)
end

handlers[1011] = function(ctx) -- Song of Peace
    local room_id = ctx.caster.current_room_id
    local calmed = 0
    if room_id then
        local creatures = DB.query("SELECT id FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        for _, c in ipairs(creatures) do
            ActiveBuffs.apply(c.id, 1011, CIRCLE_ID, ctx.caster.id, 30, { calmed=true })
            calmed = calmed + 1
        end
    end
    return string.format("Your song of peace calms %d creatures in the area.", calmed)
end

handlers[1012] = function(ctx) -- Sonic Weapon Song
    local room_id = ctx.caster.current_room_id
    local affected = 0
    if room_id then
        local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
        for _, a in ipairs(allies) do
            DB.execute([[
                UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.sonic_imbued',1)
                WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
            ]], { a.id })
            affected = affected + 1
        end
    end
    return string.format("Sonic energy hums through %d allies' weapons!", affected)
end

handlers[1013] = function(ctx) -- Song of Unravelling
    if not ctx.result.hit then return end
    local n_rem = 1 + math.floor((ctx.circle_ranks or 1) / 5)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid(ctx), n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format("Your unravelling song strips %d buff(s) from %s!", #buffs, tname(ctx))
end

handlers[1014] = function(ctx) -- Sonic Armor
    ActiveBuffs.apply(ctx.caster.id, 1014, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { sonic_armor=true, armor_asg_override=13, hindrance_redux=50 })
    return "Sonic vibrations solidify into a suit of resonant armor around you."
end

handlers[1015] = function(ctx) -- Song of Depression
    if not ctx.result.hit then return end
    local ddur = 15 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 1015, CIRCLE_ID, ctx.caster.id, ddur,
        { depressed=true, as_penalty=20, cs_all=-20 })
    return string.format("A crushing song of despair envelops %s!", tname(ctx))
end

handlers[1016] = function(ctx) -- Song of Rage
    if not ctx.result.hit then return end
    local rdur = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 1016, CIRCLE_ID, ctx.caster.id, rdur, { frenzied=true, random_target=true })
    return string.format("%s erupts into a murderous rage, lashing out wildly!", tname(ctx))
end

handlers[1017] = function(ctx) -- Song of Noise
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE rooms SET has_noise=1, noise_expires=DATE_ADD(NOW(), INTERVAL ? SECOND) WHERE id=?",
            { dur(ctx), room_id })
        local hidden = DB.query("SELECT id FROM characters WHERE current_room_id=? AND is_hidden=1", { room_id })
        for _, h in ipairs(hidden) do
            DB.execute("UPDATE characters SET is_hidden=0 WHERE id=?", { h.id })
        end
    end
    return "A cacophony of noise fills the area, ruining all attempts at stealth!"
end

handlers[1018] = function(ctx) -- Song of Power
    local cs_bonus = 5 + math.floor((ctx.circle_ranks or 1) / 4)
    local n = buff_room(ctx, 1018, { cs_all=cs_bonus, regen_bonus=2 })
    return string.format("Your song of power amplifies magic for %d spellcasters (+%d CS)!", n, cs_bonus)
end

handlers[1019] = function(ctx) -- Song of Mirrors
    ActiveBuffs.apply(ctx.caster.id, 1019, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { sonic_mirrors=true, bolt_deflect_chance=15 })
    return "Sonic mirrors materialize around you, ready to deflect incoming bolts."
end

handlers[1020] = function(ctx) -- Traveler's Song
    local n = buff_room(ctx, 1020, { movement_bonus=true, rt_reduction=1 })
    return string.format("Your traveler's song quickens the steps of %d companions.", n)
end

handlers[1025] = function(ctx) -- Singing Sword Song
    local swings = 20 + (ctx.circle_ranks or 1) * 2
    DB.execute([[
        UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.sonic_singing',1,'$.sonic_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, ctx.caster.id })
    return string.format("Your blade sings with sonic power (%d swings).", swings)
end

handlers[1030] = function(ctx) -- Song of Sonic Disruption bolt
    if not ctx.result.hit then return end
    local dmg = math.max(15, math.floor((ctx.result.total or 101) - 100) * 2)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A devastating sonic disruption TEARS through %s for %d damage!", tname(ctx), dmg)
end

handlers[1035] = function(ctx) -- Song of Tonis
    local n = buff_room(ctx, 1035, { ds=20, rt_reduction=1 })
    return string.format("Tonis's wind fills %d souls with speed and grace!", n)
end

handlers[1040] = function(ctx) -- Troubadour's Rally
    local room_id = ctx.caster.current_room_id
    if room_id then
        local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
        local hp_grant = 10 + (ctx.circle_ranks or 1)
        for _, a in ipairs(allies) do
            DB.execute("UPDATE characters SET health_current=LEAST(health_max,health_current+?) WHERE id=?",
                { hp_grant, a.id })
            ActiveBuffs.remove_spell(a.id, 9906) -- fear
        end
        return string.format("Your rally restores %d HP to %d allies and removes their fear!", hp_grant, #allies)
    end
end

function Bar.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Bar] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Bar
