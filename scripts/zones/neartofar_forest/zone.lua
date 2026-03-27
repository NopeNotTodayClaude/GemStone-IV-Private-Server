-- Zone 6: Neartofar Forest
local Zone = {}

Zone.id        = 6
Zone.name      = "Neartofar Forest"
Zone.region    = "Elanith"
Zone.level_min = 10
Zone.level_max = 20
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad() print("[Zone] Neartofar Forest loaded.") end
function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The massive oaks and elms stand in dignified silence overhead.",
    "A chipmunk darts across the trail and vanishes into the undergrowth.",
    "Wind hisses softly through the upper branches, scattering oak leaves.",
    "Owls call from somewhere deep in the canopy, their voices echoing.",
    "The acrid smell of mold and decay rises from the deep leaf detritus.",
    "Juniper berries perfume the air with a sharp, resinous fragrance.",
    "Squirrels chitter unseen from behind a veil of chestnut leaves.",
    "A boar's distant rooting noise drifts through the trees.",
}
Zone.ambient_interval = 120

return Zone
