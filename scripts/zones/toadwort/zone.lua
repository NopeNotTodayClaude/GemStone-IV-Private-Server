-- Zone 7: The Toadwort
local Zone = {}

Zone.id        = 7
Zone.name      = "The Toadwort"
Zone.region    = "Elanith"
Zone.level_min = 2
Zone.level_max = 10
Zone.climate   = "swamp"
Zone.indoor    = false

function Zone.onLoad() print("[Zone] The Toadwort loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The incessant drone of insects fills the thick, humid air.",
    "The mewling of black caimans carries from somewhere deep in the murk.",
    "A chorus of frogs erupts briefly from the reeds, then falls silent.",
    "The mucky soil sucks at every step, threatening to swallow boots whole.",
    "Fireflies blink lazily over the black surface of a stagnant pool.",
    "A thick mist clings low to the ground, swirling where disturbed.",
    "The rancid smell of decay rises from the sodden earth.",
    "Something large moves in the reeds nearby, sending ripples across dark water.",
    "Water striders skitter silently across a black pool nearby.",
}
Zone.ambient_interval = 120

return Zone
