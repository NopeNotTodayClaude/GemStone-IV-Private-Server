-- Room 5912: Catacombs, Workroom
local Room = {}

Room.id          = 5912
Room.zone_id     = 2
Room.title       = "Catacombs, Workroom"
Room.description = "Abandoned machinery, clearly decades old, lies scattered about in this chamber.  Apparently, their owners just dropped them where they stood as they hastily vacated the area.  Along the western wall, a small, mostly rusted cart lies on its side.  Hordes of small gelatinous creatures slither and squirm about on the inside of the cart.  An old, woebegone door stands slightly ajar."

Room.exits = {
    north                = 5911,
    go_door              = 5913,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
