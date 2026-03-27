-- Room 105: Town Square, Northeast
local Room = {}

Room.id          = 105
Room.zone_id     = 1
Room.title       = "Town Square, Northeast"
Room.description = "The northeastern corner of the square is dominated by a tall stone monument engraved with the names of fallen heroes.  Fresh flowers have been laid at its base.  A cobblestone path leads northeast toward the temple district."

Room.exits = {
    southwest = 100,
    south     = 103,
    west      = 101,
    northeast = 114,
}

Room.indoor = false
Room.safe   = true

return Room
