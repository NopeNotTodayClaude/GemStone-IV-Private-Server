-- Room 5909: Catacombs, Entrance
local Room = {}

Room.id          = 5909
Room.zone_id     = 2
Room.title       = "Catacombs, Entrance"
Room.description = "A vaulted ceiling allows dim rays of light to seep in through the cracks from the grate above.  Flickering shadows of various shapes and sizes play on the walls.  An odd assortment of paper, kegs and other trinkets litter the ground.  Shattered crates and barrels mar the surface of the floor, and almost hidden behind them lies the rusted top of an opened hatch."

Room.exits = {
    climb_grate          = 3503,
    go_hatch             = 5910,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
