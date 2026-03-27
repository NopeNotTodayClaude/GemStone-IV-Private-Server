-- Room 10689: Catacomb, Ossuary
local Room = {}

Room.id          = 10689
Room.zone_id     = 3
Room.title       = "Catacomb, Ossuary"
Room.description = "Bones.  Stacks and stacks of bones.  Each stack appears to contain a different type of bone, ribs, vertebrae, arm bones, leg bones, skulls and various less identifiable ones.  Other than two flickering wall sconces, all that can be found here is an uncountable number of bones."

Room.exits = {
    east                     = 10687,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
