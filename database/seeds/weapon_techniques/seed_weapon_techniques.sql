-- =============================================================================
-- Seed: Weapon Techniques
-- 24 canonical GemStone IV techniques across 6 weapon categories
-- weapon_skill_id matches skills table auto-increment order:
--   5=Edged  6=Blunt  7=Two-Handed  10=Polearm  8=Ranged  11=Brawling
-- =============================================================================

INSERT INTO weapon_techniques (
    mnemonic, name, weapon_category, technique_type,
    weapon_skill_id, min_skill_ranks, rank2_ranks, rank3_ranks, rank4_ranks, rank5_ranks,
    stamina_cost, base_roundtime, cooldown_seconds,
    description, mechanics_notes,
    available_to, reaction_trigger,
    offensive_gear, flares_enabled, racial_size_mod, target_stance_bonus, shield_def_bonus
) VALUES

-- ============================================================
-- BRAWLING  (skill_id=11)
-- ============================================================
(
    'twinhammer', 'Twin Hammerfists', 'brawling', 'setup',
    11, 10, 35, 60, 85, 110,
    7, 2, 0,
    'Attempt to knockdown and potentially stun your opponent by swinging your fists down on them.',
    'SMRv2 maneuver. Applies Vulnerable for (15+(Rank*5))s and Staggered for (SuccessMargin/10)s. Chance to stun based on success margin.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 1, 1, 1
),
(
    'fury', 'Fury', 'brawling', 'assault',
    11, 25, 50, 75, 100, 125,
    15, 2, 0,
    'Unleash your fury upon your foe in a relentless assault.',
    'Multi-round assault. Each round: attack once. Parry chance modified by (SuccessMargin/5)% max 10%. On success gain Frenzy buff for 2 minutes.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),
(
    'clash', 'Clash', 'brawling', 'aoe',
    11, 50, 75, 100, 125, 150,
    20, 3, 15,
    'Hurl yourself into a clashing brawl with one or more foes.',
    'AoE. Attacks up to (1+MOC_bonus) targets. Each target receives SMRv2 roll. Grants Evasiveness for (5+Rank)s on success.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 1, 1, 1
),
(
    'spinkick', 'Spin Kick', 'brawling', 'reaction',
    11, 75, 100, 125, 150, 175,
    0, 0, 0,
    'Spin around kicking a target.',
    'Reaction. Free action, no stamina cost, usable in self-inflicted RT. Trigger: recent_evade. Attack with +10 CER. Applies Staggered for (SuccessMargin/8)s.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_evade',
    'both_hands', 0, 0, 1, 1
),

-- ============================================================
-- BLUNT WEAPONS  (skill_id=6)
-- ============================================================
(
    'dizzyingswing', 'Dizzying Swing', 'blunt', 'setup',
    6, 10, 35, 60, 85, 110,
    7, 2, 0,
    'Smash a target in the head, confusing them.',
    'SMRv2 maneuver. Deals crush damage. Applies Dazed for (15+(Rank*5))s. On high success margin applies Staggered for (SuccessMargin/10)s.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'right_hand', 1, 0, 1, 1
),
(
    'clobber', 'Clobber', 'blunt', 'reaction',
    6, 25, 50, 75, 100, 125,
    0, 0, 0,
    'React to a parry with a devastating concussion attack.',
    'Reaction. Free action, no stamina. Trigger: recent_parry. Attack with Weakened Armament applied for (15+(Rank*5))s before resolution. Removes recent EBP from attacker.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_parry',
    'both_hands', 0, 0, 1, 1
),
(
    'pummel', 'Pummel', 'blunt', 'assault',
    6, 50, 75, 100, 125, 150,
    15, 2, 0,
    'Pummel the target repeatedly with your weapon.',
    'Multi-round assault based on MOC ranks. Parry modified by (SuccessMargin/5)% max 10% per round. On success gain Forceful Blows for 2 minutes.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),
(
    'pulverize', 'Pulverize', 'blunt', 'aoe',
    6, 75, 100, 125, 150, 175,
    20, 3, 15,
    'Target the armor of multiple targets, weakening it.',
    'AoE. Attacks up to (1+MOC_bonus) targets. Each hit applies Weakened Armament for (15+(Rank*3))s. Deals reduced crush damage.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),

-- ============================================================
-- EDGED WEAPONS  (skill_id=5)
-- ============================================================
(
    'cripple', 'Cripple', 'edged', 'setup',
    5, 10, 35, 60, 85, 110,
    7, 2, 0,
    'Slash a target''s limb to cripple their combat effectiveness.',
    'SMRv2 maneuver. Minor slash damage. Applies Crippled for (15+(Rank*5))s. Targeting a leg also applies Rooted for (10+(Rank*2))s.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'right_hand', 1, 0, 1, 1
),
(
    'riposte', 'Riposte', 'edged', 'reaction',
    5, 25, 50, 75, 100, 125,
    0, 0, 0,
    'React to a parry with a counter-attack.',
    'Reaction. Free action, no stamina, RT=ATTACK-2. Trigger: recent_parry. Applies Weakened Armament for (15+(Rank*5))s before attack resolution. Removes recent EBP from attacker.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_parry',
    'both_hands', 0, 0, 1, 1
),
(
    'flurry', 'Flurry', 'edged', 'assault',
    5, 50, 75, 100, 125, 150,
    15, 2, 0,
    'Rapidly slash a target.',
    'Assault: attacks target (1 + MOC_bonus) times. Parry modified (SuccessMargin/5)% max 10% per round. On success gain Slashing Strikes for 2 minutes.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),
(
    'wblade', 'Whirling Blade', 'edged', 'aoe',
    5, 75, 100, 125, 150, 175,
    20, 3, 15,
    'Unleash a flurry of quick attacks against a target.',
    'AoE. Attacks (1+MOC_bonus) targets. Grants Evasiveness for (5+Rank)s on execution.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 0, 0, 1, 1
),

-- ============================================================
-- POLEARM WEAPONS  (skill_id=10)
-- ============================================================
(
    'charge', 'Charge', 'polearm', 'setup',
    10, 10, 35, 60, 85, 110,
    14, 4, 0,
    'Charge at your opponent with your polearm.',
    'SMRv2. Moderate weapon + unbalance damage. Can force target to higher stance. Applies Vulnerable for (15+(Rank*5))s and Staggered for (SuccessMargin/6)s.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'right_hand', 1, 1, 1, 1
),
(
    'gthrusts', 'Guardant Thrusts', 'polearm', 'assault',
    10, 25, 50, 75, 100, 125,
    15, 2, 0,
    'Assault your target with a series of thrusts, while maximizing your defenses.',
    'Assault: each round attacks once with thrust. Each round grants +5 DS (stacks up to Rank times). On completion: Fortified Stance buff for 30s.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),
(
    'cyclone', 'Cyclone', 'polearm', 'aoe',
    10, 50, 75, 100, 125, 150,
    20, 3, 15,
    'Spin your polearm around you attacking and forcing enemies back.',
    'AoE. Attacks all enemies in room up to (1+MOC_bonus). Each hit: unbalance damage, applies Staggered for (SuccessMargin/8)s. Forces lower stance on critically hit targets.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 1, 1, 1
),
(
    'radialsweep', 'Radial Sweep', 'polearm', 'reaction',
    10, 75, 100, 125, 150, 175,
    0, 0, 0,
    'Spin your polearm around you targeting the legs of enemies.',
    'Reaction. Free action, no stamina, RT=ATTACK-2. Trigger: recent_evade. AoE vs all enemies in room. Each hit targets legs: applies Rooted for (8+(Rank*2))s.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_evade',
    'both_hands', 0, 1, 1, 1
),

-- ============================================================
-- RANGED WEAPONS  (skill_id=8)
-- ============================================================
(
    'reactiveshot', 'Reactive Shot', 'ranged', 'reaction',
    8, 10, 35, 60, 85, 110,
    0, 0, 0,
    'Harry your foe with a quick shot and retreat.',
    'Reaction. Free action, no stamina. Trigger: recent_evade. Quick ranged attack. On hit: attacker gains Evasiveness for (3+Rank)s and backs up (avoids engagement penalty 1 round).',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_evade',
    'both_hands', 0, 0, 1, 0
),
(
    'pindown', 'Pin Down', 'ranged', 'aoe',
    8, 25, 50, 75, 100, 125,
    20, 3, 15,
    'Spray multiple targets with arrows, preventing them from advancing.',
    'AoE. Shoots up to (1+MOC_bonus) targets. Each hit applies Pinned for (10+(Rank*3))s preventing movement toward attacker.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 0, 0, 1, 0
),
(
    'barrage', 'Barrage', 'ranged', 'assault',
    8, 50, 75, 100, 125, 150,
    15, 2, 0,
    'Rapidly fire at a target.',
    'Assault: fires (1+MOC_bonus) times per round. Evade modified by (SuccessMargin/10)% max 10% per round. On success: attacker and party gain Enhance Dexterity power 10 for 2 minutes.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 0, 0, 1, 0
),
(
    'volley', 'Volley', 'ranged', 'aoe',
    8, 75, 100, 125, 150, 175,
    20, 4, 20,
    'Fire multiple times into the sky to rain down on enemies.',
    'AoE. Fires (Rank+1) shots that rain down next round hitting random enemies in room. Each arrow resolves independently. Delay of 1 round before impact.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 0, 0, 1, 0
),

-- ============================================================
-- TWO-HANDED WEAPONS  (skill_id=7)
-- ============================================================
(
    'overpower', 'Overpower', 'twohanded', 'reaction',
    7, 10, 35, 60, 85, 110,
    0, 0, 0,
    'Deal your target a heavy blow that cannot be evaded, blocked, or parried.',
    'Reaction. Free action, no stamina, RT=ATTACK-2. Trigger: recent_evade OR recent_block OR recent_parry. +10 CER critical weighting. Attack cannot be evaded, blocked, or parried.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_evade_block_parry',
    'both_hands', 0, 0, 1, 1
),
(
    'thrash', 'Thrash', 'twohanded', 'assault',
    7, 25, 50, 75, 100, 125,
    15, 2, 0,
    'Repeatedly strike a target with overwhelming force.',
    'Assault: attacks (1+MOC_bonus) times. Parry modified (SuccessMargin/10)% max 10% per round. On success gain Forceful Blows for 2 minutes.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 0, 1, 1
),
(
    'reversestrike', 'Reverse Strike', 'twohanded', 'reaction',
    7, 50, 75, 100, 125, 150,
    0, 0, 0,
    'Catch your target off guard with a quick, reverse strike.',
    'Reaction. Free action, no stamina, RT=ATTACK-2. Trigger: recent_parry. Bypasses target Stance bonus to DS. Applies Disoriented for (8+(Rank*3))s on hit.',
    'warrior,rogue,ranger,bard,monk,paladin', 'recent_parry',
    'both_hands', 0, 0, 1, 1
),
(
    'whirlwind', 'Whirlwind', 'twohanded', 'aoe',
    7, 75, 100, 125, 150, 175,
    20, 3, 15,
    'Spin around hitting multiple targets.',
    'AoE. Attacks (1+MOC_bonus) targets with full weapon damage. Grants Evasiveness for (5+Rank)s. Each hit may force target to higher stance on high success margin.',
    'warrior,rogue,ranger,bard,monk,paladin', NULL,
    'both_hands', 1, 1, 1, 1
)

ON DUPLICATE KEY UPDATE
    name             = VALUES(name),
    mechanics_notes  = VALUES(mechanics_notes),
    description      = VALUES(description),
    updated_at       = CURRENT_TIMESTAMP;
