local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "ti_chronomage_clerk"
NPC.name = "a chronomage clerk"
NPC.article = "a"
NPC.title = ""
NPC.description = "An immaculate clerk stands in the niche beside a humming transit focus."
NPC.home_room_id = 13169
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
NPC.dialogues = { default = "The clerk's expression never shifts.  'Destination?'" }
NPC.ambient_emotes = { "The chronomage clerk adjusts a transit crystal until its glow steadies." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70

TravelOfficeNPC.attach(NPC, "chrono_ti")

return NPC
