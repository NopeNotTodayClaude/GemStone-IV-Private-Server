-- Room 3542: Ta'Vaalor, Victory Court
-- SUPERNODE: mana flows strongly through this location.
--   +50% HP regen rate
--   x2.0 mana regen rate
--   Sleeping/resting here restores spirit faster
-- Per GS4 wiki: Victory Court is a well-known supernode in Ta'Vaalor.
local Room = {}

Room.id          = 3542
Room.zone_id     = 2
Room.title       = "Ta'Vaalor, Victory Court"
Room.description = "An immense white marble fountain occupies the center of the court.  Perched in its center, a towering statue of Kai stands, holding his sword aloft.  His features have been painted onto the marble surface with pigments and artistry so lifelike, he appears ready to step from the fountain.  A faint hum of mana fills the air, the ground beneath subtly alive with energy."

Room.exits = {
    north = 3519,
    east  = 3541,
    west  = 3543,
    south = 3544,
}

Room.indoor    = false
Room.safe      = true
Room.supernode = true

-- Supernode ambient messages (fired by world event system when implemented)
Room.ambient = {
    "The marble fountain seems to shimmer faintly with an inner light.",
    "You feel a subtle pulse of mana emanate from the ground beneath your feet.",
    "The air around the statue of Kai crackles with a barely perceptible energy.",
    "A faint resonance hums at the edge of your awareness, as if the earth itself breathes.",
    "The fountain water catches the light in ways that seem almost unnatural.",
}

-- Hook: player enters supernode
function Room.onEnter(player)
    if player and player.mana_max and player.mana_max > 0 then
        player:sendLine(
            "  You feel a surge of mana wash over you.  The Victory Court pulses with arcane energy."
        )
    else
        player:sendLine(
            "  The air here feels charged, as though the ground itself radiates subtle power."
        )
    end
end

return Room
