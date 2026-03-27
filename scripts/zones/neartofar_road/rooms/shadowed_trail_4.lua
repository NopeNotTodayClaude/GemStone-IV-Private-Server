-- Room 31460: Shadowed Forest, Trail
local Room = {}

Room.id          = 31460
Room.zone_id     = 5
Room.title       = "Shadowed Forest, Trail"
Room.description = "Casting darkened shadows over the woods, the tops of a wide variety of towering, umbrageous trees hinder the light trying to filter down from above.  Thick shrubbery marks the roadway; the tangled barriers show signs of recent cutting with chopped lengths thrown on top of the live plants.  A discord of noises from small, rummaging creatures echoes throughout the gloomy forest."

Room.exits = {
    northwest                = 31459,
    east                     = 31461,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
