-- Room 10376: Cleric Guild, Courtyard
local Room = {}

Room.id          = 10376
Room.zone_id     = 2
Room.title       = "Cleric Guild, Courtyard"
Room.description = "Rows of neatly-trimmed hedges line the walkway leading toward an ivory-walled building to the east, while a smaller domed structure is visible to the north.  Oak trees stretch their gnarled limbs across the sky, their large boughs filled with a healthy collection of verdant leaves.  Carved wooden benches beneath the trees bear ornate, looping designs across their richly-stained surfaces, and the buzz of daily life filters in faintly from beyond the courtyard."

Room.exits = {
    out                  = 3535,
    north                = 10377,
}

Room.indoor = true
Room.safe   = true

return Room
