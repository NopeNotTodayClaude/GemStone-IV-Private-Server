-- Room 10498: Neartofar Road
local Room = {}

Room.id          = 10498
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "The top of a massive limestone coliseum peeks above a dense forest of trees that marches off to the south.  Large oaks and elms form a stately archway over a verdant path that is blocked by a sturdy barricade."

Room.exits = {
    northwest                = 10497,
    go_verdant_path          = 17885,
    southeast                = 31443,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
