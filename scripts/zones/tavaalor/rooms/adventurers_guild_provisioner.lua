-- Room 10333: Adventurers' Guild, Provisioner
local Room = {}

Room.id          = 10333
Room.zone_id     = 2
Room.title       = "Adventurers' Guild, Provisioner"
Room.description = "Stacks of crates, boxes, and bins crowd the floor of this large alcove, as rich an assortment to the eye as the pungent smells of tar, new leather and cured meats are to the nose.  Behind a long counter at the far end, an old elf bustles about, his stature so bent that he might be mistaken for a tall burghal gnome."

Room.exits = {
    south                = 10331,
}

Room.indoor = true
Room.safe   = true

return Room
