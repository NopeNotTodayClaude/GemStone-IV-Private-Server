-- Room 34464: Bee-utimous
local Room = {}

Room.id          = 34464
Room.zone_id     = 5
Room.title       = "Bee-utimous"
Room.description = "The lattice-woven walls of oak and laurel are washed in honey-colored paint, the amber and gilded tones complemented by enamel flowers interspersed between the crossed beams of wood.  A trio of beehive-shaped lanterns are nestled at the far corner of the stacked stone counter, the display firmly positioned in the center of the shop.  Short wood-planked racks are scattered along the periphery, filled from top to bottom with bolts of undyed fabric."

Room.exits = {
    out                      = 34461,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
