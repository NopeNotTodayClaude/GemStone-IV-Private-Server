-- Room 10618: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10618
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "A large dead tree has fallen into a small building, reducing it to a pile of wooden rubbish.  Skittering and scratching can be heard coming from underneath the wooden pile, obviously the home of small animals or other creatures.  Groundwort and death cap grow in abundance atop the rotting pile of leaves and wood."

Room.exits = {
    southeast                = 10599,
    south                    = 10601,
    northeast                = 10617,
    north                    = 10619,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
