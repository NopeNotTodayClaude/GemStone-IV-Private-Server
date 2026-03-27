-- Room 10509: The Toadwort, Grasping Mire
local Room = {}

Room.id          = 10509
Room.zone_id     = 7
Room.title       = "The Toadwort, Grasping Mire"
Room.description = "Aerial roots streaming down from the mangrove have formed a close-growing thicket.  Dense thorns at least six inches long cover the roots.  A small oval-shaped opening appears at the base of the mangrove bed and it is possible that its center would provide adequate shelter from the elements.  Clearly, the thorns would easily rend the flesh of anyone who was desperate enough to try to crawl through the opening."

Room.exits = {
    northeast                = 10508,
    northwest                = 10510,
    down                     = 10511,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
