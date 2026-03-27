-- Room 10530: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10530
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Oval-shaped objects are visible in the black muck that fills a narrow bayou.  Branches from a dwarfed willow tree hang low to the ground.  Their lance-shaped leaves sweeps gently over the land around it, as a chilly wind ruffles them."

Room.exits = {
    northeast                = 10523,
    southeast                = 10525,
    southwest                = 10527,
    northwest                = 10529,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
