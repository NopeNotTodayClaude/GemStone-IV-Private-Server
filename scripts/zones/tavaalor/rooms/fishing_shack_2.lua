-- Room 14032: Ta'Vaalor, Fishing Shack
local Room = {}

Room.id          = 14032
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Fishing Shack"
Room.description = "Many sizes of pots and pans hang on the walls and rest on the shelves that are mounted on all four walls of the room.  Various cooking ingredients ranging from salt to packages of herbs are haphazardly placed wherever they fit.  A large hole has been cut in the middle of the shack floor, and the opening has been lined with darkened stones, creating a firepit where a pitted iron spit stands over a small fire."

Room.exits = {
    west                 = 13482,
}

Room.indoor = true
Room.safe   = true

return Room
