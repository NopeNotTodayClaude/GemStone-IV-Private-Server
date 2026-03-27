------------------------------------------------------------------------
-- scripts/npcs/tavaalor_town_guard.lua
-- Ta'Vaalor Town Guard — combat-capable, wandering, ambient emotes
--
-- This guard patrols the city, will fight hostile creatures or players
-- who attack citizens, and fires ambient emotes while on duty.
--
-- Room IDs are real GS4 room IDs from the Ta'Vaalor map data.
------------------------------------------------------------------------

local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "tavaalor_town_guard"
NPC.name           = "a Vaalor town guard"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A disciplined elven soldier in polished crimson and gold armor bearing the insignia of the Ta'Vaalor Legion.  She moves through the city with the measured awareness of someone trained to notice everything."
NPC.home_room_id   = 3542   -- Victory Court (King's Court fountain)

-- ── Capabilities ──────────────────────────────────────────────────────────────
NPC.can_combat     = true
NPC.can_shop       = false
NPC.can_wander     = true
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = true    -- participates in invasion events

-- ── Combat stats ──────────────────────────────────────────────────────────────
NPC.level          = 8
NPC.hp             = 350
NPC.as_melee       = 145
NPC.ds_melee       = 110
NPC.ds_ranged      = 90
NPC.td             = 45
NPC.armor_asg      = 13     -- chain hauberk equivalent
NPC.body_type      = "biped"
NPC.aggressive     = false  -- only fights if attacked or invasion triggers
NPC.unkillable     = false
NPC.respawn_seconds = 300   -- 5 minutes

NPC.attacks = {
    { type = "longsword",  as = 145, damage_type = "slash" },
    { type = "kick",       as = 120, damage_type = "crush" },
}

-- ── Wander / patrol ───────────────────────────────────────────────────────────
NPC.patrol_rooms = {
    3542,   -- Victory Court (fountain)
    3519,   -- Victory Court center
    3518,   -- Hall of Justice area
    3521,   -- Warrior Guild / Resort
    3522,   -- Annatto Wey west (Pawn Shop)
    3523,   -- Annatto Wey east (Annatto Gate)
    3542,   -- return to fountain
}
NPC.wander_chance  = 0.35
NPC.move_interval  = 28     -- moves every ~28 seconds when rolling lucky

-- ── Invasion config ───────────────────────────────────────────────────────────
NPC.invasion_zone  = "tavaalor"
NPC.invasion_side  = "ally"   -- fights alongside players against invaders

-- ── Dialogue ──────────────────────────────────────────────────────────────────
NPC.dialogues = {
    trouble   = "Report any disturbance to the nearest guardsman.  We respond quickly.",
    hunting   = "Keep your hunting outside the walls.  Inside the city, weapons stay sheathed.",
    legion    = "The Legion maintains order so citizens and visitors can go about their lives.  That is the job.",
    city      = "Ta'Vaalor is the fortress city of the Elven Nations.  We've held it for seven centuries.",
    invasion  = "If the alarm sounds, stay inside a building.  The guard will handle it.",
    new       = "New to Ta'Vaalor?  The Adventurers Guild posts work.  Sassion near the Vermilion Gate is another resource.",
    default   = "The guard gives you a measured look.  'Move along.'",
}
NPC.greeting       = nil

-- ── Ambient emotes ────────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A Vaalor town guard scans the square with alert eyes.",
    "A Vaalor town guard nods to a passing citizen.",
    "A Vaalor town guard adjusts her grip on her spear.",
    "A Vaalor town guard pauses to observe a group of adventurers, then resumes her patrol.",
    "A Vaalor town guard exchanges a quiet word with a passing Legion soldier.",
    "A Vaalor town guard straightens her posture as a senior officer approaches.",
}
NPC.ambient_chance  = 0.025
NPC.emote_cooldown  = 50

-- ── Hooks ─────────────────────────────────────────────────────────────────────

function NPC:on_load()
    -- Nothing special on load for a basic guard
end

function NPC:on_invasion(zone)
    -- When an invasion starts in Ta'Vaalor, this guard becomes aggressive
    -- toward enemies. The invasion manager toggles NPC.aggressive via this hook.
    self.aggressive = true
end

function NPC:on_combat_start(target)
    -- Shout a line when entering combat
    -- (The manager broadcasts this via the world API)
end

function NPC:on_death()
    -- The guard's death is handled by the manager.
    -- A replacement will spawn in respawn_seconds.
    self.aggressive = false
end

return NPC
