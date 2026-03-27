-- Zone: Fearling Pass
-- Connects Ta'Vaalor (Amaranth Gate) north across the bridge to the rocky pass beyond
-- Level range: 3-10
local Zone = {}

Zone.id        = 9
Zone.name      = "Fearling Pass"
Zone.region    = "Elanith"
Zone.level_min = 3
Zone.level_max = 10
Zone.climate   = "temperate"
Zone.indoor    = false

function Zone.onLoad()
    print("[Zone] Fearling Pass loaded.")
end

function Zone.onTick(elapsed) end
function Zone.onPlayerEnter(player) end
function Zone.onPlayerLeave(player) end

Zone.ambient_messages = {
    "A stiff wind funnels through the pass, rattling the dry brush along the trail.",
    "The distant cry of a hawk echoes off the stone walls of the ravine.",
    "Loose gravel skitters off the path as you disturb it with your passage.",
    "The trees press close here, their roots cracking the old cobblestone.",
    "A trickle of icy water threads across the trail from some hidden source.",
    "The smell of pine and cold stone fills the air.",
}
Zone.ambient_interval = 110

return Zone
