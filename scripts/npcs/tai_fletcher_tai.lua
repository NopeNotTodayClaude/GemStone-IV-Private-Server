-- NPC: a sylvarraend bowyer
-- Zone/Town: auto-placed  |  Room: 10074
local NPC = {}

NPC.template_id    = "tai_fletcher_tai"
NPC.name           = "a sylvarraend bowyer"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A quiet sylvan craftsman producing bows of exceptional quality."
NPC.home_room_id   = 10074

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
    default = "a sylvarraend bowyer doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
