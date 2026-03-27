-- Room 31468: Shadowed Forest, Trail
local Room = {}

Room.id          = 31468
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Murky and ancient, the forest seems to go on far into the distant, veiled shadows.  Closely spaced branches wave ever slightly in the slow-moving air, the disharmony of their sounds echoing as they rub together in the dense foliage.  The wild noises of foraging creatures resonate through the area, adding more chaos to the music of the wilds."

Room.exits = {
    northwest                = 31467,
    southeast                = 31469,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
