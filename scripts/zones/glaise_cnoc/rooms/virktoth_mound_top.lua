-- Room 10746: Plains of Bone, Mound Top
local Room = {}

Room.id          = 10746
Room.zone_id     = 3
Room.title       = "Plains of Bone, Mound Top"
Room.description = "At the top of the stairs the hill flattens, small dark blades of grass cover the hilltop.  A thick mist seems to cling to everything in the area.  A gentle slope to the northeast leads to a ruined structure awash in moonlight."

Room.exits = {
    northeast                = 10747,
    northwest                = 10745,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
