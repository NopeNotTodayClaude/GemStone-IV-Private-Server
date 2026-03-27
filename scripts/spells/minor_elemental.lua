------------------------------------------------------------------------
-- scripts/spells/minor_elemental.lua
-- Minor Elemental (MnE) spell circle — spells 401-435.
-- Circle id: 4 | Sphere: elemental | CS/TD stat: aura
-- Available to: Warrior, Rogue, Wizard, Sorcerer, Bard
-- Source: gswiki.play.net/Minor_Elemental
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local MnE = {}

local CIRCLE_ID  = 4
local LUA_SCRIPT = "spells/minor_elemental"

local SPELLS = {
    [401] = { name="Elemental Defense I",       mnemonic="ED1",              spell_type="buff",    mana_cost=4,
              description="Adds +10 elemental DS. Stackable defensive buff." },
    [402] = { name="Presence",                  mnemonic="PRESENCE",         spell_type="buff",    mana_cost=2,
              description="Makes the caster detectable/visible to magical senses. Duration +2 sec per caster level." },
    [403] = { name="Lock Pick Enhancement",     mnemonic="LPE",              spell_type="buff",    mana_cost=3,
              description="Enhances Picking Locks skill. Duration and bonus scale with ranks and caster level." },
    [404] = { name="Disarm Enhancement",        mnemonic="DE",               spell_type="buff",    mana_cost=4,
              description="Enhances Disarming Traps skill. Duration and bonus scale with ranks and caster level." },
    [405] = { name="Elemental Detection",       mnemonic="ELEDETECT",        spell_type="utility", mana_cost=5,
              description="Detects magical auras and elemental properties of objects and creatures in the area." },
    [406] = { name="Elemental Defense II",      mnemonic="ED2",              spell_type="buff",    mana_cost=6,
              description="Adds +15 elemental DS. Stackable with ED1." },
    [407] = { name="Unlock",                    mnemonic="UNLOCK",           spell_type="utility", mana_cost=7,
              description="Magically unlocks a locked container or door. Success improves with caster level." },
    [408] = { name="Disarm",                    mnemonic="DISARM",           spell_type="utility", mana_cost=8,
              description="Magically disarms a trap. Success improves with caster level and ranks." },
    [409] = { name="Elemental Blast",           mnemonic="ELEBLAST",         spell_type="bolt",    mana_cost=9,
              description="element:impact. A focused blast of elemental energy." },
    [410] = { name="Elemental Wave",            mnemonic="ELEWAVE",          spell_type="maneuver",mana_cost=10,
              description="Pushes back all targets in the room with a wave of elemental force. Success scales with ranks and level." },
    [411] = { name="Elemental Blade",           mnemonic="ELEBLADE",         spell_type="buff",    mana_cost=11,
              description="Imbues a weapon with elemental energy for (20 + MnE_ranks × 3) swings." },
    [412] = { name="Weapon Deflection",         mnemonic="WEAPONDEFLECT",    spell_type="maneuver",mana_cost=12,
              description="SMR maneuver that disarms the target's weapon from their grasp." },
    [413] = { name="Elemental Saturation",      mnemonic="ELESATURATION",    spell_type="warding", mana_cost=13,
              description="Warding attack that saturates the target with elemental energy, reducing their resistance." },
    [414] = { name="Elemental Defense III",     mnemonic="ED3",              spell_type="buff",    mana_cost=14,
              description="Adds +20 elemental DS. Stackable with ED1 and ED2." },
    [415] = { name="Elemental Strike",          mnemonic="ELESTRIKE",        spell_type="bolt",    mana_cost=15,
              description="element:lightning. Powerful directed elemental strike." },
    [416] = { name="Piercing Gaze",             mnemonic="PIERCINGGAZE",     spell_type="utility", mana_cost=16,
              description="Allows the caster to see through illusions, invisibility, and magical concealments." },
    [417] = { name="Elemental Dispel",          mnemonic="ELEDISPEL",        spell_type="warding", mana_cost=17,
              description="Warding attack that dispels active elemental buffs from the target." },
    [418] = { name="Mana Focus",                mnemonic="MANAFOCUS",        spell_type="utility", mana_cost=18,
              description="Creates a mana focusing crystal that accelerates mana regeneration in an area." },
    [419] = { name="Mass Elemental Defense",    mnemonic="MED",              spell_type="buff",    mana_cost=19,
              description="Applies elemental defense to all allies in the room simultaneously." },
    [420] = { name="Magic Item Creation",       mnemonic="MIC",              spell_type="utility", mana_cost=20,
              description="Creates a single-use magic item (wand or similar) charged with an elemental spell." },
    [425] = { name="Elemental Targeting",       mnemonic="ELETARGETING",     spell_type="buff",    mana_cost=25,
              description="+AS and +CS per 2 ranks above 25, max +50 at 75 ranks. Elemental hybrid circles get half bonus." },
    [430] = { name="Elemental Barrier",         mnemonic="ELEBARRIER",       spell_type="buff",    mana_cost=30,
              description="Adds +DS and +TD per 2 ranks above 30. Powerful stacking elemental defense." },
    [435] = { name="Major Elemental Wave",      mnemonic="MAJELEWAVE",       spell_type="maneuver",mana_cost=35,
              description="Massive room-wide elemental wave. Greater damage and success than Elemental Wave. Rank scales damage." },
}

function MnE.seed()
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

handlers[401] = function(ctx)
    ActiveBuffs.apply(tid(ctx), 401, CIRCLE_ID, ctx.caster.id, dur(ctx), { td_elemental=10, ds=10 })
    return string.format("An elemental barrier shimimmers around %s.", tname(ctx))
end

handlers[402] = function(ctx)
    local d = 60 + (ctx.caster.level or 1) * 2
    ActiveBuffs.apply(tid(ctx), 402, CIRCLE_ID, ctx.caster.id, d, { magical_presence=true })
    return "Your magical presence is made clear."
end

handlers[403] = function(ctx)
    local bonus = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    local d = dur(ctx) + (ctx.caster.level or 1)
    ActiveBuffs.apply(tid(ctx), 403, CIRCLE_ID, ctx.caster.id, d, { picking_locks_bonus=bonus })
    return string.format("Your lock-picking ability is enhanced by %d.", bonus)
end

handlers[404] = function(ctx)
    local bonus = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    local d = dur(ctx) + (ctx.caster.level or 1)
    ActiveBuffs.apply(tid(ctx), 404, CIRCLE_ID, ctx.caster.id, d, { disarming_traps_bonus=bonus })
    return string.format("Your trap-disarming ability is enhanced by %d.", bonus)
end

handlers[405] = function(ctx) -- Detection — report auras in room (stub)
    return "Your senses extend, detecting elemental auras in the area."
end

handlers[406] = function(ctx)
    ActiveBuffs.apply(tid(ctx), 406, CIRCLE_ID, ctx.caster.id, dur(ctx), { td_elemental=15, ds=15 })
    return string.format("A stronger elemental barrier envelops %s.", tname(ctx))
end

handlers[407] = function(ctx) -- Unlock
    if ctx.target then
        DB.execute([[
            UPDATE character_inventory
            SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.is_locked',false)
            WHERE id=? AND JSON_EXTRACT(extra_data,'$.is_locked')=true
        ]], { ctx.target.id })
    end
    return "With a quiet click, the lock yields to elemental force."
end

handlers[408] = function(ctx) -- Disarm
    return "You sense and neutralize the magical trap."
end

handlers[409] = function(ctx) -- Elemental Blast bolt
    if not ctx.result.hit then return end
    local dmg = math.max(1, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("An elemental blast strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[410] = function(ctx) -- Elemental Wave — SMR room push
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute(
            "UPDATE characters SET position='prone' WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id }
        )
    end
    return "An elemental wave surges through the room, knocking foes prone!"
end

handlers[411] = function(ctx) -- Elemental Blade
    local swings = 20 + (ctx.circle_ranks or 1) * 3
    DB.execute([[
        UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.elemental_blade',1,'$.ele_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, tid(ctx) })
    return string.format("Elemental energy crackles through the weapon of %s (%d swings).", tname(ctx), swings)
end

handlers[412] = function(ctx) -- Weapon Deflection — SMR disarm
    if not ctx.result.hit then return end
    DB.execute([[
        UPDATE character_inventory SET slot='ground'
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { tid(ctx) })
    return string.format("The weapon flies from %s's grasp!", tname(ctx))
end

handlers[413] = function(ctx) -- Elemental Saturation
    if not ctx.result.hit then return end
    local sdur = 10 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 413, CIRCLE_ID, ctx.caster.id, sdur, { td_elemental=-15 })
    return string.format("%s is saturated with elemental energy, reducing their resistance!", tname(ctx))
end

handlers[414] = function(ctx)
    ActiveBuffs.apply(tid(ctx), 414, CIRCLE_ID, ctx.caster.id, dur(ctx), { td_elemental=20, ds=20 })
    return string.format("A powerful elemental defense surrounds %s.", tname(ctx))
end

handlers[415] = function(ctx) -- Elemental Strike bolt (lightning)
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A lightning strike crackles through %s for %d damage!", tname(ctx), dmg)
end

handlers[416] = function(ctx) -- Piercing Gaze
    ActiveBuffs.apply(tid(ctx), 416, CIRCLE_ID, ctx.caster.id, dur(ctx), { see_invisible=true, see_hidden=true })
    return "Your gaze pierces through illusions and concealment."
end

handlers[417] = function(ctx) -- Elemental Dispel
    if not ctx.result.hit then return end
    local n_rem = 1 + math.floor((ctx.circle_ranks or 1) / 10)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND circle_id IN (4,5,8,9)
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid(ctx), n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format("Elemental dispel strips %d buff(s) from %s.", #buffs, tname(ctx))
end

handlers[418] = function(ctx) -- Mana Focus — regen bonus
    ActiveBuffs.apply(tid(ctx), 418, CIRCLE_ID, ctx.caster.id, dur(ctx), { regen_bonus=3 })
    return "A mana focus crystallizes, accelerating mana regeneration."
end

handlers[419] = function(ctx) -- Mass Elemental Defense — group ED
    local room_id = ctx.caster.current_room_id
    if room_id then
        local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
        for _, a in ipairs(allies) do
            ActiveBuffs.apply(a.id, 419, CIRCLE_ID, ctx.caster.id, dur(ctx), { td_elemental=10, ds=10 })
        end
        return string.format("Elemental defense washes over %d characters in the area.", #allies)
    end
end

handlers[420] = function(ctx) -- Magic Item Creation (stub)
    return "You channel elemental energy into an item, imbuing it with a single charge."
end

handlers[425] = function(ctx) -- Elemental Targeting
    local bonus = math.min(50, math.floor(math.max(0, (ctx.circle_ranks or 0) - 25) / 2))
    ActiveBuffs.apply(tid(ctx), 425, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=bonus, cs_elemental=bonus })
    return string.format("Elemental targeting sharpens the aim of %s (+%d AS/CS).", tname(ctx), bonus)
end

handlers[430] = function(ctx) -- Elemental Barrier
    local bonus = math.max(0, math.floor(math.max(0, (ctx.circle_ranks or 0) - 30) / 2))
    ActiveBuffs.apply(tid(ctx), 430, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=bonus, td_elemental=bonus })
    return string.format("An elemental barrier of %d DS/%d TD forms around %s.", bonus, bonus, tname(ctx))
end

handlers[435] = function(ctx) -- Major Elemental Wave — room AoE
    if not ctx.result.hit then return end
    local room_id = ctx.caster.current_room_id
    local hit_count = 0
    if room_id then
        local targets = DB.query(
            "SELECT id, health_current FROM characters WHERE current_room_id=? AND id!=?",
            { room_id, ctx.caster.id })
        local dmg = 15 + (ctx.circle_ranks or 1)
        for _, t in ipairs(targets) do
            local new_hp = math.max(0, (t.health_current or 0) - dmg)
            DB.execute("UPDATE characters SET health_current=?, position='prone' WHERE id=?",
                { new_hp, t.id })
            hit_count = hit_count + 1
        end
    end
    return string.format("A massive elemental wave crashes through the room, striking %d targets!", hit_count)
end

function MnE.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[MnE] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return MnE
