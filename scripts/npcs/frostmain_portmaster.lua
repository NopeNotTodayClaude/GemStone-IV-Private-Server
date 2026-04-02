local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "frostmain_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A cold-eyed portmaster stamps boots against the frost-dark planks while waiting for the next request."
NPC.home_room_id = 32372
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster exhales a plume of white breath.  'Harbor?'" }
NPC.ambient_emotes = { "The portmaster raps a gloved knuckle against a crate and listens to the hollow sound." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_frostmain")
return NPC
