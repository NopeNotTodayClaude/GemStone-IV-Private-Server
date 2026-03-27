-- Room 10434: Locksmith
local Room = {}

Room.id          = 10434
Room.zone_id     = 2
Room.title       = "Locksmith"
Room.description = "The wooden walls are bare except for unfinished shelves adorned with locks and lockpicks of every variety.  A frayed red carpet covers the center of the room, leaving the bare wooden slats exposed around the border of the floor.  The walls and floor of the building creak and groan as patrons move about the store.  Beside the counter, a battered wooden board is covered in chalked entries listing box descriptions and offered fees — the picking queue, maintained by Shind himself.  A small hand-lettered sign reads: GOT A LOCKED BOX?  SUBMIT IT.  ROGUES: BOXPICK TO SEE OPEN JOBS."

Room.exits = {
    out                  = 3502,
}

Room.indoor = true
Room.safe   = true

return Room
