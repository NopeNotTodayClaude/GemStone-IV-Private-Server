---------------------------------------------------
-- Ta'Vaalor
-- Fortress city of the Vaalor Elves
-- Military stronghold, disciplined and orderly
-- Level range: 1-25
---------------------------------------------------

local Zone = {}

Zone.id        = 2
Zone.name      = "Ta'Vaalor"
Zone.region    = "Elanith"
Zone.level_min = 1
Zone.level_max = 25
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Ta'Vaalor loaded.")
end

function Zone.onTick(elapsed)
end

function Zone.onPlayerEnter(player)
end

function Zone.onPlayerLeave(player)
end

Zone.ambient_messages = {
    "The steady march of an elven patrol echoes through the streets.",
    "A crimson banner bearing the Vaalor crest snaps crisply in the wind.",
    "An elven soldier stands at rigid attention as you pass.",
    "The scent of polished steel and leather drifts from a nearby armory.",
    "Distant horns sound from the battlements, marking the changing of the guard.",
    "The clatter of training swords rings from the direction of the barracks.",
    "An elven citizen passes by, chin held high with quiet pride.",
}

Zone.ambient_interval = 90

return Zone
