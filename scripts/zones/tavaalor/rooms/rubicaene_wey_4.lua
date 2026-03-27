-- Room 3507: Ta'Vaalor, Rubicaene Wey
local Room = {}

Room.id          = 3507
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Rubicaene Wey"
Room.description = "A small stone cottage sits beside the wey.  The pale blue grey of the stone walls is offset by the deep red tile roof and brightly painted door.  An engraved mithglin sign hangs from an ironwork post beside the establishment's front door."

Room.exits = {
    north                = 3508,
    south                = 3509,
    northwest            = 3506,
    go_movers            = 10439,
}

Room.indoor = false
Room.safe   = true

return Room
