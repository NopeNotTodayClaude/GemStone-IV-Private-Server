-- Room 3530: Ta'Vaalor, Caerneaes Var
local Room = {}

Room.id          = 3530
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Caerneaes Var"
Room.description = "Thick-caned climbing roses nearly obscure the walls of the nearby cottage, its whitewashed stone peeking out in small patches from behind the draped greenery and heavy red blossoms that trail along its walls.  The cottage's lone window stands open, the diamond-shaped glaesine panes sparkling in the light."

Room.exits = {
    south                = 3529,
    north                = 3531,
    east                 = 3533,
    go_burghal           = 26025,
}

Room.indoor = false
Room.safe   = true

return Room
