-- Room 31462: Shadowed Forest, Trail
local Room = {}

Room.id          = 31462
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Leaves still attached to twigs and branches dot the path, creating shadowed obstacles for the unwary.  Clusters of mayapples peek out of tangles of brush that grow thick on the side of the road.  Patches of smooth cobblestones are visible beneath the dirt and dust that has accumulated."

Room.exits = {
    north                    = 31461,
    south                    = 31463,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
