-- Room 5919: Catacombs, Cavern
local Room = {}

Room.id          = 5919
Room.zone_id     = 2
Room.title       = "Catacombs, Cavern"
Room.description = "Wet black sludge lines the base of the catacombs walls.  The monotonous sound of dripping water fills the otherwise silent cavern.  Empty sconces, which once lit the arched corridor, are evenly spaced along the slimy, mold-ridden walls.  The corridor stretches to the north and south as far as the dim light carries."

Room.exits = {
    south                = 5918,
    north                = 5920,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
