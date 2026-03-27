-- Room 10740: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10740
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "A skeleton lies spread eagle on the dark hill side.  Manacles secure the remains at the wrist and ankles.  A strong night wind occasionally makes the skeleton rattle.  The skeleton is intact except for the skull which is now nothing more than small chips and powdered bone."

Room.exits = {
    northeast                = 10741,
    southwest                = 10739,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
