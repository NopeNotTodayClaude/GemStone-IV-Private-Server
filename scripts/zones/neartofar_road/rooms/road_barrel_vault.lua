-- Room 31447: Neartofar Road
local Room = {}

Room.id          = 31447
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Stately oaks and beeches with full crowns line the sides of the cobbled road, their branches meeting over it in a perfect barrel vault.  Tendrils of thick, verdant ivy weave their way around and drape from the branches, creating dense walls of greenery.  A few scrawny blackberry bushes cluster about one of the trees."

Room.exits = {
    north                    = 31446,
    south                    = 31448,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
