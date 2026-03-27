-- Room 59050: Scenario 5 - The Beast (Combat)
-- Teaches: ATTACK, STANCE, weapon use, INCANT (spellcasters)

local Room = {}

Room.id          = 59050
Room.zone_id     = 99
Room.title       = "Cave Entrance"
Room.description = "The crimson-lit path terminates at the gaping mouth of a natural cave.  Deep claw marks score the rock around the entrance, and a foul stench rolls out from within.  Bones — animal, you hope — lie scattered across the ground.  This is clearly the lair of something dangerous."

Room.exits = {
    south   = 59002,
    go_cave = 59051,
}

Room.indoor = false
Room.safe   = true

return Room
