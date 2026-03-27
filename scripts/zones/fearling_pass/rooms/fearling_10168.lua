-- Room 10168: Fearling Pass, Forest Trail
local Room = {}
Room.id          = 10168
Room.zone_id     = 9
Room.title       = "Fearling Pass, Forest Trail"
Room.description = "Uncommonly wide, the pass appears able to accommodate the girth of an army, though some of the ruts in the dirt trail suggest it has seen exactly that.  Faded boot prints and hoof marks have been baked into the earth over seasons of use.  A ridge is visible to the northwest."
Room.exits = {
    south                    = 10167,
    north                    = 10169,
    northwest                = 15931,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
