-- =============================================================================
-- scripts/globals/perception.lua
-- Perception system configuration.
-- All tuning values for Perception skill checks live here.
-- The Python engine loads this via perception_loader.py at startup.
-- Never hardcode these values in Python.
-- =============================================================================

local Perception = {}

-- Skill ID for Perception (must match scripts/data/skills.lua)
Perception.skill_id = 27

-- Bonus per rank of Perception (GS4 standard: ranks * 3)
Perception.rank_multiplier = 3

-- Stat used for the perception bonus (INT, 1:2 bonus)
-- INT bonus = (stat - 50) // 2
Perception.stat = "stat_intuition"
Perception.stat_divisor = 2

-- =============================================================================
-- HIDE DETECTION
-- When a player attempts to HIDE, every other non-hidden player in the room
-- gets a perception counter-roll against the hider's hide total.
-- If the observer's perception roll >= hider's roll, they can see through it.
-- =============================================================================

-- Base difficulty an observer must beat to spot a successful hider
-- (this is the hider's own hide total — so the roll is purely relative)
-- Additional flat bonus awarded to the hider on top of their roll result
-- to make detection feel like an active skill gap, not coin-flip
Perception.hide_hider_bonus  = 20   -- hider gets +20 free on their side
Perception.hide_observer_mod = 0    -- flat modifier to observer side (set negative to make hiding easier)

-- Dark/outdoor modifiers for the OBSERVER (stacks against them)
-- Dark rooms make it harder to spot a hidden player
Perception.dark_penalty    = -20
Perception.outdoor_penalty = -10    -- outdoors = more cover = harder to spot

-- =============================================================================
-- SNEAK DETECTION
-- When a hidden/sneaking player moves INTO a room that already has players,
-- each present player gets a perception check against the sneaker's sneak total.
-- =============================================================================

Perception.sneak_hider_bonus  = 15   -- sneaker bonus (smaller than hide — movement is harder)
Perception.sneak_observer_mod = 0

-- =============================================================================
-- SEARCH — Hidden Exits
-- When a player uses SEARCH in a room, a Perception roll is made per hidden exit.
-- If the roll beats the exit's search_dc, the exit is revealed for that player.
-- =============================================================================

-- Level contribution to search roll: level * search_level_mult
Perception.search_level_mult = 0.5

-- Once a hidden exit is revealed, it persists on the room for this many seconds
-- 0 = permanent for the session (until server restart)
Perception.search_reveal_duration = 0

-- Message shown when SEARCH finds nothing new in a room
Perception.search_nothing_msg = "You search around carefully but find nothing hidden."

-- Message shown when SEARCH reveals a hidden exit (appended with exit name)
-- The room's own hidden_exit.message overrides this if defined
Perception.search_found_exit_msg = "Your careful search reveals a hidden path: "

-- Message shown when SEARCH fails to reveal a known hidden exit (player isn't skilled enough)
Perception.search_failed_exit_msg = "You sense there may be something hidden here, but can't quite make it out."

-- Threshold below which the player gets the "failed but felt something" message
-- If roll >= (search_dc - sense_threshold), show the tease message instead of nothing
Perception.sense_threshold = 15

-- =============================================================================
-- TRAP DETECTION
-- DETECT on treasure boxes should primarily reward Perception, with optional
-- support from trap-specific training.  The lock analysis and the trap analysis
-- are separate checks and should report separate odds.
-- =============================================================================

Perception.trap_detect_skill_id = 27
Perception.trap_detect_rank_multiplier = 3
Perception.trap_detect_stat = "stat_intuition"
Perception.trap_detect_stat_divisor = 2
Perception.trap_detect_secondary_skill_id = 24
Perception.trap_detect_secondary_rank_multiplier = 1
Perception.trap_detect_sense_threshold = 15

return Perception
