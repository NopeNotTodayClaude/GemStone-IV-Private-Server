-- NPC: a locksmith
-- Zone/Town: auto-placed  |  Room: 28935
local NPC = {}

NPC.template_id    = "kf_locksmith_kf"
NPC.name           = "a locksmith"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome locksmith who arrived on the island to crack one safe and never left."
NPC.home_room_id   = 28935

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
    default = "a locksmith doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
