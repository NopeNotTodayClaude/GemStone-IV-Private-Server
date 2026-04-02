local NPC = {}
local TravelOfficeNPC = require("globals.travel_office_npc")
NPC.template_id = "mistwatch_portmaster"
NPC.name = "the portmaster"
NPC.article = ""
NPC.title = ""
NPC.description = "A stern portmaster stands where sea trade meets the Elven Nations' quay."
NPC.home_room_id = 31493
NPC.can_combat = false NPC.can_shop = false NPC.can_wander = false NPC.can_emote = true NPC.can_chat = false NPC.can_loot = false NPC.is_guild = false NPC.is_quest = false NPC.is_house = false NPC.is_bot = false NPC.is_invasion = false
NPC.dialogues = { default = "The portmaster gestures toward the posted fares.  'State the harbor.'" }
NPC.ambient_emotes = { "The portmaster smooths a curled corner of the harbor fare board." }
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 70
TravelOfficeNPC.attach(NPC, "port_mistwatch")
return NPC
