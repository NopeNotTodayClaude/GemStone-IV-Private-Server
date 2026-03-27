-- Room 10521: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10521
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Moonlight dances on the surface of a pool, as it overflows and creates a torrent of black mud.  Black spots dot the body of a decaying beast that has been nailed to the trunk of a deformed tree.  Many of the spots have split open, allowing the white, writhing bodies of maggots to plunge to the ground where they are quickly immersed by the muddy water.  From the distance, a loud crash and the sound of splashing water is heard."

Room.exits = {
    go_stream                = 10520,
    up                       = 10522,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
