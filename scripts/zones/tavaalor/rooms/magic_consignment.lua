-- Room 10365: Elantaran's Magic, Consignment
local Room = {}

Room.id          = 10365
Room.zone_id     = 2
Room.title       = "Elantaran's Magic, Consignment"
Room.description = "Filled with many miscellaneous, alchemic products, storage bins are neatly organized throughout the room.  An orb-chased candle chandelier hangs from above, offering a source of illumination.  Two shop attendants wander about, taking inventory and keeping a watchful eye."

Room.exits = {
    east                 = 10364,
    north                = 10366,
}

Room.indoor = true
Room.safe   = true

return Room
