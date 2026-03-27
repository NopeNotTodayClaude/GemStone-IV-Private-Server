-- Room 31471: Shadowed Forest, Trail
local Room = {}

Room.id          = 31471
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Thin rays of cascading light filled with swirling motes filter down to the ground, dancing between bits of dead leaves and a patchwork of ground cover.  Thick creepers dangle from the branches of a few trees, their blossoms contrasting with the dark shadows that frame the roadway.  A rustling in the foliage is evidence of the tiny creatures scurrying about."

Room.exits = {
    west                     = 31470,
    east                     = 31472,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
