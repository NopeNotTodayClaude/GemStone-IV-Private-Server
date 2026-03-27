-- Room 3513: Ta'Vaalor, Aethenireas Wey
local Room = {}

Room.id          = 3513
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Aethenireas Wey"
Room.description = "Several small cottages line the street.  Most are painted a clean white with a deep forest green trim.  Simple shutters are currently wide open on the cottages, their green paint vibrant in the light.  A few of the cottages sport copper guttering along their rooflines."

Room.exits = {
    north                = 3514,
    south                = 3512,
    go_healer            = 10396,
}

Room.indoor = false
Room.safe   = true

return Room
