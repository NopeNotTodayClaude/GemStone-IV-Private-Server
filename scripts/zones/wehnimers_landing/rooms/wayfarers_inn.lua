-- Room 127: Wayfarer's Inn
local Room = {}

Room.id          = 127
Room.zone_id     = 1
Room.title       = "Wayfarer's Inn, Common Room"
Room.description = "The common room of the Wayfarer's Inn is warm and welcoming.  A roaring fire blazes in a massive stone hearth, and the smell of roasting meat fills the air.  Heavy oak tables and benches fill the room, most occupied by weary travelers and locals sharing tales over mugs of ale.  A staircase leads up to the guest rooms."

Room.exits = {
    out = 117,
}

Room.indoor = true
Room.safe   = true

return Room
