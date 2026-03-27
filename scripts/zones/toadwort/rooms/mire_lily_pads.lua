-- Room 10505: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10505
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "A large pool of stagnant water dominates this area.  Pale green duckweed covers its surface along with a few dozen lily pads.  The lily pads are artfully arranged, almost as if someone had taken the time to place them on the surface of the water.  Wilting swamp buttercups poke their waxy yellow flowers through the water.  From time to time, an air bubble breaks the surface.  Apparently, the pool is home for some unknown creatures."

Room.exits = {
    northeast                = 10504,
    southeast                = 10506,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
