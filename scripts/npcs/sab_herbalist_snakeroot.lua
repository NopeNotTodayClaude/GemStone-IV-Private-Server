-- NPC: an apothecary clerk
-- Zone/Town: auto-placed  |  Room: 34652
local NPC = {}

NPC.template_id    = "sab_herbalist_snakeroot"
NPC.name           = "an apothecary clerk"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A darkly robed clerk whose knowledge of herbs extends into less benign applications."
NPC.home_room_id   = 34652

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
    default = "an apothecary clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
