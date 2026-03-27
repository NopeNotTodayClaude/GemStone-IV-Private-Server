-- Room 10664: Neartofar Forest, Stockade
local Room = {}

Room.id          = 10664
Room.zone_id     = 6
Room.title       = "Neartofar Forest, Stockade"
Room.description = "The uppermost log in the outer wall has been rubbed smooth in several places, perhaps by sentries habitually resting their arms as they maintain their watch over the northern approach.  From this vantage, it appears likely that the skeleton impaled on the palisade below jumped--or was dropped--from this position.  In the far distance to the north, the Timmorain Road can be seen shining in the moonlight like the finest veniom thread."

Room.exits = {
    down                     = 10663,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
