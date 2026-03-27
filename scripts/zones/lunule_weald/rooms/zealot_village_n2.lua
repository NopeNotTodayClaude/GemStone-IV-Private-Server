-- Room 10613: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10613
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "The constant wind howls through dead trees and the remains of broken-down shacks.  Scratching and chittering can be heard coming from beneath a pile of abandoned logs.  A small handaxe is imbedded in one of the logs as if the woodcutter had been suddenly called away from his work."

Room.exits = {
    northwest                = 10598,
    northeast                = 10611,
    southeast                = 10614,
    south                    = 10615,
    southwest                = 10616,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
