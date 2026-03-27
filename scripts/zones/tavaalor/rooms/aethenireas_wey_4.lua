-- Room 3512: Ta'Vaalor, Aethenireas Wey
local Room = {}

Room.id          = 3512
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Aethenireas Wey"
Room.description = "The chiming sounds of cymbals interspersed with the lilting sounds of a merrily fluted tune wafts from a nearby cottage.  Bright blue shutters frame the windows, and the cottage's blue door stands partially open.  An engraved silver sign hangs on the doorpost."

Room.exits = {
    north                = 3513,
    south                = 3511,
    go_music             = 10395,
    go_cobbler           = 33264,
}

Room.indoor = false
Room.safe   = true

return Room
