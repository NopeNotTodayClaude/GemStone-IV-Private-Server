-- NPC: a town gate guard
-- Zone/Town: auto-placed  |  Room: 1957
local NPC = {}

NPC.template_id    = "ti_gate_guard_ti"
NPC.name           = "a town gate guard"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An armored dwarven guard at the town gates with a no-nonsense expression."
NPC.home_room_id   = 1957

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
    default = "a town gate guard doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
