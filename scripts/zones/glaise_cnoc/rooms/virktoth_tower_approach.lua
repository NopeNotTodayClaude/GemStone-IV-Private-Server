-- Room 10747: Plains of Bone, Mound Top
local Room = {}

Room.id          = 10747
Room.zone_id     = 3
Room.title       = "Plains of Bone, Mound Top"
Room.description = "Crowning the mound is the rubble of what once was a tower.  Now the black stone lies broken, with only the entrance and lowest portion of the tower still standing.  A doorway darker than the night leads into the tower."

Room.exits = {
    southwest                = 10746,
    go_doorway               = 10748,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
