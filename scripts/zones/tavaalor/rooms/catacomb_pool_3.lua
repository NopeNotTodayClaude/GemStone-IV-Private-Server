-- Room 5944: Catacombs, Pool
local Room = {}

Room.id          = 5944
Room.zone_id     = 2
Room.title       = "Catacombs, Pool"
Room.description = "Vast stone pillars dot the rocky surface of this chamber.  The walls have been crafted with a raised mural, which depicts a section of buildings from the city street that is directly above this tunnel.  In the center of the ceiling is a dark gaping hole.  A rush of water pours from the hole into a seemingly bottomless pool of water."

Room.exits = {
    west                 = 5942,
    east                 = 5945,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
