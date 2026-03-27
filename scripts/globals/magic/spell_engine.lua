------------------------------------------------------------------------
-- scripts/globals/magic/spell_engine.lua
-- Central spell casting dispatcher for GemStone IV.
------------------------------------------------------------------------

local DB           = require("globals/utils/db")
local Mana         = require("globals/magic/mana_system")
local SpellCircles = require("globals/magic/spell_circles")
local CS_R         = require("globals/magic/cs_resolver")
local Warding      = require("globals/magic/warding_resolver")
local Bolt         = require("globals/magic/bolt_resolver")
local SMR          = require("globals/magic/smr_resolver")
local ActiveBuffs  = require("globals/magic/active_buffs")

local SpellEngine = {}

-- prepared[character_id] = { spell_number=N, expires=os.time()+30, spell_ranks={} }
local prepared = {}

local PREPARE_EXPIRE_SECS = 30

local function load_spell(spell_number)
    return DB.queryOne(
        "SELECT * FROM spells WHERE spell_number=?",
        { spell_number }
    )
end

local function load_spell_ranks(character_id)
    return CS_R.load_spell_ranks(character_id)
end

local function load_skill_rank(character_id, skill_id)
    local row = DB.queryOne(
        "SELECT ranks FROM character_skills WHERE character_id=? AND skill_id=?",
        { character_id, skill_id }
    )
    return row and (row.ranks or 0) or 0
end

local function validate_known(char, spell_number, spell_ranks)
    local circle = SpellCircles.primary_for_spell(spell_number)
    if not circle then
        return false, "That is not a valid spell number."
    end

    -- Arcane Blast is natively available to pures without Spell Research.
    if circle.id == 15 and spell_number == 1700 then
        local pure_professions = {
            [3] = true, -- Wizard
            [4] = true, -- Cleric
            [5] = true, -- Empath
            [6] = true, -- Sorcerer
            [11] = true, -- Savant (future-facing local id)
        }
        if pure_professions[char.profession_id] then
            return true, nil
        end
        return false, "Only pures can natively cast Arcane Blast."
    end

    if not SpellCircles.can_train(char.profession_id, circle.id) then
        return false, "Your profession cannot cast spells from that circle."
    end

    local spell_rank = spell_number % 100
    local known_ranks = (spell_ranks and spell_ranks[circle.id]) or 0
    if known_ranks < spell_rank then
        return false, string.format(
            "You have not yet researched %s spell #%d.",
            circle.name, spell_number
        )
    end

    local char_level = char.level or 1
    if spell_rank > char_level then
        return false, string.format(
            "You must be at least level %d to cast that spell.",
            spell_rank
        )
    end

    return true, nil
end

function SpellEngine.prepare(char, spell_arg)
    local spell_number

    if type(spell_arg) == "number" then
        spell_number = spell_arg
    else
        local numeric = tonumber(spell_arg)
        if numeric then
            spell_number = numeric
        else
            local row = DB.queryOne(
                "SELECT spell_number FROM spells WHERE UPPER(mnemonic)=UPPER(?) OR UPPER(name)=UPPER(?)",
                { spell_arg, spell_arg }
            )
            if not row then
                return false, string.format("You do not recognize \"%s\" as a spell.", spell_arg)
            end
            spell_number = row.spell_number
        end
    end

    local spell_ranks = load_spell_ranks(char.id)
    local ok, reason  = validate_known(char, spell_number, spell_ranks)
    if not ok then
        return false, reason
    end

    prepared[char.id] = {
        spell_number = spell_number,
        expires      = os.time() + PREPARE_EXPIRE_SECS,
        spell_ranks  = spell_ranks,
    }

    local spell = load_spell(spell_number)
    local name  = spell and spell.name or ("Spell " .. spell_number)
    return true, string.format(
        "You begin to prepare the %s spell.  Your spell is ready.", name
    )
end

function SpellEngine.release(char)
    if not prepared[char.id] then
        return false, "You have no spell prepared."
    end

    local sn = prepared[char.id].spell_number
    prepared[char.id] = nil
    local spell = load_spell(sn)
    local name  = spell and spell.name or ("Spell " .. sn)
    return true, string.format("You release the %s spell.", name)
end

local function resolve_activation_type(char, spell, spell_number, verb)
    local stype = spell.spell_type or "utility"
    if spell_number == 1700 then
        if verb == "evoke" or verb == "channel" then
            return "bolt"
        end
        if char.position == "guarded" or char.position == "defensive" then
            return "warding"
        end
        return "bolt"
    end
    return stype
end

local function run_spell_script(spell, cast_ctx, result)
    if not spell.lua_script or spell.lua_script == "" or result.blocked or result.fumble then
        return
    end

    local script_ok, spell_mod = pcall(require, spell.lua_script)
    if not script_ok or type(spell_mod) ~= "table" or not spell_mod.on_cast then
        return
    end

    local hook_ok, hook_result = pcall(spell_mod.on_cast, cast_ctx)
    if not hook_ok then
        return
    end

    if type(hook_result) == "string" and (not result.message or result.message == "") then
        result.message = hook_result
    elseif type(hook_result) == "table" and hook_result.message and (not result.message or result.message == "") then
        result.message = hook_result.message
    end
end

local function activate(char, target, spell_number, spell_ranks, verb, skip_mana)
    local spell = load_spell(spell_number)
    if not spell then
        return false, "That spell is not yet implemented."
    end

    local mana_cost = spell.mana_cost or (spell_number % 100)
    if not skip_mana then
        local ok, injured = Mana.deduct(char.mana_current or 0, mana_cost)
        if not ok then
            if injured then
                return false, "You strain to cast the spell but lack the mana, damaging yourself!"
            end
            return false, "You do not have enough mana to cast that spell."
        end

        local new_mana = (char.mana_current or 0) - mana_cost
        Mana.save_mana(char.id, new_mana)
        char.mana_current = new_mana
    end

    local armor_use_ranks    = load_skill_rank(char.id, 2)
    local spell_aiming_ranks = load_skill_rank(char.id, 17)
    local emc_ranks          = load_skill_rank(char.id, 19)
    local smc_ranks          = load_skill_rank(char.id, 20)
    local mmc_ranks          = load_skill_rank(char.id, 21)
    local mc_bonus           = math.max(emc_ranks, smc_ranks, mmc_ranks)
    local lore_ranks = {
        blessings      = load_skill_rank(char.id, 33),
        religion       = load_skill_rank(char.id, 34),
        summoning      = load_skill_rank(char.id, 35),
        air            = load_skill_rank(char.id, 36),
        earth          = load_skill_rank(char.id, 37),
        fire           = load_skill_rank(char.id, 38),
        water          = load_skill_rank(char.id, 39),
        manipulation   = load_skill_rank(char.id, 40),
        telepathy      = load_skill_rank(char.id, 41),
        transference   = load_skill_rank(char.id, 42),
        divination     = load_skill_rank(char.id, 44),
        transformation = load_skill_rank(char.id, 45),
        demonology     = load_skill_rank(char.id, 46),
        necromancy     = load_skill_rank(char.id, 47),
    }
    local mana_control = {
        elemental = emc_ranks,
        spirit    = smc_ranks,
        mental    = mmc_ranks,
    }

    local caster_asg   = char.torso_armor_asg or 1
    local target_asg   = target and target.torso_armor_asg or 1
    local in_sanctuary = char.in_sanctuary or false
    local circle       = SpellCircles.primary_for_spell(spell_number)
    local circle_ranks = (spell_ranks and circle and spell_ranks[circle.id]) or 0

    local result
    local stype = resolve_activation_type(char, spell, spell_number, verb or "cast")

    if stype == "bolt" then
        local element = (spell.description or ""):match("element:(%w+)") or "impact"
        local target_ds = 0
        if target then
            target_ds = target.ranged_ds or target.ds_ranged or 0
        end
        result = Bolt.resolve(
            char, target, spell_number, spell_aiming_ranks,
            target_ds, element, target_asg, caster_asg,
            armor_use_ranks, in_sanctuary
        )
    elseif stype == "warding" then
        result = Warding.resolve(
            char, target, spell_number, spell_ranks,
            caster_asg, armor_use_ranks, in_sanctuary, target_asg
        )
    elseif stype == "maneuver" then
        local conditions = target and target.conditions or {}
        result = SMR.resolve(
            char, target, spell_number, circle_ranks,
            spell_aiming_ranks, mc_bonus, false,
            conditions, caster_asg, armor_use_ranks, in_sanctuary
        )
    elseif stype == "buff" or stype == "healing" or stype == "utility" or stype == "summon" then
        result = { hit=true, blocked=false, fumble=false, message="" }
    else
        result = { hit=false, blocked=false, fumble=false, message="That spell type is not yet implemented." }
    end

    run_spell_script(spell, {
        caster       = char,
        target       = target,
        result       = result,
        verb         = verb,
        spell        = spell,
        circle_ranks = circle_ranks,
        lore_ranks   = lore_ranks,
        mana_control = mana_control,
    }, result)

    return true, result.message or "", result
end

function SpellEngine.cast_direct(char, target, spell_number, verb, spell_ranks, skip_mana)
    local ranks = spell_ranks or load_spell_ranks(char.id)
    return activate(char, target, spell_number, ranks, verb or "cast", skip_mana)
end

function SpellEngine.cast(char, target, verb)
    verb = verb or "cast"
    local state = prepared[char.id]
    if not state then
        return false, "You have no spell prepared."
    end

    if os.time() > state.expires then
        prepared[char.id] = nil
        return false, "Your spell fades before you can cast it."
    end

    local spell_number = state.spell_number
    local spell_ranks  = state.spell_ranks
    prepared[char.id]  = nil

    return activate(char, target, spell_number, spell_ranks, verb, false)
end

function SpellEngine.incant(char, spell_arg, target, verb)
    local ok, msg = SpellEngine.prepare(char, spell_arg)
    if not ok then
        return false, msg
    end
    return SpellEngine.cast(char, target, verb or "cast")
end

function SpellEngine.tick()
    local now = os.time()
    for cid, state in pairs(prepared) do
        if now > state.expires then
            prepared[cid] = nil
        end
    end
    ActiveBuffs.purge_expired()
end

return SpellEngine
