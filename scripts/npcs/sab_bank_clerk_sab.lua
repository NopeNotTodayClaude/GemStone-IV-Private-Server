-- NPC: Grigg
-- Zone/Town: auto-placed  |  Room: 34680
local NPC = {}

NPC.template_id    = "sab_bank_clerk_sab"
NPC.name           = "Grigg"
NPC.article        = ""
NPC.title          = "countinghouse keeper"
NPC.description    = "A meticulous accountant who keeps the countinghouse's books in perfect order."
NPC.home_room_id   = 34680

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
    default = "Grigg doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
