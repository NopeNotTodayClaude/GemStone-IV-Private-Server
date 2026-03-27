-- Room 10654: Neartofar Forest
local Room = {}

Room.id          = 10654
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Some predatory ivy is attacking the oak trees, sending thick ropes up the trunks and around the branches.  The ivy's white-veined green leaves soak up the sun, cutting the trees off from their source of energy, and life.  Travel through the area is slowed by the constant need to push the dangling vines out of the way."

Room.exits = {
    northwest                = 10653,
    southeast                = 10655,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
