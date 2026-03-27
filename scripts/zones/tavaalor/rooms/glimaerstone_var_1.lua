-- Room 3491: Ta'Vaalor, Glimaerstone Var
local Room = {}

Room.id          = 3491
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Glimaerstone Var"
Room.description = "The towering edifice of a guild hall looms above the cobbled var, casting the entire area into deep shadow.  Void of the usual carvings and stonework decorative elements, the few windows of the structure are barred with plain iron.  An ironwood door appears to be the only means of entrance to the hall."

Room.exits = {
    north                = 3490,
    east                 = 3531,
    go_guild             = 10331,
}

Room.indoor = false
Room.safe   = true

return Room
