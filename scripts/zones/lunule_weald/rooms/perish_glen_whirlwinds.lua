-- Room 10584: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10584
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A stiff breeze blows through the area forming small whirlwinds of dead leaves, moss and bits of bark.  The howling of the wind echoes through the dead trees, drowning out all other sound."

Room.exits = {
    east                     = 10582,
    south                    = 10585,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
