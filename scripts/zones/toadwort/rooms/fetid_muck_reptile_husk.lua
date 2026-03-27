-- Room 10520: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10520
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Hanging from a nearby tree branch, a translucent husk from a limbless reptile billows gently on a delicate but foul smelling breeze.  Finger-like tendrils from a rising mist creep slowly over the dampened ground and partially conceal a nest filled with more discarded husks.  Every so often a low, menacing hissing sound is audible near a small body of tea-colored water.  Dead foliage covers the surface of the water."

Room.exits = {
    southwest                = 10519,
    go_stream                = 10521,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
