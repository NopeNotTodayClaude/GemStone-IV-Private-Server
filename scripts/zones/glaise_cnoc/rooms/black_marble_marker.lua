-- Room 29575: Glaise Cnoc, Cemetery
local Room = {}

Room.id          = 29575
Room.zone_id     = 3
Room.title       = "Glaise Cnoc, Cemetery"
Room.description = "Sunlight shines down upon a black marble marker, set into the ground amid a meadow of gently swaying flowers.  The marker is worn with age, but the inscription is still legible.  The sweet smell of wildflowers and the hypnotic humming of bees create a seductive setting."

Room.exits = {
    northeast                = 29574,
    southwest                = 5882,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
