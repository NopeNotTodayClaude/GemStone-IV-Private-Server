-- NPC: Peddler Gertie
-- Zone/Town: auto-placed  |  Room: 223
local NPC = {}

NPC.template_id    = "wl_peddler_gertie"
NPC.name           = "Peddler Gertie"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A stout halfling woman with an enormous pack and aggressive salesmanship."
NPC.home_room_id   = 223

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
    default = "Peddler Gertie doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
