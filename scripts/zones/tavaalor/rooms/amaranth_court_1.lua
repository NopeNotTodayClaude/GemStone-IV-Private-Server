-- Room 3485: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3485
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "A large inn marks the bustling corner of the court, its massive walls enlivened by deeply carved intertwining vines that creep up the stonework and meet in a mass of heavy stone foliage above each window embrasure and door lintel.  An engraved silver sign swings from a post beside the inn's ironwood front doors."

Room.exits = {
    southwest            = 3484,
    east                 = 3486,
    go_inn               = 5826,
}

Room.indoor = false
Room.safe   = true

return Room
