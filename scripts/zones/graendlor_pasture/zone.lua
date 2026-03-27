---------------------------------------------------
-- Graendlor Pasture
-- Open farmland and pastures west of Wehnimer's Landing
-- Includes the Kobold Village area
-- Level range: 1-5
-- zone_id: 18
---------------------------------------------------

local Zone = {}

Zone.id        = 18
Zone.name      = "Graendlor Pasture"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 5
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Graendlor Pasture loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The grass of the pasture bends in a long, slow wave as the wind rolls through.",
    "A smell of hay, mud, and animals drifts from the direction of the village.",
    "The creaking of a cart wheel and the lowing of a bovine carry from somewhere nearby.",
    "A pair of crows pick at something in the middle distance, then scatter.",
    "The low stone walls dividing the pasture fields have been here long enough to acquire their own moss.",
    "Something scuttles between the fence posts and vanishes into the tall grass.",
}

Zone.ambient_interval = 110

return Zone
