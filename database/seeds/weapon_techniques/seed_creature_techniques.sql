-- =============================================================================
-- Seed: Creature Weapon Technique Assignments
-- Sources: GS4 Wiki pages for Twin Hammerfists and Charge confirm these creatures.
-- creature_id must match your creatures table.
-- This seed uses creature name lookup to be safe across different auto-increment orders.
-- =============================================================================

-- Wrapper: use a stored procedure so we can look up creature IDs by name safely.
-- Run this AFTER both weapon_techniques seed AND creatures seed are loaded.

-- ---------------------------------------------------------------------------
-- Creatures confirmed on GS4 Wiki to use Twin Hammerfists:
--   Flesh golem, Soul golem
-- Creatures confirmed on GS4 Wiki to use Charge (polearm):
--   Decaying Citadel guardsman, Triton combatant, Triton radical
-- ---------------------------------------------------------------------------

INSERT INTO creature_weapon_techniques (creature_id, technique_id, creature_rank, use_chance_pct, cooldown_rounds)
SELECT
    c.id                AS creature_id,
    wt.id               AS technique_id,
    2                   AS creature_rank,   -- rank 2 for these named creatures
    25                  AS use_chance_pct,  -- 25% chance per eligible round
    3                   AS cooldown_rounds
FROM creatures c
JOIN weapon_techniques wt ON wt.mnemonic = 'twinhammer'
WHERE c.name IN ('flesh golem', 'soul golem')
ON DUPLICATE KEY UPDATE
    creature_rank    = VALUES(creature_rank),
    use_chance_pct   = VALUES(use_chance_pct),
    cooldown_rounds  = VALUES(cooldown_rounds);

INSERT INTO creature_weapon_techniques (creature_id, technique_id, creature_rank, use_chance_pct, cooldown_rounds)
SELECT
    c.id                AS creature_id,
    wt.id               AS technique_id,
    2                   AS creature_rank,
    20                  AS use_chance_pct,
    4                   AS cooldown_rounds
FROM creatures c
JOIN weapon_techniques wt ON wt.mnemonic = 'charge'
WHERE c.name IN ('decaying citadel guardsman', 'triton combatant', 'triton radical')
ON DUPLICATE KEY UPDATE
    creature_rank    = VALUES(creature_rank),
    use_chance_pct   = VALUES(use_chance_pct),
    cooldown_rounds  = VALUES(cooldown_rounds);

-- ---------------------------------------------------------------------------
-- General assignment template for future use:
-- To give any creature a technique, use:
--
-- INSERT INTO creature_weapon_techniques (creature_id, technique_id, creature_rank, use_chance_pct, cooldown_rounds)
-- SELECT c.id, wt.id, <rank>, <pct>, <cooldown>
-- FROM creatures c JOIN weapon_techniques wt ON wt.mnemonic = '<mnemonic>'
-- WHERE c.name = '<creature name>'
-- ON DUPLICATE KEY UPDATE creature_rank=VALUES(creature_rank);
-- ---------------------------------------------------------------------------
