-- Room 10331: Adventurers' Guild, Foyer
local Room = {}

Room.id          = 10331
Room.zone_id     = 2
Room.title       = "Adventurers' Guild, Foyer"
Room.description = "Heavy oak posts define this large, octagonal room.  Dominating the center of the space is a massive fireplace, its dressed basalt blocks rising into the dimness of the vaults overhead.  An odd assortment of people is seated on benches scattered around the room, some sitting singly, others in small groups huddled in private conversation.  A staircase winds behind the chimney, leading to the upper story."

Room.exits = {
    north                = 10333,
    east                 = 10332,
}

Room.indoor = true
Room.safe   = true

return Room
