-- Room 5913: Catacombs, Tunnels
local Room = {}

Room.id          = 5913
Room.zone_id     = 2
Room.title       = "Catacombs, Tunnels"
Room.description = "An ungodly funk permeates throughout this chamber, and the reason for the stench rests along the southern wall.  Slumped in the corner rests the decaying corpse of a fallen warrior.  In his hands, he still clutches his instruments of warfare.  Pity, for they obviously did very little to fend off whatever may have killed him."

Room.exits = {
    go_door              = 5912,
    east                 = 5914,
}

Room.indoor = true
Room.safe   = false
Room.dark   = true

return Room
