-- Room 10503: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10503
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "Tiny footprints are clearly visible along the mud track.  Judging from the distinct dragging marks that are located behind each set of the footprints it appears that whoever created them also wears a long cloak or perhaps a robe.  The perfectly shaped footprints lead directly toward the creek, where they suddenly disappear.  The melodic sound of a woman singing in a high soprano voice is heard, under the dusky sky."

Room.exits = {
    up                       = 10502,
    south                    = 10504,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
