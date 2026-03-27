-- NPC: a healer
-- Zone/Town: auto-placed  |  Room: 28939
local NPC = {}

NPC.template_id    = "kf_healer_flora"
NPC.name           = "a healer"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A capable healer working the infirmary portion of the flora shop."
NPC.home_room_id   = 28939

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
    default = "a healer doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
