-- Room 10537: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10537
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Thick, elongated tufts of bearded grass blanket the floor and tiny granular particles from them float serenely through the air.  Flickering shadows dance across enormous mottled eggs that are resting in a nest of dead grass and leaves.  The bottom of the nest is littered with strange looking triangular seeds that seem ready to burst open and spray their contents over the eggs at any given moment."

Room.exits = {
    northwest                = 10536,
    south                    = 10538,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
