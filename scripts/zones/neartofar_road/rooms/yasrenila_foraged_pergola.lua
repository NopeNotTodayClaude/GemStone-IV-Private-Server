-- Room 34463: Freshly Foraged, Pergola
local Room = {}

Room.id          = 34463
Room.zone_id     = 5
Room.title       = "Freshly Foraged, Pergola"
Room.description = "Blending natural greenery with handcrafted art, ivory-veined ivy winds about the scrollworked legs of the whorled birch pergola, allowing only glimpses of the flora and fauna etched into the lacquered wood.  Glass jars strung with pastel ribbons hang from the crossbeams, the flame-tipped tealights within bringing a warm, flickering glow to a slatted knotty elm table flanked by matching benches."

Room.exits = {
    go_doorway               = 34462,
}

Room.indoor      = true
Room.dark        = false
Room.safe        = true
Room.supernode   = false
Room.climbable   = false

return Room
