-- Room 10369: Hall of the Arkati, Entry
local Room = {}

Room.id          = 10369
Room.zone_id     = 2
Room.title       = "Hall of the Arkati, Entry"
Room.description = "Fluted white marble columns hold up a high-arched, plastered ceiling.  Exquisite frescoes are painted across the expanse of plaster, reflecting the night sky of Elanith with her myriad moons and constellations.  Several mithglin lanterns line the edges of the rooms, each containing a small white votive that sheds just enough light to illuminate the artwork."

Room.exits = {
    out                  = 3539,
    west                 = 10370,
    south                = 10371,
}

Room.indoor = true
Room.safe   = true

return Room
