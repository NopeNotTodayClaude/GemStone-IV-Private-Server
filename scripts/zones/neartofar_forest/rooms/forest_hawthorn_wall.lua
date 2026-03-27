-- Room 10628: Neartofar Forest
local Room = {}

Room.id          = 10628
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "The trail climbs out of the depression, and up a steep rise, only to come to an abrupt end at a thirty-foot high wall of hawthorn.  Armed with five-inch, razor-sharp spiky thorns, the thicket prevents further travel through the forest.  From within its depth, a variety of scratching and snuffling noises suggest that small animals thrive within the brambles' protective embrace."

Room.exits = {
    northwest                = 10627,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
