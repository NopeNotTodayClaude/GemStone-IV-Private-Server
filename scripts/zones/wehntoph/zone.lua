---------------------------------------------------
-- Wehntoph
-- Rocky canyons northeast of Wehnimer's Landing
-- Home of slimy little grubs and nasty little gremlins
-- Level range: 1-8
-- zone_id: 102
---------------------------------------------------
local Zone = {}
Zone.id        = 102
Zone.name      = "Wehntoph"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 8
Zone.climate   = "temperate"
Zone.indoor    = false
function Zone.onLoad() print("[Zone] Wehntoph loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end
Zone.ambient_messages = {
    "A sharp wind cuts through the canyon, carrying grit and the smell of stone.",
    "The walls of the canyon press close here, leaving a narrow strip of sky above.",
    "Loose shale skitters down the canyon face with a dry clatter.",
    "Something small and fast darts between the rocks and vanishes.",
    "An echo of distant movement rolls through the canyon — hard to say from which direction.",
    "The light is strange in the canyon, pooling in the shadows at odd angles.",
}
Zone.ambient_interval = 110
return Zone
