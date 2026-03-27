-- Room 31444: Neartofar Road
local Room = {}

Room.id          = 31444
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Tufts of pale dandelions, light pink alyssum, and deep purple cornflowers dot the edges of the road.  One or two bold plants push themselves between the cobbles, reaching toward the sunlight.  Oaks and beeches intertwine to make a natural rooftop arch high above the ground.  Their brethren stretch back from the road, creating a dense forest."

Room.exits = {
    northwest                = 31443,
    southeast                = 31445,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
