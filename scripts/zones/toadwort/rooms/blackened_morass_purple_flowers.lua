-- Room 10535: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10535
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "A thicket of odd-shaped purple flowers stand sentinel over a burrow directly below it.  Tufts of fur cling to the tiny barbs that protrude from the flowers' stems.  Paw prints in the mud lead both to and from the burrow and a gnawed bone lies partially buried not far from its entrance.  Off in the distance, deep guttural growls and snarls are audible."

Room.exits = {
    south                    = 10534,
    north                    = 10536,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
