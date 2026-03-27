-- NPC: a forge clerk
-- Zone/Town: auto-placed  |  Room: 13270
local NPC = {}

NPC.template_id    = "tai_forge_clerk_tai"
NPC.name           = "a forge clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A precise elven clerk managing the forging supply shop."
NPC.home_room_id   = 13270

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
    default = "a forge clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
