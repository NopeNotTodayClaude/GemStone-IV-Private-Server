-- Room 28335: Bard Guild, Hallway
local Room = {}

Room.id          = 28335
Room.zone_id     = 2
Room.title       = "Bard Guild, Hallway"
Room.description = "The rich cherrywood paneling of this long hallway is punctuated by polished brass sconces, whose steady glow reflects from the ivory coffered ceiling.  A thick wool runner, woven in jewel-hued shades of green and blue, muffles the footsteps of passersby from the scholars of the adjacent library."

Room.exits = {
    south                = 10438,
    north                = 28338,
}

Room.indoor = true
Room.safe   = true

return Room
