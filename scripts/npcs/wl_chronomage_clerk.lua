local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "wl_chronomage_clerk"
NPC.name = "a chronomage clerk"
NPC.article = "a"
NPC.title = ""
NPC.description = "A pale clerk tends a nest of folded transit papers and humming crystals."
NPC.home_room_id = 8634
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
    travel = "Chronomage travel is clean, costly, and very rarely forgiving.",
    pass = "Ask for a pass if you need repeated jumps between two offices.",
    ticket = "A ticket is good for one clean jump.",
    default = "The chronomage clerk regards you over a stack of crystal-marked papers.  'Where to?'",
}
NPC.ambient_emotes = {
    "The chronomage clerk aligns two crystal slips until they hum in the same pitch.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_wl")

return NPC
