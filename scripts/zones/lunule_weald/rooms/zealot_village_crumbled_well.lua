-- Room 10599: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10599
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Several dead branches and rotting leaves partially cover what was once the town well.  The brick walls of the well are crumbling and many of the bricks lay on the ground, most of the wooden roof has fallen inward.  Strands of rope are coiled around a broken reel.  The handle portion of the reel has long since decayed away."

Room.exits = {
    southeast                = 10598,
    northeast                = 10600,
    southwest                = 10601,
    south                    = 10602,
    north                    = 10617,
    northwest                = 10618,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
