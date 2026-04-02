local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")

NPC.template_id = "glaoveln_portmaster"
NPC.name = "the portmaster"
NPC.article = "the"
NPC.title = ""
NPC.description = "A sharp-eyed portmaster watches the Pulct docks with a ledger tucked under one arm and one hand resting on the fare rail."
NPC.home_room_id = 35173
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
NPC.dialogues = { default = "The portmaster tilts the ledger toward you.  'State your harbor.'" }
NPC.ambient_emotes = { "The portmaster runs a thumb down a column of fares and closes the ledger with a dry clap." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

TravelOfficeNPC.attach(NPC, "port_glaoveln")

return NPC
