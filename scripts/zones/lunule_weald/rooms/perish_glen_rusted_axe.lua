-- Room 10583: Lunule Weald, Perish Glen
local Room = {}

Room.id          = 10583
Room.zone_id     = 8
Room.title       = "Lunule Weald, Perish Glen"
Room.description = "A rusted axe blade, the handle missing, is buried into the trunk of one of the trees. The sap from the once living tree has solidified around the blade, making it immovable.  A dark, reddish-brown crescent moon has been painted around the blade."

Room.exits = {
    northeast                = 10580,
    northwest                = 10581,
    west                     = 10582,
    southeast                = 10588,
    southwest                = 10591,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
