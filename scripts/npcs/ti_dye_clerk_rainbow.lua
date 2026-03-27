-- NPC: a rainbow tent clerk
-- Zone/Town: auto-placed  |  Room: 14815
local NPC = {}

NPC.template_id    = "ti_dye_clerk_rainbow"
NPC.name           = "a rainbow tent clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A cheerful halfling managing the dye tent with an eye for bold color combinations."
NPC.home_room_id   = 14815

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
    default = "a rainbow tent clerk doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
