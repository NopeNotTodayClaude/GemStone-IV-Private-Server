---------------------------------------------------
-- The Krag Slopes
-- zone_id: 103 | Level range: 8-14
---------------------------------------------------
local Zone={}
Zone.id=103; Zone.name="The Krag Slopes"; Zone.region="Elanith"
Zone.level_min=8; Zone.level_max=14
Zone.climate="temperate"; Zone.indoor=false
function Zone.onLoad() print("[Zone] The Krag Slopes loaded.") end
function Zone.onTick(e) end
function Zone.onPlayerEnter(p) end
function Zone.onPlayerLeave(p) end
Zone.ambient_messages = {
    "The slopes are steep enough that every step tests footing; the rocks here are loose and cold.",
    "Wind funnels through the krag formation with a sound that is almost but not quite a voice.",
    "The cave mouths dotting the upper face are dark and too regular to be entirely natural.",
    "Something moves between the boulders at the treeline below, tracking movement on the slope.",
    "The altitude here makes the air thinner; exertion costs slightly more than it should.",
}
Zone.ambient_interval = 110
return Zone
