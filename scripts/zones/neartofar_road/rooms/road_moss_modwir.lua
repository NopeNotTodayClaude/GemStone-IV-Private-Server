-- Room 31452: Neartofar Road
local Room = {}

Room.id          = 31452
Room.zone_id     = 5
Room.title       = "Neartofar Road"
Room.description = "Lanky moss drapes on the branches of tall modwir trees growing in a thick stand.  A few broken cobblestones peek from beneath a layer of dirt and moss.  Dense greenery cover the forest floor with its thick, verdant clusters."

Room.exits = {
    northwest                = 31451,
    southeast                = 31453,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
