-- Room 10435: Theatre Andaire, Foyer
local Room = {}

Room.id          = 10435
Room.zone_id     = 2
Room.title       = "Theatre Andaire, Foyer"
Room.description = "Thick Loenthran carpets in rich shades of garnet, sapphire and amber cover the theatre's stone floors, effectively muffling the sound of footfalls.  The granite walls are hung with tapestries depicting mummers, bards and other players in various scenes both comedic and dramatic.  Wall sconces of delicately wrought iron hold glimmering amber glaesine spheres, each containing beeswax candles whose brightly burning wicks cast a golden glow across the room."

Room.exits = {
    out                  = 3504,
    east                 = 10436,
    west                 = 10437,
}

Room.indoor = true
Room.safe   = true

return Room
