-- Room 10499: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10499
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "Along this mud trail rests a deep, narrow creek.  Pale moonlight shows tiny footprints in the mud near the edge of the water.  A huge, frog-shaped, moss-covered boulder lies close to the border of the creek.  As the rushing current spirals downward, it passes over the boulder, causing water to splash onto the road."

Room.exits = {
    climb_bank               = 10497,
    southeast                = 10500,
    down                     = 10502,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
