-- Room 5943: Catacombs, Passageway
local Room = {}

Room.id          = 5943
Room.zone_id     = 2
Room.title       = "Catacombs, Passageway"
Room.description = "This huge cavern has cart tracks going in several different directions.  Great cyclopean doors stand at the end of each track.  Only two of them remain open.  One door is covered with moss, and allows easy access to the outside of these tunnels, while the warped door leads to yet another section of the sewers.  Only the tops of the other doors are visible, their bottom halves have been blocked by an earlier avalanche of rock and debris, forever shutting off the section of tunnels that lie behind them."

Room.exits = {
    go_warped_door       = 5941,
    east                 = 5942,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
