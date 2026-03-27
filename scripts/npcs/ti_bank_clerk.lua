-- NPC: a bank clerk
-- Zone/Town: auto-placed  |  Room: 1838
local NPC = {}

NPC.template_id    = "ti_bank_clerk"
NPC.name           = "a bank clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A dwarven teller built like a vault door who handles silver with practiced authority."
NPC.home_room_id   = 1838

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
    default = "a bank clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
