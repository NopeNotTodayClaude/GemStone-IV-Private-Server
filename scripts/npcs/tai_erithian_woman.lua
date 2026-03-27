-- NPC: a light-robed erithian woman
-- Zone/Town: auto-placed  |  Room: 179
local NPC = {}

NPC.template_id    = "tai_erithian_woman"
NPC.name           = "a light-robed erithian woman"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An erithian woman in flowing robes who moves through the city with graceful assurance."
NPC.home_room_id   = 179

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
    default = "a light-robed erithian woman doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
