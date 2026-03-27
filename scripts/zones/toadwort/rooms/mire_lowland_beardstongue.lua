-- Room 10507: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10507
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Stretching off into the distance are hundreds upon hundreds of lowland beardstongue.  They are interspersed with yellow wood sorrel, green dragons and, naturally, poison ivy.  A soft sighing sound emanates from thin branches of slowly swaying willow trees.  The boles and leaves of the trees appear bleached under the pale light of the moons."

Room.exits = {
    go_arch                  = 3742,
    northwest                = 10504,
    southwest                = 10506,
    go_log                   = 10531,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
