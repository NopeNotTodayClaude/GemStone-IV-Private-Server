-- Room 10379: Ta'Vaalor Antique Goods
local Room = {}

Room.id          = 10379
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Antique Goods"
Room.description = "Beautiful gold sconces adorn both sides of the doorway in this quaint little shop.  A frosted glass cabinet, resting in the center of the royal-blue carpeting, holds an assortment of beautiful glass figurines.  An elegant emerald-green tapestry with gold stitching covers the wall above the fireplace.  Emptied of its cargo, a fair-sized gold chest lies on its side.  Its contents have been strewn haphazardly on the floor behind the counter."

Room.exits = {
    out                  = 3522,
    east                 = 10380,
}

Room.indoor = true
Room.safe   = true

return Room
