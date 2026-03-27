-- Room 10652: Neartofar Forest
local Room = {}

Room.id          = 10652
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Beaked hazelnut shrubs grow to a height of nine feet in the spaces between some towering oaks.  The ground is littered with thin, brittle shells long since emptied of their contents by the birds and squirrels that frequent the thicket.  A faint trail leads to the northwest, curving around a wooden signpost that stands, oddly enough, in the center of the thicket."

Room.exits = {
    southwest                = 10651,
    northeast                = 10653,
    northwest                = 10658,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
