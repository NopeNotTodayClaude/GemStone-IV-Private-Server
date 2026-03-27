-- Room 10168: Fearling Pass, Forest Trail
local Room = {}
Room.id          = 10168
Room.zone_id     = 9
Room.title       = "Fearling Pass, Forest Trail"
Room.description = "Uncommonly wide, the pass appears able to accommodate the girth of an army, though some of the ruts in the dirt trail suggest it has seen exactly that.  Faded boot prints and hoof marks have been baked into the earth over seasons of use.  A ridge is visible to the northwest."
Room.exits = {
    northwest                = 10167,
    south                    = 10169,
    go_path                  = 13917,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
