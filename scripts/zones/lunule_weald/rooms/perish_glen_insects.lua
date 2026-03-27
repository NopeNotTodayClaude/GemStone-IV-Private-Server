-- Room 10592: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10592
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "Spiders, beetles and centipedes creep and crawl over the rotting deadfall of the forest floor.  The rancid smell of decay pervades the area, the constant wind providing no relief from the stench."

Room.exits = {
    west                     = 10586,
    northeast                = 10591,
    southeast                = 10593,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
