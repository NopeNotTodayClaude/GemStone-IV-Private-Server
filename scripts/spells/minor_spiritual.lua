------------------------------------------------------------------------
-- scripts/spells/minor_spiritual.lua
-- Minor Spiritual (MnS) spell circle — spells 101-140.
-- Circle id: 1 | Sphere: spiritual | CS/TD stat: wisdom
-- Available to: Warrior, Rogue, Cleric, Empath, Sorcerer, Ranger, Paladin, Monk
-- Source: gswiki.play.net/Minor_Spiritual, Category:Minor_Spiritual_Spells
--
-- seed()     → Upserts all MnS spell rows into the `spells` table.
-- on_cast(ctx) → Dispatches to per-spell handler tables.
--
-- Duration formula for stackable buffs: 60 sec × circle_ranks
-- (per wiki: "All stackable/refreshable defensive spells last +60 sec per rank")
------------------------------------------------------------------------

local DB         = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local MnS = {}

local CIRCLE_ID  = 1
local LUA_SCRIPT = "spells/minor_spiritual"

-- ── Spell definitions ─────────────────────────────────────────────────
-- mana_cost: rank is the default (spell_number % 100), overridden where
-- the wiki specifies a different cost.
local SPELLS = {
    [101] = { name="Spirit Warding I",    mnemonic="SPIRITWARDING1",
              spell_type="buff",    mana_cost=4,
              description="Adds +10 spiritual TD and +10 bolt DS. Duration scales with circle ranks." },
    [102] = { name="Spirit Barrier",      mnemonic="SPIRITBARRIER",
              spell_type="buff",    mana_cost=5,
              description="Adds +20 DS, imposes -20 AS on melee/ranged/unarmed attackers. Self-cast limited unless target is warded." },
    [103] = { name="Spirit Defense",      mnemonic="SPIRITDEFENSE",
              spell_type="buff",    mana_cost=3,
              description="Adds +10 DS. Stackable when self-cast, refreshable on others." },
    [104] = { name="Disease Resistance",  mnemonic="DISEASERESISTANCE",
              spell_type="buff",    mana_cost=4,
              description="Provides additional warding against disease attacks." },
    [105] = { name="Poison Resistance",   mnemonic="POISONRESISTANCE",
              spell_type="buff",    mana_cost=5,
              description="Provides additional warding against poison attacks." },
    [106] = { name="Spirit Fog",          mnemonic="SPIRITFOG",
              spell_type="buff",    mana_cost=6,
              description="A shroud of ethereal fog provides enhanced dodge and Stalking/Hiding bonus." },
    [107] = { name="Spirit Warding II",   mnemonic="SPIRITWARDING2",
              spell_type="buff",    mana_cost=9,
              description="Adds +15 spiritual TD and +25 bolt DS. Requires Spirit Warding I active for full effect." },
    [108] = { name="Stun Relief",         mnemonic="STUNRELIEF",
              spell_type="utility", mana_cost=8,
              description="Removes the stun status effect from the target." },
    [109] = { name="Dispel Invisibility", mnemonic="DISPELINVISIBILITY",
              spell_type="utility", mana_cost=9,
              description="Reveals hidden and invisible creatures and characters in the room." },
    [110] = { name="Unbalance",           mnemonic="UNBALANCE",
              spell_type="warding", mana_cost=10,
              description="Warding attack that may knock the target down and/or stun them." },
    [111] = { name="Fire Spirit",         mnemonic="FIRESPIRIT",
              spell_type="bolt",    mana_cost=11,
              description="element:fire. A spirit of fire that attacks the target." },
    [112] = { name="Water Walking",       mnemonic="WATERWALKING",
              spell_type="buff",    mana_cost=12,
              description="Allows the target to walk on water surfaces without penalty. Prevents slowdown in marshy areas." },
    [113] = { name="Undisease",           mnemonic="UNDISEASE",
              spell_type="utility", mana_cost=13,
              description="Cures a disease condition from the target." },
    [114] = { name="Unpoison",            mnemonic="UNPOISON",
              spell_type="utility", mana_cost=14,
              description="Neutralizes a poison condition from the target." },
    [115] = { name="Fasthr's Reward",     mnemonic="FASTHRSREWARD",
              spell_type="buff",    mana_cost=15,
              description="Grants a second chance to resist a failed warding attack. Self-cast limited." },
    [116] = { name="Locate Person",       mnemonic="LOCATEPERSON",
              spell_type="utility", mana_cost=16,
              description="Locates a named character in the world and reports their general area." },
    [117] = { name="Spirit Strike",       mnemonic="SPIRITSTRIKE",
              spell_type="buff",    mana_cost=17,
              description="Grants +75 AS for one successful strike or 2 minutes. Non-stackable." },
    [118] = { name="Web",                 mnemonic="WEB",
              spell_type="warding", mana_cost=18,
              description="Warding attack that roots and heavily immobilizes the target in spiritual webbing." },
    [119] = { name="Spirit Dispel",       mnemonic="SPIRITDISPEL",
              spell_type="utility", mana_cost=19,
              description="Removes active spiritual buffs from the target. Number of buffs removed scales with MnS ranks." },
    [120] = { name="Lesser Shroud",       mnemonic="LESSERSHROUD",
              spell_type="buff",    mana_cost=20,
              description="Surrounds the target in a shroud of spiritual energy granting +25 DS." },
    [125] = { name="Call Lightning",      mnemonic="CALLLIGHTNING",
              spell_type="bolt",    mana_cost=25,
              description="element:lightning. Calls lightning from the sky to strike the target." },
    [130] = { name="Spirit Guide",        mnemonic="SPIRITGUIDE",
              spell_type="utility", mana_cost=30,
              description="Guides a slain character's spirit back to the nearest sanctuary for recall." },
    [135] = { name="Searing Light",       mnemonic="SEARINGLIGHT",
              spell_type="bolt",    mana_cost=35,
              description="element:fire. A blast of searing spiritual light strikes the target and may affect nearby opponents." },
    [140] = { name="Wall of Force",       mnemonic="WALLOFFORCE",
              spell_type="buff",    mana_cost=40,
              description="Creates a wall of spiritual force around the target granting significant DS. Fixed duration (not rank-scaled)." },
}

-- ── Seed function ──────────────────────────────────────────────────────
function MnS.seed()
    for num, sp in pairs(SPELLS) do
        DB.execute([[
            INSERT INTO spells
                (spell_number, name, mnemonic, circle_id, spell_type, mana_cost, description, lua_script)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name), mnemonic=VALUES(mnemonic),
                spell_type=VALUES(spell_type), mana_cost=VALUES(mana_cost),
                description=VALUES(description), lua_script=VALUES(lua_script)
        ]], { num, sp.name, sp.mnemonic, CIRCLE_ID, sp.spell_type,
              sp.mana_cost, sp.description, LUA_SCRIPT })
    end
end

-- ── Helper: buff duration ──────────────────────────────────────────────
local function buff_duration(ctx, override_secs)
    if override_secs then return override_secs end
    return 60 * math.max(1, ctx.circle_ranks or 1)
end

local function target_id(ctx)
    return ctx.target and ctx.target.id or ctx.caster.id
end

local function target_name(ctx)
    if ctx.target and ctx.target.id ~= ctx.caster.id then
        return ctx.target.name or "your target"
    end
    return "you"
end

-- ── Per-spell on_cast handlers ─────────────────────────────────────────
local handlers = {}

-- 101: Spirit Warding I — +10 spiritual TD, +10 bolt DS
handlers[101] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 101, CIRCLE_ID, ctx.caster.id, dur,
        { td_spiritual=10, ds=10 })
    return string.format("A white light briefly surrounds %s.", target_name(ctx))
end

-- 102: Spirit Barrier — +20 DS, -20 AS to attackers (self-cast limited)
handlers[102] = function(ctx)
    local dur = buff_duration(ctx)
    -- Self-cast only unless target is warded (simplified: allow freely)
    ActiveBuffs.apply(target_id(ctx), 102, CIRCLE_ID, ctx.caster.id, dur,
        { ds=20, attacker_as_penalty=20 })
    return string.format("A shimmering barrier of spiritual force encases %s.", target_name(ctx))
end

-- 103: Spirit Defense — +10 DS
handlers[103] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 103, CIRCLE_ID, ctx.caster.id, dur,
        { ds=10 })
    return string.format("A pale blue glow briefly surrounds %s.", target_name(ctx))
end

-- 104: Disease Resistance — +20 spiritual TD vs disease warding attacks
handlers[104] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 104, CIRCLE_ID, ctx.caster.id, dur,
        { td_spiritual=20, disease_resist=true })
    return string.format("The spiritual defenses of %s strengthen against disease.", target_name(ctx))
end

-- 105: Poison Resistance — +20 spiritual TD vs poison warding attacks
handlers[105] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 105, CIRCLE_ID, ctx.caster.id, dur,
        { td_spiritual=20, poison_resist=true })
    return string.format("The spiritual defenses of %s strengthen against poison.", target_name(ctx))
end

-- 106: Spirit Fog — dodge bonus, Stalking & Hiding bonus
handlers[106] = function(ctx)
    local dur    = buff_duration(ctx)
    local sh_bon = 5 + math.floor((ctx.circle_ranks or 1) / 5) -- +1 per 5 ranks
    ActiveBuffs.apply(target_id(ctx), 106, CIRCLE_ID, ctx.caster.id, dur,
        { dodge_bonus=5, stalking_hiding_bonus=sh_bon })
    return string.format("A swirling fog of spiritual energy wraps around %s.", target_name(ctx))
end

-- 107: Spirit Warding II — +15 spiritual TD, +25 bolt DS
handlers[107] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 107, CIRCLE_ID, ctx.caster.id, dur,
        { td_spiritual=15, ds=25 })
    return string.format("A brilliant white aura suffuses %s.", target_name(ctx))
end

-- 108: Stun Relief — remove stun
handlers[108] = function(ctx)
    local tid = target_id(ctx)
    DB.execute(
        "UPDATE characters SET position='standing' WHERE id=? AND position='stunned'",
        { tid }
    )
    ActiveBuffs.remove_spell(tid, 9900) -- internal stun effect ID
    return string.format("The stun gripping %s fades away.", target_name(ctx))
end

-- 109: Dispel Invisibility — reveal hidden/invisible in room
handlers[109] = function(ctx)
    local room_id = ctx.caster.current_room_id
    if room_id then
        DB.execute(
            "UPDATE characters SET is_hidden=0 WHERE current_room_id=? AND is_hidden=1",
            { room_id }
        )
    end
    return "A wave of revealing light ripples through the area."
end

-- 110: Unbalance — warding knockdown
handlers[110] = function(ctx)
    if not ctx.result.hit then
        return ctx.result.message
    end
    local tid = target_id(ctx)
    -- Apply prone + stun (duration based on warding result margin)
    local margin = math.max(0, (ctx.result.total or 101) - 100)
    local stun_dur = math.floor(margin / 10) + 1
    ActiveBuffs.apply(tid, 9901, nil, ctx.caster.id, stun_dur,
        { prone=true, stunned=true })
    DB.execute("UPDATE characters SET position='prone' WHERE id=?", { tid })
    return string.format(
        "%s is knocked off balance and falls to the ground!",
        ctx.target and ctx.target.name or "Your target"
    )
end

-- 111: Fire Spirit — bolt (fire); damage handled by bolt_resolver
handlers[111] = function(ctx)
    if not ctx.result.hit then return end
    local tid = target_id(ctx)
    local dmg = math.max(1, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid })
    return string.format(
        "A spirit of fire streaks toward %s and scorches them for %d damage!",
        ctx.target and ctx.target.name or "your target", dmg
    )
end

-- 112: Water Walking — utility buff
handlers[112] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 112, CIRCLE_ID, ctx.caster.id, dur,
        { water_walking=true })
    return string.format("%s can now walk on water.", target_name(ctx))
end

-- 113: Undisease — remove disease
handlers[113] = function(ctx)
    local tid = target_id(ctx)
    DB.execute("UPDATE characters SET is_diseased=0 WHERE id=?", { tid })
    ActiveBuffs.remove_spell(tid, 9902) -- disease debuff effect
    return string.format("The disease afflicting %s is purged.", target_name(ctx))
end

-- 114: Unpoison — remove poison
handlers[114] = function(ctx)
    local tid = target_id(ctx)
    DB.execute("UPDATE characters SET is_poisoned=0 WHERE id=?", { tid })
    ActiveBuffs.remove_spell(tid, 9903) -- poison debuff effect
    return string.format("The poison afflicting %s is neutralized.", target_name(ctx))
end

-- 115: Fasthr's Reward — second warding chance
handlers[115] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 115, CIRCLE_ID, ctx.caster.id, dur,
        { warding_second_chance=true })
    return string.format(
        "Fasthr's grace shields %s, granting a second chance against warding attacks.",
        target_name(ctx)
    )
end

-- 116: Locate Person — utility (requires a name argument; ctx.target may be nil)
handlers[116] = function(ctx)
    -- Locate is handled by command layer; on_cast just confirms the cast succeeded
    return "Your spiritual senses reach outward across the land..."
end

-- 117: Spirit Strike — +75 AS for one strike (non-stackable)
handlers[117] = function(ctx)
    -- Duration: 2 minutes flat per wiki
    ActiveBuffs.apply(target_id(ctx), 117, CIRCLE_ID, ctx.caster.id, 120,
        { as_bonus=75, one_strike_only=true })
    return string.format(
        "The spirit of %s is channeled into a single devastating strike!",
        target_name(ctx)
    )
end

-- 118: Web — warding immobilization
handlers[118] = function(ctx)
    if not ctx.result.hit then return end
    local margin   = math.max(0, (ctx.result.total or 101) - 100)
    local web_dur  = 5 + math.floor(margin / 5)
    ActiveBuffs.apply(target_id(ctx), 118, CIRCLE_ID, ctx.caster.id, web_dur,
        { webbed=true, immobilized=true })
    return string.format(
        "Strands of spiritual webbing erupt and wrap tightly around %s!",
        ctx.target and ctx.target.name or "your target"
    )
end

-- 119: Spirit Dispel — remove buffs from target
handlers[119] = function(ctx)
    local tid   = target_id(ctx)
    local n_rem = 1 + math.floor((ctx.circle_ranks or 1) / 10)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND circle_id IN (1,2,3)
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid, n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format(
        "Spiritual energy disperses %d active effect(s) from %s.",
        #buffs, target_name(ctx)
    )
end

-- 120: Lesser Shroud — +25 DS
handlers[120] = function(ctx)
    local dur = buff_duration(ctx)
    ActiveBuffs.apply(target_id(ctx), 120, CIRCLE_ID, ctx.caster.id, dur,
        { ds=25 })
    return string.format(
        "A shroud of shimmering spiritual energy surrounds %s.",
        target_name(ctx)
    )
end

-- 125: Call Lightning — bolt (lightning); impact via bolt_resolver
handlers[125] = function(ctx)
    if not ctx.result.hit then return end
    local dmg    = math.max(1, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?",
        { new_hp, target_id(ctx) })
    return string.format(
        "A searing bolt of lightning strikes %s for %d damage!",
        ctx.target and ctx.target.name or "your target", dmg
    )
end

-- 130: Spirit Guide — guide spirit to nearest sanctuary
handlers[130] = function(ctx)
    -- Marks target spirit for recall-point transport; actual transport
    -- is handled by the death/recall system.
    if ctx.target then
        DB.execute(
            "UPDATE characters SET spirit_guided=1 WHERE id=?",
            { ctx.target.id }
        )
    end
    return "A gentle spiritual current reaches out to guide the fallen soul homeward."
end

-- 135: Searing Light — bolt (fire)
handlers[135] = function(ctx)
    if not ctx.result.hit then return end
    local dmg    = math.max(1, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?",
        { new_hp, target_id(ctx) })
    return string.format(
        "Searing spiritual light engulfs %s for %d damage!",
        ctx.target and ctx.target.name or "your target", dmg
    )
end

-- 140: Wall of Force — +50 DS, fixed 600s duration
handlers[140] = function(ctx)
    -- Wiki: fixed duration, not rank-scaled
    ActiveBuffs.apply(target_id(ctx), 140, CIRCLE_ID, ctx.caster.id, 600,
        { ds=50 })
    return string.format(
        "An invisible wall of pure spiritual force encompasses %s.",
        target_name(ctx)
    )
end

-- ── Main dispatch ─────────────────────────────────────────────────────
function MnS.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            -- msg is the error string; log via print (re-routed to Python logger)
            print(string.format("[MnS] on_cast error spell %d: %s",
                ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return MnS
