-- Room 10539: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10539
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Disfigured trees have coiled and twisted themselves together and a thick tangle of dark grey roots protrude from the ground, which is covered with dark roiling mud from the overflowing bourn.  Small hillocks provide just a touch of solid ground and offer some relief from treading through the thick mud.  Littering the ground are small rocks and stones that, combined with fallen branches and mud, make this a hazardous area for walking."

Room.exits = {
    south                    = 10533,
    northeast                = 10536,
    go_trail                 = 10540,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
