-- Room 10669: Neartofar Forest, Barracks
local Room = {}

Room.id          = 10669
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Barracks"
Room.description = "In a wide brick hearth, a bright and merry fire burns a roast to a crisp, sending thick black smoke up the chimney and filling the room with a sharp, foul odor.  Resting on some shelves nearby, a variety of jars and baskets contain various herbs and spices.  A small table pushed up against the brick interior wall functions as a butcher's block, judging from the deep cuts that have been hacked and slashed into the dark-stained wood."

Room.exits = {
    south                    = 10668,
    west                     = 10670,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
