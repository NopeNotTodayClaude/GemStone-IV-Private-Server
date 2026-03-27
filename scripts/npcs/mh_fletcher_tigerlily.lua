-- NPC: a Tigerlily bowyer
-- Zone/Town: auto-placed  |  Room: 16365
local NPC = {}

NPC.template_id    = "mh_fletcher_tigerlily"
NPC.name           = "a Tigerlily bowyer"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A skilled craftsman producing bows suited to the island's humid climate."
NPC.home_room_id   = 16365

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
    default = "a Tigerlily bowyer doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
