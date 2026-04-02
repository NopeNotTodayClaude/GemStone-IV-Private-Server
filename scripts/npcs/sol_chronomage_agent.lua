local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "sol_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A sharply dressed agent watches the beacon chamber with detached professional calm."
NPC.home_room_id = 14358
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
NPC.dialogues = { default = "The agent folds their hands.  'Ticket or pass?  Name the town.'" }
NPC.ambient_emotes = { "The chronomage agent checks the beacon's pulse and records a note in a thin ledger." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_sol")

return NPC
