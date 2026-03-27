-- =============================================================================
-- scripts/globals/ambush.lua
-- Ambush system configuration.
-- Hidden ambush and open aiming tuning lives here so combat math is loader-driven.
-- =============================================================================

local Ambush = {}

-- Canonical Ambush skill id from scripts/data/skills.lua.
Ambush.skill_id = 43
Ambush.cm_skill_id = 4

-- ---------------------------------------------------------------------------
-- Hidden ambushes
-- ---------------------------------------------------------------------------
Ambush.hidden = {
    -- Aiming from hiding leans entirely on the ambush-driving skill.
    aim_bonus_mult     = 0.25,
    threshold_level_mult = 2.0,
    threshold_flat     = 0,

    -- We do not model E/B/P as separate DS buckets yet, so we approximate the
    -- GS4 "halve EBP" behavior by reducing only a slice of total DS.
    ebp_ds_share       = 0.30,
    ebp_reduction_pct  = 0.50,

    -- Approximate stance pushdown based on ambush skill bonus relative to
    -- target level.  Higher relative stealth skill pushes the defender farther
    -- toward offensive stance for the ambushing strike.
    stance_pushdown = {
        minimum_steps   = 1,
        level_scale     = 3,
        bonus_step_every = 60,
        max_steps       = 4,
    },

    -- Small server-specific reward for successfully ambushing with any weapon.
    any_weapon_as_bonus = 2,
    weapon_as_bonus = {
        edged     = 1,
        blunt     = 0,
        twohanded = 0,
        polearm   = 0,
        ranged    = 0,
        thrown    = 0,
        brawling  = 0,
    },
    favored_weapons = {
        dagger = {
            as_bonus = 5,
            crit_flat = 8,
        },
        ["main gauche"] = {
            as_bonus = 4,
            crit_flat = 6,
        },
        katar = {
            as_bonus = 3,
            crit_flat = 4,
        },
    },

    -- Hidden ambush adds crit weighting, not raw HP damage.
    crit_weighting = {
        bonus_divisor  = 30,
        rank_divisor   = 12,
        any_weapon_flat = 1,
        weapon_bonus = {
            edged     = 2,
            blunt     = 1,
            twohanded = 1,
            polearm   = 1,
            ranged    = 1,
            thrown    = 1,
            brawling  = 1,
        },
    },

    rt_reduction = 1,
}

-- ---------------------------------------------------------------------------
-- Open aimed melee attacks
-- GM Naijin (2021-04-27) indicated open aimed melee considers CM and Ambush
-- equally, using skill bonus rather than raw ranks.
-- ---------------------------------------------------------------------------
Ambush.open_aim = {
    ambush_bonus_mult    = 0.25,
    cm_bonus_mult        = 0.25,
    threshold_level_mult = 2.0,
    threshold_flat       = 0,
}

return Ambush
