---------------------------------------------------
-- Room Template
-- Each room is a Lua file returning a room table
---------------------------------------------------

local Room = {}

Room.id          = 0            -- Unique room ID (matches DB)
Room.zone_id     = 0            -- Parent zone ID
Room.title       = "A Template Room"
Room.description = "You find yourself in a nondescript area. There is nothing remarkable here."

-- Exits: direction = room_id (or "go_target" = room_id for non-compass exits)
Room.exits = {
    north = 0,
    south = 0,
    -- east = 0,
    -- west = 0,
    -- northeast = 0,
    -- go_door = 0,        -- triggered by "GO DOOR"
}

-- Hidden exits (require SEARCH to find)
Room.hidden_exits = {
    -- go_trapdoor = { room_id = 0, search_dc = 15, message = "You notice a trapdoor hidden beneath some debris!" }
}

Room.indoor      = false        -- true = "Obvious exits:", false = "Obvious paths:"
Room.dark        = false        -- requires light source to see
Room.safe        = false        -- no combat allowed (town squares, etc.)
Room.supernode   = false        -- mana regeneration bonus
Room.climbable   = false        -- requires CLIMB to traverse

-- Items/objects in the room (decoration, interactable)
Room.objects = {
    -- { noun = "bench", description = "A sturdy wooden bench sits against the wall." }
}

-- Called when a player LOOKs at the room
function Room.onLook(player)
    return Room.description
end

-- Called when a player enters this room
function Room.onEnter(player)
end

-- Called when a player SEARCHes
function Room.onSearch(player)
end

return Room
