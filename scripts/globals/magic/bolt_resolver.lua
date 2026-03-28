------------------------------------------------------------------------
-- scripts/globals/magic/bolt_resolver.lua
-- Bolt spell attack resolution for GemStone IV.
-- Source: gswiki.play.net/Magic — "Bolt Spells" section, /Spell_Aiming
--
-- Bolt spells produce magical projectiles (fireball, lightning bolt, etc.)
-- and use an AS vs DS attack roll — the same system as physical weapons.
--
-- Attack roll:
--   Result = AS - DS + AvD + d100
--   If Result > 100 → hit
--
-- AS (Attack Strength) for bolts:
--   Primarily driven by Spell Aiming skill bonus.
--   Stance modifier also applies (same as physical combat).
--
-- DS (Defense Strength):
--   Target's ranged defense — stance, shield (limited vs bolts), etc.
--
-- AvD (Attack vs Defense):
--   How well the bolt type penetrates the target's armor.
--   Varies by bolt element and armor ASG.
--
-- Display format (from wiki example):
--   AS: +297 vs DS: +116 with AvD: +37 + d100 roll: +97 = +315
--      ... and hit for 134 points of damage!
------------------------------------------------------------------------

local Hindrance    = require("globals/magic/spell_hindrance")
local SpellCircles = require("globals/magic/spell_circles")
local ActiveBuffs  = require("globals/magic/active_buffs")
local GS4Math      = require("globals/utils/gs4_math")

local Bolt = {}

-- ── AvD table for bolt spells vs armor ASG ───────────────────────────
-- Source: GS4 combat system; AvD for bolts differs by element type.
-- element: "fire" | "ice" | "lightning" | "acid" | "impact" | "void"
-- These values are approximate from GS4 documentation; per-spell overrides
-- can be defined in each spell's lua_script.
Bolt.avd_table = {
    -- { asg1, asg2 ... asg20 }
    fire      = { 52,52,47,47,47,47,42,42,37,37,37,37,22,22,22,22,12,12,12,12 },
    ice       = { 52,52,47,47,47,47,42,42,37,37,37,37,22,22,22,22,12,12,12,12 },
    lightning = { 52,52,47,47,47,47,42,42,42,42,42,42,37,37,37,37,32,32,32,32 },
    acid      = { 52,52,50,50,50,50,48,48,45,45,43,43,30,30,28,28,18,18,16,16 },
    impact    = { 52,52,47,47,47,47,42,42,37,37,37,37,22,22,22,22,12,12,12,12 },
    void      = { 60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60 },
}

-- ── Spell Aiming skill bonus ──────────────────────────────────────────
-- Each bonus point in Spell Aiming = +1 AS on bolt spells.
-- ── Stance AS modifier ────────────────────────────────────────────────
-- position: "offensive" | "advanced" | "neutral" | "guarded" | "defensive"
local STANCE_AS_MOD = {
    offensive = 30,
    advanced  = 15,
    neutral   = 0,
    guarded   = -15,
    defensive = -30,
}

local STANCE_DS_MOD = {
    offensive = -30,
    advanced  = -15,
    neutral   = 0,
    guarded   = 15,
    defensive = 30,
}

-- ── Calculate bolt AS ─────────────────────────────────────────────────
-- caster:           character row (.position for stance)
-- spell_aiming_ranks: caster's Spell Aiming ranks
-- as_override:      flat AS override from active buffs (e.g. Enhancement spells)
function Bolt.calculate_as(caster, spell_aiming_ranks, as_override)
    local base_as = GS4Math.skill_bonus_from_ranks(spell_aiming_ranks or 0)
    local stance  = STANCE_AS_MOD[caster.position or "neutral"] or 0
    local buff_as = (caster.id and ActiveBuffs.get_active(caster.id)) or {}
    local total_buff = 0
    for _, b in ipairs(buff_as) do
        total_buff = total_buff + (b.effects.as_bonus or 0)
        total_buff = total_buff + (b.effects.bolt_as_bonus or 0)
    end
    return base_as + stance + total_buff + (as_override or 0)
end

-- ── Resolve a bolt spell attack ────────────────────────────────────────
-- caster:              character row
-- target:              character or creature row
-- spell_number:        the spell being cast
-- spell_aiming_ranks:  caster's Spell Aiming ranks
-- target_ds:           target's current ranged DS (computed externally)
-- element:             "fire"|"ice"|"lightning"|"acid"|"impact"|"void"
-- target_armor_asg:    ASG of target's torso armor (for AvD)
-- caster_armor_asg:    ASG of caster's torso armor (for hindrance)
-- armor_use_ranks:     caster's Armor Use ranks
-- in_sanctuary:        bool
--
-- Returns result table:
--   { as, ds, avd, d100, total, hit, fumble, blocked, hindrance, message }
function Bolt.resolve(caster, target, spell_number, spell_aiming_ranks,
                       target_ds, element, target_armor_asg,
                       caster_armor_asg, armor_use_ranks, in_sanctuary)

    local circle    = SpellCircles.primary_for_spell(spell_number)
    local circle_id = circle and circle.id or 4

    -- ── Fumble check ─────────────────────────────────────────────────
    local d100_fumble = math.random(1, 100)
    if d100_fumble == 1 then
        return {
            fumble  = true,
            blocked = false,
            hit     = false,
            message = string.format(
                "You gesture.\nd100 == 1 FUMBLE!  You fumble spell %d!", spell_number
            ),
        }
    end

    -- ── Hindrance check ───────────────────────────────────────────────
    local blocked, hind_pct, hind_roll = Hindrance.roll(
        circle_id, caster_armor_asg, armor_use_ranks, caster.id, in_sanctuary
    )
    if blocked then
        return {
            fumble    = false,
            blocked   = true,
            hit       = false,
            hindrance = hind_pct,
            message   = string.format(
                "[Spell Hindrance for your armor is %d%% with current Armor Use skill, d100= %d]\n"
              .."Your armor prevents the spell from working correctly.\n"
              .."Cast Roundtime 3 Seconds.",
                hind_pct, hind_roll
            ),
        }
    end

    -- ── AvD lookup ────────────────────────────────────────────────────
    local asg     = math.max(1, math.min(20, target_armor_asg or 1))
    local avd_row = Bolt.avd_table[element or "impact"]
    local avd     = avd_row and avd_row[asg] or 37

    -- ── AS ────────────────────────────────────────────────────────────
    local as_val = Bolt.calculate_as(caster, spell_aiming_ranks)

    -- ── DS is passed in (computed by combat system) ───────────────────
    local ds_val = target_ds or 0
    if target and target.id then
        for _, b in ipairs(ActiveBuffs.get_active(target.id) or {}) do
            ds_val = ds_val + (b.effects.bolt_resist or 0)
        end
    end

    -- ── Roll ──────────────────────────────────────────────────────────
    local d100  = math.random(1, 100)
    local total = as_val - ds_val + avd + d100
    local hit   = total > 100

    -- ── Format message ────────────────────────────────────────────────
    local msg = string.format(
        "AS: +%d vs DS: +%d with AvD: +%d + d100 roll: +%d = %s%d",
        as_val, ds_val, avd, d100,
        (total >= 0 and "+" or ""), total
    )
    if hit then
        msg = msg .. "\n   ... and hit!"
    else
        msg = msg .. "\n   ... and missed!"
    end

    return {
        as        = as_val,
        ds        = ds_val,
        avd       = avd,
        d100      = d100,
        total     = total,
        hit       = hit,
        fumble    = false,
        blocked   = false,
        hindrance = 0,
        message   = msg,
    }
end

return Bolt
