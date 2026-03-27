-- Room 10441: Guardian Keep, Outer Gate
local Room = {}

Room.id          = 10441
Room.zone_id     = 2
Room.title       = "Guardian Keep, Outer Gate"
Room.description = "Two unlit torches are mounted on either side of the bailey gate leading back out to the city.  A trio of well-traveled paths has been trampled through the grass leading off to the north, west, and east.  Various shoppers can be seen entering the area and heading off down the paths towards shops located throughout the grassy sward."

Room.exits = {
    out                  = 3520,
    north                = 10442,
    east                 = 10450,
    west                 = 10454,
}

Room.indoor = true
Room.safe   = true

return Room
