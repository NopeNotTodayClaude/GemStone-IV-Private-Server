-- Room 10527: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10527
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Boldened by the protection offered under the moonless sky, the mewling of black caimans grows louder from the distance.  Decumbent vines cover the ground like a plush carpet, with their trifoliate leaves and oddly shaped white and green flowers that bear a strong likeness to a hooded figure.  Clusters of star-shaped, pink and purple flowers rise up from the water that is hidden by the vines."

Room.exits = {
    southeast                = 10526,
    northwest                = 10528,
    northeast                = 10530,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
