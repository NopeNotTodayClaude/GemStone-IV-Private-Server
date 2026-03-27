-- Room 10522: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10522
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Groves of dead trees occupy a fair-sized nearby reef, their branches swaying briskly back and forth, though there is no perceptible wind.  The soil, from which the trees managed to thrive even though for a short time, is of a loose powdery consistency.  A nest is perched precariously on a lone, lifeless bush, its roots protruding from the soil.  Though none are in plain sight from here, the sad crying song of the limpkin can be heard at intermittent periods."

Room.exits = {
    down                     = 10521,
    southeast                = 10523,
    southwest                = 10529,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
