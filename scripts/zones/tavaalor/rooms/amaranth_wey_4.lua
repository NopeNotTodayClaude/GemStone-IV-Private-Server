-- Room 3490: Ta'Vaalor, Amaranth Wey
local Room = {}

Room.id          = 3490
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Wey"
Room.description = "The crowded intersection of wey and var teems with people, each hurrying in his or her own direction.  A row of pennants of the Vaalor ruby and gold colors flutter atop the nearby city gate, bringing cheer to the otherwise austere limestone edifice."

Room.exits = {
    west                 = 3489,
    south                = 3491,
    go_gate              = 5827,
    go_battlements       = 25588,
}

Room.indoor = false
Room.safe   = true

return Room
