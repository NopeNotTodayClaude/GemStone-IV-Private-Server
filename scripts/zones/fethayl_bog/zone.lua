-- Zone: Fethayl Bog
local Zone = {}

Zone.id        = 127
Zone.name      = "Fethayl Bog"
Zone.region    = "Elanith"
Zone.level_min = 44
Zone.level_max = 48
Zone.climate   = "swamp"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Fethayl Bog loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The bog breathes out a cold, sulphurous exhalation.",
    "Pale lights drift above the waterlogged ground, directionless and silent.",
    "The surface of a dark pool ripples with no visible cause.",
    "Something old and unseen watches from the mist.",
    "Dead reeds rattle with a sound like dry bones.",
    "The mud here makes a sound like a last breath when disturbed.",
    "A faint keening rises from somewhere deeper in the bog, then stops.",
    "The cold here has a quality beyond mere temperature.",
    "Waterlogged timber shows the marks of something with very large hands.",
    "Mist pools in the low places, shifting as though alive.",
}

Zone.ambient_interval = 120

return Zone
