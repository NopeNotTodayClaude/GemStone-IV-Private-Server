-- Room 3523: Ta'Vaalor, Annatto Wey
local Room = {}

Room.id          = 3523
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Annatto Wey"
Room.description = "The sparkling glaesine windows of the city's finest jewelry shop catch the eye of many passing through the Annatto Gate.  Although the shop is clad in pristine white limestone, its loveliness is dwarfed by the grandeur of the elaborately carved city gate.  Several city guardsmen carefully inspect travellers passing through the gates."

Room.exits = {
    west                 = 3522,
    north                = 3524,
    go_gate              = 5906,
    go_jeweler           = 10378,
    go_tunnel            = 25626,
}

Room.indoor = false
Room.safe   = true

return Room
