-- Room 10607: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10607
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Broken furniture, pottery and cutlery litter the floor, joining the rotting leaves that have blown in through the broken window.  Every wall is splattered with a brownish substance and the smell of death is overpowering.  Scattered amongst the leaves and household debris are several bleached white bones.  Small worms crawl in and out of the eye holes of a skull sitting alone in a dark corner of this malodorous room."

Room.exits = {
    go_window                = 10597,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
