-- Room 10743: Plains of Bone, Virktoth's Path
local Room = {}

Room.id          = 10743
Room.zone_id     = 3
Room.title       = "Plains of Bone, Virktoth's Path"
Room.description = "The slope of the stairway increases uncomfortably, the risers becoming higher steadily.  The steps become narrower, nothing more than room to place toes or fingers during descent or ascent.  A few iron rings anchored to the outside edge of the stairway still hold their black paint, moonlight glinting from their rustless metal."

Room.exits = {
    east                     = 10742,
    west                     = 10744,
}

Room.indoor      = false
Room.dark        = true
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
