-- Room 3504: Ta'Vaalor, Rubicaene Wey
local Room = {}

Room.id          = 3504
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Rubicaene Wey"
Room.description = "The elegant facade of the Ta'Vaalor Theatre towers above, its ornate carvings and gargoyles reminiscent of the architectural style of the Illistim.  Grinning and leering statues perch atop the window embrasures and doorframes, and the waterspouts have been carved into stylized representations of plant life.  A large silver plaque is mounted beside the front doors."

Room.exits = {
    north                = 3503,
    south                = 3508,
    go_theatre           = 10435,
}

Room.indoor = false
Room.safe   = true

return Room
