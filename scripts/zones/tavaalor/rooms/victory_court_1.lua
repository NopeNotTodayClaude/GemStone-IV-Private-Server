-- Room 3518: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3518
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "Windowless and forbidding, the grey granite walls of the Hall of Justice sit squarely beneath the Keep.  Several city guardsmen patrol the tops of the crennelated walls while half a dozen guards flank the double doors leading into the Hall.  A large mithril plaque hangs from the rightmost ironbound door."

Room.exits = {
    west                 = 3517,
    east                 = 3519,
    go_justice           = 10382,
}

Room.indoor = false
Room.safe   = true

return Room
