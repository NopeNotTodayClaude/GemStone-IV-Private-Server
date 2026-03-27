-- Room 10720: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10720
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "A lone sapling resides here, centered in a small field.  In the Bone Plains, it is the only green vegetation.  The young tree seems to radiate life from itself amid the desolation that encompasses it.  Dead grass crunches underfoot, dried enough to ignite with little effort.  Chill winds blow bits of dead grass around in small swirls."

Room.exits = {
    northwest                = 10719,
    southeast                = 10721,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
