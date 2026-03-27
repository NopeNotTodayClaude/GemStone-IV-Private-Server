-- Room 10748: Plains of Bone, Ruins
local Room = {}

Room.id          = 10748
Room.zone_id     = 3
Room.title       = "Plains of Bone, Ruins"
Room.description = "The black stone rubble nearly fills what's left of the tower.  Only a small area near the doorway remains rubble free.  A small break in the rubble overhead allows moonlight to stream in.  Stars can be seen twinkling above through gaps in the rubble.  One of the double doors that forms the entrance to the tower is missing."

Room.exits = {
    out                      = 10747,
}

Room.indoor      = true
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
