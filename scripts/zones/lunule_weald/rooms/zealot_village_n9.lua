-- Room 10620: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10620
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "A rock wall, about the height of a human man, though only a few paces in length, stands inexplicably alone, neither bordering nor enclosing anything.  A large circle of wooden sticks poke out from in between the spaces of the rocks.  Inside the circle, painted upon the face of the rock wall, is the image of a silver-haired woman driving a chariot pulled by two grey stallions."

Room.exits = {
    north                    = 10603,
    southeast                = 10621,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
