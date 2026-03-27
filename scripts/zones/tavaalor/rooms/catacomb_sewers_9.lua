-- Room 5945: Catacombs, Sewers
local Room = {}

Room.id          = 5945
Room.zone_id     = 2
Room.title       = "Catacombs, Sewers"
Room.description = "Heaps of warped and withered wood litter the ground.  Sections of the old tracks used to carry rocks and other minerals to the outside are visible from underneath the rubbish.  A twisted, slender pipe runs the length of the western wall.  Drops of water seep from a small hole in the pipe, which is creating a small pool of mud."

Room.exits = {
    west                 = 5944,
    east                 = 5946,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
