-- Room 10688: Catacomb, Ossuary
local Room = {}

Room.id          = 10688
Room.zone_id     = 3
Room.title       = "Catacomb, Ossuary"
Room.description = "Bones.  Stacks and stacks of bones.  Each stack appears to contain the bones of entire skeletons of similar size and race.  Other than two flickering wall sconces, all that can be found here is an uncountable number of bones."

Room.exits = {
    west                     = 10687,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
