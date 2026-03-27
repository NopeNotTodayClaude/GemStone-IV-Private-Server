-- Room 10122: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10122
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "Meadowlike fields awash with wildflowers stretch in all directions, a symphony of crickets and locusts filling the air with sound.  The rocky trail narrows here as it climbs between two low ridges, the ground underfoot unstable with loose shale."
Room.exits = {
    south                    = 10121,
    north                    = 10123,
    northeast                = 10158,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
