-- NPC: an Isle Dyes clerk
-- Zone/Town: auto-placed  |  Room: 16323
local NPC = {}

NPC.template_id    = "mh_dye_clerk_isle"
NPC.name           = "an Isle Dyes clerk"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A vibrant merchant whose dyes are inspired by the island's extraordinary flora."
NPC.home_room_id   = 16323

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
    default = "an Isle Dyes clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
