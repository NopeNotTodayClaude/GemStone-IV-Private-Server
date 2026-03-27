---------------------------------------------------
-- Muddy Village
-- zone_id: 202 | Level range: 6-10
---------------------------------------------------
local Zone={}
Zone.id=202; Zone.name="Muddy Village"; Zone.region="Elanith"
Zone.level_min=6; Zone.level_max=10
Zone.climate="temperate"; Zone.indoor=false
function Zone.onLoad() print("[Zone] Muddy Village loaded.") end
function Zone.onTick(e) end
function Zone.onPlayerEnter(p) end
function Zone.onPlayerLeave(p) end
Zone.ambient_messages = {
    "The village sits in a permanent state of damp, its buildings listing into the soft earth.",
    "Mud-spattered hobgoblins move between the huts with the purposeful indifference of residents.",
    "The smell of something cooking — and something else not cooking — drifts from the central fire.",
    "A crow picks at something in the mud, decides against it, and moves on.",
    "The village is louder than it looks; argument echoes through the walls of every hut.",
}
Zone.ambient_interval = 110
return Zone
