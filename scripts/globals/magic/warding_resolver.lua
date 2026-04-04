------------------------------------------------------------------------
-- scripts/globals/magic/warding_resolver.lua
-- Warding spell resolution for GemStone IV.
-- Source: gswiki.play.net/Magic — "Warding Spells" section,
--         /Casting_strength, /Target_defense
--
-- Warding roll:
--   Result = CS - TD + CvA + d100
--   If Result > 100 → spell affects the target ("warding failed" for target)
--   If Result <= 100 → spell does NOT affect the target
--
-- Display format (from wiki example):
--   CS: +204 - TD: +88 + CvA: +19 + d100: +88 == +223
--   Warding failed!
--
-- 1% fumble chance on any attack spell (d100 == 1).
------------------------------------------------------------------------

local CS          = require("globals/magic/cs_resolver")
local TD          = require("globals/magic/td_resolver")
local Hindrance   = require("globals/magic/spell_hindrance")
local SpellCircles = require("globals/magic/spell_circles")

local Warding = {}

-- ── Warding roll ──────────────────────────────────────────────────────
-- caster:       character row with .level, stat fields, .profession_id
-- target:       character or creature row with .level, stat fields, .race_id
-- spell_number: the spell being cast
-- spell_ranks:  { [circle_id]=ranks } table for the caster
-- caster_armor_asg: caster's torso armor ASG (for hindrance check)
-- armor_use_ranks:  caster's Armor Use ranks
-- in_sanctuary: bool — hindrance nullified in sanctuaries
--
-- Returns a result table:
--   {
--     cs         = N,       -- calculated CS
--     td         = N,       -- calculated TD
--     cva        = N,       -- CvA modifier (positive = easier to ward)
--     d100       = N,       -- dice roll
--     total      = N,       -- cs - td + cva + d100
--     hit        = bool,    -- true if warding "failed" (spell affects target)
--     fumble     = bool,    -- true on d100 == 1 (attack spell fumble)
--     blocked    = bool,    -- true if armor hindered the cast
--     hindrance  = N,       -- % hindrance rolled against
--     message    = string,  -- formatted result line
--   }
function Warding.resolve(caster, target, spell_number, spell_ranks,
                          caster_armor_asg, armor_use_ranks,
                          in_sanctuary, target_armor_asg)
    local circle = SpellCircles.primary_for_spell(spell_number)

    -- ── Fumble check (1% on attack spells) ───────────────────────────
    local d100_fumble = math.random(1, 100)
    if d100_fumble == 1 then
        return {
            fumble  = true,
            blocked = false,
            hit     = false,
            total   = 0,
            message = string.format(
                "You gesture.\nd100 == 1 FUMBLE!  You fumble spell %d!", spell_number
            ),
        }
    end

    -- ── Hindrance check ───────────────────────────────────────────────
    local circle_id = circle and circle.id or 7
    local blocked, hind_pct, hind_roll = Hindrance.roll(
        circle_id, caster_armor_asg, armor_use_ranks,
        caster.id, in_sanctuary
    )
    if blocked then
        return {
            fumble    = false,
            blocked   = true,
            hit       = false,
            hindrance = hind_pct,
            total     = 0,
            message   = string.format(
                "[Spell Hindrance for your armor is %d%% with current Armor Use skill, d100= %d]\n"
              .."Your armor prevents the spell from working correctly.\n"
              .."Cast Roundtime 3 Seconds.",
                hind_pct, hind_roll
            ),
        }
    end

    -- ── Warding math ─────────────────────────────────────────────────
    local cs_val  = CS.calculate(caster, spell_number, spell_ranks)
    local td_val  = TD.calculate(target, spell_number)
    local cva_val = TD.get_cva(target_armor_asg or 1)
    local d100    = math.random(1, 100)
    local total   = cs_val - td_val + cva_val + d100
    local hit     = total > 100

    -- ── Format message (matches GS4 wire format) ─────────────────────
    local cva_sign = cva_val >= 0 and "+" or ""
    local msg = string.format(
        "CS: +%d - TD: +%d + CvA: %s%d + d100: +%d == %s%d\n%s",
        cs_val, td_val, cva_sign, cva_val, d100,
        (total >= 0 and "+" or ""), total,
        hit and "Your spell takes hold." or "Your spell fails to penetrate the target's defenses."
    )

    return {
        cs        = cs_val,
        td        = td_val,
        cva       = cva_val,
        d100      = d100,
        total     = total,
        hit       = hit,
        fumble    = false,
        blocked   = false,
        hindrance = hind_pct or 0,
        message   = msg,
    }
end

return Warding
