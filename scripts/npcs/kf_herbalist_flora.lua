-- NPC: a flora merchant
-- Zone/Town: auto-placed  |  Room: 28938
local NPC = {}

NPC.template_id    = "kf_herbalist_flora"
NPC.name           = "a flora merchant"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A skilled herbalist whose intoxicating flora shop carries remedies for every ailment."
NPC.home_room_id   = 28938

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
    default = "a flora merchant doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
