-- Room 10619: Lunule Weald, Zealot Village
local Room = {}

Room.id          = 10619
Room.zone_id     = 8
Room.title       = "Lunule Weald, Zealot Village"
Room.description = "Only two rotting, wooden walls remain standing of what was once a small home.  Painted all over the walls, both inside and out, are strange pictures, symbols and gibberish words.  Broken pottery and bits of furniture peek out from under the rotting leaves and decaying debris on the dirt floor."

Room.exits = {
    southeast                = 10617,
    south                    = 10618,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
