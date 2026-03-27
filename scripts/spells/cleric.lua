------------------------------------------------------------------------
-- scripts/spells/cleric.lua
-- Cleric Base (Cle) spell circle — spells 301-350.
-- Circle id: 3 | Sphere: spiritual | CS/TD stat: wisdom
-- Available to: Cleric only
-- Source: gswiki.play.net/Cleric_Base
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local Cle = {}

local CIRCLE_ID  = 3
local LUA_SCRIPT = "spells/cleric"

local SPELLS = {
    [301] = { name="Prayer of Holding",      mnemonic="PRAYEROFHOLDING",    spell_type="warding", mana_cost=1,
              description="Warding attack that holds the target motionless in a prayerful grip." },
    [302] = { name="Smite/Bane",             mnemonic="SMITE",               spell_type="warding", mana_cost=2,
              description="Warding attack. Smite vs undead; Bane vs demons/constructs. Extremely effective vs those types." },
    [303] = { name="Prayer of Protection",   mnemonic="PRAYEROFPROTECTION",  spell_type="buff",    mana_cost=3,
              description="Adds +10 DS (+1 per 2 ranks above 3). Stackable defensive prayer." },
    [304] = { name="Bless",                  mnemonic="BLESS",               spell_type="buff",    mana_cost=4,
              description="Blesses a weapon, adding holy flares. Rank scaling adds swings and holy water flares at 25 ranks." },
    [305] = { name="Preservation",           mnemonic="PRESERVATION",        spell_type="utility", mana_cost=5,
              description="Preserves a corpse against decay, extending the window for resurrection." },
    [306] = { name="Holy Bolt",              mnemonic="HOLYBOLT",            spell_type="bolt",    mana_cost=6,
              description="element:impact. A bolt of holy energy. Highly effective against undead." },
    [307] = { name="Benediction",            mnemonic="BENEDICTION",         spell_type="buff",    mana_cost=7,
              description="Grants +AS and +DS (+1 each per 2 ranks above 7, max +15 at 27). Group-capable." },
    [308] = { name="Well of Life",           mnemonic="WELLOFLIFE",          spell_type="utility", mana_cost=8,
              description="Creates a minor life ward. If the recipient falls below 0 HP, the ward triggers to restore some health." },
    [309] = { name="Condemn",                mnemonic="CONDEMN",             spell_type="warding", mana_cost=9,
              description="Warding attack condemning the target, inflicting progressive spiritual damage." },
    [310] = { name="Warding Sphere",         mnemonic="WARDINGSPHERE",       spell_type="buff",    mana_cost=10,
              description="Adds +DS and +TD scaling with ranks (max +10/+10 at 20 ranks)." },
    [311] = { name="Blind",                  mnemonic="BLIND",               spell_type="warding", mana_cost=11,
              description="Warding attack that blinds the target, applying heavy AS/DS penalties." },
    [312] = { name="Fervent Reproach",       mnemonic="FERVENTREPROACH",     spell_type="warding", mana_cost=12,
              description="Warding attack with holy fire. Very effective against undead and evil beings." },
    [313] = { name="Prayer",                 mnemonic="PRAYER",              spell_type="buff",    mana_cost=13,
              description="Devotional prayer granting +DS (+1 per rank above 35). Stackable with most defenses." },
    [314] = { name="Relieve Burden",         mnemonic="RELIEVEBURDEN",       spell_type="utility", mana_cost=14,
              description="Reduces encumbrance penalty. Can temporarily allow a character to carry more." },
    [315] = { name="Remove Curse",           mnemonic="REMOVECURSE",         spell_type="utility", mana_cost=15,
              description="Removes a curse from the target. Higher ranks allow removal of more potent curses." },
    [316] = { name="Censure",                mnemonic="CENSURE",             spell_type="warding", mana_cost=16,
              description="Warding attack using divine censure. Inflicts spiritual damage and may stun." },
    [317] = { name="Divine Fury",            mnemonic="DIVINEFURY",          spell_type="warding", mana_cost=17,
              description="Warding attack channeling divine wrath. Enhanced damage against undead and demonic foes." },
    [318] = { name="Raise Dead",             mnemonic="RAISEDEAD",           spell_type="utility", mana_cost=18,
              description="Restores a dead character to life. At 25 ranks becomes Life Restoration; at 40 becomes Resurrection." },
    [319] = { name="Soul Ward",              mnemonic="SOULWARD",            spell_type="buff",    mana_cost=19,
              description="Powerful defensive ward protecting the spirit. Provides TD and resistance to death effects." },
    [320] = { name="Ethereal Censer",        mnemonic="ETHEREALCENSER",      spell_type="warding", mana_cost=20,
              description="Summons a holy censer that attacks undead and purifies the area of evil influence." },
    [325] = { name="Holy Receptacle",        mnemonic="HOLYRECEPTACLE",      spell_type="utility", mana_cost=25,
              description="Imbues holy water into a container, creating a powerful sanctified liquid weapon against undead." },
    [330] = { name="Sanctify",               mnemonic="SANCTIFY",            spell_type="utility", mana_cost=30,
              description="Sanctifies an area or object, purifying it of evil influence and creating a temporary holy ground." },
    [335] = { name="Divine Wrath",           mnemonic="DIVINEWRATH",         spell_type="bolt",    mana_cost=35,
              description="element:impact. Devastating channeled divine wrath. AoE capable at high ranks." },
    [340] = { name="Symbol of the Proselyte",mnemonic="SYMBOLPROSELYTE",     spell_type="buff",    mana_cost=40,
              description="Powerful offensive buff granting massive AS bonus and holy weapon flares." },
    [350] = { name="Miracle",                mnemonic="MIRACLE",             spell_type="utility", mana_cost=50,
              description="Calls upon divine intervention for miraculous effects — resurrection, healing, or smiting evil." },
}

function Cle.seed()
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
local function is_undead(ctx) return ctx.target and (ctx.target.is_undead == 1 or ctx.target.is_undead == true) end

local handlers = {}

handlers[301] = function(ctx) -- Prayer of Holding
    if not ctx.result.hit then return end
    local hold_dur = 5 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 10)
    ActiveBuffs.apply(tid(ctx), 301, CIRCLE_ID, ctx.caster.id, hold_dur, { held=true, immobilized=true })
    return string.format("%s is held fast by a prayerful grip!", tname(ctx))
end

handlers[302] = function(ctx) -- Smite/Bane
    if not ctx.result.hit then return end
    local dmg_bonus = is_undead(ctx) and 50 or 15
    local dmg = math.max(1, math.floor((ctx.result.total or 101) - 100) + dmg_bonus)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    if is_undead(ctx) then
        return string.format("Divine smite scorches %s for %d damage!", tname(ctx), dmg)
    end
    return string.format("A bane strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[303] = function(ctx) -- Prayer of Protection
    local ds_bonus = 10 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 3) / 2)
    ActiveBuffs.apply(tid(ctx), 303, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("Divine protection shields %s.", tname(ctx))
end

handlers[304] = function(ctx) -- Bless
    -- Bless target's held weapon with holy flares
    local swings = 25 + (ctx.circle_ranks or 1) * 3
    DB.execute([[
        UPDATE character_inventory SET extra_data=JSON_SET(COALESCE(extra_data,'{}'),'$.holy_blessed',1,'$.bless_swings',?)
        WHERE character_id=? AND slot IN ('right_hand','left_hand') LIMIT 1
    ]], { swings, tid(ctx) })
    return string.format("The weapon of %s glows with holy light.", tname(ctx))
end

handlers[305] = function(ctx) -- Preservation
    if not ctx.target then return end
    DB.execute("UPDATE characters SET body_preserved=1, preserve_expires=DATE_ADD(NOW(), INTERVAL 3600 SECOND) WHERE id=?",
        { tid(ctx) })
    return string.format("A preserving aura settles over the remains of %s.", tname(ctx))
end

handlers[306] = function(ctx) -- Holy Bolt
    if not ctx.result.hit then return end
    local dmg = math.max(1, math.floor((ctx.result.total or 101) - 100))
    if is_undead(ctx) then dmg = math.floor(dmg * 1.5) end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("A bolt of holy energy strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[307] = function(ctx) -- Benediction
    local bonus = 7 + math.floor(math.max(0, (ctx.circle_ranks or 0) - 7) / 2)
    local capped = math.min(bonus, 15)
    ActiveBuffs.apply(tid(ctx), 307, CIRCLE_ID, ctx.caster.id, dur(ctx), { as_bonus=capped, ds=capped })
    return string.format("Benediction empowers %s.", tname(ctx))
end

handlers[308] = function(ctx) -- Well of Life
    local heal_amount = 20 + (ctx.circle_ranks or 1) * 2
    ActiveBuffs.apply(tid(ctx), 308, CIRCLE_ID, ctx.caster.id, dur(ctx), { life_ward=heal_amount })
    return string.format("A well of life forms around %s, ready to sustain them.", tname(ctx))
end

handlers[309] = function(ctx) -- Condemn
    if not ctx.result.hit then return end
    local dmg = math.max(1, math.floor((ctx.result.total or 101) - 100) * 2)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Divine condemnation strikes %s for %d damage!", tname(ctx), dmg)
end

handlers[310] = function(ctx) -- Warding Sphere
    local bonus = math.min(10, math.floor((ctx.circle_ranks or 0) / 2))
    ActiveBuffs.apply(tid(ctx), 310, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=bonus, td_spiritual=bonus })
    return string.format("A warding sphere of divine energy protects %s.", tname(ctx))
end

handlers[311] = function(ctx) -- Blind
    if not ctx.result.hit then return end
    local bdur = 10 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5)
    ActiveBuffs.apply(tid(ctx), 311, CIRCLE_ID, ctx.caster.id, bdur, { blinded=true })
    return string.format("Divine light blinds %s!", tname(ctx))
end

handlers[312] = function(ctx) -- Fervent Reproach
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    if is_undead(ctx) then dmg = dmg * 2 end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Holy flames of fervent reproach lash %s for %d damage!", tname(ctx), dmg)
end

handlers[313] = function(ctx) -- Prayer
    local ds_bonus = math.max(0, math.floor(math.max(0, (ctx.circle_ranks or 0) - 35)))
    ActiveBuffs.apply(tid(ctx), 313, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("A quiet prayer strengthens the defenses of %s.", tname(ctx))
end

handlers[314] = function(ctx) -- Relieve Burden
    ActiveBuffs.apply(tid(ctx), 314, CIRCLE_ID, ctx.caster.id, dur(ctx), { burden_relief=50 })
    return string.format("The burden on %s is eased by divine grace.", tname(ctx))
end

handlers[315] = function(ctx) -- Remove Curse
    ActiveBuffs.remove_spell(tid(ctx), 715) -- Curse spell
    DB.execute("UPDATE characters SET is_cursed=0 WHERE id=?", { tid(ctx) })
    return string.format("The curse afflicting %s is dissolved.", tname(ctx))
end

handlers[316] = function(ctx) -- Censure
    if not ctx.result.hit then return end
    local sdur = 3 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 15)
    ActiveBuffs.apply(tid(ctx), 316, CIRCLE_ID, ctx.caster.id, sdur, { stunned=true })
    return string.format("Divine censure strikes %s speechless!", tname(ctx))
end

handlers[317] = function(ctx) -- Divine Fury
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100) * 2)
    if is_undead(ctx) then dmg = math.floor(dmg * 1.75) end
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Divine fury descends upon %s for %d damage!", tname(ctx), dmg)
end

handlers[318] = function(ctx) -- Raise Dead
    if not ctx.target then return end
    local ranks = ctx.circle_ranks or 0
    if ctx.target.health_current and ctx.target.health_current <= 0 then
        local restore = ranks >= 40 and ctx.target.health_max or
                        ranks >= 25 and math.floor((ctx.target.health_max or 100) * 0.75) or
                        math.floor((ctx.target.health_max or 100) * 0.5)
        DB.execute("UPDATE characters SET health_current=?, position='standing' WHERE id=?",
            { restore, tid(ctx) })
        if ctx.caster and ctx.caster.id then
            local caster_rows = DB.query("SELECT id FROM characters WHERE id=? LIMIT 1", { ctx.caster.id })
            if caster_rows and caster_rows[1] then
                local fame_award = math.max(25, math.floor((ctx.target.level or 1) * 5))
                DB.execute("UPDATE characters SET fame = GREATEST(0, fame + ?) WHERE id=?", { fame_award, ctx.caster.id })
                DB.execute(
                    "INSERT INTO character_fame_ledger (character_id, amount, source_key, detail_text) VALUES (?, ?, ?, ?)",
                    { ctx.caster.id, fame_award, "resurrection", string.format("Resurrected %s.", tname(ctx)) }
                )
            end
        end
        return string.format("%s is raised from death, restored to %d health!", tname(ctx), restore)
    end
    return string.format("%s does not need raising.", tname(ctx))
end

handlers[319] = function(ctx) -- Soul Ward
    local td_bonus = 15 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 319, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { td_spiritual=td_bonus, death_resist=true })
    return string.format("A soul ward of divine light envelops %s.", tname(ctx))
end

handlers[320] = function(ctx) -- Ethereal Censer (room-wide undead attack)
    local room_id = ctx.caster.current_room_id
    if room_id then
        local undead = DB.query(
            "SELECT id, health_current FROM characters WHERE current_room_id=? AND is_undead=1",
            { room_id })
        for _, u in ipairs(undead) do
            local dmg = 20 + (ctx.circle_ranks or 1)
            DB.execute("UPDATE characters SET health_current=? WHERE id=?",
                { math.max(0, (u.health_current or 0) - dmg), u.id })
        end
        return string.format("An ethereal censer sweeps through the room, scorching %d undead!", #undead)
    end
end

handlers[325] = function(ctx) -- Holy Receptacle
    return "You imbue a container with holy water, sanctifying its contents."
end

handlers[330] = function(ctx) -- Sanctify
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE rooms SET is_holy=1, holy_expires=DATE_ADD(NOW(), INTERVAL 3600 SECOND) WHERE id=?",
            { room_id })
    end
    return "The ground is sanctified by divine will."
end

handlers[335] = function(ctx) -- Divine Wrath bolt
    if not ctx.result.hit then return end
    local dmg = math.max(10, math.floor((ctx.result.total or 101) - 100) * 2)
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Divine wrath EXPLODES upon %s for %d damage!", tname(ctx), dmg)
end

handlers[340] = function(ctx) -- Symbol of the Proselyte
    ActiveBuffs.apply(tid(ctx), 340, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { as_bonus=40, holy_flares=true })
    return string.format("The symbol of the proselyte blazes around %s!", tname(ctx))
end

handlers[350] = function(ctx) -- Miracle (conditional effects)
    local target = ctx.target
    if target and (target.health_current or 99) <= 0 then
        DB.execute("UPDATE characters SET health_current=health_max, position='standing' WHERE id=?",
            { tid(ctx) })
        return string.format("A miracle restores %s to full health!", tname(ctx))
    end
    -- Smite nearby undead
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute("UPDATE characters SET health_current=0 WHERE current_room_id=? AND is_undead=1", { room_id })
    end
    return "A divine miracle sweeps through the area, annihilating undead!"
end

function Cle.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[Cle] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return Cle
