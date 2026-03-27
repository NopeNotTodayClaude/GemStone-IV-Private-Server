-- Room 10685: Catacomb, Entrance
local Room = {}

Room.id          = 10685
Room.zone_id     = 3
Room.title       = "Catacomb, Entrance"
Room.description = "Flickering torches on the walls light the entrance of the catacombs.  Several chairs provide seating in what seems to serve as a waiting room.  Arches flank both sides of this room and a hallway extends to the north."

Room.exits = {
    north                    = 10686,
    east                     = 10693,
    west                     = 10692,
    out                      = 5879,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
