-- Room 10340: Ta'Vaalor Historical Society
local Room = {}

Room.id          = 10340
Room.zone_id     = 2
Room.title       = "Ta'Vaalor Historical Society"
Room.description = "Heavy wood paneling topped with egg and dart molding lines the walls of this broad hallway.  A claw-footed roll top desk presides at one end, while at the other stands a gilded and enameled suit of platemail.  Snapdragons nod brightly in a porcelain vase underneath a round window."

Room.exits = {
    north                = 10341,
    west                 = 10342,
}

Room.indoor = true
Room.safe   = true

return Room
