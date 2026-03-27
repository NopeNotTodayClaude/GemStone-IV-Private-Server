-- Room 10373: Ta'Vaalor, Garden of Ancients
local Room = {}

Room.id          = 10373
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Garden of Ancients"
Room.description = "Delicately formed stargazer lilies proudly wave their pink blossoms above beds filled with creeping thyme, fragrant rosemary, sweet buttercups, and pale lavender verbena.  A nearby birdbath provides the musical accompaniment of trickling water, as the statue in the bath's bowl pours a bubbling stream into the basin."

Room.exits = {
    out                  = 3540,
    south                = 10374,
}

Room.indoor = false
Room.safe   = true

return Room
