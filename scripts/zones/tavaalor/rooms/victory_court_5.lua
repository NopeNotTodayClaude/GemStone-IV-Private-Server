-- Room 3542: Ta'Vaalor, Victory Court
local Room = {}

Room.id          = 3542
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "An immense white marble fountain occupies the center of the court.  Perched in its center, a towering statue of Kai stands, holding his sword aloft.  His features have been painted onto the marble surface with pigments and artistry so lifelike, he appears ready to step from the fountain."

Room.exits = {
    north                = 3519,
    east                 = 3541,
    west                 = 3543,
    south                = 3544,
}

Room.indoor = false
Room.safe   = true

return Room
