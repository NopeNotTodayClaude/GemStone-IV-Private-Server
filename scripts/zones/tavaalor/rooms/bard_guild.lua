-- Room 10438: Bard Guild, Entry
local Room = {}

Room.id          = 10438
Room.zone_id     = 2
Room.title       = "Bard Guild, Entry"
Room.description = "Slender oak columns frame this grand entry hall, whose pale granite walls rise the full two stories of the building.  The columns support a second floor gallery, reached by a sweeping staircase and bordered by a heavily carved balustrade from which are hung dozens of banners bearing crests of ancient elven families.  The east and west walls are pierced by tall, lancet-topped leaded glass windows, through which dappled sunlight pours into the hall."

Room.exits = {
    out                  = 3508,
    north                = 28335,
}

Room.indoor = true
Room.safe   = true

return Room
