-- Room 3502: Ta'Vaalor, Shimeraern Var
local Room = {}

Room.id          = 3502
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimeraern Var"
Room.description = "A plain wooden building stands near the edge of the airship docks.  Nondescript in appearance and lacking the usual stone cladding on so many city buildings, it would escape notice but for the large maoral sign attached to the wall near the front door."

Room.exits = {
    east                 = 3500,
    south                = 3503,
    go_locksmith         = 10434,
}

Room.indoor = false
Room.safe   = true

return Room
