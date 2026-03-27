-- Zone 5: Neartofar Road
local Zone = {}

Zone.id        = 5
Zone.name      = "Neartofar Road"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 15
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad() print("[Zone] Neartofar Road loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "Ancient cobblestones stretch through a corridor of towering oaks and beeches.",
    "The songs of birds filter down through a thick leafy canopy overhead.",
    "A fresh breeze carries the loamy smell of rich forest earth.",
    "Acorns clatter down onto the cobblestones from the oaks overhead.",
    "The shadows deepen between the trees as the canopy thickens.",
    "Salt-tinged ocean air drifts inland on the breeze near the coast.",
    "A woodpecker hammers a steady rhythm somewhere deeper in the forest.",
}
Zone.ambient_interval = 120

return Zone
