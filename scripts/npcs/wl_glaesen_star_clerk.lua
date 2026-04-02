local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "wl_glaesen_star_clerk"
NPC.name = "a shipping clerk"
NPC.article = "a"
NPC.title = ""
NPC.description = "A shipping clerk in slate-blue livery keeps a close eye on manifests bound for the Glaesen Star."
NPC.home_room_id = 8899

NPC.can_combat = false
NPC.can_shop = false
NPC.can_wander = false
NPC.can_emote = true
NPC.can_chat = false
NPC.can_loot = false
NPC.is_guild = false
NPC.is_quest = false
NPC.is_house = false
NPC.is_bot = false
NPC.is_invasion = false

NPC.dialogues = {
    travel = "If you're Kharam-Dzu bound, say so.  If not, step clear of the counter.",
    fares = "The Glaesen Star does not sail on goodwill.",
    default = "The shipping clerk smooths a fresh manifest.  'Name your destination.'",
}
NPC.ambient_emotes = {
    "The shipping clerk folds a route slip and stamps it with practiced force.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "wl_airship")

return NPC
