-- Zone: Teras Isle
local Zone = {}

Zone.id        = 0  -- set by DB zone_id
Zone.name      = "Teras Isle"
Zone.region    = "Elanthia"
Zone.level_min = 26
Zone.level_max = 63
Zone.climate   = "volcanic"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Teras Isle loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The volcano rumbles in the distance, a deep sound felt more than heard.",
    "Ash drifts on the heated air, settling on every surface.",
    "A geyser erupts somewhere ahead with a hiss of steam.",
    "The ground here is warm to the touch even through boots.",
    "Sulfurous fumes drift from a nearby vent, acrid and eye-watering.",
    "The sky above the volcano glows orange against the night.",
    "Lava cools in slow, black rivers across the basalt flats.",
}

Zone.ambient_interval = 120

return Zone
