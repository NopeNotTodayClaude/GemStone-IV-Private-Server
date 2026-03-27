-- NPC: a learned scribe
-- Zone/Town: auto-placed  |  Room: 34
local NPC = {}

NPC.template_id    = "tai_elven_scribe"
NPC.name           = "a learned scribe"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An elven scribe carefully copying documents at a small portable desk."
NPC.home_room_id   = 34

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
    default = "a learned scribe doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
