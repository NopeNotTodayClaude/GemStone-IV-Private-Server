local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "ornath_chronomage_agent"
NPC.name = "a chronomage agent"
NPC.article = "a"
NPC.title = ""
NPC.description = "An urbane agent waits on the manor floor above the transit alcove."
NPC.home_room_id = 35431
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
NPC.dialogues = { default = "The agent glances toward the veranda doors.  'Ticket or pass?'" }
NPC.ambient_emotes = { "The chronomage agent flicks a speck of salt from a neatly folded travel paper." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_ornath")

return NPC
