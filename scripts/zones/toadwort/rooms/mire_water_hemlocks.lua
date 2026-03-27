-- Room 10517: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10517
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Lush water hemlocks mingle with wood nettles, completely covering the sodden ground underfoot.  White clusters of tiny flowers occupy the tops of the tall stalks on the water hemlocks.  Tasting or even touching these plants could release a toxic poison.  The natural defense of the wood nettles lies in their thick barbs that cover their stems.  If one barb pricks flesh, it releases a deadly acid into its victim's bloodstream."

Room.exits = {
    north                    = 10511,
    east                     = 10516,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
