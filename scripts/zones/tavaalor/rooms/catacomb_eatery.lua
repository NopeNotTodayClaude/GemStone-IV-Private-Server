-- Room 5910: Catacombs, Eatery
local Room = {}

Room.id          = 5910
Room.zone_id     = 2
Room.title       = "Catacombs, Eatery"
Room.description = "A gentle breeze from the open hatch above creates enough disturbances in the air to send tiny particles of dust and dirt sailing through the air.  An old wood burner is slumped over onto its side in the far corner of the room.  A wooden bowl still contains the molded remnants of the last meal served in this morbid place."

Room.exits = {
    go_hatch             = 5909,
    south                = 5911,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
