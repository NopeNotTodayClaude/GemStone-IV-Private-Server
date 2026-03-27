---------------------------------------------------
-- The Cairnfang
-- Dense upland forest south of Wehnimer's Landing
-- Home of hobgoblins and other forest creatures
-- Level range: 1-10
-- zone_id: 37
---------------------------------------------------
local Zone = {}
Zone.id        = 37
Zone.name      = "The Cairnfang"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 10
Zone.climate   = "temperate"
Zone.indoor    = false
function Zone.onLoad() print("[Zone] The Cairnfang loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end
Zone.ambient_messages = {
    "The dense canopy muffles sound — the forest feels close and watchful.",
    "A crow calls once from the high branches, then goes silent.",
    "Dead leaves shift underfoot without wind, as if something passed recently.",
    "The light filters through the trees in thin shafts that illuminate nothing useful.",
    "The smell of pine and rot mingles in the cold air.",
    "Somewhere ahead, something large moves through the undergrowth and stops.",
}
Zone.ambient_interval = 120
return Zone
