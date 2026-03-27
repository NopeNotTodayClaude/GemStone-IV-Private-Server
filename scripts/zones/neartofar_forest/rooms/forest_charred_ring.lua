-- Room 10647: Neartofar Forest
local Room = {}

Room.id          = 10647
Room.zone_id     = 6
Room.title       = "Neartofar Forest"
Room.description = "A charred ring of stones to one side of the trail is the likely source of the fire that damaged this section of the forest.  The soil is covered with a layer of ash, and all but the largest oak and maple trees were destroyed by the flame.  The hoary old veterans of the forest are scarred, but alive ... perhaps indicating that a flash rain quenched the fire before it developed into a conflagration."

Room.exits = {
    southwest                = 10642,
    northeast                = 10646,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
