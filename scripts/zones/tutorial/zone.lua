---------------------------------------------------
-- Tutorial Zone
-- New player experience with sprite guide (Ridijy)
-- 5 scenarios teaching core game mechanics
---------------------------------------------------

local Zone = {}

Zone.id        = 99
Zone.name      = "Tutorial"
Zone.region    = "Between Worlds"
Zone.level_min = 0
Zone.level_max = 2
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Tutorial zone loaded.")
end

Zone.ambient_messages = {}
Zone.ambient_interval = 0

return Zone
