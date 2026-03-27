-- Room 5885: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5885
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Crushed granite forms a somber path through the cemetery.  The grey of the path is in stark contrast to the verdant green grass flanking on either side.  A grave on the west side is marked by a short marble pillar.  A leafy vine winds its way around the pillar, before displaying a single white bloom at the pillar's capital."

Room.exits = {
    north                    = 5882,
    south                    = 5886,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
