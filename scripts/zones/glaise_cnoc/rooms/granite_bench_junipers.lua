-- Room 5845: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 5845
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "A granite bench, which also serves as a grave marker, sits nestled between a pair of junipers.  The dual purpose of the bench is both inviting and repelling in design.  A chipmunk sits beneath the bench busily eating an acorn."

Room.exits = {
    southeast                = 5844,
    northwest                = 5846,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
