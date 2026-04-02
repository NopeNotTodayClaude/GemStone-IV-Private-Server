local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "imt_chronomage_halfling"
NPC.name = "a halfling chronomage"
NPC.article = "a"
NPC.title = ""
NPC.description = "A round-faced halfling chronomage keeps transit papers tucked into color-coded sleeves."
NPC.home_room_id = 8916
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
NPC.dialogues = { default = "The halfling chronomage taps a sheaf of passes.  'Town name, please.'" }
NPC.ambient_emotes = { "The halfling chronomage flips a transit pass over and checks its crystal watermark." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_imt")

return NPC
