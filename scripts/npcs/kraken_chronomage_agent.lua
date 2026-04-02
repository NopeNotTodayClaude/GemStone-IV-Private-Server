local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "kraken_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A sea-weathered agent stands beside the transportation arch with a bundle of sealed passes."
NPC.home_room_id = 28965
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
NPC.dialogues = { default = "The agent hooks a thumb toward the booth.  'Destination?'" }
NPC.ambient_emotes = { "The chronomage agent seals a folded pass with a quick press of one thumbnail." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_kraken")

return NPC
