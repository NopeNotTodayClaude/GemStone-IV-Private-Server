-- Zone: Zul Logoth
local Zone = {}

Zone.id        = 0  -- set by DB zone_id
Zone.name      = "Zul Logoth"
Zone.region    = "Elanthia"
Zone.level_min = 24
Zone.level_max = 36
Zone.climate   = "underground"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Zul Logoth loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "Distant pickaxes ring against stone, the sound echoing strangely.",
    "The lanterns of Zul Logoth cast amber pools across the tunnel walls.",
    "Water drips from unseen heights in a slow, irregular rhythm.",
    "The smell of deep earth and stone dust is pervasive.",
    "Somewhere ahead, the creak of a mining cart on its rails.",
    "Bioluminescent fungi cast a faint blue glow on the tunnel ceiling.",
    "A deep vibration moves through the stone beneath your feet.",
}

Zone.ambient_interval = 120

return Zone
