-- NPC: a Gaunt's Run broker
-- Zone/Town: auto-placed  |  Room: 34679
local NPC = {}

NPC.template_id    = "sab_pawnbroker_sab"
NPC.name           = "a Gaunt's Run broker"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A calculating merchant who buys and sells without sentiment."
NPC.home_room_id   = 34679

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
    default = "a Gaunt's Run broker doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
