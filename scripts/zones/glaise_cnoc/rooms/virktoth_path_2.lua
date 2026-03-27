-- Room 10731: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10731
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "Ahead, the stairway begins to curve ever so slightly to the south.  Here, the steps begin to narrow to accommodate the turn to the west.  Torches formed from long leg bones are placed in the ground on the outside edge of the stairway.  Small sparks occasionally float down into the darkness from the burning torches."

Room.exits = {
    east                     = 10730,
    west                     = 10732,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
