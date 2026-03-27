-- Zone: Rambling Meadows
local Zone = {}

Zone.id        = 99
Zone.name      = "Rambling Meadows"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 22
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Rambling Meadows loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The meadow stretches broad and sun-drenched in every direction.",
    "Honeybees work the clover heads along the path's edge.",
    "A distant farmhouse chimney puts up a thin thread of smoke.",
    "The orchard rows cast long afternoon shadows across the grass.",
    "Birdsong fills the warm air from a dozen directions at once.",
    "The grass is thick and lush from recent rains.",
    "A fat bumblebee drones past on some errand of its own.",
    "The hilltop ahead shows the outline of something larger moving in the scrub.",
    "Apple blossoms catch in the breeze and drift like pink snow.",
    "The smell of turned earth and growing things is thick here.",
}

Zone.ambient_interval = 120

return Zone
