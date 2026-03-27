-- NPC: a locksmith
-- Zone/Town: auto-placed  |  Room: 9491
local NPC = {}

NPC.template_id    = "zl_locksmith_zl"
NPC.name           = "a locksmith"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome descendant of a long line of locksmiths who takes pride in the family tradition."
NPC.home_room_id   = 9491

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
    default = "a locksmith doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
