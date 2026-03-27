-- Room 10368: Annatto Rations Shop
local Room = {}

Room.id          = 10368
Room.zone_id     = 2
Room.title       = "Annatto Rations Shop"
Room.description = "A long counter, manned by a flour-dusted young elf, runs the length of the room, displaying the various rations for sale.  Savory smells of roasting meat, baking bread and pungent spices drift from behind a set of swinging doors in the back wall.  Occasionally, the dark, rich scent of chocolate wafts in from the kitchen, but there are no chocolates laid out on the display counter."

Room.exits = {
    out                  = 3524,
}

Room.indoor = true
Room.safe   = true

return Room
