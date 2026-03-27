---------------------------------------------------
-- Zone Template
-- Copy this folder to create a new zone
-- Rename and fill in zone-specific data
---------------------------------------------------

local Zone = {}

Zone.id        = 0              -- Unique zone ID (matches DB)
Zone.name      = "Template Zone"
Zone.region    = "Unknown"
Zone.level_min = 1
Zone.level_max = 5
Zone.climate   = "temperate"    -- temperate, arctic, desert, tropical, underground
Zone.indoor    = false

-- Called when zone is loaded by the server
function Zone.onLoad()
    print("[Zone] " .. Zone.name .. " loaded.")
end

-- Called every server tick while zone has players
function Zone.onTick(elapsed)
end

-- Called when a player enters this zone
function Zone.onPlayerEnter(player)
end

-- Called when a player leaves this zone
function Zone.onPlayerLeave(player)
end

-- Weather/ambient messaging
Zone.ambient_messages = {
    "A gentle breeze rustles through the area.",
    "You hear the distant sound of birds.",
}

Zone.ambient_interval = 120  -- seconds between ambient messages

return Zone
