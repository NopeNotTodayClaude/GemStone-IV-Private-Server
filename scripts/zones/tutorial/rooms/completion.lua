-- Room 59099: Tutorial Complete - Silverwood Manor / Departure
local Room = {}

Room.id          = 59099
Room.zone_id     = 99
Room.title       = "Silverwood Manor, Entry Hall"
Room.description = "You stand in the warm, wood-paneled entry hall of Silverwood Manor.  A fire crackles in a wide stone hearth, and comfortable chairs are arranged around it.  This place serves as a refuge for new adventurers before they venture into the wider world.  A shimmering portal swirls with light at the far end of the hall — it will take you to your home city."

Room.exits = {
    go_portal = 0,
}

Room.indoor = true
Room.safe   = true

return Room
