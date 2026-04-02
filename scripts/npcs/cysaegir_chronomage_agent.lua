local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "cysaegir_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "A silver-haired agent stands within the disk's faintly resonant field."
NPC.home_room_id = 17130
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
NPC.dialogues = { default = "The agent waits in the disk's glow.  'State the office you need.'" }
NPC.ambient_emotes = { "The chronomage agent traces a slow circle through the disk's pale light." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_cysa")

return NPC
