-- Room 10667: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10667
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "A sturdy platform runs the length of the wall, providing a view over the parapet of the southern approach to the stockade.  Commanding a view of the clearing and the surrounding forest as well, this vantage does not allow for reliable scouting, as the vast field of trees collapses the distinction between near and far.  Impossibly distant or just at the foot of the hill, a break in the tree line indicates the position of a river to the south, while beyond a rocky ridge rises up to block the horizon."

Room.exits = {
    down                     = 10660,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
