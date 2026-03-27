-- Zone 8: Lunule Weald
local Zone = {}

Zone.id        = 8
Zone.name      = "Lunule Weald"
Zone.region    = "Elanith"
Zone.level_min = 13
Zone.level_max = 30
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad() print("[Zone] Lunule Weald loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "Swarms of insects buzz loudly in the thick, humid air.",
    "The lonely sound of an owl hooting breaks the monotony of silence.",
    "A piercing whistle from atop the hill reverberates through the area.",
    "Dead leaves periodically float to the forest floor as the breeze shakes them loose.",
    "The howling wind scatters dead debris into the air, shredding spider webs.",
    "Strange crescent-moon symbols painted on rocks catch the moonlight.",
    "The sense of death and decay is pervasive — not even crickets dare disturb the air.",
    "Small metal crescent moons tinkle softly as they bump against each other in the trees.",
    "Worms and insects ooze from the rotting bark of the dark fel trees.",
}
Zone.ambient_interval = 120

return Zone
