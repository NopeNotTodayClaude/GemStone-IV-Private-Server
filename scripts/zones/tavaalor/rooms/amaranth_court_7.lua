-- Room 3494: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3494
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "A small stonework cottage sits near the wey, a cobblestone path leading straight into its front door.  The cottage's stone walls have been painted with a pale gold wash, and the door stained a deep crimson.  A thick maoral sign swings from the doorpost."

Room.exits = {
    east                 = 3493,
    west                 = 3484,
    go_jeweler           = 10327,
}

Room.indoor = false
Room.safe   = true

return Room
