-- Room 10512: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10512
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "As one of the moons pokes its face through the clouds, a dozen bald cypress trees encircling an ancient burial ground come into view.  A multitude of stone caskets are scattered around the cemetery.  None of the stone caskets bears any marking to tell the tale of its occupant.  Some of the tombs lay wide open, as their covers have broken down to nothing more than dust and pebbles over the years."

Room.exits = {
    west                     = 10511,
    northeast                = 10513,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
