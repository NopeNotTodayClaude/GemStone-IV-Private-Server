-- NPC: Sister Cocytel
-- Zone/Town: auto-placed  |  Room: 9506
local NPC = {}

NPC.template_id    = "zl_healer_cocytel"
NPC.name           = "Sister Cocytel"
NPC.article        = ""
NPC.title          = "healer"
NPC.description    = "A dwarven healer whose hospice is a model of underground efficiency."
NPC.home_room_id   = 9506

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
    default = "Sister Cocytel doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
