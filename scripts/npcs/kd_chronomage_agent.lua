local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "kd_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A dwarven chronomage agent keeps a row of marked transit passes sorted by destination."
NPC.home_room_id = 12790
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
NPC.dialogues = { default = "The agent looks up from a slate board of departures.  'Ticket or pass?'" }
NPC.ambient_emotes = { "The chronomage agent taps a transit crystal against a stone counter and listens to the tone." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_kd")

return NPC
