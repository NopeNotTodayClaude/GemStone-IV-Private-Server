-- Room 5832: Timmorain Road
local Room = {}

Room.id          = 5832
Room.zone_id     = 4
Room.title       = "Timmorain Road"
Room.description = "The road runs steadily northeast and southwest, and though the trees press in rather close, no cobblestones are buckled by encroaching tree roots.  The road's surface is smooth, and the cobblestones huddle closely together to allow fast, unhindered travel.  Strangely, the cobblestones are cleaner than one might expect for a road through the forest, as if someone has recently come out and given them a brisk sweeping."

Room.exits = {
    southwest                = 5831,
    northeast                = 5833,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
