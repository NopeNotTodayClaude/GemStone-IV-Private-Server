-- Room 10396: Saphrie's Herbs and Tinctures
local Room = {}

Room.id          = 10396
Room.zone_id     = 2
Room.title       = "Saphrie's Herbs and Tinctures"
Room.description = "Soft aquamarine curtains frame the glaesine-paned windows of the herb shop.  Whitewashed haon shelves line the walls, each shelf carefully stocked with a variety of glaes bottles.  A long monir counter, well worn and apparently used as a worktable, rests in the center of the shop."

Room.exits = {
    out                  = 3513,
    east                 = 10397,
}

Room.indoor = true
Room.safe   = true

return Room
