---------------------------------------------------
-- Cliffwalk
-- zone_id: 204 | Level range: 7-12
---------------------------------------------------
local Zone={}
Zone.id=204; Zone.name="Cliffwalk"; Zone.region="Elanith"
Zone.level_min=7; Zone.level_max=12
Zone.climate="coastal"; Zone.indoor=false
function Zone.onLoad() print("[Zone] Cliffwalk loaded.") end
function Zone.onTick(e) end
function Zone.onPlayerEnter(p) end
function Zone.onPlayerLeave(p) end
Zone.ambient_messages = {
    "The path here is barely a path — more a suggestion of footing along the cliff face.",
    "The wind off the sea hits the cliff at an angle that makes staying upright an active task.",
    "Loose stones tumble from somewhere above, clattering down to the base a long way below.",
    "Something moves along the upper ledge, silhouetted briefly before dropping out of sight.",
    "The coastal noise is constant here: water, wind, and the calls of birds nesting in the rock.",
}
Zone.ambient_interval = 110
return Zone
