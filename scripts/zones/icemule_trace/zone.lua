-- Zone: Icemule Trace
local Zone = {}

Zone.id        = 0  -- set by DB zone_id
Zone.name      = "Icemule Trace"
Zone.region    = "Elanthia"
Zone.level_min = 1
Zone.level_max = 38
Zone.climate   = "arctic"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Icemule Trace loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The wind carries snow horizontally, reducing visibility to a dozen feet.",
    "The cold here has a specific quality — it gets into the joints.",
    "Ice groans somewhere deep in the glacier.",
    "A wolf howls from the white distance, then another answers.",
    "Snowflakes catch the light in shifting, crystalline patterns.",
    "Frost breath plumes in the air and is immediately carried away.",
    "The deep silence of a snowfield settles over everything.",
}

Zone.ambient_interval = 120

return Zone
