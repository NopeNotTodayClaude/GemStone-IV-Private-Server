-- Room 31456: Neartofar Road, Grassy Field
local Room = {}

Room.id          = 31456
Room.zone_id     = 5
Room.title       = "Neartofar Road, Grassy Field"
Room.description = "Leaving the dense forest, the road meanders through a secluded meadow.  A wide creek winds about the green pasture before disappearing into the thick brush that lines the boundaries of the woods.  Patches of colorful wildflowers brighten the lush, grassy plain with their vibrant hues."

Room.exits = {
    west                     = 31455,
    east                     = 31457,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
