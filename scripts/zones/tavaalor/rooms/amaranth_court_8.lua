-- Room 3495: Ta'Vaalor, Amaranth Court
local Room = {}

Room.id          = 3495
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Amaranth Court"
Room.description = "A small garden has been cultivated near the exterior wall of Guardian Keep.  Thick towering maoral trees provide shade to a thick carpet of grass surrounded by an abundance of flora.  Fragrant herbs mingle with outrageously colorful flowers, bringing a serenity and cheer to the otherwise austere court."

Room.exits = {
    north                = 3493,
    go_wizard            = 18041,
}

Room.indoor = false
Room.safe   = true

return Room
