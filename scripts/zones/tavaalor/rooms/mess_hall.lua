-- Room 25585: Mess Hall, Dining Area
local Room = {}

Room.id          = 25585
Room.zone_id     = 2
Room.title       = "Mess Hall, Dining Area"
Room.description = "Numerous long oak tables line this large open hall, neatly lined in two rows along the breadth of the room.  A fair number of soldiers can be seen, most sitting and enjoying a hearty meal, while a few stand as they quickly eat a small snack.  At the very north end of the room are a number of large buffets, hosting a variety of foods for any appetite."

Room.exits = {
    out                  = 3500,
    north                = 25584,
}

Room.indoor = true
Room.safe   = true

return Room
