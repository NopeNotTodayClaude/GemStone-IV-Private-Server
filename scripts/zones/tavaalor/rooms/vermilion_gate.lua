-- Room 5827: Ta'Vaalor, Vermilion Gate
local Room = {}

Room.id          = 5827
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Vermilion Gate"
Room.description = "A massive stone wall rises high above, crennelated along the top of the city's last defense as far as the eye can see.  As it reaches the surface of the river the wall disappears into the murky depths of the Mistydeep, leaving no hint as to how far down the stonework may go.  The wall is pierced by the Vermilion Gate, a large ironwork gate above which the crest of House Vaalor is deeply carved into limestone blocks.  Decorated with rich dark red enamel and lined with pure gold, the crest glitters opulently."

Room.exits = {
    west                     = 3490,
    northeast                = 5828,
    go_gate                  = 5828,
}

Room.indoor = false
Room.safe   = true

return Room
