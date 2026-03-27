-- Room 10589: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10589
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A rusted rake and shovel lean against the trunk of a dead tree, their ends partially buried in the soil of the forest floor, their handles split and broken.  Several other metal implements are strewn around the area, abandoned to rust in the thick, malodorous deadfall."

Room.exits = {
    northwest                = 10588,
    southeast                = 10590,
    southwest                = 10593,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
