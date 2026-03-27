-- Room 31481: Oceanside Forest, Trail
local Room = {}

Room.id          = 31481
Room.zone_id     = 5
Room.title       = "Oceanside Forest, Trail"
Room.description = "Dark, thick moss encircles a large boulder jutting out of the ground by the roadside.  The massive object fractures the tangled barrier of shrubs and plants growing along the stony trail.  Stands of gigantic trees give way to the landmark, their towering presence sheltering from high above."

Room.exits = {
    north                    = 31480,
    southeast                = 31482,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
