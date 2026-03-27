-- NPC: a robed figure
-- Zone/Town: auto-placed  |  Room: 13350
local NPC = {}

NPC.template_id    = "tai_rogue_contact_tai"
NPC.name           = "a robed figure"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A figure seated in the arboretum who watches visitors with quiet assessment."
NPC.home_room_id   = 13350

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    rogue = "The arboretum is quiet enough for the right kind of conversation.",
    guild = "The guild hears from every city.  Use GLD if you need the formal ledger.",
    training = "Lock Mastery and Gambits separate a merely sneaky rogue from a polished one.",
    quest = "Use GLD QUEST START if you want the guild to lay out your next proving ground.",
    default = "The robed figure folds slender hands and waits.  'If you have guild business, speak it.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
