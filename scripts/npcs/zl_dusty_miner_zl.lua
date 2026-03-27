-- NPC: a dusty miner
-- Zone/Town: auto-placed  |  Room: 9422
local NPC = {}

NPC.template_id    = "zl_dusty_miner_zl"
NPC.name           = "a dusty miner"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A dwarf returning from a deep vein with ore dust on every surface."
NPC.home_room_id   = 9422

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
    default = "a dusty miner doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
