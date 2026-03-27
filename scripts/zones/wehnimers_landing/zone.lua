---------------------------------------------------
-- Wehnimer's Landing
-- Primary starting town, human harbor settlement
-- Level range: 1-20 (town and surrounding areas)
---------------------------------------------------

local Zone = {}

Zone.id        = 1
Zone.name      = "Wehnimer's Landing"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 20
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Wehnimer's Landing loaded.")
end

function Zone.onTick(elapsed)
end

function Zone.onPlayerEnter(player)
end

function Zone.onPlayerLeave(player)
end

Zone.ambient_messages = {
    "A cool breeze blows in from the harbor.",
    "You hear the distant cry of a seagull.",
    "The murmur of townsfolk going about their business fills the air.",
    "A merchant hawk calls out, advertising his wares.",
    "The scent of freshly baked bread wafts from a nearby shop.",
    "A guard patrol marches past, armor clanking softly.",
}

Zone.ambient_interval = 90

return Zone
