-- Room 10708: Plains of Bone, Outer Circle
local Room = {}

Room.id          = 10708
Room.zone_id     = 3
Room.title       = "Plains of Bone, Outer Circle"
Room.description = "Orc skulls dangle from chains hanging from rusted bars protruding from the outer wall.  One of the bars has come loose and now tilts downward.  Dried wax from now dormant candles drips from the skulls like the drool that did when the creature was alive, while fresh wax drips from now burning candles."

Room.exits = {
    south                    = 10709,
    northwest                = 10707,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
