-- Room 3538: Ta'Vaalor, Shimaerslin Wey
local Room = {}

Room.id          = 3538
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Shimaerslin Wey"
Room.description = "A limestone-clad structure stands back from the wey, its pale ivory walls delicately carved with symbols of the Arkati.  Narrow windows of stained glaes frame the building's wide double doors.  A small mithril plaque is mounted on the doorpost."

Room.exits = {
    north                = 3539,
    south                = 3537,
}

Room.indoor = false
Room.safe   = true

return Room
