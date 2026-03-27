-- NPC: Bushybrow
-- Zone/Town: auto-placed  |  Room: 28940
local NPC = {}

NPC.template_id    = "kf_pawnbroker_kf"
NPC.name           = "Bushybrow"
NPC.article        = ""
NPC.title          = "pawnbroker"
NPC.description    = "A halfling pawnbroker with extravagant eyebrows and a fair dealing reputation."
NPC.home_room_id   = 28940

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
    default = "Bushybrow doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
