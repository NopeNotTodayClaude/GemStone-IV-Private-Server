-- Room 10722: Plains of Bone, Boneyard
local Room = {}

Room.id          = 10722
Room.zone_id     = 3
Room.title       = "Plains of Bone, Boneyard"
Room.description = "A large patch of brambles engulfs this section of the boneyard, a nasty surprise for those careless in their nighttime travels.  The long thorns mix with sharpened bones to create a dangerous display.  The broken remains of an ancient rowboat have nearly been consumed by the thorny vines."

Room.exits = {
    north                    = 10721,
    south                    = 10723,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
