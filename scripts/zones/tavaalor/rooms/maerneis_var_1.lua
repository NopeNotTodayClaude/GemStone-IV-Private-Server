-- Room 3524: Ta'Vaalor, Maerneis Var
local Room = {}

Room.id          = 3524
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Maerneis Var"
Room.description = "The rich smell of chocolate drifts from the nearby shop.  The stone-clad building, its windows thrown open to the breeze, is carved about the door and window embrasures with flighty impressions of faeries and other fanciful creatures.  A hand-lettered maoral sign hangs on the shop's door."

Room.exits = {
    south                = 3523,
    east                 = 3525,
    go_rations           = 10368,
}

Room.indoor = false
Room.safe   = true

return Room
