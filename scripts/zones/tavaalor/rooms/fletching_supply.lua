-- Room 10363: Vonder's Fletching Supply
local Room = {}

Room.id          = 10363
Room.zone_id     = 2
Room.title       = "Vonder's Fletching Supply"
Room.description = "This well lit chamber holds a variety of fletching supplies.  Stacked bins positioned against the back wall contain vials of paint in all different colors as well as thin paint sticks.  Beside the bins are several barrels of trimmed fletchings in a variety of hues."

Room.exits = {
    north                = 10362,
}

Room.indoor = true
Room.safe   = true

return Room
