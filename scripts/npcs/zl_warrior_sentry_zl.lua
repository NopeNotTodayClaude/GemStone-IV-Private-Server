-- NPC: a Zul Logoth warrior
-- Zone/Town: auto-placed  |  Room: 16917
local NPC = {}

NPC.template_id    = "zl_warrior_sentry_zl"
NPC.name           = "a Zul Logoth warrior"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An armored dwarven warrior on the iron walkway watching for trouble."
NPC.home_room_id   = 16917

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
    default = "a Zul Logoth warrior doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
