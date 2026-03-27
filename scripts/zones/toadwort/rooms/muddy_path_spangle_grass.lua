-- Room 10500: The Toadwort, Muddy Path
local Room = {}

Room.id          = 10500
Room.zone_id     = 7
Room.title       = "The Toadwort, Muddy Path"
Room.description = "Patches of spangle grass haphazardly dot the mucky soil and their oat-shaped flowers, which dangle from limping leaves, might cause one to think of bats hanging from a belfry.  The blackened and rotting corpse of a fanged goblin is concealed in darkness, as a bank of clouds obscures the light of the moon.  Water continues to ebb and flow along this path from the narrow creek.  Blossoming purple milkweeds line both sides of the creek."

Room.exits = {
    northwest                = 10499,
    down                     = 10501,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
