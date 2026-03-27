-- Zone 4: Timmorain Road
local Zone = {}

Zone.id        = 4
Zone.name      = "Timmorain Road"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 5
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad() print("[Zone] Timmorain Road loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "A cool river breeze drifts up from the Mistydeep, carrying the scent of fresh water.",
    "The cobblestone road stretches steadily northeast, its surface worn smooth by countless travelers.",
    "Leaves rustle overhead as a gust of wind passes through the thick canopy.",
    "Birdsong echoes from the treetops lining the well-maintained road.",
    "Dappled sunlight shifts across the cobblestones as clouds drift overhead.",
    "A squirrel skitters across the cobblestones and disappears into the underbrush.",
}
Zone.ambient_interval = 120

return Zone
