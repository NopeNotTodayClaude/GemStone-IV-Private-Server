-- Room 10597: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10597
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The outside walls of this one-room home are covered with symbols, letters and gibberish.  The whole front door has been painted black with a silver crescent moon in the center and appears to have been nailed shut.  A single window, its glass panes broken and scattered on the ground, provides access to the interior."

Room.exits = {
    northeast                = 10595,
    southwest                = 10598,
    northwest                = 10600,
    north                    = 10605,
    go_window                = 10607,
    southeast                = 10611,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
