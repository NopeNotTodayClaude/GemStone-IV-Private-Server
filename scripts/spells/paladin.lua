------------------------------------------------------------------------
-- scripts/spells/paladin.lua
-- Paladin Base (Pal) spell circle — spells 1601-1650.
-- Circle id: 11 | Sphere: spiritual | CS/TD stat: wisdom
-- Available to: Paladin only
-- Source: gswiki.play.net/Paladin_Base
--
-- Deity conversion (CONVERT verb) affects messaging and some mechanics.
-- Spell hindrance: Faith's Clarity (1612) reduces hindrance by 1% per 5
-- ranks, max 10% at 50 ranks; MnS hindrance also reduced to match.
-- All stackable/refreshable enhancement spells: +60 sec per rank.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local Pal = {}

local CIRCLE_ID  = 11
local LUA_SCRIPT = "spells/paladin"

local SPELLS = {
    [1601] = { name="Mantle of Faith",     mnemonic="MANTLEOFFAITH",    spell_type="buff",    mana_cost=1,
               description="Surrounds the paladin in divine light, granting DS. The paladin's foundational defense." },
    [1602] = { name="Pious Trial",         mnemonic="PIOUSTRIAL",       spell_type="warding", mana_cost=2,
               description="Warding attack that puts the target on trial before the paladin's deity. Duration +2 sec per rank." },
    [1603] = { name="Templar's Verdict",   mnemonic="TEMPLARSVERDICT",  spell_type="warding", mana_cost=3,
               description="Warding attack delivering the deity's verdict on the target. Heavy damage on success." },
    [1604] = { name="Consecrate",          mnemonic="CONSECRATE",       spell_type="utility", mana_cost=4,
               description="Consecrates a weapon with Guiding Light flares. Duration: 20 + (3 × rank) swings." },
    [1605] = { name="Arm of the Arkati",   mnemonic="ARMOFTHEARKATI",   spell_type="buff",    mana_cost=5,
               description="Divine arm of the paladin's patron grants +AS and enhanced melee combat." },
    [1606] = { name="Dauntless",           mnemonic="DAUNTLESS",        spell_type="buff",    mana_cost=6,
               description="Dauntless resolve grants immunity to fear and a significant AS bonus in combat." },
    [1607] = { name="Rejuvenation",        mnemonic="REJUVENATION",     spell_type="utility", mana_cost=7,
               description="Restores HP and stamina to the paladin or target through divine rejuvenation." },
    [1608] = { name="Defense of the Faithful", mnemonic="DOFFAITHFUL", spell_type="utility", mana_cost=8,
               description="Radiates divine defense to all allies in the room. +DS per 5 ranks to group." },
    [1609] = { name="Divine Shield",       mnemonic="DIVINESHIELD",     spell_type="buff",    mana_cost=9,
               description="Powerful personal divine shield. +DS per 5 ranks (max +20 at 43 ranks) granted to group." },
    [1610] = { name="Higher Vision",       mnemonic="HIGHERVISION",     spell_type="buff",    mana_cost=10,
               description="+1 DS per 2 ranks above 10, max +55 DS at 100 ranks. +1 MP per DS." },
    [1611] = { name="Patron's Blessing",   mnemonic="PATRONSBLESSING",  spell_type="buff",    mana_cost=11,
               description="+0.75 phantom CM ranks per rank above 11. +1 mana per 3 additional CM ranks." },
    [1612] = { name="Faith's Clarity",     mnemonic="FAITHSCLARITY",    spell_type="utility", mana_cost=12,
               description="Reduces spell hindrance by 1% per 5 ranks (max 10% at 50). Also reduces MnS hindrance to match." },
    [1613] = { name="Aid the Fallen",      mnemonic="AIDTHEFALLEN",     spell_type="utility", mana_cost=13,
               description="Divine aid to a fallen ally, stabilizing them and preventing further decay." },
    [1614] = { name="Aura of the Arkati",  mnemonic="AURAOFTHEARKATI",  spell_type="warding", mana_cost=14,
               description="Warding attack channeling the paladin's patron's aura against an enemy." },
    [1615] = { name="Repentance",          mnemonic="REPENTANCE",       spell_type="warding", mana_cost=15,
               description="Warding attack demanding the target repent. Undead and evil creatures suffer greatly." },
    [1616] = { name="Vigor",               mnemonic="VIGOR",            spell_type="buff",    mana_cost=16,
               description="+1 CON and +2 HP per 4 ranks, max +10 CON/+20 HP at 40 ranks." },
    [1617] = { name="Zealot",              mnemonic="ZEALOT",           spell_type="buff",    mana_cost=17,
               description="Zealous divine fury grants a significant AS bonus and reduces incoming CS." },
    [1618] = { name="Fervor",              mnemonic="FERVOR",           spell_type="buff",    mana_cost=18,
               description="Burning divine fervor grants enhanced offensive ability and holy flares." },
    [1619] = { name="Faith Shield",        mnemonic="FAITHSHIELD",      spell_type="buff",    mana_cost=19,
               description="A shield of pure faith. Duration +1 sec per 2 ranks above 19. Absorbs damage." },
    [1620] = { name="Battle Standard",     mnemonic="BATTLESTANDARD",   spell_type="utility", mana_cost=20,
               description="Plants a divine battle standard in the room, granting group bonuses to all allies." },
    [1625] = { name="Holy Weapon",         mnemonic="HOLYWEAPON",       spell_type="buff",    mana_cost=25,
               description="Bonds a weapon with the paladin's divine power. +1 max bonding level per rank (max 5 at 29)." },
    [1630] = { name="Judgment",            mnemonic="JUDGMENT",         spell_type="warding", mana_cost=30,
               description="Final divine judgment on the target. Devastating warding attack; maximally effective vs evil." },
    [1635] = { name="Divine Intervention", mnemonic="DIVINEINTERV",     spell_type="utility", mana_cost=35,
               description="Calls upon divine intervention to save the paladin or an ally from death or grievous harm." },
    [1640] = { name="Divine Word",         mnemonic="DIVINEWORD",       spell_type="utility", mana_cost=40,
               description="Speaks a divine word of tremendous power, capable of banishing undead and evil entities." },
    [1650] = { name="Divine Incarnation",  mnemonic="DIVINEINCARNATION",spell_type="utility", mana_cost=50,
               description="The paladin briefly incarnates divine power, gaining massive combat bonuses and healing." },
}

function Pal.seed()
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
local function is_undead_or_evil(ctx)
    return ctx.target and (ctx.target.is_undead == 1 or ctx.target.is_undead == true
        or ctx.target.creature_type == "demon")
end

-- Room ally buff helper
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

handlers[1601] = function(ctx) -- Mantle of Faith
    local ds_bonus = 10 + math.floor((ctx.circle_ranks or 1) / 5)
    ActiveBuffs.apply(tid(ctx), 1601, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus, td_spiritual=5 })
    return string.format("A mantle of divine faith settles upon %s (+%d DS).", tname(ctx), ds_bonus)
end

handlers[1602] = function(ctx) -- Pious Trial
    if not ctx.result.hit then return end
    local tdur = 2 + (ctx.circle_ranks or 1) * 2
    ActiveBuffs.apply(tid(ctx), 1602, CIRCLE_ID, ctx.caster.id, tdur,
        { on_trial=true, as_penalty=15, ds_penalty=15 })
    return string.format("%s is placed on divine trial!", tname(ctx))
end

handlers[1603] = function(ctx) -- Templar's Verdict
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100) * 2)
    if is_undead_or_evil(ctx) then dmg = math.floor(dmg * 1.5) end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("The Templar's verdict strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[1604] = function(ctx) -- Consecrate
    local swings = 20 + (ctx.circle_ranks or 1) * 3
    DB.execute([[
        UPDATE character_inventory
        SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.guiding_light',1,'$.consecrate_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, tid(ctx) })
    return string.format("A holy light consecrates the weapon of %s (%d swings).", tname(ctx), swings)
end

handlers[1605] = function(ctx) -- Arm of the Arkati
    local as_bonus = 15 + math.floor((ctx.circle_ranks or 1) / 5)
    ActiveBuffs.apply(tid(ctx), 1605, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=as_bonus, divine_arm=true })
    return string.format("The arm of the Arkati empowers %s (+%d AS)!", tname(ctx), as_bonus)
end

handlers[1606] = function(ctx) -- Dauntless
    ActiveBuffs.apply(tid(ctx), 1606, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { fear_immune=true, as_bonus=20, dauntless=true })
    return string.format("Dauntless resolve fills %s — fear has no hold here!", tname(ctx))
end

handlers[1607] = function(ctx) -- Rejuvenation
    local hp = 25 + (ctx.circle_ranks or 1) * 3
    local new_hp = math.min(ctx.target.health_max or 999, (ctx.target.health_current or 0) + hp)
    DB.execute("UPDATE characters SET health_current=?, stamina_current=LEAST(stamina_max,stamina_current+20) WHERE id=?",
        { new_hp, tid(ctx) })
    return string.format("Divine rejuvenation restores %d health to %s.", hp, tname(ctx))
end

handlers[1608] = function(ctx) -- Defense of the Faithful
    local ds_bonus = math.floor((ctx.circle_ranks or 1) / 5)
    local n = buff_room(ctx, 1608, { ds=ds_bonus })
    return string.format("Defense of the Faithful radiates to %d allies (+%d DS each).", n, ds_bonus)
end

handlers[1609] = function(ctx) -- Divine Shield — group
    local ds_bonus = math.min(20, math.floor(math.max(0, (ctx.circle_ranks or 0) - 9) / 5))
    local n = buff_room(ctx, 1609, { ds=ds_bonus })
    return string.format("A divine shield protects %d allies (+%d DS each).", n, ds_bonus)
end

handlers[1610] = function(ctx) -- Higher Vision
    local ds_bonus = math.min(55, math.floor(math.max(0, (ctx.circle_ranks or 0) - 10) / 2))
    ActiveBuffs.apply(tid(ctx), 1610, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("Higher vision grants %s divine sight (+%d DS).", tname(ctx), ds_bonus)
end

handlers[1611] = function(ctx) -- Patron's Blessing
    local phantom_cm = math.floor(math.max(0, (ctx.circle_ranks or 0) - 11) * 0.75)
    ActiveBuffs.apply(tid(ctx), 1611, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { phantom_cm=phantom_cm })
    return string.format("Your patron blesses %s with +%d phantom CM ranks.", tname(ctx), phantom_cm)
end

handlers[1612] = function(ctx) -- Faith's Clarity
    local redux = math.min(10, math.floor((ctx.circle_ranks or 1) / 5))
    ActiveBuffs.apply(tid(ctx), 1612, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { hindrance_redux=redux })
    return string.format("Faith's clarity reduces spell hindrance for %s by %d%%.", tname(ctx), redux)
end

handlers[1613] = function(ctx) -- Aid the Fallen
    if not ctx.target then return end
    if (ctx.target.health_current or 1) <= 0 then
        DB.execute("UPDATE characters SET health_current=1, position='kneeling' WHERE id=?", { tid(ctx) })
        return string.format("Divine aid stabilizes %s at 1 health.", tname(ctx))
    end
    return string.format("%s does not need aid at this time.", tname(ctx))
end

handlers[1614] = function(ctx) -- Aura of the Arkati
    if not ctx.result.hit then return end
    local dmg = math.max(8, math.floor((ctx.result.total or 101) - 100))
    if is_undead_or_evil(ctx) then dmg = math.floor(dmg * 1.75) end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("The Arkati's aura BLAZES through %s for %d damage!", tname(ctx), dmg)
end

handlers[1615] = function(ctx) -- Repentance
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100))
    if is_undead_or_evil(ctx) then dmg = dmg * 3 end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Repentance BURNS through %s for %d damage!", tname(ctx), dmg)
end

handlers[1616] = function(ctx) -- Vigor
    local con_bonus = math.min(10, math.floor((ctx.circle_ranks or 1) / 4))
    local hp_bonus  = con_bonus * 2
    ActiveBuffs.apply(tid(ctx), 1616, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { constitution_bonus=con_bonus, max_hp_bonus=hp_bonus })
    DB.execute("UPDATE characters SET health_max=health_max+?, health_current=health_current+? WHERE id=?",
        { hp_bonus, hp_bonus, tid(ctx) })
    return string.format("Vigor flows through %s (+%d CON, +%d max HP).", tname(ctx), con_bonus, hp_bonus)
end

handlers[1617] = function(ctx) -- Zealot
    ActiveBuffs.apply(tid(ctx), 1617, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=25, cs_reduction_shield=10, zealot=true })
    return string.format("Zealous divine fury courses through %s!", tname(ctx))
end

handlers[1618] = function(ctx) -- Fervor
    ActiveBuffs.apply(tid(ctx), 1618, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=20, holy_flares=true, fervor=true })
    return string.format("Divine fervor burns within %s, empowering every strike!", tname(ctx))
end

handlers[1619] = function(ctx) -- Faith Shield
    local sdur = 30 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 19) / 2)
    ActiveBuffs.apply(tid(ctx), 1619, CIRCLE_ID, ctx.caster.id, sdur,
        { faith_shield=true, damage_absorb=20, ds=20 })
    return string.format("A shield of pure faith materializes around %s for %d seconds.", tname(ctx), sdur)
end

handlers[1620] = function(ctx) -- Battle Standard
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute([[
            UPDATE rooms SET battle_standard=1, standard_expires=DATE_ADD(NOW(), INTERVAL ? SECOND) WHERE id=?
        ]], { dur(ctx), room_id })
        local allies = DB.query("SELECT id FROM characters WHERE current_room_id=?", { room_id })
        for _, a in ipairs(allies) do
            ActiveBuffs.apply(a.id, 1620, CIRCLE_ID, ctx.caster.id, dur(ctx),
                { as_bonus=10, ds=10, standard_nearby=true })
        end
        return string.format("A divine battle standard blazes in the room, inspiring %d allies!", #allies)
    end
end

handlers[1625] = function(ctx) -- Holy Weapon
    local bond_level = math.min(5, math.floor(math.max(0, (ctx.circle_ranks or 0) - 25)) + 1)
    DB.execute([[
        UPDATE character_inventory
        SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.holy_bonded',1,'$.bond_level',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { bond_level, tid(ctx) })
    return string.format("A holy weapon bond of level %d forms between %s and their weapon.", bond_level, tname(ctx))
end

handlers[1630] = function(ctx) -- Judgment
    if not ctx.result.hit then return end
    local dmg = math.max(20, math.floor((ctx.result.total or 101) - 100) * 3)
    if is_undead_or_evil(ctx) then dmg = math.floor(dmg * 2) end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("DIVINE JUDGMENT descends upon %s for %d damage!", tname(ctx), dmg)
end

handlers[1635] = function(ctx) -- Divine Intervention
    local target = ctx.target or ctx.caster
    if (target.health_current or 1) <= 0 then
        local restore = math.floor((target.health_max or 100) * 0.75)
        DB.execute("UPDATE characters SET health_current=?, position='standing' WHERE id=?",
            { restore, target.id })
        return string.format("Divine intervention restores %s from the brink!", target.name or "you")
    end
    -- Otherwise grant temporary invincibility
    ActiveBuffs.apply(target.id, 1635, CIRCLE_ID, ctx.caster.id, 10,
        { divine_intervention=true, damage_immune=true })
    return "Divine intervention shields you from all harm for a brief moment!"
end

handlers[1640] = function(ctx) -- Divine Word
    local room_id = ctx.caster.current_room_id
    if room_id then
        local undead = DB.query(
            "SELECT id, level FROM characters WHERE current_room_id=? AND is_undead=1",
            { room_id })
        local banished = 0
        for _, u in ipairs(undead) do
            if (u.level or 1) < (ctx.caster.level or 1) then
                DB.execute("UPDATE characters SET health_current=0 WHERE id=?", { u.id })
                banished = banished + 1
            end
        end
        return string.format("The Divine Word BANISHES %d undead from this place!", banished)
    end
end

handlers[1650] = function(ctx) -- Divine Incarnation
    local dur_secs = 30 + (ctx.circle_ranks or 1)
    ActiveBuffs.apply(ctx.caster.id, 1650, CIRCLE_ID, ctx.caster.id, dur_secs, {
        divine_incarnation = true,
        as_bonus           = 50,
        ds                 = 50,
        td_spiritual       = 50,
        regen_bonus        = 20,
        fear_immune        = true,
        holy_flares        = true,
    })
    return "Divine power INCARNATES through you! You blaze with the full might of your patron!"
end

function Pal.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Pal] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Pal
