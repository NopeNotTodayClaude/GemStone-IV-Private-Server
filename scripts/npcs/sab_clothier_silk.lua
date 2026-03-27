-- NPC: a silk and shade clerk
-- Zone/Town: auto-placed  |  Room: 34655
local NPC = {}

NPC.template_id    = "sab_clothier_silk"
NPC.name           = "a silk and shade clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A sleek merchant whose clothing carries subtle Lornon-affiliated designs."
NPC.home_room_id   = 34655

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
    default = "a silk and shade clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
