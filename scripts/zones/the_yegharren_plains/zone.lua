---------------------------------------------------
-- The Yegharren Plains
-- Vast open grassland north of Wehnimer's Landing
-- Home of tawny brindlecats and plains predators
-- Level range: 11-16
-- zone_id: 87
---------------------------------------------------

local Zone = {}

Zone.id        = 87
Zone.name      = "The Yegharren Plains"
Zone.region    = "Elanith"
Zone.level_min = 11
Zone.level_max = 16
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] The Yegharren Plains loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The grass stretches to the horizon without interruption, moving in long slow waves.",
    "Something large passes through the grass to the east — just a ripple of movement, then nothing.",
    "The wind carries the smell of dry earth and something faintly musky.",
    "A distant sound, low and rumbling, rolls across the plain from the direction of the barrows.",
    "A hawk circles at height, tracking something on the ground below with patient precision.",
    "The plain is quieter than it should be. Something has been through here recently.",
}

Zone.ambient_interval = 120

return Zone
