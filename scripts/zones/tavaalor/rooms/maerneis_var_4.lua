-- Room 3537: Ta'Vaalor, Maerneis Var
local Room = {}

Room.id          = 3537
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Maerneis Var"
Room.description = "Clusters of cottages crowd the edge of the cobbled var, each vying for a scrap of the limited sunlight skittering over the high city walls nearby.  Though closely spaced, the cottages show no sign of neglect, each one painted a pale hue and possessing windowboxes that brim with bright blossoms."

Room.exits = {
    west                 = 3536,
    north                = 3538,
    go_repose            = 33340,
}

Room.indoor = false
Room.safe   = true

return Room
