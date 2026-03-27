-- NPC: a bank teller
-- Zone/Town: auto-placed  |  Room: 16411
local NPC = {}

NPC.template_id    = "mh_bank_clerk_mh"
NPC.name           = "a bank teller"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An efficient teller managing island finances."
NPC.home_room_id   = 16411

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    default = "a bank teller doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
