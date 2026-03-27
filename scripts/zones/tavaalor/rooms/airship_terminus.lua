-- Room 30286: Ta'Vaalor, Airship Terminus
local Room = {}

Room.id          = 30286
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Airship Terminus"
Room.description = "A constant stream of passengers flows through this long, narrow room, transmitting a nervous energy as they bustle on their way to or from the loading docks.  A small queue has formed in front of the ticket windows, where elves and sullen dwarves wait impassively, with a smattering of humans and other outlanders among them.  Those with tickets move intently up a wide staircase to one side.  At the other end of the room, porters come and go through a broad archway, bearing light cargo of various sorts."

Room.exits = {
    out                  = 3503,
}

Room.indoor = true
Room.safe   = true

return Room
