-- Room 3529: Ta'Vaalor, Jacinthea Wey
local Room = {}

Room.id          = 3529
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Jacinthea Wey"
Room.description = "A dark stone cottage sits nearby, tendrils of creeping fig grasping at the structure's deep grey stones as they imperil visibility from the cottage's lone window.  The entire affair is saved from dourness by the brightly painted crimson door.  A small mithril plaque swings from the doorpost."

Room.exits = {
    south                = 3528,
    north                = 3530,
    go_magic             = 10364,
}

Room.indoor = false
Room.safe   = true

return Room
