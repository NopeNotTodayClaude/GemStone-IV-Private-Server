---------------------------------------------------
-- Melgorehn's Valley
-- zone_id: 75 | Level range: 7-12
---------------------------------------------------
local Zone={}
Zone.id=75; Zone.name="Melgorehn's Valley"; Zone.region="Elanith"
Zone.level_min=7; Zone.level_max=12
Zone.climate="underground"; Zone.indoor=true
function Zone.onLoad() print("[Zone] Melgorehn's Valley loaded.") end
function Zone.onTick(e) end
function Zone.onPlayerEnter(p) end
function Zone.onPlayerLeave(p) end
Zone.ambient_messages = {
    "The valley opens from a narrow tunnel mouth into a chamber high enough to feel like outside.",
    "The burrow network runs through every wall; distant movement is a constant background sensation.",
    "Torch light reaches only to the nearest wall; the far side of the chamber is suggestion and sound.",
    "The smell here is deep earth and old fires and something with a very specific territorial musk.",
    "A stone shifts somewhere in the wall and everything goes quiet for a moment.",
}
Zone.ambient_interval = 110
return Zone
