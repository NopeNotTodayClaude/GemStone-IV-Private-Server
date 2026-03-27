-- NPC: Big Snorri
-- Zone/Town: auto-placed  |  Room: 1856
local NPC = {}

NPC.template_id    = "ti_fletcher_snorri"
NPC.name           = "Big Snorri"
NPC.article        = ""
NPC.title          = "master bowyer"
NPC.description    = "A massive dwarf whose large hands move with surprising delicacy when crafting a bow."
NPC.home_room_id   = 1856

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
    default = "Big Snorri doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
