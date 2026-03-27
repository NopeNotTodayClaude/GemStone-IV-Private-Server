-- Room 10550: Lunule Weald, Slade
local Room = {}

Room.id          = 10550
Room.zone_id     = 8
Room.title       = "Lunule Weald, Slade"
Room.description = "Tufts of feathers and broken eggshells spill out of a rotten bird's nest sitting forlornly in the thick grass.  No breeze is evident and not even an insect breaks the monotony of silence in the air."

Room.exits = {
    north                    = 10549,
    east                     = 10551,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
