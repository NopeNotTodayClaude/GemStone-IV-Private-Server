local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "tv_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A severe elven chronomage agent keeps a meticulous stack of transit forms and crystal-marked spheres at the ready."
NPC.home_room_id = 5883
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
    travel = "Chronomage travel runs on schedule, not on impatience.",
    ticket = "A travel orb is for the next scheduled departure.  Hold it in your right hand in the waiting room.",
    pass = "A day pass can be raised for immediate travel from the proper departure room.",
    default = "The chronomage agent folds slender hands atop the counter.  'State your destination.'",
}
NPC.ambient_emotes = {
    "The chronomage agent rolls a brass-flecked orb between gloved fingers until it emits a steady hum.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_tv")

return NPC
