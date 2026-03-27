-- Room 31459: Shadowed Forest, Trail
local Room = {}

Room.id          = 31459
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Cover from the entwined branches of the massive trees that fill the forest allows very little light to pass down to the moist leaves that blanket the ground below.  Thick brush lines the narrow road, while a wide array of debris hides thick roots that make travel treacherous.  Rustling leaves high above blend with the sounds of creaking branches."

Room.exits = {
    northwest                = 31458,
    southeast                = 31460,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
