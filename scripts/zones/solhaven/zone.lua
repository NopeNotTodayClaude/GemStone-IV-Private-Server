-- Zone: Solhaven
local Zone = {}

Zone.id        = 0  -- set by DB zone_id
Zone.name      = "Solhaven"
Zone.region    = "Elanthia"
Zone.level_min = 1
Zone.level_max = 33
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Solhaven loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "Salt air carries in from the bay, sharp and clean.",
    "The cry of seabirds echoes off the coastal cliffs.",
    "Surf crashes somewhere below, a continuous background roar.",
    "A fishing boat bobs on the distant water.",
    "The smell of kelp and low tide is thick in the air.",
    "Wind scours the clifftops, bending the coastal scrub flat.",
    "The lighthouse sweeps a slow beam across the darkening water.",
}

Zone.ambient_interval = 120

return Zone
