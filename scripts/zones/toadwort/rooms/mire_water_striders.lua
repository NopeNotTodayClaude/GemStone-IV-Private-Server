-- Room 10513: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10513
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Scores of long-legged water striders send minute ripples over the muddy water as they quickly traverse its surface and disappear around a stand of trees.  Mutant trees and shrubs dot the black mucky soil.  The ghostly grey branches on one particular tree are folded in upon themselves.  For all the world, the thin branches appear to be trying to cover the hollowed out bough, which creates an unsettling impression that the tree is silently screaming."

Room.exits = {
    southwest                = 10512,
    south                    = 10514,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
