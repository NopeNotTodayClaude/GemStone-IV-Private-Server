-- Room 24511: Alabaster Bastion, Atrium
local Room = {}

Room.id          = 24511
Room.zone_id     = 2
Room.title       = "Alabaster Bastion, Atrium"
Room.description = "The atrium is tucked into a hollow at the center of the building, forming a pocket of shelter surrounded on all four sides by walls of white stone.  The brittle stalks of dead Vines wrap and wind around the legs of a pair of marble benches, and threaten to choke the base of a stone socle.  Above, the view of the sky is unobstructed.  Above, the view of the sky is unobstructed, though the light of several alabaster-shaded lanterns casts a glow that hides all but the brightest of the stars."

Room.exits = {
    west                 = 24512,
    east                 = 24514,
}

Room.indoor = true
Room.safe   = true

return Room
