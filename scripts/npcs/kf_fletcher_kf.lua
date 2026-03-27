-- NPC: a Storm Petrel bowyer
-- Zone/Town: auto-placed  |  Room: 29130
local NPC = {}

NPC.template_id    = "kf_fletcher_kf"
NPC.name           = "a Storm Petrel bowyer"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A craftsman specializing in bows for use at sea."
NPC.home_room_id   = 29130

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
    default = "a Storm Petrel bowyer doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
