-- Zone: Grasslands
local Zone = {}

Zone.id        = 35
Zone.name      = "Grasslands"
Zone.region    = "Elanith"
Zone.level_min = 14
Zone.level_max = 20
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Grasslands loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The tall grass ripples in waves across the open plain.",
    "A hawk circles lazily overhead, riding the thermals.",
    "The distant treeline marks the edge of the apple orchards.",
    "Wind rustles through the barley field, bending the stalks in unison.",
    "The smell of wildflowers carries across the meadow on a warm breeze.",
    "A thunderhead builds in the distance, dark and slow-moving.",
    "Insects hum in the warm grass as you pass.",
    "The vineyard rows stretch toward the horizon in neat, orderly lines.",
    "Something large moves through the tall grass nearby, then is still.",
    "The ground here is rich and dark, soft underfoot.",
}

Zone.ambient_interval = 120

return Zone
