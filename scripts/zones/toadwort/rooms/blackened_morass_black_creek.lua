-- Room 10538: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10538
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Clumps of dead grass lie trampled in the mud along a narrow path that leads to a rushing creek of black water.  A fallen, algae-covered tree rests in the creek and hordes of mud whelks are clearly visible as they slowly trek across its trunk.  Along the edge of the creek, scores of tiny crustaceans crawl around in the thick mud."

Room.exits = {
    west                     = 10534,
    north                    = 10537,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
