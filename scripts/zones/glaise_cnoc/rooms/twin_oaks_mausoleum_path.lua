-- Room 5843: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5843
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Sunlight filters through the canopy of leaves created by towering twin oaks flanking the sides of a small mausoleum.  The giant oaks make the mausoleum appear smaller than it is.  A cobblestoned walk leads from the path to ornately carved ebon doors that mark the entrance to the mausoleum."

Room.exits = {
    south                    = 5842,
    north                    = 5844,
    go_doors                 = 10674,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
