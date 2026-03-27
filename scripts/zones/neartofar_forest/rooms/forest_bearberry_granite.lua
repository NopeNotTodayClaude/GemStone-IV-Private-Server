-- Room 10649: Neartofar Forest
local Room = {}

Room.id          = 10649
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "Some bearberry bushes grow in a dense thicket around a peculiar granite outcropping.  Scraped by the passage of a glacier some aeons ago, the stone's rough edges are covered with a matting of thick, black hair.  Paw prints in the loamy soil beside the rock suggest that bears frequent this area."

Room.exits = {
    southeast                = 10648,
    northwest                = 10650,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
