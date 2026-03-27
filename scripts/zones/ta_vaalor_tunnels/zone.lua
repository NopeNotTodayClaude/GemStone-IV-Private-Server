-- Zone: Ta'Vaalor Tunnels
-- The cramped service tunnels and shallow catacombs beneath the city.
-- Level range: 1-3  |  Primary creature: fanged rodent
local Zone = {}

Zone.id        = 42
Zone.name      = "Ta'Vaalor Tunnels"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 3
Zone.climate   = "underground"
Zone.indoor    = true

function Zone.onLoad()
    print("[Zone] Ta'Vaalor Tunnels loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "Something small skitters in the darkness ahead.",
    "The faint sound of claws on stone echoes down the passage.",
    "A musty smell of damp earth and animal fills the narrow tunnel.",
    "Loose gravel shifts somewhere behind you in the dark.",
    "The low ceiling forces you into an uncomfortable crouch.",
    "Water drips steadily from an unseen crack above.",
}
Zone.ambient_interval = 90

return Zone
