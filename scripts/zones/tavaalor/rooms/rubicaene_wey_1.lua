-- Room 3503: Ta'Vaalor, Rubicaene Wey
local Room = {}

Room.id          = 3503
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Rubicaene Wey"
Room.description = "The bustle of the airship docks occasionally ascends into a deafening roar, as shouting sailors climb ship riggings, and dock workers operate winches and nets to move cargo to and from the various vessels.  Foremen and ship captains alike yell orders to the workers, their voices carrying above the din.  A thick metal grate is set into the cobbled street."

Room.exits = {
    south                = 3504,
    north                = 3502,
    southwest            = 3505,
    climb_grate          = 5909,
    go_terminus          = 30286,
}

Room.indoor = false
Room.safe   = true

return Room
