------------------------------------------------------------------------
-- scripts/spells/minor_mental.lua
-- Minor Mental (MnM) spell circle — spells 1201-1235.
-- Circle id: 12 | Sphere: mental | CS stat: logic | TD stat: discipline
-- Available to: Monk (and eventually Savant)
-- Source: gswiki.play.net/Minor_Mental
--
-- TD stat is Discipline (not the caster's Logic used for CS).
-- Defensive buffs: +60 sec per rank.
-- Mindward (1208): +1 TD per 2 ranks above 8, max +40 TD at 48 ranks.
-- Premonition (1220): +1 DS per 2 ranks above 20.
------------------------------------------------------------------------

local DB          = require("globals/utils/db")
local ActiveBuffs = require("globals/magic/active_buffs")

local MnM = {}

local CIRCLE_ID  = 12
local LUA_SCRIPT = "spells/minor_mental"

local SPELLS = {
    [1201] = { name="Soothing Word",       mnemonic="SOOTHINGWORD",     spell_type="utility", mana_cost=1,
               description="A calming word that removes the stun condition and reduces emotional distress." },
    [1202] = { name="Iron Skin",           mnemonic="IRONSKIN",         spell_type="buff",    mana_cost=2,
               description="Mental focus hardens the skin granting natural armor equivalent to leather." },
    [1203] = { name="Powersink",           mnemonic="POWERSINK",        spell_type="warding", mana_cost=3,
               description="Warding attack that siphons mana from the target and disrupts their spellcasting." },
    [1204] = { name="Foresight",           mnemonic="FORESIGHT",        spell_type="buff",    mana_cost=4,
               description="Mental foresight grants a DS bonus by anticipating enemy actions." },
    [1205] = { name="Glamour",             mnemonic="GLAMOUR",          spell_type="utility", mana_cost=5,
               description="Creates a mental glamour altering the caster's apparent appearance." },
    [1206] = { name="Telekinesis",         mnemonic="TELEKINESIS",      spell_type="warding", mana_cost=6,
               description="Warding attack using telekinetic force to throw or crush the target." },
    [1207] = { name="Force Projection",    mnemonic="FORCEPROJECTION",  spell_type="maneuver",mana_cost=7,
               description="SMR maneuver projecting pure mental force. Rank increases knockdown chance." },
    [1208] = { name="Mindward",            mnemonic="MINDWARD",         spell_type="buff",    mana_cost=8,
               description="+1 TD per 2 ranks above 8, max +40 TD at 48 ranks. Primary mental TD buff." },
    [1209] = { name="Dragonclaw",          mnemonic="DRAGONCLAW",       spell_type="buff",    mana_cost=9,
               description="Focuses mental energy into a chi-driven strike, greatly enhancing unarmed/brawling attacks." },
    [1210] = { name="Thought Lash",        mnemonic="THOUGHTLASH",      spell_type="bolt",    mana_cost=10,
               description="element:impact. A lash of raw mental energy causes neural pain and potential stun." },
    [1211] = { name="Confusion",           mnemonic="CONFUSION",        spell_type="warding", mana_cost=11,
               description="Warding attack that confuses the target, causing them to act erratically." },
    [1212] = { name="Shroud of Deception", mnemonic="SHROUDDECEPTION",  spell_type="utility", mana_cost=12,
               description="Creates a mental shroud making the caster appear as something else entirely." },
    [1213] = { name="Mind over Body",      mnemonic="MINDOVERBODY",     spell_type="utility", mana_cost=13,
               description="Overrides physical limitations through mental discipline, ignoring minor wounds." },
    [1214] = { name="Brace",               mnemonic="BRACE",            spell_type="buff",    mana_cost=14,
               description="Mental bracing against incoming force, reducing knockdown and maneuver damage." },
    [1215] = { name="Blink",               mnemonic="BLINK",            spell_type="buff",    mana_cost=15,
               description="Rapid mental prediction causes the monk to blink out of harm's way, granting DS." },
    [1216] = { name="Focus Barrier",       mnemonic="FOCUSBARRIER",     spell_type="buff",    mana_cost=16,
               description="A focused mental barrier providing strong TD and DS bonuses." },
    [1217] = { name="Vision",              mnemonic="VISION",           spell_type="utility", mana_cost=17,
               description="Grants a mental vision of a distant place or entity the caster knows." },
    [1218] = { name="Mental Dispel",       mnemonic="MENTALDISPEL",     spell_type="utility", mana_cost=18,
               description="Dispels active mental buffs from the target. Number removed scales with MnM ranks." },
    [1219] = { name="Vertigo",             mnemonic="VERTIGO",          spell_type="warding", mana_cost=19,
               description="Warding attack that causes disorienting vertigo, imposing heavy AS/DS penalties." },
    [1220] = { name="Premonition",         mnemonic="PREMONITION",      spell_type="buff",    mana_cost=20,
               description="+1 DS per 2 ranks above 20. Mental precognition of incoming attacks." },
    [1225] = { name="Mindwipe",            mnemonic="MINDWIPE",         spell_type="warding", mana_cost=25,
               description="Warding attack wiping the target's short-term memory and disorienting them severely." },
    [1235] = { name="Provoke",             mnemonic="PROVOKE",          spell_type="utility", mana_cost=35,
               description="Mentally provokes a creature, forcing it to target the caster instead of others." },
}

function MnM.seed()
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

handlers[1201] = function(ctx) -- Soothing Word
    local id = tid(ctx)
    DB.execute("UPDATE characters SET position='standing' WHERE id=? AND position='stunned'", { id })
    ActiveBuffs.remove_spell(id, 9900) -- stun debuff
    return string.format("A soothing word calms %s, relieving the stun.", tname(ctx))
end

handlers[1202] = function(ctx) -- Iron Skin
    ActiveBuffs.apply(tid(ctx), 1202, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { iron_skin=true, armor_asg_override=6, natural_padding=true })
    return string.format("Mental focus hardens the skin of %s like iron.", tname(ctx))
end

handlers[1203] = function(ctx) -- Powersink
    if not ctx.result.hit then return end
    local transference = (ctx.lore_ranks and ctx.lore_ranks.transference) or 0
    local drained = math.min(ctx.target.mana_current or 0,
        math.floor((ctx.result.total or 101) - 100) + (ctx.circle_ranks or 1) + math.floor(transference / 15))
    DB.execute("UPDATE characters SET mana_current=MAX(0,mana_current-?) WHERE id=?",
        { drained, tid(ctx) })
    ActiveBuffs.apply(tid(ctx), 1203, CIRCLE_ID, ctx.caster.id, 15,
        { silenced=true, hindrance_penalty=25 })
    return string.format("A powersink drains %d mana from %s and disrupts their casting!", drained, tname(ctx))
end

handlers[1204] = function(ctx) -- Foresight
    local divination = (ctx.lore_ranks and ctx.lore_ranks.divination) or 0
    local ds_bonus = 10 + math.floor((ctx.circle_ranks or 1) / 5) + math.floor(divination / 20)
    ActiveBuffs.apply(tid(ctx), 1204, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("Foresight sharpens %s's defenses (+%d DS).", tname(ctx), ds_bonus)
end

handlers[1205] = function(ctx) -- Glamour
    ActiveBuffs.apply(ctx.caster.id, 1205, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { glamoured=true, disguised=true })
    return "A mental glamour shifts your apparent form."
end

handlers[1206] = function(ctx) -- Telekinesis
    if not ctx.result.hit then return end
    local dmg = math.max(5, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=?, position='prone' WHERE id=?", { new_hp, tid(ctx) })
    return string.format("Telekinetic force HURLS %s aside for %d damage!", tname(ctx), dmg)
end

handlers[1207] = function(ctx) -- Force Projection
    if not ctx.result.hit then return end
    local margin = math.max(0, (ctx.result.total or 101) - 100)
    local kdur   = math.floor(margin / 20) + 1
    DB.execute("UPDATE characters SET position='prone' WHERE id=?", { tid(ctx) })
    ActiveBuffs.apply(tid(ctx), 1207, CIRCLE_ID, ctx.caster.id, kdur, { prone=true })
    return string.format("A projection of pure mental force slams %s to the ground!", tname(ctx))
end

handlers[1208] = function(ctx) -- Mindward
    local telepathy = (ctx.lore_ranks and ctx.lore_ranks.telepathy) or 0
    local td_bonus = math.min(40, math.floor(math.max(0, (ctx.circle_ranks or 0) - 8) / 2) + math.floor(telepathy / 20))
    ActiveBuffs.apply(tid(ctx), 1208, CIRCLE_ID, ctx.caster.id, dur(ctx), { td_mental=td_bonus })
    return string.format("A mindward of mental discipline surrounds %s (+%d TD).", tname(ctx), td_bonus)
end

handlers[1209] = function(ctx) -- Dragonclaw
    local as_bonus = 20 + math.floor((ctx.circle_ranks or 1) / 3)
    local swings   = 10 + (ctx.circle_ranks or 1) * 2
    ActiveBuffs.apply(tid(ctx), 1209, CIRCLE_ID, ctx.caster.id, 60,
        { as_bonus=as_bonus, dragonclaw=true, dragonclaw_swings=swings })
    return string.format("Chi-focused power blazes through %s's strikes (+%d AS for %d swings)!",
        tname(ctx), as_bonus, swings)
end

handlers[1210] = function(ctx) -- Thought Lash bolt
    if not ctx.result.hit then return end
    local dmg = math.max(3, math.floor((ctx.result.total or 101) - 100))
    local new_hp = math.max(0, (ctx.target.health_current or 0) - dmg)
    DB.execute("UPDATE characters SET health_current=? WHERE id=?", { new_hp, tid(ctx) })
    -- Small stun chance on high result
    if (ctx.result.total or 0) > 130 then
        ActiveBuffs.apply(tid(ctx), 9920, nil, ctx.caster.id, 3, { stunned=true })
    end
    return string.format("A thought lash sears through %s's mind for %d damage!", tname(ctx), dmg)
end

handlers[1211] = function(ctx) -- Confusion
    if not ctx.result.hit then return end
    local manipulation = (ctx.lore_ranks and ctx.lore_ranks.manipulation) or 0
    local cdur = 10 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5) + math.floor(manipulation / 20)
    ActiveBuffs.apply(tid(ctx), 1211, CIRCLE_ID, ctx.caster.id, cdur,
        { confused=true, as_penalty=20, ds_penalty=20, random_target=true })
    return string.format("Mental confusion FLOODS %s's mind!", tname(ctx))
end

handlers[1212] = function(ctx) -- Shroud of Deception
    ActiveBuffs.apply(ctx.caster.id, 1212, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { shroud_deception=true, perception_penalty_to_others=20 })
    return "A shroud of deception warps how others perceive you."
end

handlers[1213] = function(ctx) -- Mind over Body
    local transformation = (ctx.lore_ranks and ctx.lore_ranks.transformation) or 0
    ActiveBuffs.apply(ctx.caster.id, 1213, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { mind_over_body=true, minor_wound_ignore=true, pain_resist=true, stamina_regen=1 + math.floor(transformation / 25) })
    return "Your mind overrides physical limitations through sheer discipline."
end

handlers[1214] = function(ctx) -- Brace
    local bonus = 10 + math.floor((ctx.circle_ranks or 1) / 4)
    ActiveBuffs.apply(tid(ctx), 1214, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=bonus, knockdown_resist=true, maneuver_resist=bonus })
    return string.format("%s braces against incoming force (+%d DS).", tname(ctx), bonus)
end

handlers[1215] = function(ctx) -- Blink
    local ds_bonus = 15 + math.floor((ctx.circle_ranks or 1) / 4)
    ActiveBuffs.apply(tid(ctx), 1215, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=ds_bonus, blink=true })
    return string.format("%s blinks rapidly, evading attacks (+%d DS).", tname(ctx), ds_bonus)
end

handlers[1216] = function(ctx) -- Focus Barrier
    local bonus = 15 + math.floor((ctx.circle_ranks or 1) / 3)
    ActiveBuffs.apply(tid(ctx), 1216, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { ds=bonus, td_mental=bonus })
    return string.format("A focused mental barrier surrounds %s (+%d DS, +%d TD).",
        tname(ctx), bonus, bonus)
end

handlers[1217] = function(ctx) -- Vision (stub)
    return "A mental vision unfolds in your mind, revealing a distant place..."
end

handlers[1218] = function(ctx) -- Mental Dispel
    local n_rem = 1 + math.floor((ctx.circle_ranks or 1) / 5)
    local buffs = DB.query([[
        SELECT id FROM character_active_buffs
        WHERE character_id=? AND circle_id IN (12,13,14)
          AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY applied_at ASC LIMIT ?
    ]], { tid(ctx), n_rem })
    for _, row in ipairs(buffs) do
        DB.execute("DELETE FROM character_active_buffs WHERE id=?", { row.id })
    end
    return string.format("Mental dispel strips %d mental buff(s) from %s.", #buffs, tname(ctx))
end

handlers[1219] = function(ctx) -- Vertigo
    if not ctx.result.hit then return end
    local vdur = 10 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5)
    ActiveBuffs.apply(tid(ctx), 1219, CIRCLE_ID, ctx.caster.id, vdur,
        { vertigo=true, as_penalty=30, ds_penalty=30 })
    return string.format("Crushing vertigo overwhelms %s!", tname(ctx))
end

handlers[1220] = function(ctx) -- Premonition
    local divination = (ctx.lore_ranks and ctx.lore_ranks.divination) or 0
    local ds_bonus = math.floor(math.max(0, (ctx.circle_ranks or 0) - 20) / 2) + math.floor(divination / 25)
    ActiveBuffs.apply(tid(ctx), 1220, CIRCLE_ID, ctx.caster.id, dur(ctx), { ds=ds_bonus })
    return string.format("Premonition of incoming attacks sharpens %s's defenses (+%d DS).",
        tname(ctx), ds_bonus)
end

handlers[1225] = function(ctx) -- Mindwipe
    if not ctx.result.hit then return end
    local wdur = 15 + math.floor(math.max(0, (ctx.result.total or 101) - 100) / 5)
    ActiveBuffs.apply(tid(ctx), 1225, CIRCLE_ID, ctx.caster.id, wdur,
        { mindwiped=true, confused=true, as_penalty=30, ds_penalty=30, silenced=true })
    return string.format("A mindwipe ERASES %s's short-term memory and disorienting them completely!", tname(ctx))
end

handlers[1235] = function(ctx) -- Provoke
    if not ctx.target then return end
    ActiveBuffs.apply(tid(ctx), 1235, CIRCLE_ID, ctx.caster.id, dur(ctx),
        { provoked=true, provoked_target=ctx.caster.id })
    return string.format("Mental provocation forces %s to fixate on you!", tname(ctx))
end

function MnM.on_cast(ctx)
    local h = handlers[ctx.spell.spell_number]
    if h then
        local ok, msg = pcall(h, ctx)
        if ok and type(msg) == "string" then
            ctx.result.message = (ctx.result.message or "") .. "\n" .. msg
        elseif not ok then
            print(string.format("[MnM] on_cast error spell %d: %s", ctx.spell.spell_number, tostring(msg)))
        end
    end
end

return MnM
