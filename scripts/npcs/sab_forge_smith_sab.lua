-- NPC: a smith
-- Zone/Town: auto-placed  |  Room: 34690
local NPC = {}

NPC.template_id    = "sab_forge_smith_sab"
NPC.name           = "a smith"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A skilled metalworker at the Matters of Metal smithy."
NPC.home_room_id   = 34690

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
    default = "a smith doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
