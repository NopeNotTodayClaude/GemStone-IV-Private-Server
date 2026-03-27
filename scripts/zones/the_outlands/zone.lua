---------------------------------------------------
-- The Outlands
-- Open plains and farmland of Vornavis Holdings
-- Home of Bresnahanini roltons and plains wildlife
-- Level range: 1-6
-- zone_id: 94
---------------------------------------------------
local Zone = {}
Zone.id        = 94
Zone.name      = "The Outlands"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 6
Zone.climate   = "temperate"
Zone.indoor    = false
function Zone.onLoad() print("[Zone] The Outlands loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end
Zone.ambient_messages = {
    "The wind rolls unobstructed across the open plain, flattening the grass ahead.",
    "A distant farmstead chimney sends up a thin column of smoke.",
    "The road here is old and cracked, the stones scattered by years of frost and thaw.",
    "A hawk turns lazily overhead, riding a thermal with indifferent ease.",
    "The smell of turned earth and cut grass drifts across from the nearest field.",
    "Somewhere in the scrub, something bleats once and goes quiet.",
}
Zone.ambient_interval = 110
return Zone
