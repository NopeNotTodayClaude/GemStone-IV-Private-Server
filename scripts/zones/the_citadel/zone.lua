---------------------------------------------------
-- The Citadel
-- Underground river tunnels and caverns
-- Home of night golems and other underground creatures
-- Level range: 1-8
-- zone_id: 141
---------------------------------------------------
local Zone = {}
Zone.id        = 141
Zone.name      = "The Citadel"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 8
Zone.climate   = "underground"
Zone.indoor    = true
function Zone.onLoad() print("[Zone] The Citadel loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end
Zone.ambient_messages = {
    "The sound of running water echoes from somewhere deeper in the tunnels.",
    "A cold draft moves through the passage, carrying the smell of damp stone.",
    "Something drips steadily in the darkness ahead.",
    "The torchlight barely reaches the far walls of this chamber.",
    "A distant mechanical grinding sound reverberates through the stone.",
    "Faint luminescence clings to the cavern walls — something alchemical, perhaps.",
}
Zone.ambient_interval = 100
return Zone
