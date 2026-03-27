-- =============================================================================
-- scripts/weapon_techniques/definitions.lua
-- Pure data: all 24 weapon techniques, keyed by mnemonic.
-- This is the Lua-side source of truth; the SQL seed mirrors it.
-- Engine scripts require() this to know technique metadata without a DB query.
-- =============================================================================

local Techniques = {}

-- Helper: build a technique definition
local function def(t)
    return t
end

-- ────────────────────────────────────────────────────────────────────────────
-- BRAWLING
-- ────────────────────────────────────────────────────────────────────────────
Techniques["twinhammer"] = def {
    mnemonic        = "twinhammer",
    name            = "Twin Hammerfists",
    category        = "brawling",
    type            = "setup",
    weapon_skill    = "brawling",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 7,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Attempt to knockdown and potentially stun your opponent by swinging your fists down on them.",
    -- Mechanics constants
    vulnerable_base = 15,   -- Vulnerable duration = 15 + (rank*5)
    vulnerable_per_rank = 5,
    stagger_divisor = 10,   -- Staggered = margin / 10
    stun_threshold  = 50,   -- margin needed for stun chance
    -- Messaging (first entry used; script picks by result)
    msg_attempt = "You raise your hands high, lace them together and bring them crashing down towards {target}!",
    msg_success = "You catch {target} square in the back!  {He} topples to the ground!",
    msg_success_stun = "You catch {target} square in the back! {It} topples to the ground in a dazed heap!",
    msg_fail    = "{Target} sidesteps your hammerfist attempt!",
}

Techniques["fury"] = def {
    mnemonic        = "fury",
    name            = "Fury",
    category        = "brawling",
    type            = "assault",
    weapon_skill    = "brawling",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Unleash your fury upon your foe in a relentless assault.",
    -- Mechanics
    parry_mod_divisor = 5,   -- parry modified (margin/5)% per round, max 10%
    parry_mod_cap     = 10,
    success_buff      = "frenzy",
    success_buff_duration = 120,
    msg_attempt = "You rush at {target} in a blinding fury!",
    msg_hit     = "You lash out wildly at {target}!",
    msg_final   = "With a primal roar you pull back from {target}!",
}

Techniques["clash"] = def {
    mnemonic        = "clash",
    name            = "Clash",
    category        = "brawling",
    type            = "aoe",
    weapon_skill    = "brawling",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Hurl yourself into a clashing brawl with one or more foes.",
    -- Mechanics
    evasiveness_base     = 5,   -- Evasiveness = 5 + rank
    evasiveness_per_rank = 1,
    msg_attempt = "You hurl yourself into a wild brawling clash!",
    msg_hit     = "You crash into {target} with reckless abandon!",
}

Techniques["spinkick"] = def {
    mnemonic        = "spinkick",
    name            = "Spin Kick",
    category        = "brawling",
    type            = "reaction",
    weapon_skill    = "brawling",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 0,
    base_rt         = 0,   -- ATTACK - 2
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_evade",
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Spin around kicking a target.",
    -- Mechanics
    cer_bonus       = 10,   -- +10 CER
    stagger_divisor = 8,    -- Staggered = margin / 8
    msg_attempt = "You spin rapidly and launch a kick at {target}!",
    msg_hit     = "Your spinning kick catches {target} solidly!",
    msg_fail    = "Your spin kick finds only air!",
}

-- ────────────────────────────────────────────────────────────────────────────
-- BLUNT WEAPONS
-- ────────────────────────────────────────────────────────────────────────────
Techniques["dizzyingswing"] = def {
    mnemonic        = "dizzyingswing",
    name            = "Dizzying Swing",
    category        = "blunt",
    type            = "setup",
    weapon_skill    = "blunt",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 7,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "right_hand",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Smash a target in the head, confusing them.",
    damage_type     = "crush",
    daze_base       = 15,   -- Dazed = 15 + (rank*5)
    daze_per_rank   = 5,
    stagger_divisor = 10,
    msg_attempt = "You wind up and swing your weapon in a wide arc at {target}'s head!",
    msg_hit     = "Your blow lands solidly, {target}'s eyes going glassy!",
    msg_fail    = "{Target} ducks away from your wild swing!",
}

Techniques["clobber"] = def {
    mnemonic        = "clobber",
    name            = "Clobber",
    category        = "blunt",
    type            = "reaction",
    weapon_skill    = "blunt",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_parry",
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "React to a parry with a devastating concussion attack.",
    -- Mechanics: Weakened Armament applied BEFORE resolution
    weakened_armament_base = 15,   -- 15 + (rank*5)
    weakened_armament_per_rank = 5,
    removes_recent_ebp = true,
    msg_attempt = "Capitalizing on {target}'s parry, you bring your weapon crashing down!",
    msg_hit     = "The concussive blow staggers {target}!",
}

Techniques["pummel"] = def {
    mnemonic        = "pummel",
    name            = "Pummel",
    category        = "blunt",
    type            = "assault",
    weapon_skill    = "blunt",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Pummel the target repeatedly with your weapon.",
    parry_mod_divisor = 5,
    parry_mod_cap     = 10,
    success_buff      = "forceful_blows",
    success_buff_duration = 120,
    msg_attempt = "You begin hammering {target} relentlessly!",
    msg_hit     = "You bring your weapon crashing into {target}!",
    msg_final   = "With a final crushing blow you pull back from {target}!",
}

Techniques["pulverize"] = def {
    mnemonic        = "pulverize",
    name            = "Pulverize",
    category        = "blunt",
    type            = "aoe",
    weapon_skill    = "blunt",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Target the armor of multiple targets, weakening it.",
    damage_type     = "crush",
    -- Weakened Armament on all targets
    weakened_armament_base     = 15,
    weakened_armament_per_rank = 3,
    msg_attempt = "You swing your weapon in a massive arc to batter all nearby foes!",
    msg_hit     = "Your crushing blow weakens {target}'s armor!",
}

-- ────────────────────────────────────────────────────────────────────────────
-- EDGED WEAPONS
-- ────────────────────────────────────────────────────────────────────────────
Techniques["cripple"] = def {
    mnemonic        = "cripple",
    name            = "Cripple",
    category        = "edged",
    type            = "setup",
    weapon_skill    = "edged",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 7,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "right_hand",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Slash a target's limb to cripple their combat effectiveness.",
    damage_type     = "slash",
    crippled_base       = 15,  -- Crippled = 15 + (rank*5)
    crippled_per_rank   = 5,
    rooted_base         = 10,  -- Rooted (leg target) = 10 + (rank*2)
    rooted_per_rank     = 2,
    -- Supported limb targets
    valid_limbs     = {"right arm","left arm","right leg","left leg","right hand","left hand"},
    leg_targets     = {"right leg","left leg"},
    msg_attempt     = "You slash at {target}'s {limb}!",
    msg_hit         = "Your blade cuts deep into {target}'s {limb}, crippling them!",
    msg_hit_leg     = "Your slash severs the tendons in {target}'s {limb}, rooting them!",
    msg_fail        = "{Target} pulls back before you can cripple {him}!",
}

Techniques["riposte"] = def {
    mnemonic        = "riposte",
    name            = "Riposte",
    category        = "edged",
    type            = "reaction",
    weapon_skill    = "edged",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_parry",
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "React to a parry with a counter-attack.",
    -- Weakened Armament applied BEFORE attack resolution
    weakened_armament_base     = 15,  -- 15 + (rank*5)
    weakened_armament_per_rank = 5,
    removes_recent_ebp = true,
    msg_attempt = "You seize {target}'s parry and drive your blade forward!",
    msg_hit     = "Your riposte slips past {target}'s guard!",
    msg_fail    = "{Target} recovers and your riposte misses!",
}

Techniques["flurry"] = def {
    mnemonic        = "flurry",
    name            = "Flurry",
    category        = "edged",
    type            = "assault",
    weapon_skill    = "edged",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Rapidly slash a target.",
    parry_mod_divisor = 5,   -- (margin/5)%, max 10%
    parry_mod_cap     = 10,
    success_buff      = "slashing_strikes",
    success_buff_duration = 120,
    msg_attempt = "You launch into a rapid flurry of slashes at {target}!",
    msg_hit     = "You carve a slash across {target}!",
    msg_final   = "With a final flourish you step back from {target}!",
}

Techniques["wblade"] = def {
    mnemonic        = "wblade",
    name            = "Whirling Blade",
    category        = "edged",
    type            = "aoe",
    weapon_skill    = "edged",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Unleash a flurry of quick attacks against a target.",
    evasiveness_base     = 5,   -- 5 + rank
    evasiveness_per_rank = 1,
    msg_attempt = "You spin your blade in a brilliant whirling arc!",
    msg_hit     = "Your whirling blade slashes across {target}!",
}

-- ────────────────────────────────────────────────────────────────────────────
-- POLEARM WEAPONS
-- ────────────────────────────────────────────────────────────────────────────
Techniques["charge"] = def {
    mnemonic        = "charge",
    name            = "Charge",
    category        = "polearm",
    type            = "setup",
    weapon_skill    = "polearm",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 14,
    base_rt         = 4,
    cooldown        = 0,
    offensive_gear  = "right_hand",
    flares_enabled  = true,
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Charge at your opponent with your polearm.",
    damage_type_primary   = "weapon",
    damage_type_secondary = "unbalance",
    vulnerable_base     = 15,
    vulnerable_per_rank = 5,
    stagger_divisor     = 6,   -- Staggered = margin / 6
    can_force_stance    = true,
    msg_attempt = "You lower your weapon and charge at {target}!",
    msg_success_minor  = "{Target} loses {his} footing!",
    msg_success_major  = "{Target} flips through the air, landing on {his} head with a crash!",
    msg_fail    = "{Target} sidesteps your charge!",
}

Techniques["gthrusts"] = def {
    mnemonic        = "gthrusts",
    name            = "Guardant Thrusts",
    category        = "polearm",
    type            = "assault",
    weapon_skill    = "polearm",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Assault your target with a series of thrusts, while maximizing your defenses.",
    -- Per-round: +5 DS, stacks up to Rank times
    ds_bonus_per_round = 5,
    completion_buff    = "fortified_stance",
    completion_buff_duration = 30,
    msg_attempt = "You advance on {target} with measured thrusts!",
    msg_hit     = "You drive your weapon forward into {target}!",
    msg_final   = "With a final thrust you settle back into a guarded stance!",
}

Techniques["cyclone"] = def {
    mnemonic        = "cyclone",
    name            = "Cyclone",
    category        = "polearm",
    type            = "aoe",
    weapon_skill    = "polearm",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Spin your polearm around you attacking and forcing enemies back.",
    damage_type     = "unbalance",
    stagger_divisor = 8,
    force_stance_threshold = 80,   -- margin > this forces lower stance
    msg_attempt = "You spin your polearm in a wide cyclone arc!",
    msg_hit     = "Your sweeping polearm crashes into {target}!",
}

Techniques["radialsweep"] = def {
    mnemonic        = "radialsweep",
    name            = "Radial Sweep",
    category        = "polearm",
    type            = "reaction",
    weapon_skill    = "polearm",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_evade",
    offensive_gear  = "both_hands",
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Spin your polearm around you targeting the legs of enemies.",
    rooted_base     = 8,   -- Rooted = 8 + (rank*2)
    rooted_per_rank = 2,
    msg_attempt = "You spin low, sweeping your polearm at the legs of your foes!",
    msg_hit     = "Your sweeping polearm tangles {target}'s legs!",
}

-- ────────────────────────────────────────────────────────────────────────────
-- RANGED WEAPONS
-- ────────────────────────────────────────────────────────────────────────────
Techniques["reactiveshot"] = def {
    mnemonic        = "reactiveshot",
    name            = "Reactive Shot",
    category        = "ranged",
    type            = "reaction",
    weapon_skill    = "ranged",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_evade",
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Harry your foe with a quick shot and retreat.",
    evasiveness_base     = 3,  -- 3 + rank
    evasiveness_per_rank = 1,
    avoid_engagement_rounds = 1,
    msg_attempt = "You snap a quick shot at {target} and step back!",
    msg_hit     = "Your arrow finds {target}!",
    msg_fail    = "Your hasty shot misses wide!",
}

Techniques["pindown"] = def {
    mnemonic        = "pindown",
    name            = "Pin Down",
    category        = "ranged",
    type            = "aoe",
    weapon_skill    = "ranged",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Spray multiple targets with arrows, preventing them from advancing.",
    pinned_base     = 10,   -- Pinned = 10 + (rank*3)
    pinned_per_rank = 3,
    msg_attempt = "You loose a rapid volley of arrows to pin down multiple foes!",
    msg_hit     = "An arrow pins {target} in place!",
}

Techniques["barrage"] = def {
    mnemonic        = "barrage",
    name            = "Barrage",
    category        = "ranged",
    type            = "assault",
    weapon_skill    = "ranged",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Rapidly fire at a target.",
    -- Evade modified (margin/10)%, max 10%
    evade_mod_divisor = 10,
    evade_mod_cap     = 10,
    -- Party buff on success
    success_buff          = "enhance_dexterity",
    success_buff_power    = 10,
    success_buff_duration = 120,
    success_buff_party    = true,
    msg_attempt = "You rapidly nock and fire arrow after arrow at {target}!",
    msg_hit     = "An arrow from your barrage finds {target}!",
    msg_final   = "You lower your bow as your barrage concludes!",
}

Techniques["volley"] = def {
    mnemonic        = "volley",
    name            = "Volley",
    category        = "ranged",
    type            = "aoe",
    weapon_skill    = "ranged",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 20,
    base_rt         = 4,
    cooldown        = 20,
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Fire multiple times into the sky to rain down on enemies.",
    -- rank+1 shots, 1 round delay before impact
    impact_delay_rounds = 1,
    msg_attempt = "You fire a volley high into the sky!",
    msg_rain    = "Arrows rain down from above!",
    msg_hit     = "An arrow from above strikes {target}!",
}

-- ────────────────────────────────────────────────────────────────────────────
-- TWO-HANDED WEAPONS
-- ────────────────────────────────────────────────────────────────────────────
Techniques["overpower"] = def {
    mnemonic        = "overpower",
    name            = "Overpower",
    category        = "twohanded",
    type            = "reaction",
    weapon_skill    = "twohanded",
    min_ranks       = 10,
    rank_thresholds = {10, 35, 60, 85, 110},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_evade_block_parry",  -- any of the three
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Deal your target a heavy blow that cannot be evaded, blocked, or parried.",
    cer_bonus       = 10,      -- +10 CER critical weighting
    bypass_ebp      = true,    -- cannot be evaded, blocked, or parried
    msg_attempt = "You bring your weapon around in an unstoppable arc at {target}!",
    msg_hit     = "Your overpowering blow connects solidly!",
    msg_fail    = "{Target} manages to avoid your overpower attempt!",
}

Techniques["thrash"] = def {
    mnemonic        = "thrash",
    name            = "Thrash",
    category        = "twohanded",
    type            = "assault",
    weapon_skill    = "twohanded",
    min_ranks       = 25,
    rank_thresholds = {25, 50, 75, 100, 125},
    stamina_cost    = 15,
    base_rt         = 2,
    cooldown        = 0,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Repeatedly strike a target with overwhelming force.",
    parry_mod_divisor = 10,   -- (margin/10)%, max 10%
    parry_mod_cap     = 10,
    success_buff      = "forceful_blows",
    success_buff_duration = 120,
    msg_attempt = "You rush {target}, raising your weapon high to deliver a sound thrashing!",
    msg_hit     = "You bring your weapon around in a tight arc to batter {target} into submission!",
    msg_final   = "With a final, explosive breath, you pull your weapon back to a ready position.",
}

Techniques["reversestrike"] = def {
    mnemonic        = "reversestrike",
    name            = "Reverse Strike",
    category        = "twohanded",
    type            = "reaction",
    weapon_skill    = "twohanded",
    min_ranks       = 50,
    rank_thresholds = {50, 75, 100, 125, 150},
    stamina_cost    = 0,
    base_rt         = 0,
    rt_mod          = -2,
    cooldown        = 0,
    reaction_trigger = "recent_parry",
    offensive_gear  = "both_hands",
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Catch your target off guard with a quick, reverse strike.",
    bypass_stance_ds = true,   -- ignores target stance DS bonus
    disoriented_base     = 8,  -- Disoriented = 8 + (rank*3)
    disoriented_per_rank = 3,
    msg_attempt = "You feint then snap your weapon back in a sudden reverse strike at {target}!",
    msg_hit     = "Your unexpected reverse strike catches {target} completely off guard!",
    msg_fail    = "{Target} recovers before your reverse strike lands!",
}

Techniques["whirlwind"] = def {
    mnemonic        = "whirlwind",
    name            = "Whirlwind",
    category        = "twohanded",
    type            = "aoe",
    weapon_skill    = "twohanded",
    min_ranks       = 75,
    rank_thresholds = {75, 100, 125, 150, 175},
    stamina_cost    = 20,
    base_rt         = 3,
    cooldown        = 15,
    offensive_gear  = "both_hands",
    flares_enabled  = true,
    racial_size_mod = true,
    available_to    = {"warrior","rogue","ranger","bard","monk","paladin"},
    description     = "Spin around hitting multiple targets.",
    evasiveness_base     = 5,   -- 5 + rank
    evasiveness_per_rank = 1,
    force_stance_threshold = 100, -- high margin forces stance change
    msg_attempt = "You spin in a powerful whirlwind attack!",
    msg_hit     = "Your spinning weapon crashes into {target}!",
}

-- ---------------------------------------------------------------------------
-- Category index (for WEAPON LIST filtering)
-- ---------------------------------------------------------------------------
Techniques._by_category = {
    brawling  = {"twinhammer","fury","clash","spinkick"},
    blunt     = {"dizzyingswing","clobber","pummel","pulverize"},
    edged     = {"cripple","riposte","flurry","wblade"},
    polearm   = {"charge","gthrusts","cyclone","radialsweep"},
    ranged    = {"reactiveshot","pindown","barrage","volley"},
    twohanded = {"overpower","thrash","reversestrike","whirlwind"},
}

-- Type index (for WEAPON LIST <type> filtering)
Techniques._by_type = {
    setup     = {"twinhammer","dizzyingswing","cripple","charge"},
    assault   = {"fury","pummel","flurry","gthrusts","barrage","thrash"},
    reaction  = {"spinkick","clobber","riposte","radialsweep","reactiveshot","overpower","reversestrike"},
    aoe       = {"clash","pulverize","wblade","cyclone","pindown","volley","whirlwind"},
}

-- Profession eligibility check
function Techniques.can_use(mnemonic, profession_name)
    local t = Techniques[mnemonic]
    if not t then return false end
    local prof = (profession_name or ""):lower()
    for _, p in ipairs(t.available_to or {}) do
        if p == prof then return true end
    end
    return false
end

return Techniques
