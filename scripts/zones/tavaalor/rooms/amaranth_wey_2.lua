-- Room 3484: Ta'Vaalor, Amaranth Wey
local Room = {}

Room.id          = 3484
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Wey"
Room.description = "The wey branches off in several directions, the bustling crowd splitting as they pursue their various courses.  Haon bushes line the edges of the limestone cobbles, their neatly trimmed branches forming a tight phalanx to keep passersby on the road.  A large limestone building stands off to the side, with a constant flow of travelers heading in and out.  Two city guardsmen stand next to a mithril gate, eyeing everyone suspiciously."

Room.exits = {
    west                 = 3483,
    northeast            = 3485,
    east                 = 3494,
    go_travel            = 10302,
    go_barracks          = 27919,
}

Room.indoor = false
Room.safe   = true

return Room
