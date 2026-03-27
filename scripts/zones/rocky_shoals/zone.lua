---------------------------------------------------
-- Rocky Shoals
-- Black stone beach and coastal shoals near Solhaven
-- Level range: 1-5
-- zone_id: 205
-- NOTE: Coconut crab (L2) is the canonical creature but has no wiki stats.
---------------------------------------------------
local Zone = {}
Zone.id        = 205
Zone.name      = "Rocky Shoals"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 5
Zone.climate   = "coastal"
Zone.indoor    = false
function Zone.onLoad() print("[Zone] Rocky Shoals loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end
Zone.ambient_messages = {
    "Waves crash against the black rocks, throwing spray high into the salt air.",
    "The stones here are slick with algae and require careful footing.",
    "Gulls wheel overhead, calling in sharp complaint at your presence.",
    "A crab scuttles sideways across a flat rock and disappears into a crevice.",
    "The smell of brine and rotting kelp hangs thick over the shoals.",
    "The tide is changing — water rushes in channels between the stone formations.",
}
Zone.ambient_interval = 100
return Zone
