-------------------------------------------------------------------
-- status_effects.lua
-- GemStone IV Status Effect Registry
--
-- Single source of truth for every effect/condition in the game.
-- Covers all 57 canonical GS4 wiki effects plus server-state effects.
--
-- Categories:
--   DEBUFF_COMBAT   -- locks out or heavily penalizes actions
--   DEBUFF_DOT      -- damage-over-time effects
--   DEBUFF_STAT     -- stat/combat penalties without action lock
--   DEBUFF_CONTROL  -- behavioral control (flee, stop, redirect)
--   BUFF_COMBAT     -- offensive/defensive bonuses
--   BUFF_REACTIVE   -- triggered/reactive combat bonuses
--   BUFF_SPECIAL    -- special mechanics (inner mind, enhance, etc.)
--   STATE           -- position/game-state flags (in_combat, sitting, etc.)
--
-- Field reference:
--   name            display name shown in STATUS command
--   category        one of the above strings
--   prompt_char     single char for the GS4 status prompt bar (nil = not shown)
--   stackable       whether stacks > 1 are meaningful
--   max_stacks      hard stack cap
--   tick_interval   seconds between ticks (0 = no periodic tick, just expires)
--   duration_default default duration in seconds if caller does not specify
--   combat_mods     { as=N, ds=N, evade_pct=N, parry_pct=N, block_pct=N }
--                   as/ds are flat additive; _pct fields reduce chance by that %
--   blocks          table of string flags:
--                     "actions"   can't attack or use skills
--                     "movement"  can't move between rooms
--                     "speech"    can't speak
--                     "hide"      can't enter hiding
--                     "cast"      can't cast spells
--   can_clear       list of effect ids that REMOVE this effect when applied
--   description     single-sentence mechanical summary
-------------------------------------------------------------------

local Effects = {}

-- ============================================================
-- DEBUFF_COMBAT  (locks or severely restricts actions)
-- ============================================================

Effects["stunned"] = {
    name             = "Stunned",
    category         = "DEBUFF_COMBAT",
    prompt_char      = "S",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 5,       -- 1 round = 5 seconds; cap 6 rounds players / 12 creatures
    combat_mods      = { as = 0, ds = -20, evade_pct = 50, parry_pct = 50, block_pct = 50 },
    blocks           = { "actions", "movement", "speech", "hide", "cast" },
    can_clear        = {},
    description      = "Cannot act; -20 DS, 50% evade/parry/block penalty.",
}

Effects["webbed"] = {
    name             = "Webbed",
    category         = "DEBUFF_COMBAT",
    prompt_char      = "W",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 5,
    duration_default = 30,
    combat_mods      = { as = 0, ds = -20, evade_pct = 50, parry_pct = 50, block_pct = 50 },
    blocks           = { "actions", "movement", "speech", "hide", "cast" },
    can_clear        = {},
    description      = "Entangled in webbing; cannot act or move, -20 DS.",
}

Effects["rooted"] = {
    name             = "Rooted",
    category         = "DEBUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 15,
    combat_mods      = { as = 0, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "movement", "hide" },
    can_clear        = {},
    description      = "Rooted in place; cannot move but may still act.",
}

Effects["immobile"] = {
    name             = "Immobile",
    category         = "DEBUFF_COMBAT",
    prompt_char      = "I",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 20,
    combat_mods      = { as = 0, ds = -15, evade_pct = 25, parry_pct = 0, block_pct = 0 },
    blocks           = { "movement", "hide" },
    can_clear        = {},
    description      = "Cannot move; -15 DS, -25% evade chance.",
}

Effects["silenced"] = {
    name             = "Silenced",
    category         = "DEBUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "speech", "cast" },
    can_clear        = {},
    description      = "Cannot speak or cast spells.",
}

Effects["unconscious"] = {
    name             = "Unconscious",
    category         = "DEBUFF_COMBAT",
    prompt_char      = "U",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = 0, ds = -50, evade_pct = 100, parry_pct = 100, block_pct = 100 },
    blocks           = { "actions", "movement", "speech", "hide", "cast" },
    can_clear        = {},
    description      = "Knocked unconscious; completely helpless.",
}

Effects["possessed"] = {
    name             = "Possessed",
    category         = "DEBUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 5,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "actions" },
    can_clear        = {},
    description      = "Possessed by a spirit; actions may be hijacked.",
}

-- ============================================================
-- DEBUFF_DOT  (damage over time)
-- ============================================================

Effects["bleeding"] = {
    name             = "Bleeding",
    category         = "DEBUFF_DOT",
    prompt_char      = "!",
    stackable        = true,
    max_stacks       = 5,
    tick_interval    = 8,
    duration_default = 120,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Losing health each tick from an open wound; reduced by tending.",
}

Effects["major_bleed"] = {
    name             = "Major Bleed",
    category         = "DEBUFF_DOT",
    prompt_char      = "!",
    stackable        = true,
    max_stacks       = 5,
    tick_interval    = 5,
    duration_default = 180,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Severe bleeding; higher damage per tick, percentage-based.",
}

Effects["poisoned"] = {
    name             = "Poisoned",
    category         = "DEBUFF_DOT",
    prompt_char      = "P",
    stackable        = true,
    max_stacks       = 3,
    tick_interval    = 12,
    duration_default = 120,
    combat_mods      = { as = -5, ds = -5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = { "unpoison" },
    description      = "Toxic damage per round; dissipates 5 damage/tick by default.",
}

Effects["major_poison"] = {
    name             = "Major Poison",
    category         = "DEBUFF_DOT",
    prompt_char      = "P",
    stackable        = true,
    max_stacks       = 3,
    tick_interval    = 8,
    duration_default = 180,
    combat_mods      = { as = -10, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = { "unpoison" },
    description      = "Major poison; percentage-of-remaining-health damage per tick.",
}

Effects["disease"] = {
    name             = "Diseased",
    category         = "DEBUFF_DOT",
    prompt_char      = "D",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 30,
    duration_default = 600,
    combat_mods      = { as = -5, ds = -5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = { "curedisease" },
    description      = "Diseased; periodic health damage, reduced natural recovery.",
}

Effects["wounded"] = {
    name             = "Wounded",
    category         = "DEBUFF_DOT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 300,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Prevents natural regeneration; increases all concussion damage taken.",
}

Effects["mind_rot"] = {
    name             = "Mind Rot",
    category         = "DEBUFF_DOT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 20,
    duration_default = 300,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Spirit drains each tick; if spirit reaches zero, death follows.",
}

-- ============================================================
-- DEBUFF_STAT  (stat/combat penalties)
-- ============================================================

Effects["staggered"] = {
    name             = "Staggered",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 10,
    combat_mods      = { as = -15, ds = -15, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "-15 AS and DS while unsteady.",
}

Effects["prone"] = {
    name             = "Prone",
    category         = "DEBUFF_STAT",
    prompt_char      = "p",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 5,
    duration_default = 15,
    combat_mods      = { as = -50, ds = -50, evade_pct = 50, parry_pct = 50, block_pct = 50 },
    blocks           = { "hide" },
    can_clear        = {},
    description      = "Lying on the ground; -50 AS and DS, 50% evade/parry/block penalty.",
}

Effects["blinded"] = {
    name             = "Blinded",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = -20, ds = -20, evade_pct = 25, parry_pct = 0, block_pct = 0 },
    blocks           = { "hide" },
    can_clear        = {},
    description      = "Cannot see; -20 AS and DS, -25% evade chance.",
}

Effects["slowed"] = {
    name             = "Slowed",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 20,
    combat_mods      = { as = -10, ds = -5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Movement and attacks slowed; +2 RT on all actions.",
}

Effects["crippled"] = {
    name             = "Crippled",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = -20, ds = -10, evade_pct = 15, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Leg injury; movement halved, -20 AS, -10 DS.",
}

Effects["demoralized"] = {
    name             = "Demoralized",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = -20, ds = -20, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Morale broken; -20 AS and DS.",
}

Effects["feeble"] = {
    name             = "Feeble",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = -15, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Strength severely reduced; -15 AS, encumbrance worsened.",
}

Effects["clumsy"] = {
    name             = "Clumsy",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = -10, ds = -5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Chance to stumble on attack; -10 AS, -5 DS.",
}

Effects["dazed"] = {
    name             = "Dazed",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 10,
    combat_mods      = { as = -15, ds = -15, evade_pct = 25, parry_pct = 25, block_pct = 25 },
    blocks           = {},
    can_clear        = {},
    description      = "Disoriented but not fully stunned; -15 AS/DS, 25% defense penalty.",
}

Effects["disoriented"] = {
    name             = "Disoriented",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 15,
    combat_mods      = { as = -10, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Spatial confusion; -10 AS and DS.",
}

Effects["overexerted"] = {
    name             = "Overexerted",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = -20, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Stamina depleted; -20 AS, -10 DS, slow stamina recovery.",
}

Effects["vulnerable"] = {
    name             = "Vulnerable",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 30,
    combat_mods      = { as = 0, ds = -30, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Defense critically lowered; -30 DS and increased damage taken.",
}

Effects["weakened_armament"] = {
    name             = "Weakened Armament",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = -20, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Weapon enchantment suppressed; reduced weapon bonus to AS.",
}

Effects["groggy"] = {
    name             = "Groggy",
    category         = "DEBUFF_STAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 10,
    combat_mods      = { as = -20, ds = -20, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Post-sleep grogginess; -20 AS/DS for 10 seconds after waking from Sleep (501).",
}

-- ============================================================
-- DEBUFF_CONTROL  (behavioral effects)
-- ============================================================

Effects["calmed"] = {
    name             = "Calmed",
    category         = "DEBUFF_CONTROL",
    prompt_char      = "C",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "actions" },
    can_clear        = {},
    description      = "Soothed into non-aggression; cannot initiate attacks.",
}

Effects["confused"] = {
    name             = "Confused",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 5,
    duration_default = 30,
    combat_mods      = { as = -10, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Confused; may attack random targets, -10 AS/DS.",
}

Effects["frenzied"] = {
    name             = "Frenzied",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 3,
    duration_default = 30,
    combat_mods      = { as = 20, ds = -20, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Berserk rage; +20 AS, -20 DS, cannot disengage or flee.",
}

Effects["sheer_fear"] = {
    name             = "Sheer Fear",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 3,
    duration_default = 30,
    combat_mods      = { as = -20, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "actions" },
    can_clear        = {},
    description      = "Paralyzed with fear; cannot act, -20 AS, -10 DS.",
}

Effects["terrified"] = {
    name             = "Terrified",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 3,
    duration_default = 30,
    combat_mods      = { as = -10, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Overcome by terror; may flee combat each tick.",
}

Effects["horrified"] = {
    name             = "Horrified",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 3,
    duration_default = 20,
    combat_mods      = { as = -15, ds = -15, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Stricken with horror; may flee, -15 AS/DS.",
}

Effects["fear"] = {
    name             = "Frightened",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 3,
    duration_default = 30,
    combat_mods      = { as = -10, ds = -10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Frightened; may flee combat each tick.",
}

Effects["disengaged"] = {
    name             = "Disengaged",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 10,
    combat_mods      = { as = -10, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Stepped back from engagement; brief -10 AS penalty.",
}

Effects["pressed"] = {
    name             = "Pressed",
    category         = "DEBUFF_CONTROL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 15,
    combat_mods      = { as = 0, ds = -15, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Forced into defensive position; -15 DS.",
}

-- ============================================================
-- BUFF_COMBAT  (offensive / defensive bonuses)
-- ============================================================

Effects["empowered"] = {
    name             = "Empowered",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 20, ds = 10, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "+20 AS, +10 DS from an empowerment source.",
}

Effects["quickness"] = {
    name             = "Quickness",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Reduced roundtime on all actions.",
}

Effects["evasiveness"] = {
    name             = "Evasiveness",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 15, evade_pct = -15, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "+15 evade DS; increased chance to outright dodge attacks.",
}

Effects["defensive_posture"] = {
    name             = "Defensive Posture",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = -20, ds = 30, evade_pct = -10, parry_pct = -10, block_pct = -10 },
    blocks           = {},
    can_clear        = {},
    description      = "+30 DS, improved parry/block/evade; -20 AS tradeoff.",
}

Effects["forceful_blows"] = {
    name             = "Forceful Blows",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 15, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "+15 AS; attacks strike with greater impact.",
}

Effects["slashing_strikes"] = {
    name             = "Slashing Strikes",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 10, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "+10 AS with slashing weapons; increased chance to cause bleeding.",
}

Effects["concussive_blows"] = {
    name             = "Concussive Blows",
    category         = "BUFF_COMBAT",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 10, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "+10 AS with blunt weapons; increased stun chance.",
}

-- ============================================================
-- BUFF_REACTIVE  (triggered on parry / block / evade events)
-- ============================================================

Effects["recent_block"] = {
    name             = "Recent Block",
    category         = "BUFF_REACTIVE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 5,
    combat_mods      = { as = 5, ds = 5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Just blocked an attack; brief +5 AS/DS window.",
}

Effects["recent_parry"] = {
    name             = "Recent Parry",
    category         = "BUFF_REACTIVE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 5,
    combat_mods      = { as = 5, ds = 5, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Just parried an attack; brief +5 AS/DS window.",
}

Effects["recent_evade"] = {
    name             = "Recent Evade",
    category         = "BUFF_REACTIVE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 5,
    combat_mods      = { as = 5, ds = 5, evade_pct = -10, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Just evaded an attack; brief bonus and slightly improved evade chance.",
}

Effects["counter"] = {
    name             = "Counter",
    category         = "BUFF_REACTIVE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 3,
    combat_mods      = { as = 20, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Counter-attack window open; next attack has +20 AS.",
}

-- ============================================================
-- BUFF_SPECIAL  (unique mechanics)
-- ============================================================

Effects["inner_mind"] = {
    name             = "Inner Mind",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 600,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Meditation state; enhanced XP absorption rate.",
}

Effects["enhance"] = {
    name             = "Enhanced",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Generic enhancement; effect varies by source spell or item.",
}

Effects["shrouded"] = {
    name             = "Shrouded",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 120,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Aura of concealment; harder to perceive and detect.",
}

-- ============================================================
-- STATE  (position and game-state flags)
-- ============================================================

-- ** in_combat **
-- The core fix: this was a raw boolean. Now it's a timed status that
-- auto-expires 8 seconds after the last combat action. Every swing,
-- every creature attack refreshes it. When it expires and no hostile
-- creatures remain in the room, combat is cleanly cleared.
Effects["in_combat"] = {
    name             = "In Combat",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 8,   -- refreshed every attack; 8 sec after last action
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "hide", "sleep", "rest" },
    can_clear        = {},
    description      = "Engaged in combat; cannot hide, sleep, or rest.",
}

-- Brief grace period immediately after combat clears.
-- Used to suppress spurious "You flee from combat!" on movement.
Effects["exited_combat"] = {
    name             = "Exited Combat",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 3,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Brief post-combat grace period; movement is normal.",
}

Effects["sitting"] = {
    name             = "Sitting",
    category         = "STATE",
    prompt_char      = "s",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,  -- -1 = indefinite until cleared
    combat_mods      = { as = -15, ds = -20, evade_pct = 10, parry_pct = 10, block_pct = 10 },
    blocks           = { "hide" },
    can_clear        = { "stand" },
    description      = "Seated; -15 AS, -20 DS, slower recovery than lying.",
}

Effects["kneeling"] = {
    name             = "Kneeling",
    category         = "STATE",
    prompt_char      = "K",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = -10, ds = -15, evade_pct = 10, parry_pct = 10, block_pct = 10 },
    blocks           = { "hide" },
    can_clear        = { "stand" },
    description      = "Kneeling; -10 AS, -15 DS.",
}

Effects["sleeping"] = {
    name             = "Sleeping",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = -50, evade_pct = 100, parry_pct = 100, block_pct = 100 },
    blocks           = { "actions", "movement", "speech", "hide", "cast" },
    can_clear        = { "stand", "wake" },
    description      = "Asleep; completely defenseless, XP absorption doubled.",
}

Effects["resting"] = {
    name             = "Resting",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = -15, ds = -20, evade_pct = 10, parry_pct = 10, block_pct = 10 },
    blocks           = { "hide" },
    can_clear        = { "stand" },
    description      = "Resting; slightly improved recovery, -15 AS, -20 DS.",
}

Effects["hidden"] = {
    name             = "Hidden",
    category         = "STATE",
    prompt_char      = "H",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = { "in_combat" },
    description      = "Hidden from sight; revealed by movement or combat.",
}

Effects["sneaking"] = {
    name             = "Sneaking",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Moving with stealth; each step rolls stealth instead of immediately breaking hiding.",
}

Effects["invisible"] = {
    name             = "Invisible",
    category         = "STATE",
    prompt_char      = "i",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 120,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Invisible; cannot be directly targeted by creatures.",
}

Effects["dead"] = {
    name             = "Dead",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "actions", "movement", "cast" },
    can_clear        = { "raise", "resurrect" },
    description      = "Dead; spirit lingers, awaiting raise or departure.",
}

Effects["death_sting"] = {
    name             = "Death's Sting",
    category         = "STATE",
    prompt_char      = nil,
    stackable        = true,
    max_stacks       = 10,
    tick_interval    = 0,
    duration_default = -1,  -- decays via absorbed XP, not time
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "XP absorption reduced to 25%; each stack decays as experience is absorbed.",
}

Effects["lumnis"] = {
    name             = "Gift of Lumnis",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Weekend blessing; bonus experience absorption is active.",
}

Effects["bonus_xp"] = {
    name             = "Bonus Experience",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = -1,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "Server-wide event bonus; creatures award additional experience.",
}

Effects["floofer_glow"] = {
    name             = "Comforting Glow",
    category         = "BUFF_SPECIAL",
    prompt_char      = nil,
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 5,
    duration_default = 60,
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = {},
    can_clear        = {},
    description      = "A Floofer's restorative glow quietly heals you every five seconds while active.",
}

Effects["roundtime"] = {
    name             = "Roundtime",
    category         = "STATE",
    prompt_char      = "R",
    stackable        = false,
    max_stacks       = 1,
    tick_interval    = 0,
    duration_default = 3,   -- actual RT duration set per-action
    combat_mods      = { as = 0, ds = 0, evade_pct = 0, parry_pct = 0, block_pct = 0 },
    blocks           = { "actions", "cast" },
    can_clear        = {},
    description      = "In roundtime; cannot perform actions until it expires.",
}

return Effects
