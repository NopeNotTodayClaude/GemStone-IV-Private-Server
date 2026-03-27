-- Room 34453: Yasrenila, Honeybee Circle
local Room = {}

Room.id          = 34453
Room.zone_id     = 5
Room.title       = "Yasrenila, Honeybee Circle"
Room.description = "Magnificently ancient, a lone oak tree encroaches upon the glade, its massive roots diving beneath the log fence hidden behind pale-flowered ivybriar.  A series of squat, round-topped homes clad in lacy vines trim the forest's edge.  Nearby, a clothesline stretches between two trunks, bearing hanging garments that wave in the faint breeze.  Flat stones cut a trail between a pair of flower beds before disappearing into the shelter of a natural arbor."

Room.exits = {
    southeast                = 34452,
    go_arbor                 = 34454,
    northwest                = 34455,
    east                     = 34456,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
