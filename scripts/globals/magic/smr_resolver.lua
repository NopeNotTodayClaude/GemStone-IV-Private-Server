------------------------------------------------------------------------
-- scripts/globals/magic/smr_resolver.lua
-- Standard Maneuver Roll (SMR) for maneuver-type spells in GemStone IV.
-- Source: gswiki.play.net/Standard_maneuver_roll, /Magic — "Maneuver Spells"
--
-- SMR result = Open d100 + Bonus + Spell Power
--   If SMR result > 100 → maneuver hits
--   Higher result = more severe effect
--
-- Open d100: 1-100 normally, small chance to exceed range (open-ended).
-- Bonus: conditions at cast time (immobilized target = large bonus, etc.)
-- Spell Power: derived from:
--   - Caster's spell circle ranks
--   - Caster's level vs target's level
--   - Spell Aiming ranks (if projectile-based maneuver spell)
--   - Mana Control ranks (if non-projectile maneuver spell)
--
-- Display format (from wiki example):
--   [SMR result: 147 (Open d100: 32, Bonus: 48)]
------------------------------------------------------------------------

local Hindrance    = require("globals/magic/spell_hindrance")
local SpellCircles = require("globals/magic/spell_circles")
local GS4Math      = require("globals/utils/gs4_math")

local SMR = {}

-- ── Open d100 roll ────────────────────────────────────────────────────
-- Standard GS4 open roll: 1-100, but a roll of 100 re-rolls and adds.
-- Cap at 240 to prevent infinite loops (practical ceiling).
local function open_roll()
    local total = 0
    local cap   = 0
    repeat
        local r = math.random(1, 100)
        total   = total + r
        cap     = cap + 1
        if r < 100 or cap >= 3 then break end
    until false
    return math.min(total, 240)
end

-- ── Spell Power ───────────────────────────────────────────────────────
-- Spell Power is the hidden modifier not shown in the SMR line.
-- For rank-based non-projectile spells: driven by circle ranks + level delta.
-- For projectile maneuver spells: Spell Aiming skill bonus is factored in.
--
-- Approximate formula based on wiki description:
--   spell_power = circle_ranks_bonus + level_delta_bonus + skill_bonus
--
-- circle_ranks_bonus: ranks in primary circle (capped at level) × 0.5
-- level_delta_bonus:  (caster_level - target_level) × 2  (capped at ±20)
-- skill_bonus:        spell_aiming OR mana_control bonus, depending on spell
local function calc_spell_power(caster, target, circle_ranks,
                                 spell_aiming_bonus, mc_bonus, is_projectile)
    local caster_level = caster.level or 1
    local target_level = (target and target.level) or 1
    local capped_ranks = math.min(circle_ranks, caster_level)

    local rank_bonus   = math.floor(capped_ranks * 0.5)
    local level_delta  = math.max(-20, math.min(20, (caster_level - target_level) * 2))
    local skill_part   = is_projectile
                            and (spell_aiming_bonus or 0)
                            or  (mc_bonus or 0)
    return rank_bonus + level_delta + math.floor(skill_part * 0.5)
end

-- ── Condition bonuses ──────────────────────────────────────────────────
-- Standard condition modifiers to the SMR Bonus value.
-- The calling spell script should pass in applicable conditions.
-- conditions table keys and their bonus values:
SMR.condition_bonuses = {
    immobilized      = 50,   -- target is fully immobilized (e.g. web, bind)
    prone            = 20,   -- target is on the ground
    stunned          = 15,   -- target is stunned
    blind            = 15,   -- target is blind
    webbed           = 40,   -- target is webbed (partial immobilize)
    level_advantage  = 0,    -- handled separately via level_delta
}

-- ── Resolve a maneuver spell ───────────────────────────────────────────
-- caster:              character row
-- target:              character or creature row (nil for area effects)
-- spell_number:        the spell being cast
-- circle_ranks:        caster's ranks in the spell's primary circle
-- spell_aiming_ranks:  caster's Spell Aiming ranks
-- mc_bonus:            relevant Mana Control skill bonus (for non-projectile)
-- is_projectile:       bool — true if spell has a projectile component
-- conditions:          table of condition keys (e.g. { immobilized=true })
-- caster_armor_asg:    for hindrance check
-- armor_use_ranks:     for hindrance check
-- in_sanctuary:        bool
--
-- Returns result table:
--   { open_roll, bonus, spell_power, total, hit, fumble, blocked,
--     hindrance, severity, message }
function SMR.resolve(caster, target, spell_number, circle_ranks,
                      spell_aiming_ranks, mc_bonus, is_projectile,
                      conditions, caster_armor_asg, armor_use_ranks,
                      in_sanctuary)

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

    -- ── Compute SMR components ────────────────────────────────────────
    local sa_bonus = GS4Math.skill_bonus_from_ranks(spell_aiming_ranks or 0)

    local spell_power = calc_spell_power(
        caster, target, circle_ranks or 0,
        sa_bonus, mc_bonus, is_projectile
    )

    -- Condition bonus
    local condition_bonus = 0
    if conditions then
        for cond, active in pairs(conditions) do
            if active and SMR.condition_bonuses[cond] then
                condition_bonus = condition_bonus + SMR.condition_bonuses[cond]
            end
        end
    end

    local open_d100 = open_roll()
    local total     = open_d100 + condition_bonus + spell_power
    local hit       = total > 100

    -- Severity tier (higher result = worse for target)
    local severity
    if not hit then
        severity = "none"
    elseif total <= 120 then
        severity = "minor"
    elseif total <= 160 then
        severity = "moderate"
    elseif total <= 200 then
        severity = "major"
    else
        severity = "severe"
    end

    -- Format message
    local msg = string.format(
        "[SMR result: %d (Open d100: %d, Bonus: %d)]",
        total, open_d100, condition_bonus
    )

    return {
        open_roll    = open_d100,
        bonus        = condition_bonus,
        spell_power  = spell_power,
        total        = total,
        hit          = hit,
        fumble       = false,
        blocked      = false,
        hindrance    = 0,
        severity     = severity,
        message      = msg,
    }
end

return SMR
