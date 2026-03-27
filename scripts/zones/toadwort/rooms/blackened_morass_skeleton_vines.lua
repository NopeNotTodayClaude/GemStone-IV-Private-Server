-- Room 10534: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10534
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "A disheveled skeleton lies in a tangle of roots and vines, and patches of bluish-green mold and mildew are visible on the shredded remains of its clothing.  A gut-wrenching stench seems to be coming from small crevices in the ground that are filled with a greenish, bubbling goop.  Under the light of the moon the goop appears to shimmer.  The air thickens with moisture as dense fog blankets the ground and rises steadily."

Room.exits = {
    west                     = 10533,
    north                    = 10535,
    east                     = 10538,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
