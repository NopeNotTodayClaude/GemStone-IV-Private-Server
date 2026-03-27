-- Room 10502: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10502
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "Standing taller than the average halfling, yellow-eyed grass stretches out as far as the eye can see.  At the tops of very long stalks, beautiful specimens of their cone-like flower clusters sway back and forth gently in the slight breeze.  Underfoot lies dead and decaying grass and leaves that have been trampled into the mud by the passage of both man and beast."

Room.exits = {
    up                       = 10499,
    down                     = 10503,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
