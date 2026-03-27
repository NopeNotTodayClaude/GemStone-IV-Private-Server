-- Zone: Rivers Rest
local Zone = {}

Zone.id        = 0  -- set by DB zone_id
Zone.name      = "Rivers Rest"
Zone.region    = "Elanthia"
Zone.level_min = 33
Zone.level_max = 54
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Rivers Rest loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The marsh smells of peat and dark water, carried on a perpetual damp wind.",
    "Something large moves through the reeds nearby, then is still.",
    "A grey heron lifts from the water ahead and beats slowly away.",
    "The call of something nocturnal carries from the deeper marsh.",
    "Fog pools in the low places here, shifting where disturbed.",
    "The wooden planks of the path creak and shift underfoot.",
    "A distant bell rings from the direction of the town.",
}

Zone.ambient_interval = 120

return Zone
