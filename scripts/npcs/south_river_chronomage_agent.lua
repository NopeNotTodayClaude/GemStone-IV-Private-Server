local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "south_river_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A road-worn agent leans beside the carved opening in the giant stump, transit papers tucked into a weatherproof folio."
NPC.home_room_id = 16115
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
NPC.dialogues = { default = "The agent brushes bark dust from a pass.  'Which office?'" }
NPC.ambient_emotes = { "The chronomage agent checks the grain of the fallen giant as if listening for a distant pulse." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_south_river")

return NPC
