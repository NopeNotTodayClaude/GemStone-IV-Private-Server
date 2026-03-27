-- Zone: Ta'Illistim
-- The Shining City, seat of House Argent Mirror in the Elven Nations.
-- DB zone_id: 7  |  Rooms loaded from database (33k+ room map)
-- This file satisfies the world_manager zone.lua requirement so the
-- zone directory is not skipped on startup.
local Zone = {}

Zone.id        = 7
Zone.name      = "Ta'Illistim"
Zone.region    = "Elanthia"
Zone.level_min = 1
Zone.level_max = 100
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    -- Rooms are loaded from the database; no Lua room files needed here.
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The silver spires of Ta'Illistim glimmer in the distance.",
    "A cool breeze carries the faint scent of elven incense.",
    "Elven script adorns the stones beneath your feet.",
    "The sound of distant harp music drifts through the air.",
}
Zone.ambient_interval = 120

return Zone
