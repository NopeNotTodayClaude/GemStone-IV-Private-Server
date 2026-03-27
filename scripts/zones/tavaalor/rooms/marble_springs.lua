-- Room 10343: Marble Springs, Arch
local Room = {}

Room.id          = 10343
Room.zone_id     = 2
Room.title       = "Marble Springs, Arch"
Room.description = "An elegant archway of grey-veined, pale white marble stands as a solemn attendant at the entrance to this small, riverside neighborhood.  Embraced by the thriving local flora, the lower portions of the marble columns have become entangled in flower-laden vines and lush, leafy creepers, whose natural beauty and slender tendrils seem to add to the quiet dignity of the carven stone."

Room.exits = {
    southwest            = 10344,
    southeast            = 10346,
}

Room.indoor = true
Room.safe   = true

return Room
