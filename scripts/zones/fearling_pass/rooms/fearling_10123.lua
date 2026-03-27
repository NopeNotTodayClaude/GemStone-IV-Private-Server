-- Room 10123: Fearling Pass, Rocky Trail
local Room = {}
Room.id          = 10123
Room.zone_id     = 9
Room.title       = "Fearling Pass, Rocky Trail"
Room.description = "Lakebed rocks become more prominent along this offshoot of the trail, as though the ground here was once submerged.  The dark rich soil between the stones is damp and soft.  The trail loops back south or continues northeast into the pass proper."
Room.exits = {
    south                    = 10122,
    northeast                = 10158,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
