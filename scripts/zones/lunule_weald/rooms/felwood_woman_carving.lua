-- Room 10565: Lunule Weald, Felwood Grove
local Room = {}

Room.id          = 10565
Room.zone_id     = 8
Room.title       = "Lunule Weald, Felwood Grove"
Room.description = "The figure of a woman has been carved into the living bark of one of the trees.  The woman's shape is long and thin, her face lined and haggard.  The bark of other trees has also been carved with symbols, letters and different shapes.  Thick sap flows slowly from the carvings, making them appear to be weeping."

Room.exits = {
    west                     = 10564,
    south                    = 10566,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
