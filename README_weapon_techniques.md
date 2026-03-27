# Weapon Techniques System
## GemStone IV Private Server

---

## What This Implements

Full GS4-canonical Weapon Techniques system: all 24 techniques across 6 weapon
categories, SMRv2 math, auto-grant on training, player WEAPON verb, and creature
integration.

---

## File List

### SQL
| File | Purpose |
|------|---------|
| `database/migrations/011_weapon_techniques.sql` | Creates 4 tables |
| `database/seeds/weapon_techniques/seed_weapon_techniques.sql` | Seeds all 24 techniques |
| `database/seeds/weapon_techniques/seed_creature_techniques.sql` | Assigns techniques to wiki-confirmed creatures |

### Lua
| File | Purpose |
|------|---------|
| `scripts/globals/utils/smr.lua` | Full SMRv2 roll engine (offense + defense math) |
| `scripts/weapon_techniques/definitions.lua` | All 24 technique data tables keyed by mnemonic |
| `scripts/weapon_techniques/engine.lua` | Dispatcher, WEAPON LIST/HELP, auto-grant, creature dispatch |
| `scripts/weapon_techniques/techniques/brawling.lua` | Twin Hammerfists, Fury, Clash, Spin Kick |
| `scripts/weapon_techniques/techniques/blunt.lua` | Dizzying Swing, Clobber, Pummel, Pulverize |
| `scripts/weapon_techniques/techniques/edged.lua` | Cripple, Riposte, Flurry, Whirling Blade |
| `scripts/weapon_techniques/techniques/polearm.lua` | Charge, Guardant Thrusts, Cyclone, Radial Sweep |
| `scripts/weapon_techniques/techniques/ranged.lua` | Reactive Shot, Pin Down, Barrage, Volley |
| `scripts/weapon_techniques/techniques/twohanded.lua` | Overpower, Thrash, Reverse Strike, Whirlwind |

### Python (new files)
| File | Purpose |
|------|---------|
| `server/core/engine/combat/smr_engine.py` | Python-native SMRv2 (mirrors Lua, used by bridge) |
| `server/core/scripting/lua_bindings/weapon_api.py` | Lua bridge: effects, stamina, RT, grants, creatures |
| `server/core/commands/player/weapon_techniques.py` | WEAPON verb handler + `check_technique_grants()` |

### Patch files (manual edits required)
| File | What to do |
|------|-----------|
| `PATCH_training.txt` | Add 1 import + 1 line to `training.py` |
| `PATCH_command_router.txt` | Add 1 import + 1 dict entry to `command_router.py` |

---

## Deployment Steps

### 1. Run the migration
```
mysql -u root -p gemstone < database/migrations/011_weapon_techniques.sql
```

### 2. Run the seeds
```
mysql -u root -p gemstone < database/seeds/weapon_techniques/seed_weapon_techniques.sql
mysql -u root -p gemstone < database/seeds/weapon_techniques/seed_creature_techniques.sql
```

### 3. Copy Lua files
Copy everything under `scripts/` into your server's `scripts/` directory.
The Lua require paths are:
- `require("globals/utils/smr")`
- `require("weapon_techniques/definitions")`
- `require("weapon_techniques/engine")`
- `require("weapon_techniques/techniques/brawling")` etc.

### 4. Copy Python files
Copy the three Python files to their paths as listed above.

### 5. Apply patches
Read `PATCH_training.txt` and `PATCH_command_router.txt` and make the small
manual edits described. Each patch is exactly 1 import line + 1 code line.

### 6. Enable the MySQL event scheduler (for reaction log cleanup)
```sql
SET GLOBAL event_scheduler = ON;
```
Or add `event_scheduler = ON` to your `my.cnf`.

---

## How It Works

### Auto-Grant
When a player trains any weapon skill via `TRAIN`, `training.py` calls
`check_technique_grants(session, skill_id, new_ranks, server)`.

The Lua engine (`engine.onAutoGrant`) scans all techniques for that skill
category and returns any where `weapon_ranks >= threshold` that the player
doesn't already have (or has at a lower rank than earned).

The Python bridge inserts/updates `character_weapon_techniques` and messages
the player immediately:

```
You have learned the Cripple weapon technique!
Your Riposte technique has improved to rank 2!
```

### WEAPON Verb
```
WEAPON LIST               -- all techniques, shows learned status
WEAPON LIST edged         -- filter by category
WEAPON LIST reaction      -- filter by type
WEAPON HELP cripple       -- full mechanic description
WEAPON cripple kobold     -- execute (auto-grants already happened)
WEAPON cripple kobold right leg   -- with limb targeting
WEAPON whirlwind          -- AoE techniques don't need a named target
```

### Reaction Techniques
Reaction triggers (`recent_parry`, `recent_evade`, `recent_block`) are set
by `combat_engine.py` when the event occurs:

```python
# In combat_engine.py, when a parry occurs:
from server.core.scripting.lua_bindings.weapon_api import set_reaction_trigger
set_reaction_trigger(session, 'recent_parry')
```

Triggers expire after 8 seconds (GS4 canonical window).  They are stored
in `session.reaction_triggers` (dict of `{trigger: expiry_monotonic_time}`).
The Lua engine reads them as booleans and consumes them on use (success or fail).

### Creature Techniques
The combat engine should call `creature_use_technique()` during creature turns:

```python
from server.core.scripting.lua_bindings.weapon_api import creature_use_technique

# Inside the creature's attack routine, after checking creature_weapon_techniques:
msg = await creature_use_technique(
    creature, target_session, mnemonic, creature_rank, server
)
if msg:
    # broadcast msg to room
```

The `creature_weapon_techniques` table drives which creatures can use which
techniques, their rank, use chance %, and cooldown in rounds.

---

## All 24 Techniques — Quick Reference

| Mnemonic | Name | Category | Type | Min Ranks | Stamina | Key Effect |
|----------|------|----------|------|-----------|---------|-----------|
| twinhammer | Twin Hammerfists | Brawling | Setup | 10 | 7 | Vulnerable(15+r*5)s, Staggered(margin/10)s |
| fury | Fury | Brawling | Assault | 25 | 15 | Multi-hit, parry mod(margin/5)%, Frenzy 120s |
| clash | Clash | Brawling | AoE | 50 | 20 | AoE crush, Evasiveness(5+r)s |
| spinkick | Spin Kick | Brawling | Reaction | 75 | 0 | recent_evade, +10 CER, Staggered(margin/8)s |
| dizzyingswing | Dizzying Swing | Blunt | Setup | 10 | 7 | Dazed(15+r*5)s, Staggered(margin/10)s |
| clobber | Clobber | Blunt | Reaction | 25 | 0 | recent_parry, Weakened Armament(15+r*5)s |
| pummel | Pummel | Blunt | Assault | 50 | 15 | Multi-hit, parry mod(margin/5)%, Forceful Blows 120s |
| pulverize | Pulverize | Blunt | AoE | 75 | 20 | AoE crush, Weakened Armament(15+r*3)s all targets |
| cripple | Cripple | Edged | Setup | 10 | 7 | Crippled(15+r*5)s; leg→Rooted(10+r*2)s |
| riposte | Riposte | Edged | Reaction | 25 | 0 | recent_parry, Weakened Armament(15+r*5)s pre-attack |
| flurry | Flurry | Edged | Assault | 50 | 15 | Multi-hit, parry mod(margin/5)%, Slashing Strikes 120s |
| wblade | Whirling Blade | Edged | AoE | 75 | 20 | AoE slash, Evasiveness(5+r)s, 15s cooldown |
| charge | Charge | Polearm | Setup | 10 | 14 | Vulnerable(15+r*5)s, Staggered(margin/6)s, stance force |
| gthrusts | Guardant Thrusts | Polearm | Assault | 25 | 15 | Multi-hit, +5 DS/round stacking, Fortified Stance 30s |
| cyclone | Cyclone | Polearm | AoE | 50 | 20 | AoE unbalance, Staggered(margin/8)s each |
| radialsweep | Radial Sweep | Polearm | Reaction | 75 | 0 | recent_evade, AoE legs, Rooted(8+r*2)s each |
| reactiveshot | Reactive Shot | Ranged | Reaction | 10 | 0 | recent_evade, quick shot, Evasiveness(3+r)s |
| pindown | Pin Down | Ranged | AoE | 25 | 20 | AoE puncture, Pinned(10+r*3)s each |
| barrage | Barrage | Ranged | Assault | 50 | 15 | Multi-shot, evade mod(margin/10)%, Enhance Dex party 120s |
| volley | Volley | Ranged | AoE | 75 | 20 | (r+1) arrows, 1 round delay, random targets |
| overpower | Overpower | Two-Handed | Reaction | 10 | 0 | any EBP trigger, +10 CER, bypass evade/block/parry |
| thrash | Thrash | Two-Handed | Assault | 25 | 15 | Multi-hit, parry mod(margin/10)%, Forceful Blows 120s |
| reversestrike | Reverse Strike | Two-Handed | Reaction | 50 | 0 | recent_parry, bypass stance DS, Disoriented(8+r*3)s |
| whirlwind | Whirlwind | Two-Handed | AoE | 75 | 20 | AoE full damage, Evasiveness(5+r)s |

---

## SMRv2 Math Summary

**Offense** = SkillBonus(avg(CM_eff, WeaponSkill_eff)) + StanceMod + RacialSize + WeaponSpecBonus + MKBonus - Penalties

**Defense** = SkillBonus(avg(Dodge+RacialDodge, CM, Perc, PF [,Shield])) + StatMod(Agi*0.6 + (Dex+Int)*0.2) + StanceMod + SpellBonus + MKBonus - Penalties

**Roll** = open_d100 + Offense - Defense + extra_bonuses
**Success** = Roll > 100
**Margin** = Roll - 100

Maneuver knowledge bonuses (per rank): Off = [2,4,8,12,20], Def = [2,4,8,12,20]

Racial size endroll (offense): Giantman/HKrolv +10, Human/Dwarf +5, Elf/Aelotoi -5, ForestGnome -10, Halfling -15, BurghalGnome -20

---

## Adding Techniques to New Creatures

In your creature's zone Lua script (`scripts/zones/<zone>/mobs/<creature>.lua`),
add a `combat_round` hook:

```lua
local WeaponAPI = nil  -- loaded via Python bridge

function Creature.onCombatRound(creature, target, server)
    -- Check the creature_weapon_techniques table entry (Python bridge handles this)
    -- Python combat_engine calls creature_use_technique() automatically
    -- when creature_weapon_techniques rows exist for this creature.
end
```

Or insert a row directly in `creature_weapon_techniques`:
```sql
INSERT INTO creature_weapon_techniques (creature_id, technique_id, creature_rank, use_chance_pct, cooldown_rounds)
SELECT c.id, wt.id, 3, 30, 3
FROM creatures c JOIN weapon_techniques wt ON wt.mnemonic = 'thrash'
WHERE c.name = 'krolvin warrior';
```

The combat engine will automatically poll this table per creature during its
attack turn and call `creature_use_technique()` at the configured chance.
