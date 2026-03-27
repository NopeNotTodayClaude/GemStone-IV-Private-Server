-- Room 10425: Helgreth's Tavern, Second Floor
local Room = {}

Room.id          = 10425
Room.zone_id     = 2
Room.title       = "Helgreth's Tavern, Second Floor"
Room.description = "Most of the central area of this spacious room has been cordoned off, leaving a comfortable walkway around its perimeter, replete with padded leather benches and stools.  A trio of burnished chandeliers remain unlit as sunlight streams in through cut-glass windows from all four sides, illuminating the highly detailed, miniaturized terrain of the City-States laid out upon the floor.  A small alcove branches off from the main chamber to the north.  Several wooden cases line the walls, their glass fronts revealing tiny figures within."

Room.exits = {
    go_stair             = 10424,
    north                = 10426,
}

Room.indoor = true
Room.safe   = true

return Room
