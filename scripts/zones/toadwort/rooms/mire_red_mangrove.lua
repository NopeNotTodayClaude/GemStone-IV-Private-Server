-- Room 10506: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10506
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "A cyclopean red mangrove stands in the center of several clusters of various shrubs and trees, under the starry sky.  A gentle breeze softly stirs the dark, waxy leaves.  Its twisted and gnarled roots are a ghostly pale hue and they eerily creep along the ground as if in search of something to devour."

Room.exits = {
    northwest                = 10505,
    northeast                = 10507,
    southeast                = 10508,
    southwest                = 10510,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
