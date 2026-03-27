-- Room 10167: Fearling Pass, Forest Trail
local Room = {}
Room.id          = 10167
Room.zone_id     = 9
Room.title       = "Fearling Pass, Forest Trail"
Room.description = "Snaking out from a narrow crevasse tucked away within a wall of towering boulders, a small stream skirts the edge of the forest trail.  Ancient pines crowd the path on both sides, their roots buckling the earth into natural steps."
Room.exits = {
    go_crevasse              = 10166,
    southeast                = 10168,
}
Room.indoor = false
Room.dark   = false
Room.safe   = false
return Room
