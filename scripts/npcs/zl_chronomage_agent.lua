local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "zl_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A cave gnome agent stands beside the white arch, one hand resting on a bundle of transit slips."
NPC.home_room_id = 9550
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
NPC.dialogues = { default = "The agent gives you a brisk nod.  'Speak the destination clearly.'" }
NPC.ambient_emotes = { "The chronomage agent brushes cave dust from a transit slip and tucks it away again." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_zl")

return NPC
