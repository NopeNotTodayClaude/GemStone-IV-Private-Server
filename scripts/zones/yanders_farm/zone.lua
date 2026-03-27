-- Zone: Yander's Farm
local Zone = {}

Zone.id        = 100
Zone.name      = "Yander's Farm"
Zone.region    = "Elanith"
Zone.level_min = 10
Zone.level_max = 14
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Yander's Farm loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "The wheat bends in long, golden waves as the wind crosses the field.",
    "A rooster crows from somewhere near the distant barn.",
    "The smell of manure and fresh-turned earth is pervasive.",
    "Crows wheel noisily over the corn, driven away by nothing visible.",
    "The ruts of wagon wheels track through the mud of the farm road.",
    "Something has been at the turnip patch — the rows are churned and scattered.",
    "The barley is nearly head-height, offering plenty of concealment.",
    "A dog barks from the direction of the farmhouse, then falls silent.",
    "The corn stands tall enough to hide a man — or something considerably larger.",
    "Harvest time has left the fields half-stripped and disheveled.",
}

Zone.ambient_interval = 120

return Zone
