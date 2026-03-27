-- NPC: Empath Sargassa
-- Zone/Town: auto-placed  |  Room: 5723
local NPC = {}

NPC.template_id    = "sol_sargassa"
NPC.name           = "Empath Sargassa"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A composed empath whose calm demeanor has a steadying effect on anyone who enters her infirmary."
NPC.home_room_id   = 5723

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
    default = "Empath Sargassa doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
