-- Room 10524: The Toadwort, Fetid Muck
local Room = {}

Room.id          = 10524
Room.zone_id     = 7
Room.title       = "The Toadwort, Fetid Muck"
Room.description = "Patches of tri-colored lady-slippers cluster around the bases of buttonwood trees.  Approximately one half of an inch from the sodden ground, the sagging royal blue, white and blood-red pouches of the flowers flutter softly, caressed by the gentlest of breezes.  Two trees have twisted themselves around each other and a thick mat of creeping dogwood has covered their roots.  The gnarly boles of the trees are covered with slimy, bluish mold."

Room.exits = {
    northwest                = 10523,
    southwest                = 10525,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
