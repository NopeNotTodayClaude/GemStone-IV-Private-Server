-- Room 10533: The Toadwort, Blackened Morass
local Room = {}

Room.id          = 10533
Room.zone_id     = 7
Room.title       = "The Toadwort, Blackened Morass"
Room.description = "Smoke rises in thick, choking vines from the depth of a hollow cavity in the ground.  A stench like that of sulfur and burning flesh punishes the air.  A narrow thread of land spirals downward into the pit.  Huge shiny pieces of ore are embedded into its walls and are illuminated by a particularly bright moonbeam.  The ground surrounding the pit is dry and sandy and completely devoid of life."

Room.exits = {
    west                     = 10532,
    east                     = 10534,
    north                    = 10539,
}

Room.indoor      = false
Room.dark        = false
Room.safe        = false
Room.supernode   = false
Room.climbable   = false

return Room
