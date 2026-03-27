-- Room 10419: Bastille, Entrance Hall
local Room = {}

Room.id          = 10419
Room.zone_id     = 2
Room.title       = "Bastille, Entrance Hall"
Room.description = "Not quite the grim welcome a prisoner might expect at the doorway to incarceration, vivid red and gold banners hang from the surrounding stone walls.  Casting candlelight down from its midst, a wrought iron chandelier hovers overhead, suspended from the high beams of the ceiling.  Several guards pass by, their footsteps clattering harshly on the dark fel wood flooring.  Set into the eastern wall, several barred windows peer out at the city."

Room.exits = {
    out                  = 3501,
    north                = 10420,
}

Room.indoor = true
Room.safe   = true

return Room
