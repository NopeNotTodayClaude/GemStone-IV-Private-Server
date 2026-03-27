-- Room 10516: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10516
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Moonlight shines through the heavy fog that blankets the ground, making it appear as if the fog itself glows with an inner white light.  Yellow grass conceals fallen twigs and branches, which snap and crackle underfoot.  From a distance, the sounds of bubbling water and low growls fill the air."

Room.exits = {
    east                     = 10515,
    west                     = 10517,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
