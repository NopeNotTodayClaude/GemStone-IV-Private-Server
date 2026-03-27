-- NPC: Kilron
-- Zone/Town: auto-placed  |  Room: 408
local NPC = {}

NPC.template_id    = "wl_kilron"
NPC.name           = "Kilron"
NPC.article        = ""
NPC.title          = "pawnbroker"
NPC.description    = "A weathered half-elf with a jeweler's loupe perched above one eye."
NPC.home_room_id   = 408

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
    default = "Kilron doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
