-- Room 3498: Ta'Vaalor, Shimeraern Var
local Room = {}

Room.id          = 3498
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimeraern Var"
Room.description = "The cobbled var provides a distant view of the city's airships dock several blocks to the west, the sound of the vessels only occasionally drifting in on a puff of wind.  Raucous laughter pours from the open windows of a tavern on the corner, filling the var with the sounds of merriment."

Room.exits = {
    north                = 3497,
    south                = 3501,
    west                 = 3500,
    go_tavern            = 10424,
    go_burghal           = 26016,
}

Room.indoor = false
Room.safe   = true

return Room
